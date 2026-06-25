from datetime import datetime, timezone, date, timedelta
from typing import Optional, List
from sqlmodel import Session, select
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


def _waterfall_apply(
    db: Session,
    transaction_id: str,
    deposit_amount: float,
    pending_trips: List[DriverTrip],
    batch_id: Optional[int] = None
) -> int:
    """
    Greedily applies deposit_amount across pending_trips (must be sorted oldest-first by booked_at).

    For each trip, applies as much of the remaining deposit as needed to fully cover it.
    If the deposit is exhausted before all trips are covered, the last touched trip gets
    a Partial Deposit and remaining trips stay Pending.
    If the deposit exceeds all trips, the surplus is applied to the last trip (Excess Deposit).

    Creates one DepositTripLink per trip touched, recording the exact amount applied.
    Returns the number of trips touched (>0 means the transaction should be stored).
    """
    remaining = deposit_amount
    trips_touched = 0
    last_trip: Optional[DriverTrip] = None
    last_link: Optional[DepositTripLink] = None

    for trip in pending_trips:
        if remaining < 0.005:
            break

        target_amount = trip.cash_collected if trip.cash_collected is not None else 0.0
        needed = max(0.0, target_amount - trip.deposited_amount)

        if needed < 0.005:
            # Already fully covered (shouldn't appear in pool, but guard safely)
            continue

        # Apply as much as needed (capped at remaining); excess handled after loop
        applied = min(remaining, needed)

        trip.deposited_amount += applied
        trip.reconciliation_status = recalculate_trip_status(trip)
        db.add(trip)

        link = DepositTripLink(
            transaction_id=transaction_id,
            trip_id=trip.id,
            amount_applied=applied,
            batch_id=batch_id
        )
        db.add(link)

        remaining -= applied
        trips_touched += 1
        last_trip = trip
        last_link = link

    # If deposit exceeded all trips, apply the surplus to the last touched trip
    if remaining > 0.005 and last_trip is not None and last_link is not None:
        last_trip.deposited_amount += remaining
        last_trip.reconciliation_status = recalculate_trip_status(last_trip)
        db.add(last_trip)
        last_link.amount_applied += remaining
        db.add(last_link)

    return trips_touched


def _build_pending_trips_query(
    db: Session,
    driver_id: int,
    before_timestamp: datetime,
    reconciliation_start_date: Optional[date] = None
):
    """
    Returns all eligible unreconciled cash trips for a driver, sorted oldest-first.
    Includes both Pending and Partial Deposit trips so bulk deposits can top up
    partially-paid trips before moving on to fully-unpaid ones.
    """
    stmt = select(DriverTrip).where(
        DriverTrip.driver_id == driver_id,
        DriverTrip.payment_method == "cash",
        DriverTrip.status == "complete",
        DriverTrip.reconciliation_status.in_(["Pending", "Partial Deposit"]),
        DriverTrip.booked_at <= before_timestamp
    )

    if reconciliation_start_date:
        stmt = stmt.where(
            DriverTrip.booked_at >= datetime.combine(
                reconciliation_start_date, datetime.min.time()
            ).replace(tzinfo=timezone.utc)
        )

    return db.exec(stmt.order_by(DriverTrip.booked_at.asc())).all()


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
    Records a Telebirr transaction and reconciles it against a driver's outstanding cash trips
    using a waterfall strategy: oldest trips are paid first, partial deposits are allowed,
    and any surplus after all trips are covered is applied to the last trip as Excess Deposit.

    A single transaction may satisfy multiple trips. One DepositTripLink is created per trip touched.
    The transaction is only stored in the database if the driver is found AND at least one trip is touched.
    """
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    # 1. Idempotency Check
    existing_tx = db.exec(
        select(TelebirrTransaction).where(TelebirrTransaction.transaction_id == transaction_id)
    ).first()
    if existing_tx:
        return {"status": "skipped", "message": f"Transaction {transaction_id} already exists."}

    # 2. Find the driver (by operator_id, then yango_driver_id, then phone)
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

    # 3. Fetch all eligible unreconciled/partially-reconciled cash trips (oldest first)
    pending_trips = _build_pending_trips_query(
        db, driver.id, timestamp, driver.reconciliation_start_date
    )

    if not pending_trips:
        return {
            "status": "success",
            "driver_found": True,
            "driver_name": driver.name,
            "trips_reconciled": 0,
            "amount": amount,
            "is_reconciled": False
        }

    # 4. Store the transaction now that we have a confirmed driver and pending trips
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
    db.flush()  # Ensure transaction_id is available for DepositTripLink FKs

    # 5. Waterfall: apply deposit across trips oldest-first
    trips_touched = _waterfall_apply(db, transaction_id, amount, pending_trips, batch_id)

    return {
        "status": "success",
        "driver_found": True,
        "driver_name": driver.name,
        "trips_reconciled": trips_touched,
        "amount": amount,
        "is_reconciled": True
    }


def reverse_batch(db: Session, batch_id: int) -> dict:
    """
    Undoes all reconciliations linked to a specific batch.
    Reverts trip amounts and statuses, deletes links, marks transactions as unreconciled.
    Handles multiple DepositTripLinks per transaction (waterfall splits).
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
            trip.deposited_amount = max(0.0, trip.deposited_amount - link.amount_applied)
            trip.reconciliation_status = recalculate_trip_status(trip)
            db.add(trip)
            trips_affected.add(trip.id)

        txs_affected.add(link.transaction_id)
        db.delete(link)

    for tx_id in txs_affected:
        tx = db.exec(
            select(TelebirrTransaction).where(TelebirrTransaction.transaction_id == tx_id)
        ).first()
        if tx:
            # Only un-reconcile if no other batches still reference this transaction
            other_links = db.exec(
                select(DepositTripLink).where(
                    DepositTripLink.transaction_id == tx_id,
                    DepositTripLink.batch_id != batch_id
                )
            ).first()
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
    Takes all completed but unreconciled Telebirr deposits for a driver and applies them
    against outstanding cash trips using the waterfall strategy (oldest trips first).

    Each unreconciled transaction is processed in timestamp order, so earlier deposits
    are applied before later ones. Returns the total number of trips touched.
    """
    driver = db.get(Driver, driver_id)
    if not driver:
        return 0

    # Get all completed but unreconciled transactions for this driver, oldest first
    unreconciled_txs = db.exec(
        select(TelebirrTransaction)
        .where(TelebirrTransaction.driver_id == driver_id)
        .where(TelebirrTransaction.is_reconciled == False)
        .where(TelebirrTransaction.status == "Completed")
        .order_by(TelebirrTransaction.timestamp.asc())
    ).all()

    if not unreconciled_txs:
        return 0

    total_trips_reconciled = 0

    for tx in unreconciled_txs:
        # Fetch all pending/partial trips before this deposit's timestamp (oldest first)
        pending_trips = _build_pending_trips_query(
            db, driver_id, tx.timestamp, driver.reconciliation_start_date
        )

        if not pending_trips:
            continue

        # Waterfall: apply this transaction's amount across eligible trips
        trips_touched = _waterfall_apply(db, tx.transaction_id, tx.amount, pending_trips, batch_id=None)

        if trips_touched > 0:
            tx.is_reconciled = True
            db.add(tx)
            total_trips_reconciled += trips_touched

    return total_trips_reconciled
