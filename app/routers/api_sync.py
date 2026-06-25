import csv
import re
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Form, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlmodel import Session, select
from datetime import date, datetime, timedelta, timezone

from app.core.dependencies import get_session, get_current_user, yango_client
from app.models import User, Driver, ExpectedRevenue, TelebirrTransaction, ReconciliationRecord, DriverTrip, SystemConfig, Notification, ReconciliationBatch, DepositTripLink
from app.services.reconciliation import process_telebirr_deposit, reverse_batch, recalculate_trip_status, get_shift_windows
from app.database import engine

router = APIRouter()

active_syncs = {
    "bulk": {
        "status": "idle",
        "progress": 0,
        "current_driver": None,
        "started_at": None,
        "completed_at": None,
        "drivers_processed": 0,
        "trips_inserted": 0,
        "trips_updated": 0,
        "error": None
    },
    "drivers": {}
}

def _parse_dt(dt_str):
    """Parse an ISO-8601 datetime string safely using stdlib only."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.fromisoformat(dt_str[:19])
        except Exception:
            return None

def _upsert_trip(db, o, driver_id, cash_collected=None):
    o_id = o.get("id")
    if not o_id:
        return None, False, False

    car_info = (o.get("car") or {})
    park_details = (o.get("park_details") or {})
    passenger_info = (park_details.get("passenger") or {})
    addr_from = (o.get("address_from") or {})
    car_license = (car_info.get("license") or {})
    order_type = (o.get("type") or {})
    work_rule = (o.get("driver_work_rule") or {})

    booked_at = _parse_dt(o.get("booked_at"))
    created_at = _parse_dt(o.get("created_at"))
    ended_at = _parse_dt(o.get("ended_at"))

    price = o.get("price")
    try:
        price = float(price) if price is not None else None
    except (ValueError, TypeError):
        price = None

    db_trip = db.get(DriverTrip, o_id)
    if not db_trip:
        db_trip = DriverTrip(
            id=o_id,
            short_id=o.get("short_id"),
            driver_id=driver_id,
            status=o.get("status", ""),
            category=o.get("category"),
            payment_method=o.get("payment_method"),
            price=price,
            cash_collected=cash_collected,
            provider=o.get("provider"),
            booked_at=booked_at,
            yango_created_at=created_at,
            ended_at=ended_at,
            address_from=addr_from.get("address"),
            address_from_lat=addr_from.get("lat"),
            address_from_lon=addr_from.get("lon"),
            car_id=car_info.get("id"),
            car_brand_model=car_info.get("brand_model"),
            car_license=car_license.get("number"),
            car_callsign=car_info.get("callsign"),
            order_type_name=order_type.get("name"),
            driver_work_rule=work_rule.get("name"),
            passenger_name=passenger_info.get("name"),
            mileage=o.get("mileage"),
            synced_at=datetime.now(timezone.utc)
        )
        db.add(db_trip)
        return o_id, True, False
    else:
        changed = db_trip.status != o.get("status") or (not db_trip.ended_at and ended_at)
        if changed or (cash_collected is not None and db_trip.cash_collected != cash_collected):
            db_trip.status = o.get("status", "")
            db_trip.ended_at = ended_at
            db_trip.price = price
            if cash_collected is not None:
                db_trip.cash_collected = cash_collected
            db_trip.payment_method = o.get("payment_method")
            db_trip.synced_at = datetime.now(timezone.utc)
        return o_id, False, changed


async def run_bulk_sync_background(is_scheduled: bool = False):
    global active_syncs
    active_syncs["bulk"] = {
        "status": "running",
        "progress": 0,
        "current_driver": "Initializing...",
        "started_at": datetime.now(timezone.utc).isoformat() + "Z",
        "completed_at": None,
        "drivers_processed": 0,
        "trips_inserted": 0,
        "trips_updated": 0,
        "error": None,
        "is_scheduled": is_scheduled
    }
    try:
        # --- Session 1: Initialization & Metadata Reading ---
        with Session(engine) as db:
            # Create starting notification
            try:
                if is_scheduled:
                    start_notif = Notification(
                        title="Automated Sync Started",
                        message="The scheduled automated bulk sync has been initiated in the background.",
                        type="info",
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                else:
                    start_notif = Notification(
                        title="Manual Bulk Sync Started",
                        message="A manual bulk trips sync has been initiated in the background for all internal drivers.",
                        type="info",
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                db.add(start_notif)
                db.commit()
            except Exception as start_err:
                print(f"Error creating start bulk sync notification: {start_err}")

            order_sync_conf = db.get(SystemConfig, "LATEST_ORDERS_SYNC_DAYS")
            lookback_days = int(order_sync_conf.value) if order_sync_conf else 1
            
            from app.services.reconciliation import get_shift_windows
            
            internal_drivers = db.exec(select(Driver).where(Driver.driver_type == "internal")).all()
            # Extract driver tuples to decouple from active DB session objects
            drivers_data = [(d.id, d.name, d.yango_driver_id, d.shift) for d in internal_drivers]

            now = datetime.now(timezone.utc)
            date_from_day = date.today() - timedelta(days=lookback_days)
            
            day_shift_windows = get_shift_windows(db, "Day", date_from_day)
            night_shift_windows = get_shift_windows(db, "Night", date_from_day)
            none_shift_windows = get_shift_windows(db, "None", date_from_day)
            
            shift_starts = {
                "Day": day_shift_windows[0],
                "Night": night_shift_windows[0],
                "None": none_shift_windows[0]
            }
        # Session 1 is closed. The database connection is returned to the pool, and all locks are released.

        # Session 1 is closed. The database connection is returned to the pool, and all locks are released.
        
        total_drivers = len(drivers_data)
        drivers_processed = 0
        trips_inserted = 0
        trips_updated = 0

        if total_drivers == 0:
            active_syncs["bulk"]["status"] = "completed"
            active_syncs["bulk"]["progress"] = 100
            active_syncs["bulk"]["current_driver"] = "No drivers found"
            active_syncs["bulk"]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            return

        for driver_id, driver_name, yango_driver_id, shift in drivers_data:
            active_syncs["bulk"]["current_driver"] = driver_name
            
            driver_date_from = shift_starts.get(shift, shift_starts["None"])
            
            yango_orders = []
            try:
                # Slow network call - executed with NO active database sessions or transactions held.
                yango_orders = await yango_client.get_all_completed_orders(
                    date_from=driver_date_from,
                    date_to=now,
                    driver_profile_id=yango_driver_id
                )
            except Exception as driver_err:
                print(f"Error calling Yango API for driver {driver_name} ({driver_id}): {driver_err}")
            
            # --- Session 2: Short-lived database session to write trips ---
            if yango_orders:
                # Fetch exact cash transactions
                order_ids = [o.get("id") for o in yango_orders if o.get("id") and o.get("payment_method") == "cash"]
                cash_map = {}
                if order_ids:
                    try:
                        transactions = await yango_client.get_order_transactions(order_ids)
                        for tx in transactions:
                            if tx.get("category_id") == "cash_collected":
                                o_id = tx.get("order_id")
                                amt_str = tx.get("amount")
                                if o_id and amt_str:
                                    try:
                                        cash_map[o_id] = float(amt_str)
                                    except ValueError:
                                        pass
                    except Exception as tx_err:
                        print(f"Error fetching transactions for driver {driver_name}: {tx_err}")
                        
                try:
                    with Session(engine) as db:
                        for o in yango_orders:
                            o_id = o.get("id")
                            exact_cash = cash_map.get(o_id)
                            _, inserted, updated = _upsert_trip(db, o, driver_id, cash_collected=exact_cash)
                            if inserted: trips_inserted += 1
                            if updated:  trips_updated += 1
                        db.commit()
                        
                        # Call auto-reconciliation for this driver
                        from app.services.reconciliation import reconcile_driver_unreconciled_deposits
                        try:
                            reconcile_driver_unreconciled_deposits(db, driver_id)
                            db.commit()
                        except Exception as recon_err:
                            print(f"Error during bulk auto-reconciliation for driver {driver_name} ({driver_id}): {recon_err}")
                            db.rollback()
                except Exception as write_err:
                    print(f"Error saving trips for driver {driver_name} ({driver_id}) to DB: {write_err}")
                
            drivers_processed += 1
            progress_pct = int((drivers_processed / total_drivers) * 100)
            
            active_syncs["bulk"]["progress"] = progress_pct
            active_syncs["bulk"]["drivers_processed"] = drivers_processed
            active_syncs["bulk"]["trips_inserted"] = trips_inserted
            active_syncs["bulk"]["trips_updated"] = trips_updated

        # --- Session 3: Final Config Updating & Completion Notification ---
        with Session(engine) as db:
            # Store the LAST_BULK_SYNC in SystemConfig
            config_key = "LAST_BULK_SYNC"
            last_sync_conf = db.get(SystemConfig, config_key)
            if not last_sync_conf:
                last_sync_conf = SystemConfig(
                    key=config_key,
                    value=datetime.now(timezone.utc).isoformat() + "Z",
                    description="Timestamp of last bulk trips sync",
                    data_type="string",
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(last_sync_conf)
            else:
                last_sync_conf.value = datetime.now(timezone.utc).isoformat() + "Z"
                last_sync_conf.updated_at = datetime.now(timezone.utc)
                db.add(last_sync_conf)
                
            db.commit()

            # Create completion notification
            try:
                if is_scheduled:
                    notif = Notification(
                        title="Automated Sync Completed",
                        message=f"Scheduled sync completed successfully: Processed {drivers_processed} drivers, imported {trips_inserted} new trips, and updated {trips_updated} trips.",
                        type="success",
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                else:
                    notif = Notification(
                        title="Manual Bulk Sync Completed",
                        message=f"Manual sync completed successfully: Processed {drivers_processed} drivers, imported {trips_inserted} new trips, and updated {trips_updated} trips.",
                        type="success",
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                db.add(notif)
                db.commit()
            except Exception as notif_err:
                print(f"Error creating sync success notification: {notif_err}")

        active_syncs["bulk"]["status"] = "completed"
        active_syncs["bulk"]["progress"] = 100
        active_syncs["bulk"]["current_driver"] = None
        active_syncs["bulk"]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"

    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Create failure notification
        try:
            with Session(engine) as db:
                if is_scheduled:
                    notif = Notification(
                        title="Automated Sync Failed",
                        message=f"Scheduled sync failed: {str(e)}",
                        type="error",
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                else:
                    notif = Notification(
                        title="Manual Bulk Sync Failed",
                        message=f"Manual sync failed: {str(e)}",
                        type="error",
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                db.add(notif)
                db.commit()
        except Exception as notif_err:
            print(f"Error creating sync failure notification: {notif_err}")

        active_syncs["bulk"]["status"] = "failed"
        active_syncs["bulk"]["error"] = str(e)
        active_syncs["bulk"]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"


@router.post("/sync/internal-trips")
async def sync_internal_trips(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Trigger background bulk-sync trip history for ALL internal drivers from Yango API."""
    if not user:
        raise HTTPException(status_code=401)
    
    global active_syncs
    if active_syncs["bulk"]["status"] == "running":
        return {"status": "running", "message": "Bulk sync is already in progress"}
        
    # Check if any individual driver sync is running
    drivers_dict = active_syncs.get("drivers", {})
    for d_id, d_sync in drivers_dict.items():
        if d_sync.get("status") == "running" and not d_sync.get("is_bulk"):
            return {"status": "running", "message": "An individual driver sync is currently in progress. Please wait for it to complete."}
            
    background_tasks.add_task(run_bulk_sync_background)
    return {"status": "started", "message": "Bulk sync started in the background"}


@router.get("/sync/status")
async def get_bulk_sync_status(db: Session = Depends(get_session)):
    global active_syncs
    last_sync_conf = db.get(SystemConfig, "LAST_BULK_SYNC")
    last_sync = last_sync_conf.value if last_sync_conf else None
    
    # Check if any individual driver sync is running
    is_ind_running = False
    ind_driver_name = None
    ind_driver_id = None
    ind_progress = 0
    ind_trips_inserted = 0
    ind_trips_updated = 0
    ind_started_at = None
    
    drivers_dict = active_syncs.get("drivers", {})
    for d_id, d_sync in drivers_dict.items():
        if d_sync.get("status") == "running" and not d_sync.get("is_bulk"):
            is_ind_running = True
            ind_driver_id = d_id
            ind_progress = d_sync.get("progress", 0)
            ind_trips_inserted = d_sync.get("trips_inserted", 0)
            ind_trips_updated = d_sync.get("trips_updated", 0)
            ind_started_at = d_sync.get("started_at")
            driver_obj = db.get(Driver, d_id)
            ind_driver_name = driver_obj.name if driver_obj else f"Driver #{d_id}"
            break
            
    if is_ind_running:
        return {
            "active": {
                "status": "running",
                "progress": ind_progress,
                "current_driver": ind_driver_name,
                "is_individual": True,
                "driver_id": ind_driver_id,
                "started_at": ind_started_at,
                "completed_at": None,
                "drivers_processed": 0,
                "trips_inserted": ind_trips_inserted,
                "trips_updated": ind_trips_updated,
                "error": None
            },
            "last_sync": last_sync
        }
        
    return {
        "active": active_syncs["bulk"],
        "last_sync": last_sync
    }

@router.post("/sync/yango")
async def sync_yango_data(db: Session = Depends(get_session)):
    """Sync drivers (Delta Sync) from Yango."""
    try:
        driver_sync_conf = db.get(SystemConfig, "DRIVER_SYNC_LOOKBACK_DAYS")
        lookback_days = int(driver_sync_conf.value) if driver_sync_conf else 7
        # Snap to the very beginning of the lookback day (midnight)
        lookback_date_day = date.today() - timedelta(days=lookback_days)
        lookback_date = datetime.combine(lookback_date_day, datetime.min.time()).replace(tzinfo=timezone.utc)
        yango_drivers = await yango_client.get_drivers(updated_since=lookback_date)
        
        batch_size = 500
        for i in range(0, len(yango_drivers), batch_size):
            batch = yango_drivers[i:i + batch_size]
            for yd in batch:
                profile = yd.get("driver_profile", {})
                y_id = profile.get("id")
                name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Unknown"
                phones = profile.get("phones", [])
                phone = phones[0] if phones else None
                
                driver = db.exec(select(Driver).where(Driver.yango_driver_id == y_id)).first()
                if not driver:
                    driver = Driver(yango_driver_id=y_id, name=name, phone=phone)
                    db.add(driver)
                else:
                    driver.name = name
                    driver.phone = phone
            db.commit()

        notif = Notification(
            title="Yango Sync Completed",
            message=f"Successfully delta-synced {len(yango_drivers)} drivers.",
            type="info",
            action_url="/drivers"
        )
        db.add(notif)
        db.commit()
        
        return {"status": "success", "drivers_synced": len(yango_drivers), "orders_processed": 0}
    except Exception as e:
        print(f"Error during driver sync: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/reconciliation/run")
async def run_reconciliation(target_date: date = None, db: Session = Depends(get_session)):
    """Batch job to reconcile expected vs actual for a given day."""
    if not target_date:
        target_date = date.today()
        
    drivers = db.exec(select(Driver).where(Driver.driver_type == "internal")).all()
    
    # 1. Run waterfall auto-reconciliation for each driver (applies unreconciled deposits oldest-trip-first)
    total_trips_matched = 0
    from app.services.reconciliation import reconcile_driver_unreconciled_deposits
    for d in drivers:
        if d.shift not in ("Day", "Night"):
            try:
                notif = Notification(
                    title="Missing Shift Assignment",
                    message=f"Driver {d.name} has no valid shift assigned. Falling back to 24-hour reconciliation window.",
                    type="warning",
                    is_read=False,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(notif)
                db.commit()
            except Exception:
                pass
        try:
            matched = reconcile_driver_unreconciled_deposits(db, d.id)
            total_trips_matched += matched
        except Exception as e:
            print(f"Error during batch auto-reconciliation for driver {d.name} ({d.id}): {e}")
            
    # 2. Run legacy daily summary calculation for dashboards
    results = []
    
    for d in drivers:
        # Delete any existing reconciliation record for this driver and date to prevent duplicates
        existing_records = db.exec(
            select(ReconciliationRecord).where(
                ReconciliationRecord.driver_id == d.id,
                ReconciliationRecord.date == target_date
            )
        ).all()
        for rec in existing_records:
            db.delete(rec)
            
        # Get shift windows for this driver's shift on target_date
        trip_start, trip_end, deposit_start, deposit_end = get_shift_windows(db, d.shift, target_date)
        
        # Filter cash trips within this driver's shift trip window
        start_datetime = None
        if d.reconciliation_start_date:
            start_datetime = datetime.combine(d.reconciliation_start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            
        expected_stmt = select(DriverTrip).where(
            DriverTrip.driver_id == d.id,
            DriverTrip.payment_method == "cash",
            DriverTrip.status == "complete",
            DriverTrip.booked_at >= trip_start,
            DriverTrip.booked_at < trip_end
        )
        if start_datetime:
            expected_stmt = expected_stmt.where(DriverTrip.booked_at >= start_datetime)
            
        expected_trips = db.exec(expected_stmt).all()
        expected_amt = sum([(t.cash_collected if t.cash_collected is not None else 0.0) for t in expected_trips])
        
        # Calculate actual Telebirr deposits in this driver's deposit window
        actual_stmt = select(TelebirrTransaction).where(
            TelebirrTransaction.driver_id == d.id,
            TelebirrTransaction.timestamp >= deposit_start,
            TelebirrTransaction.timestamp < deposit_end
        )
        actual_txs = db.exec(actual_stmt).all()
        actual_amt = sum([tx.amount for tx in actual_txs])
        
        if expected_amt == 0 and actual_amt == 0:
            continue
            
        if abs(actual_amt - expected_amt) < 0.01:
            status = "Verified"
        elif actual_amt == 0:
            status = "Missing Deposit"
        elif actual_amt < expected_amt:
            status = "Partial Deposit"
        else:
            status = "Excess Deposit"
            
        record = ReconciliationRecord(
            driver_id=d.id,
            date=target_date,
            expected_amount=expected_amt,
            actual_amount=actual_amt,
            status=status
        )
        db.add(record)
        results.append(record)
        
    db.commit()
    return {
        "message": f"Batch reconciliation complete for {target_date}. Reconciled {total_trips_matched} trips across {len(drivers)} drivers.", 
        "records_processed": len(results),
        "trips_reconciled": total_trips_matched
    }

from pydantic import BaseModel
class WebhookPayload(BaseModel):
    transaction_id: str
    amount: float
    sender_identifier: str
    merchant_id: str
    timestamp: datetime
    status: str

@router.post("/telebirr/webhook")
async def telebirr_webhook(payload: WebhookPayload, db: Session = Depends(get_session)):
    """Receives a webhook from Telebirr and reconciles it against pending trips."""
    result = process_telebirr_deposit(
        db=db,
        transaction_id=payload.transaction_id,
        amount=payload.amount,
        timestamp=payload.timestamp,
        yango_driver_id=payload.sender_identifier, # Webhook usually sends Yango ID
        merchant_id=payload.merchant_id,
        status=payload.status
    )
    
    if result["status"] == "skipped":
        return {"message": result["message"]}
        
    db.commit()
    
    notif = Notification(
        title="Telebirr Deposit Received",
        message=f"Received ETB {payload.amount} from {payload.sender_identifier}. trips reconciled.",
        type="success",
        action_url="/exceptions" if not result["driver_found"] else f"/drivers/{result['driver_found']}"
    )
    db.add(notif)
    db.commit()
    
    return {"message": "Transaction recorded and reconciled", "details": result}

@router.post("/reconciliation/analyze-telebirr-csv")
async def analyze_telebirr_csv(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """Analyze a Telebirr CSV export and return stats before importing."""
    if not user:
        raise HTTPException(status_code=401)
        
    content = await file.read()
    lines = content.decode("utf-8").splitlines()
    
    if len(lines) < 6:
        return {"error": "Invalid CSV format"}
        
    f = lines[5:]
    reader = csv.DictReader(f)
    reader.fieldnames = [name.strip() for name in reader.fieldnames]
    
    total_payments = 0
    total_amount = 0.0
    unique_operators = set()
    
    for row in reader:
        row = {k.strip(): v.strip() for k, v in row.items()}
        
        if row.get("Transaction Status") != "Completed":
            continue
            
        paid_in = row.get("Paid In", "").replace(",", "")
        if not paid_in:
            continue
            
        try:
            amount = float(paid_in)
        except ValueError:
            continue
            
        details = row.get("Details", "")
        op_match = re.search(r'-\s*(\d+)', details)
        if op_match:
            operator_id = op_match.group(1)
            total_payments += 1
            total_amount += amount
            unique_operators.add(operator_id)
            
    return {
        "valid_payments": total_payments,
        "total_amount": total_amount,
        "unique_operators": len(unique_operators)
    }

@router.post("/reconciliation/upload-telebirr-csv")
async def upload_telebirr_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Upload and process a Telebirr CSV export for reconciliation."""
    if not user:
        raise HTTPException(status_code=401)
        
    content = await file.read()
    lines = content.decode("utf-8").splitlines()
    
    # Skip metadata (lines 1-5)
    if len(lines) < 6:
        return {"error": "Invalid CSV format"}
        
    f = lines[5:] # Header is at line 6
    reader = csv.DictReader(f)
    # Clean headers
    reader.fieldnames = [name.strip() for name in reader.fieldnames]
    
    # Create the batch record
    batch = ReconciliationBatch(
        filename=file.filename,
        uploaded_by=user.id,
        status="active"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    processed_count = 0
    skipped_count = 0
    drivers_matched = set()
    total_trips_reconciled = 0
    total_amount = 0.0
    
    for row in reader:
        # Clean row values
        row = {k.strip(): v.strip() for k, v in row.items()}
        
        status = row.get("Transaction Status")
        if status != "Completed":
            continue
            
        paid_in = row.get("Paid In", "").replace(",", "")
        if not paid_in:
            continue
            
        try:
            amount = float(paid_in)
        except ValueError:
            continue
            
        receipt_no = row.get("Receipt No.")
        completion_time_str = row.get("Completion Time")
        details = row.get("Details", "")
        opposite_party = row.get("Opposite Party", "")
        
        # Telebirr timestamps are in Ethiopia time (UTC+3)
        ETH_TZ = timezone(timedelta(hours=3))
        try:
            timestamp = datetime.strptime(completion_time_str, "%d/%m/%Y %H:%M:%S").replace(tzinfo=ETH_TZ)
        except:
            timestamp = datetime.now(timezone.utc)
            
        # Extract Operator ID from Details
        operator_id = None
        op_match = re.search(r'-\s*(\d+)', details)
        if op_match:
            operator_id = op_match.group(1)
        else:
            # Strictly take only those with Operator ID as per user request
            print(f"DEBUG: Skipping row {receipt_no} - No Operator ID found in Details: {details}")
            skipped_count += 1
            continue
            
        result = process_telebirr_deposit(
            db=db,
            transaction_id=receipt_no,
            amount=amount,
            timestamp=timestamp,
            operator_id=operator_id,
            opposite_party=opposite_party,
            batch_id=batch.id
        )
        
        if result["status"] == "success":
            processed_count += 1
            total_amount += amount
            if result["driver_found"]:
                drivers_matched.add(operator_id)
                total_trips_reconciled += result["trips_reconciled"]
            else:
                print(f"DEBUG: Row {receipt_no} - Driver not found for Operator ID {operator_id}")
        else:
            print(f"DEBUG: Skipping row {receipt_no} - {result.get('message', 'Unknown reason')}")
            skipped_count += 1
            
    # Update batch stats
    batch.total_transactions = processed_count
    batch.total_amount = total_amount
    batch.drivers_matched = len(drivers_matched)
    batch.trips_reconciled = total_trips_reconciled
    db.add(batch)
    db.commit()
    
    notif = Notification(
        title="Telebirr CSV Processed",
        message=f"Processed {processed_count} payments. {total_trips_reconciled} trips reconciled.",
        type="success",
        action_url="/exceptions"
    )
    db.add(notif)
    db.commit()
    
    return {
        "status": "success",
        "processed": processed_count,
        "skipped": skipped_count,
        "drivers_matched": len(drivers_matched),
        "trips_reconciled": total_trips_reconciled,
        "batch_id": batch.id
    }

@router.post("/simulator/deposit")
async def simulate_deposit(
    driver_id: int = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_session)
):
    """Called from our simulator UI to trigger the webhook logic."""
    driver = db.get(Driver, driver_id)
    if not driver:
        return {"error": "Driver not found"}
        
    payload = WebhookPayload(
        transaction_id=f"TB-{uuid.uuid4().hex[:8].upper()}",
        amount=amount,
        sender_identifier=driver.yango_driver_id,
        merchant_id="G2G-MERCHANT-001",
        timestamp=datetime.now(timezone.utc),
        status="success"
    )
    # We could call telebirr_webhook here if we wanted to simulate completely, 
    # but the current architecture seems to just have this shell.
    return {"message": "Simulated", "payload": payload.model_dump()}

@router.get("/reconciliation/batches")
async def list_reconciliation_batches(db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """List all reconciliation batches."""
    if not user:
        raise HTTPException(status_code=401)
    batches = db.exec(select(ReconciliationBatch).order_by(ReconciliationBatch.created_at.desc())).all()
    return batches

@router.post("/reconciliation/batches/{batch_id}/reverse")
async def reverse_reconciliation_batch(
    batch_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Reverse a reconciliation batch."""
    if not user:
        raise HTTPException(status_code=401)
        
    # Check if this is the latest active batch
    latest_batch = db.exec(
        select(ReconciliationBatch)
        .where(ReconciliationBatch.status == "active")
        .order_by(ReconciliationBatch.created_at.desc())
    ).first()
    
    if not latest_batch or latest_batch.id != batch_id:
        raise HTTPException(status_code=400, detail="Only the latest active batch can be reversed.")
        
    result = reverse_batch(db, batch_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
        
    db.commit()
    return result

@router.get("/drivers/{driver_id}/available-deposits")
async def get_available_deposits(
    driver_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Retrieve all available (unreconciled or partially reconciled) Telebirr transactions for a driver."""
    if not user:
        raise HTTPException(status_code=401)
        
    # Fetch all completed transactions for this driver
    txs = db.exec(
        select(TelebirrTransaction)
        .where(TelebirrTransaction.driver_id == driver_id)
        .where(TelebirrTransaction.status == "Completed")
    ).all()
    
    available = []
    for tx in txs:
        # Sum the amount_applied across all existing links
        links = db.exec(select(DepositTripLink).where(DepositTripLink.transaction_id == tx.transaction_id)).all()
        applied_sum = sum([l.amount_applied for l in links])
        remaining = tx.amount - applied_sum
        
        # If there's remaining unapplied balance, it's available for linking
        if remaining > 0.01:
            available.append({
                "transaction_id": tx.transaction_id,
                "amount": tx.amount,
                "remaining": remaining,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M") if tx.timestamp else "—",
                "sender": tx.sender_identifier
            })
            
    return available

@router.post("/trips/{trip_id}/unlink-deposit")
async def unlink_deposit(
    trip_id: str,
    transaction_id: str = Form(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Surgically break the link between a trip and a specific Telebirr transaction receipt."""
    if not user:
        raise HTTPException(status_code=401)
        
    trip = db.get(DriverTrip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    link = db.exec(
        select(DepositTripLink)
        .where(DepositTripLink.trip_id == trip_id)
        .where(DepositTripLink.transaction_id == transaction_id)
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link between trip and transaction not found")
        
    amount_reverted = link.amount_applied
    db.delete(link)
    
    # Subtract applied amount and recalculate trip reconciliation status
    trip.deposited_amount = max(0.0, trip.deposited_amount - amount_reverted)
    trip.reconciliation_status = recalculate_trip_status(trip)
    trip.synced_at = datetime.now(timezone.utc)
    db.add(trip)
    
    # Release the transaction's reconciled state so it returns to the available general pool
    tx = db.exec(
        select(TelebirrTransaction)
        .where(TelebirrTransaction.transaction_id == transaction_id)
    ).first()
    if tx:
        tx.is_reconciled = False
        db.add(tx)
        
    db.commit()
    return {"status": "success", "trip_id": trip.id, "reconciliation_status": trip.reconciliation_status}

@router.post("/trips/{trip_id}/link-deposit")
async def link_deposit(
    trip_id: str,
    transaction_id: str = Form(...),
    amount_to_apply: float = Form(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Surgically link a specific Telebirr transaction receipt to a trip with a defined amount."""
    if not user:
        raise HTTPException(status_code=401)
        
    trip = db.get(DriverTrip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    tx = db.exec(
        select(TelebirrTransaction)
        .where(TelebirrTransaction.transaction_id == transaction_id)
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    # Validation: Confirm transaction belongs to the same driver
    if tx.driver_id != trip.driver_id:
        raise HTTPException(status_code=400, detail="Transaction does not belong to this driver")
        
    # Calculate transaction remaining balance
    links = db.exec(select(DepositTripLink).where(DepositTripLink.transaction_id == tx.transaction_id)).all()
    applied_sum = sum([l.amount_applied for l in links])
    remaining = tx.amount - applied_sum
    
    if amount_to_apply > remaining + 0.01:
        raise HTTPException(status_code=400, detail=f"Amount exceeds transaction remaining balance of {remaining:.2f} ETB")
        
    # Add new link or update existing link
    existing_link = db.exec(
        select(DepositTripLink)
        .where(DepositTripLink.trip_id == trip_id)
        .where(DepositTripLink.transaction_id == transaction_id)
    ).first()
    
    if existing_link:
        existing_link.amount_applied += amount_to_apply
        db.add(existing_link)
    else:
        new_link = DepositTripLink(
            transaction_id=transaction_id,
            trip_id=trip_id,
            amount_applied=amount_to_apply,
            batch_id=None # Denotes manual admin override link
        )
        db.add(new_link)
        
    # Update trip status and deposited amount
    trip.deposited_amount += amount_to_apply
    trip.reconciliation_status = recalculate_trip_status(trip)
    trip.reconciliation_notes = f"Manually linked {amount_to_apply:.2f} ETB from receipt {transaction_id[-6:]}"
    trip.synced_at = datetime.now(timezone.utc)
    db.add(trip)
    
    # Update transaction is_reconciled state
    new_applied_sum = applied_sum + amount_to_apply
    if abs(new_applied_sum - tx.amount) < 0.01:
        tx.is_reconciled = True
    else:
        tx.is_reconciled = False
    db.add(tx)
    
    db.commit()
    return {"status": "success", "trip_id": trip.id, "reconciliation_status": trip.reconciliation_status}

@router.post("/trips/{trip_id}/resolve")
async def resolve_trip_exception(
    trip_id: str,
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    deposited_amount: Optional[float] = Form(None),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Fallback manual status/notes override endpoint to maintain backward compatibility."""
    if not user:
        raise HTTPException(status_code=401)
        
    trip = db.get(DriverTrip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    from app.core.dependencies import _record_audit_log
    
    old_status = trip.reconciliation_status
    old_deposited = trip.deposited_amount
    old_notes = trip.reconciliation_notes
    
    if deposited_amount is not None:
        trip.deposited_amount = deposited_amount
        
    trip.reconciliation_status = status
    trip.reconciliation_notes = notes
    trip.synced_at = datetime.now(timezone.utc)
    
    db.add(trip)
    
    # Audit logging
    if old_status != status:
        _record_audit_log(db, user.id, "trip", trip.id, "reconciliation_status", old_status, status)
    if deposited_amount is not None and old_deposited != deposited_amount:
        _record_audit_log(db, user.id, "trip", trip.id, "deposited_amount", str(old_deposited), str(deposited_amount))
    if old_notes != notes:
        _record_audit_log(db, user.id, "trip", trip.id, "reconciliation_notes", old_notes or "", notes or "")
        
    db.commit()
    db.refresh(trip)
    return {"status": "success", "trip_id": trip.id, "reconciliation_status": trip.reconciliation_status}


