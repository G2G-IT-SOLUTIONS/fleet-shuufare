from datetime import datetime, timezone, date, timedelta
from typing import Optional, Tuple
from sqlmodel import Session, select, or_
from app.models import Driver, TelebirrTransaction, DriverTrip, DepositTripLink, ReconciliationBatch, SystemConfig

def _parse_shift_times(db: Session):
    """Read shift boundary times from SystemConfig and return parsed (hour, minute) tuples."""
    day_start_c = db.get(SystemConfig, "SHIFT_DAY_START")
    day_end_c = db.get(SystemConfig, "SHIFT_DAY_END")
    night_start_c = db.get(SystemConfig, "SHIFT_NIGHT_START")
    night_end_c = db.get(SystemConfig, "SHIFT_NIGHT_END")

    def _parse(t_str, fallback_h, fallback_m):
        try:
            h, m = map(int, t_str.split(":"))
            return h, m
        except:
            return fallback_h, fallback_m

    day_start = _parse(day_start_c.value if day_start_c else "07:00", 7, 0)
    day_end   = _parse(day_end_c.value   if day_end_c   else "19:00", 19, 0)
    night_start = _parse(night_start_c.value if night_start_c else "19:00", 19, 0)
    night_end   = _parse(night_end_c.value   if night_end_c   else "07:00", 7, 0)

    return day_start, day_end, night_start, night_end


def get_shift_windows(db: Session, driver_shift: str, target_date: date):
    """
    Returns (trip_start, trip_end, deposit_start, deposit_end) for a driver's shift on a target date.
    All returned values are timezone-aware in UTC.
    """
    (dh_s, dm_s), (dh_e, dm_e), (nh_s, nm_s), (nh_e, nm_e) = _parse_shift_times(db)
    eat = timezone(timedelta(hours=3))

    if driver_shift == "Day":
        trip_start = datetime.combine(target_date, datetime.min.time().replace(hour=dh_s, minute=dm_s)).replace(tzinfo=eat)
        trip_end   = datetime.combine(target_date, datetime.min.time().replace(hour=dh_e, minute=dm_e)).replace(tzinfo=eat)
        deposit_start = trip_start
        deposit_end   = datetime.combine(target_date + timedelta(days=1), datetime.min.time().replace(hour=dh_s, minute=dm_s)).replace(tzinfo=eat)

    elif driver_shift == "Night":
        trip_start = datetime.combine(target_date, datetime.min.time().replace(hour=nh_s, minute=nm_s)).replace(tzinfo=eat)
        trip_end   = datetime.combine(target_date + timedelta(days=1), datetime.min.time().replace(hour=nh_e, minute=nm_e)).replace(tzinfo=eat)
        deposit_start = trip_start
        deposit_end   = datetime.combine(target_date + timedelta(days=1), datetime.min.time().replace(hour=nh_s, minute=nm_s)).replace(tzinfo=eat)

    else:
        trip_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=eat)
        trip_end   = datetime.combine(target_date, datetime.max.time().replace(microsecond=0)).replace(tzinfo=eat)
        deposit_start = trip_start
        deposit_end   = trip_end

    return trip_start.astimezone(timezone.utc), trip_end.astimezone(timezone.utc), deposit_start.astimezone(timezone.utc), deposit_end.astimezone(timezone.utc)



def recalculate_trip_status(trip: DriverTrip) -> str:
    """Helper to determine the correct reconciliation status based strictly on deposited vs cash_collected."""
    target_amount = trip.cash_collected if trip.cash_collected is not None else 0.0
    if trip.deposited_amount <= 0:
        return "Pending"
    elif trip.deposited_amount >= target_amount and target_amount > 0:
        if trip.deposited_amount > target_amount + 0.01:
            return "Excess Deposit"
        return "Verified"
    elif trip.deposited_amount > 0 and trip.deposited_amount < target_amount:
        return "Partial Deposit"
    return "Pending"

def process_telebirr_deposit(
    db: Session,
    transaction_id: str,
    amount: float,
    timestamp: datetime,
    status: str = "Completed",
    operator_id: Optional[str] = None,
    yango_driver_id: Optional[str] = None,
    phone: Optional[str] = None,
    merchant_id: str = "SYSTEM_UPLOAD",
    opposite_party: Optional[str] = None,
    batch_id: Optional[int] = None
) -> dict:
    """
    Core logic to record a Telebirr transaction and reconcile it against a driver's pending trips.
    Uses the driver's shift to scope which trips are eligible, then applies amount matching
    (exact first, closest-amount fallback). Only stores the transaction if it matches a trip.
    """
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    # 1. Idempotency Check
    existing_tx = db.exec(select(TelebirrTransaction).where(TelebirrTransaction.transaction_id == transaction_id)).first()
    if existing_tx:
        return {"status": "skipped", "message": f"Transaction {transaction_id} already exists."}

    # 2. Find the driver
    driver = None
    if operator_id:
        driver = db.exec(select(Driver).where(Driver.operator_id == operator_id)).first()
    elif yango_driver_id:
        driver = db.exec(select(Driver).where(Driver.yango_driver_id == yango_driver_id)).first()
    elif phone:
        driver = db.exec(select(Driver).where(Driver.phone == phone)).first()

    if not driver:
        return {
            "status": "success",
            "driver_found": False,
            "driver_name": None,
            "trips_reconciled": 0,
            "amount": amount,
            "is_reconciled": False
        }

    # 3. Search all pending cash trips up to the deposit timestamp
    stmt = select(DriverTrip).where(
        DriverTrip.driver_id == driver.id,
        DriverTrip.payment_method == "cash",
        DriverTrip.reconciliation_status != "Verified",
        DriverTrip.status == "complete",
        DriverTrip.deposited_amount == 0.0,
        DriverTrip.booked_at <= timestamp
    )

    if driver.reconciliation_start_date:
        stmt = stmt.where(DriverTrip.booked_at >= datetime.combine(driver.reconciliation_start_date, datetime.min.time()).replace(tzinfo=timezone.utc))

    pending_trips = db.exec(stmt.order_by(DriverTrip.booked_at.desc())).all()

    # Phase 1: Exact Amount Matching (1-to-1)
    matched_trip = None
    for trip in pending_trips:
        target_amount = trip.cash_collected if trip.cash_collected is not None else 0.0
        amount_needed = target_amount - trip.deposited_amount

        # Allow a small float tolerance
        if abs(amount - amount_needed) < 0.01:
            matched_trip = trip
            break

    # Phase 2: Closest-Amount Matching (1-to-1 fallback)
    if not matched_trip and pending_trips:
        trips_with_needed = []
        for t in pending_trips:
            target_amt = t.cash_collected if t.cash_collected is not None else 0.0
            needed = target_amt - t.deposited_amount
            trips_with_needed.append((t, needed))

        if trips_with_needed:
            matched_trip, _ = min(
                trips_with_needed,
                # Prefer closest amount; on tie, prefer the most RECENT trip
                key=lambda x: (abs(x[1] - amount), -(x[0].booked_at.timestamp() if x[0].booked_at else 0))
            )

    # 4. Only store the transaction if it matched a trip
    if not matched_trip:
        return {
            "status": "success",
            "driver_found": True,
            "driver_name": driver.name,
            "trips_reconciled": 0,
            "amount": amount,
            "is_reconciled": False
        }

    # Store transaction only now that we have a confirmed match
    tx = TelebirrTransaction(
        transaction_id=transaction_id,
        amount=amount,
        sender_identifier=operator_id or yango_driver_id or phone or "UNKNOWN",
        merchant_id=merchant_id,
        timestamp=timestamp,
        status=status,
        opposite_party=opposite_party,
        driver_id=driver.id,
        is_reconciled=True
    )
    db.add(tx)
    db.flush()

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

    return {
        "status": "success",
        "driver_found": True,
        "driver_name": driver.name,
        "trips_reconciled": 1,
        "amount": amount,
        "is_reconciled": True
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
    batch.reversed_at = datetime.now(timezone.utc)
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
    Scopes trips to the driver's shift window. Returns the number of trips successfully reconciled.
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

    for tx in unreconciled_txs:
        # Fetch all pending cash trips prior to the deposit timestamp
        stmt = select(DriverTrip).where(
            DriverTrip.driver_id == driver_id,
            DriverTrip.payment_method == "cash",
            DriverTrip.reconciliation_status != "Verified",
            DriverTrip.status == "complete",
            DriverTrip.deposited_amount == 0.0,
            DriverTrip.booked_at <= tx.timestamp
        )

        if driver.reconciliation_start_date:
            stmt = stmt.where(DriverTrip.booked_at >= datetime.combine(driver.reconciliation_start_date, datetime.min.time()).replace(tzinfo=timezone.utc))

        pending_trips = db.exec(stmt.order_by(DriverTrip.booked_at.desc())).all()

        if not pending_trips:
            continue

        # Phase 1: Exact Amount Matching (1-to-1)
        matched_trip = None
        for trip in pending_trips:
            target_amount = trip.cash_collected if trip.cash_collected is not None else 0.0
            amount_needed = target_amount - trip.deposited_amount

            # Allow a small float tolerance
            if abs(tx.amount - amount_needed) < 0.01:
                matched_trip = trip
                break

        # Phase 2: Closest-Amount Matching (1-to-1 fallback)
        if not matched_trip and pending_trips:
            trips_with_needed = []
            for t in pending_trips:
                target_amt = t.cash_collected if t.cash_collected is not None else 0.0
                needed = target_amt - t.deposited_amount
                trips_with_needed.append((t, needed))

            if trips_with_needed:
                matched_trip, _ = min(
                    trips_with_needed,
                    # Prefer closest amount; on tie, prefer the most RECENT trip
                    key=lambda x: (abs(x[1] - tx.amount), -(x[0].booked_at.timestamp() if x[0].booked_at else 0))
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
                batch_id=None  # Post-sync auto-reconciliation has no CSV batch ID
            )
            db.add(link)

            tx.is_reconciled = True
            db.add(tx)

            trips_reconciled += 1

    return trips_reconciled
