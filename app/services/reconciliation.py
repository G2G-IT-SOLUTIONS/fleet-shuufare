from datetime import datetime, timezone, date, timedelta
from typing import Optional
from sqlmodel import Session, select, or_
from app.models import Driver, TelebirrTransaction, DriverTrip, DepositTripLink, ReconciliationBatch, SystemConfig

def get_shift_windows(db: Session, driver_shift: str, target_date: date):
    """
    Returns (trip_start, trip_end, deposit_start, deposit_end) for a driver's shift on a target date.
    All returned values are timezone-aware in UTC.
    """
    # Fetch shift times from config
    day_start_c = db.get(SystemConfig, "SHIFT_DAY_START")
    day_end_c = db.get(SystemConfig, "SHIFT_DAY_END")
    night_start_c = db.get(SystemConfig, "SHIFT_NIGHT_START")
    night_end_c = db.get(SystemConfig, "SHIFT_NIGHT_END")
    
    day_start_str = day_start_c.value if day_start_c else "06:00"
    day_end_str = day_end_c.value if day_end_c else "18:00"
    night_start_str = night_start_c.value if night_start_c else "18:00"
    night_end_str = night_end_c.value if night_end_c else "06:00"
    
    # Parse times
    def parse_time(t_str):
        try:
            h, m = map(int, t_str.split(":"))
            return h, m
        except:
            return 0, 0
        
    dh_start, dm_start = parse_time(day_start_str)
    dh_end, dm_end = parse_time(day_end_str)
    nh_start, nm_start = parse_time(night_start_str)
    nh_end, nm_end = parse_time(night_end_str)
    
    if driver_shift == "Day":
        trip_start = datetime.combine(target_date, datetime.min.time().replace(hour=dh_start, minute=dm_start)).replace(tzinfo=timezone.utc)
        trip_end = datetime.combine(target_date, datetime.min.time().replace(hour=dh_end, minute=dm_end)).replace(tzinfo=timezone.utc)
        
        deposit_start = trip_start
        # Deposit window runs until the start of the next Day shift
        deposit_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time().replace(hour=dh_start, minute=dm_start)).replace(tzinfo=timezone.utc)
        
    elif driver_shift == "Night":
        trip_start = datetime.combine(target_date, datetime.min.time().replace(hour=nh_start, minute=nm_start)).replace(tzinfo=timezone.utc)
        # Night shift ends on the next calendar day
        trip_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time().replace(hour=nh_end, minute=nm_end)).replace(tzinfo=timezone.utc)
        
        deposit_start = trip_start
        # Deposit window runs until the start of the next Night shift
        deposit_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time().replace(hour=nh_start, minute=nm_start)).replace(tzinfo=timezone.utc)
        
    else: # "None" or fallback
        trip_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        trip_end = datetime.combine(target_date, datetime.max.time().replace(microsecond=0)).replace(tzinfo=timezone.utc)
        deposit_start = trip_start
        deposit_end = trip_end
        
    return trip_start, trip_end, deposit_start, deposit_end

def recalculate_trip_status(trip: DriverTrip) -> str:
    """Helper to determine the correct reconciliation status based on deposited vs price."""
    price = trip.price or 0.0
    if trip.deposited_amount <= 0:
        return "Pending"
    elif trip.deposited_amount >= price and price > 0:
        if trip.deposited_amount > price + 0.01:
            return "Excess Deposit"
        return "Verified"
    elif trip.deposited_amount > 0 and trip.deposited_amount < price:
        return "Partial Deposit"
    return "Pending"

def process_telebirr_deposit(
    db: Session,
    transaction_id: str,
    amount: float,
    timestamp: datetime,
    operator_id: Optional[str] = None,
    phone: Optional[str] = None,
    yango_driver_id: Optional[str] = None,
    merchant_id: str = "SYSTEM_UPLOAD",
    status: str = "Completed",
    opposite_party: Optional[str] = None,
    batch_id: Optional[int] = None
) -> dict:
    """
    Core logic to record a Telebirr transaction and reconcile it against a driver's pending trips.
    Uses amount matching first, falls back to FIFO. Applies time constraints.
    Always stores the transaction.
    """
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    # 1. Idempotency Check (with lock for webhooks if possible, but simple check first)
    # SQLAlchemy doesn't easily do INSERT ON CONFLICT DO NOTHING across all dialects in a simple way
    # We will check if it exists. In a high concurrency environment, we'd use a unique constraint and handle IntegrityError
    existing_tx = db.exec(select(TelebirrTransaction).where(TelebirrTransaction.transaction_id == transaction_id)).first()
    if existing_tx:
        return {"status": "skipped", "message": f"Transaction {transaction_id} already exists."}

    tx = TelebirrTransaction(
        transaction_id=transaction_id,
        amount=amount,
        sender_identifier=operator_id or yango_driver_id or phone or "UNKNOWN",
        merchant_id=merchant_id,
        timestamp=timestamp,
        status=status,
        opposite_party=opposite_party,
        is_reconciled=False
    )
    
    # 2. Find the driver
    driver = None
    if operator_id:
        driver = db.exec(select(Driver).where(Driver.operator_id == operator_id)).first()
    elif yango_driver_id:
        driver = db.exec(select(Driver).where(Driver.yango_driver_id == yango_driver_id)).first()
    elif phone:
        driver = db.exec(select(Driver).where(Driver.phone == phone)).first()
        
    trips_reconciled = 0
    
    if driver:
        tx.driver_id = driver.id
        remaining_deposit = amount
        
        # Get pending cash trips ordered by booked_at, optionally enforcing booked_at < timestamp
        enforce_seq_conf = db.get(SystemConfig, "RECONCILE_ENFORCE_TIME_SEQUENCE")
        enforce_seq = enforce_seq_conf.value.lower() == "true" if enforce_seq_conf else True
        
        stmt = select(DriverTrip).where(
            DriverTrip.driver_id == driver.id,
            DriverTrip.payment_method == "cash",
            DriverTrip.reconciliation_status != "Verified",
            DriverTrip.status == "complete"
        )
        if enforce_seq:
            stmt = stmt.where(DriverTrip.booked_at < timestamp)
        
        if driver.reconciliation_start_date:
            stmt = stmt.where(DriverTrip.booked_at >= datetime.combine(driver.reconciliation_start_date, datetime.min.time()).replace(tzinfo=timezone.utc))
            
        pending_trips = db.exec(stmt.order_by(DriverTrip.booked_at.asc())).all()
        
        # Phase 1: Exact Amount Matching (1-to-1)
        matched_trip = None
        for trip in pending_trips:
            trip_price = trip.price or 0.0
            amount_needed = trip_price - trip.deposited_amount
            
            # Allow a small float tolerance
            if abs(amount - amount_needed) < 0.01:
                matched_trip = trip
                break
                
        # Phase 2: Closest-Amount Matching (1-to-1 fallback)
        if not matched_trip and pending_trips:
            # Find the single trip whose needed amount is closest to the deposit amount
            # Tie-breaker is the older trip (booked_at ascending)
            trips_with_needed = []
            for t in pending_trips:
                needed = (t.price or 0.0) - t.deposited_amount
                trips_with_needed.append((t, needed))
                
            if trips_with_needed:
                matched_trip, _ = min(
                    trips_with_needed,
                    key=lambda x: (abs(x[1] - amount), x[0].booked_at)
                )
                
        if matched_trip:
            # Apply the entire deposit to this single matched trip
            matched_trip.deposited_amount += amount
            matched_trip.reconciliation_status = recalculate_trip_status(matched_trip)
            db.add(matched_trip)
            
            link = DepositTripLink(
                transaction_id=transaction_id,
                trip_id=matched_trip.id,
                amount_applied=amount,
                batch_id=batch_id
            )
            db.add(link)
            trips_reconciled = 1
            tx.is_reconciled = True
            
    # Always save the transaction
    db.add(tx)
    
    return {
        "status": "success",
        "driver_found": bool(driver),
        "driver_name": driver.name if driver else None,
        "trips_reconciled": trips_reconciled,
        "amount": amount,
        "is_reconciled": tx.is_reconciled
    }

def reverse_batch(db: Session, batch_id: int) -> dict:
    """
    Undoes all reconciliations linked to a specific batch.
    Reverts trip amounts and statuses, deletes links, marks transactions as unreconciled.
    """
    batch = db.get(ReconciliationBatch, batch_id)
    if not batch:
        return {"status": "error", "message": "Batch not found."}
        
    if batch.status == "reversed":
        return {"status": "error", "message": "Batch is already reversed."}
        
    links = db.exec(select(DepositTripLink).where(DepositTripLink.batch_id == batch_id)).all()
    
    trips_affected = set()
    txs_affected = set()
    
    for link in links:
        trip = db.get(DriverTrip, link.trip_id)
        if trip:
            trip.deposited_amount = max(0, trip.deposited_amount - link.amount_applied)
            trip.reconciliation_status = recalculate_trip_status(trip)
            db.add(trip)
            trips_affected.add(trip.id)
            
        txs_affected.add(link.transaction_id)
        db.delete(link)
        
    for tx_id in txs_affected:
        tx = db.exec(select(TelebirrTransaction).where(TelebirrTransaction.transaction_id == tx_id)).first()
        if tx:
            # Check if this tx still has other links (shouldn't if it was all in this batch, but just in case)
            other_links = db.exec(select(DepositTripLink).where(DepositTripLink.transaction_id == tx_id, DepositTripLink.batch_id != batch_id)).first()
            if not other_links:
                tx.is_reconciled = False
                db.add(tx)
                
    batch.status = "reversed"
    batch.reversed_at = datetime.utcnow()
    db.add(batch)
    
    return {
        "status": "success",
        "trips_reverted": len(trips_affected),
        "transactions_unreconciled": len(txs_affected)
    }

def reconcile_driver_unreconciled_deposits(db: Session, driver_id: int) -> int:
    """
    Takes all completed but unreconciled Telebirr deposits for a driver,
    and matches them against pending cash trips using the 1-to-1 matching logic.
    Returns the number of trips successfully reconciled.
    """
    driver = db.get(Driver, driver_id)
    if not driver:
        return 0
        
    # Get all completed but unreconciled transactions for the driver
    unreconciled_txs = db.exec(
        select(TelebirrTransaction)
        .where(TelebirrTransaction.driver_id == driver_id)
        .where(TelebirrTransaction.is_reconciled == False)
        .where(TelebirrTransaction.status == "Completed")
        .order_by(TelebirrTransaction.timestamp.asc())
    ).all()
    
    if not unreconciled_txs:
        return 0
        
    trips_reconciled = 0
    enforce_seq_conf = db.get(SystemConfig, "RECONCILE_ENFORCE_TIME_SEQUENCE")
    enforce_seq = enforce_seq_conf.value.lower() == "true" if enforce_seq_conf else True
    
    for tx in unreconciled_txs:
        # Fetch pending cash trips dynamically in each iteration to avoid matching the same trip twice
        stmt = select(DriverTrip).where(
            DriverTrip.driver_id == driver_id,
            DriverTrip.payment_method == "cash",
            DriverTrip.reconciliation_status != "Verified",
            DriverTrip.status == "complete"
        )
        if enforce_seq:
            stmt = stmt.where(DriverTrip.booked_at < tx.timestamp)
        
        if driver.reconciliation_start_date:
            stmt = stmt.where(DriverTrip.booked_at >= datetime.combine(driver.reconciliation_start_date, datetime.min.time()).replace(tzinfo=timezone.utc))
            
        pending_trips = db.exec(stmt.order_by(DriverTrip.booked_at.asc())).all()
        
        if not pending_trips:
            continue
            
        # Phase 1: Exact Amount Matching (1-to-1)
        matched_trip = None
        for trip in pending_trips:
            trip_price = trip.price or 0.0
            amount_needed = trip_price - trip.deposited_amount
            
            # Allow a small float tolerance
            if abs(tx.amount - amount_needed) < 0.01:
                matched_trip = trip
                break
                
        # Phase 2: Closest-Amount Matching (1-to-1 fallback)
        if not matched_trip and pending_trips:
            trips_with_needed = []
            for t in pending_trips:
                needed = (t.price or 0.0) - t.deposited_amount
                trips_with_needed.append((t, needed))
                
            if trips_with_needed:
                matched_trip, _ = min(
                    trips_with_needed,
                    key=lambda x: (abs(x[1] - tx.amount), x[0].booked_at)
                )
                
        if matched_trip:
            # Apply the entire deposit to this single matched trip
            matched_trip.deposited_amount += tx.amount
            matched_trip.reconciliation_status = recalculate_trip_status(matched_trip)
            db.add(matched_trip)
            
            link = DepositTripLink(
                transaction_id=tx.transaction_id,
                trip_id=matched_trip.id,
                amount_applied=tx.amount,
                batch_id=None # Post-sync auto-reconciliation has no CSV batch ID
            )
            db.add(link)
            
            tx.is_reconciled = True
            db.add(tx)
            
            trips_reconciled += 1
            
    return trips_reconciled
