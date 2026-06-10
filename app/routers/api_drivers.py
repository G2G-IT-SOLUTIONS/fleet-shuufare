from fastapi import APIRouter, Form, Depends, HTTPException, BackgroundTasks, File, UploadFile
from sqlmodel import Session, select, or_
from typing import Optional
from datetime import date, datetime, timedelta, timezone


from app.core.dependencies import get_session, get_current_user, yango_client, _record_audit_log
from app.models import User, Driver, SystemConfig, DriverTrip, AuditLog, Notification, DriverDocument

router = APIRouter()

@router.post("/update-type")
async def update_driver_type(
    driver_id: int = Form(...),
    driver_type: str = Form(...),
    db: Session = Depends(get_session)
):
    """Update a driver's type (internal/external)."""
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    driver.driver_type = driver_type
    db.add(driver)
    db.commit()
    return {"message": f"Driver {driver.name} updated to {driver_type}"}

@router.get("/search")
async def search_drivers_api(query: str = "", db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """Search all drivers by name, phone or yango ID."""
    if not user:
        raise HTTPException(status_code=401)
    
    statement = select(Driver)
    if query:
        statement = statement.where(
            (Driver.name.ilike(f"%{query}%")) | 
            (Driver.yango_driver_id.ilike(f"%{query}%")) |
            (Driver.phone.ilike(f"%{query}%"))
        )
    
    # Limit to 10 results for performance
    drivers = db.exec(statement.limit(10)).all()
    return drivers

@router.post("/add-internal")
async def add_internal_driver(
    yango_driver_id: str = Form(...),
    name: str = Form(...),
    phone: str = Form(None),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Add a driver from Yango directly as an internal driver."""
    if not user:
        raise HTTPException(status_code=401)

    # Check if already in our DB
    existing = db.exec(select(Driver).where(Driver.yango_driver_id == yango_driver_id)).first()
    if existing:
        existing.driver_type = "internal"
        if name:
            existing.name = name
        if phone:
            existing.phone = phone
        db.add(existing)
        db.commit()
        return {"status": "updated", "driver_id": existing.id, "message": f"{existing.name} marked as internal."}

    # New driver — create record
    driver = Driver(
        yango_driver_id=yango_driver_id,
        name=name,
        phone=phone,
        driver_type="internal"
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"status": "created", "driver_id": driver.id, "message": f"{driver.name} added as internal driver."}

@router.post("/{driver_id}/update-name")
async def update_driver_name(
    driver_id: int, 
    name: str = Form(...), 
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """Update a driver's name in the local database."""
    if not user:
        raise HTTPException(status_code=401)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    old_name = driver.name
    if old_name != name:
        driver.name = name
        db.add(driver)
        _record_audit_log(db, user.id, "driver", driver.id, "name", old_name, name)
        db.commit()
    
    return {"status": "success", "new_name": name}

@router.post("/{driver_id}/update-operator-id")
async def update_driver_operator_id(
    driver_id: int, 
    operator_id: str = Form(...), 
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """Update a driver's Operator ID in the local database."""
    if not user:
        raise HTTPException(status_code=401)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    old_id = driver.operator_id
    if old_id != operator_id:
        driver.operator_id = operator_id
        db.add(driver)
        _record_audit_log(db, user.id, "driver", driver.id, "operator_id", old_id, operator_id)
        db.commit()
        
    return {"status": "success", "new_operator_id": operator_id}
    
@router.post("/{driver_id}/update-shift")
async def update_driver_shift(
    driver_id: int, 
    shift: str = Form(...), 
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """Update a driver's shift (Day, Night, or None) in the local database."""
    if not user:
        raise HTTPException(status_code=401)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    old_shift = driver.shift
    if old_shift != shift:
        driver.shift = shift
        db.add(driver)
        _record_audit_log(db, user.id, "driver", driver.id, "shift", old_shift, shift)
        db.commit()
        
    return {"status": "success", "new_shift": shift}

@router.post("/{driver_id}/update-recon-date")
async def update_driver_recon_date(
    driver_id: int, 
    recon_date: str = Form(""), 
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """Update a driver's reconciliation start date."""
    if not user:
        raise HTTPException(status_code=401)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    old_date = str(driver.reconciliation_start_date) if driver.reconciliation_start_date else "None"
    new_date_obj = datetime.strptime(recon_date, "%Y-%m-%d").date() if recon_date else None
    new_date_str = str(new_date_obj) if new_date_obj else "None"
    
    if old_date != new_date_str:
        driver.reconciliation_start_date = new_date_obj
        db.add(driver)
        _record_audit_log(db, user.id, "driver", driver.id, "recon_start_date", old_date, new_date_str)
        db.commit()
        
    return {"status": "success", "new_recon_date": new_date_str}

@router.post("/{driver_id}/add-note")
async def add_driver_note(
    driver_id: int,
    note: str = Form(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Add a custom note/comment to the driver's audit log."""
    if not user:
        raise HTTPException(status_code=401)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    _record_audit_log(db, user.id, "driver", driver.id, "note", None, note)
    db.commit()
    return {"status": "success", "note": note}

@router.get("/{driver_id}/audit-logs")
async def get_driver_audit_logs(driver_id: int, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """Fetch change history for a specific driver."""
    if not user:
        raise HTTPException(status_code=401)
        
    logs = db.exec(
        select(AuditLog, User.email)
        .join(User, AuditLog.user_id == User.id)
        .where(AuditLog.target_type == "driver", AuditLog.target_id == str(driver_id))
        .order_by(AuditLog.timestamp.desc())
    ).all()
    
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "username": email,
            "field": log.field_name,
            "old": log.old_value,
            "new": log.new_value
        } for log, email in logs
    ]

async def run_driver_sync_background(driver_id: int):
    from app.routers.api_sync import active_syncs, _upsert_trip
    from app.database import engine

    # Ensure the drivers sub-dictionary exists
    if "drivers" not in active_syncs:
        active_syncs["drivers"] = {}

    active_syncs["drivers"][driver_id] = {
        "status": "running",
        "progress": 0,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": None,
        "trips_inserted": 0,
        "trips_updated": 0,
        "error": None
    }
    
    try:
        # --- Session 1: Initialization & Metadata Reading ---
        with Session(engine) as db:
            driver = db.get(Driver, driver_id)
            if not driver:
                active_syncs["drivers"][driver_id]["status"] = "failed"
                active_syncs["drivers"][driver_id]["error"] = "Driver not found"
                active_syncs["drivers"][driver_id]["completed_at"] = datetime.utcnow().isoformat() + "Z"
                return
            
            driver_name = driver.name
            yango_driver_id = driver.yango_driver_id
            
            # Create driver sync started notification
            try:
                start_notif = Notification(
                    title="Manual Driver Sync Started",
                    message=f"Manual sync has been initiated in the background for driver {driver_name}.",
                    type="info",
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(start_notif)
                db.commit()
            except Exception as start_err:
                print(f"Error creating driver sync start notification: {start_err}")
            
            order_sync_conf = db.get(SystemConfig, "LATEST_ORDERS_SYNC_DAYS")
            lookback_days = int(order_sync_conf.value) if order_sync_conf else 1
            
        # Session 1 is closed. The database connection is returned to the pool and locks are released.

        now = datetime.now(timezone.utc)
        date_from_day = date.today() - timedelta(days=lookback_days)
        date_from = datetime.combine(date_from_day, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        active_syncs["drivers"][driver_id]["progress"] = 10 # starting fetch
        
        # Slow network call - executed with NO active database sessions or transactions held.
        yango_orders = await yango_client.get_all_completed_orders(
            date_from=date_from, 
            date_to=now,
            driver_profile_id=yango_driver_id
        )
        
        active_syncs["drivers"][driver_id]["progress"] = 50 # fetch complete, processing
        
        trips_inserted = 0
        trips_updated = 0
        
        # --- Session 2: Short-lived database session to write trips & success state ---
        with Session(engine) as db:
            for o in yango_orders:
                _, inserted, updated = _upsert_trip(db, o, driver_id)
                if inserted:
                    trips_inserted += 1
                if updated:
                    trips_updated += 1
            
            # Save the LAST_SYNC_DRIVER_{driver_id} in SystemConfig
            config_key = f"LAST_SYNC_DRIVER_{driver_id}"
            last_sync_conf = db.get(SystemConfig, config_key)
            if not last_sync_conf:
                last_sync_conf = SystemConfig(
                    key=config_key,
                    value=datetime.utcnow().isoformat() + "Z",
                    description=f"Timestamp of last sync for driver {driver_id}",
                    data_type="string",
                    updated_at=datetime.utcnow()
                )
                db.add(last_sync_conf)
            else:
                last_sync_conf.value = datetime.utcnow().isoformat() + "Z"
                last_sync_conf.updated_at = datetime.utcnow()
                db.add(last_sync_conf)
            
            db.commit()
            
            # Run post-sync auto-reconciliation of existing unreconciled deposits
            from app.services.reconciliation import reconcile_driver_unreconciled_deposits
            try:
                auto_reconciled = reconcile_driver_unreconciled_deposits(db, driver_id)
                if auto_reconciled > 0:
                    print(f"Post-sync auto-reconciliation: matched {auto_reconciled} trips for driver {driver_id}")
                db.commit()
            except Exception as auto_recon_err:
                print(f"Error in post-sync auto-reconciliation for driver {driver_id}: {auto_recon_err}")
                db.rollback()
            
            # Create success notification
            try:
                notif = Notification(
                    title="Manual Driver Sync Completed",
                    message=f"Manual sync for driver {driver_name} completed successfully: Imported {trips_inserted} new trips and updated {trips_updated} trips.",
                    type="success",
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(notif)
                db.commit()
            except Exception as notif_err:
                print(f"Error creating driver sync success notification: {notif_err}")

        active_syncs["drivers"][driver_id]["status"] = "completed"
        active_syncs["drivers"][driver_id]["progress"] = 100
        active_syncs["drivers"][driver_id]["trips_inserted"] = trips_inserted
        active_syncs["drivers"][driver_id]["trips_updated"] = trips_updated
        active_syncs["drivers"][driver_id]["completed_at"] = datetime.utcnow().isoformat() + "Z"
            
    except Exception as e:
        print(f"Error syncing driver orders: {e}")
        try:
            with Session(engine) as db:
                driver = db.get(Driver, driver_id)
                driver_name = driver.name if driver else f"Driver #{driver_id}"
                notif = Notification(
                    title="Manual Driver Sync Failed",
                    message=f"Manual sync failed for driver {driver_name}: {str(e)}",
                    type="error",
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(notif)
                db.commit()
        except Exception as notif_err:
            print(f"Error creating driver sync failure notification: {notif_err}")

        active_syncs["drivers"][driver_id]["status"] = "failed"
        active_syncs["drivers"][driver_id]["error"] = str(e)
        active_syncs["drivers"][driver_id]["completed_at"] = datetime.utcnow().isoformat() + "Z"


@router.post("/{driver_id}/sync-orders")
async def sync_driver_orders(
    driver_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Trigger background sync of latest orders for a specific driver."""
    if not user:
        raise HTTPException(status_code=401)
        
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    from app.routers.api_sync import active_syncs
    
    # Block if bulk sync is currently running
    if active_syncs.get("bulk", {}).get("status") == "running":
        return {"status": "running", "message": "Bulk sync is currently in progress. Please wait for it to complete."}
        
    if "drivers" not in active_syncs:
        active_syncs["drivers"] = {}
        
    driver_sync = active_syncs["drivers"].get(driver_id)
    if driver_sync and driver_sync["status"] == "running":
        return {"status": "running", "message": "Sync is already in progress for this driver"}
        
    background_tasks.add_task(run_driver_sync_background, driver_id)
    return {"status": "started", "message": "Sync started in the background"}


@router.get("/{driver_id}/sync-status")
async def get_driver_sync_status(driver_id: int, db: Session = Depends(get_session)):
    from app.routers.api_sync import active_syncs
    
    config_key = f"LAST_SYNC_DRIVER_{driver_id}"
    last_sync_conf = db.get(SystemConfig, config_key)
    last_sync = last_sync_conf.value if last_sync_conf else None
    
    # Check if bulk sync is currently running
    if active_syncs.get("bulk", {}).get("status") == "running":
        driver = db.get(Driver, driver_id)
        current_bulk_driver = active_syncs["bulk"].get("current_driver")
        is_this_driver = (driver.name == current_bulk_driver) if (driver and current_bulk_driver) else False
        
        return {
            "active": {
                "status": "running",
                "progress": active_syncs["bulk"].get("progress", 0),
                "started_at": active_syncs["bulk"].get("started_at"),
                "completed_at": None,
                "trips_inserted": active_syncs["bulk"].get("trips_inserted", 0),
                "trips_updated": active_syncs["bulk"].get("trips_updated", 0),
                "error": None,
                "is_bulk": True,
                "current_driver": current_bulk_driver,
                "is_this_driver": is_this_driver
            },
            "last_sync": last_sync
        }
        
    if "drivers" not in active_syncs:
        active_syncs["drivers"] = {}
        
    active_state = active_syncs["drivers"].get(driver_id, {
        "status": "idle",
        "progress": 0,
        "started_at": None,
        "completed_at": None,
        "trips_inserted": 0,
        "trips_updated": 0,
        "error": None
    })
    
    return {
        "active": active_state,
        "last_sync": last_sync
    }

from pydantic import BaseModel

class AvatarUpdate(BaseModel):
    avatar_data: str

@router.post("/{driver_id}/update-avatar")
async def update_driver_avatar(
    driver_id: int,
    payload: AvatarUpdate,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    avatar_data = payload.avatar_data
    """Update a driver's avatar image (Base64 string)."""
    if not user:
        raise HTTPException(status_code=401)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    old_avatar = "[Image Data]" if driver.avatar_data else "None"
    
    if not avatar_data or avatar_data.lower() in ("none", "null", ""):
        driver.avatar_data = None
        new_avatar = "None"
    else:
        driver.avatar_data = avatar_data
        new_avatar = "[Image Data]"
        
    db.add(driver)
    _record_audit_log(db, user.id, "driver", driver.id, "avatar_data", old_avatar, new_avatar)
    db.commit()
    return {"status": "success", "avatar_data": driver.avatar_data}

@router.post("/{driver_id}/reconciliation/mark-shift-paid")
async def mark_shift_paid(
    driver_id: int,
    target_date: str = Form(...),
    shift: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Mark an entire shift's unpaid cash trips as paid physically to the manager."""
    if not user:
        raise HTTPException(status_code=401)
        
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    try:
        parsed_date = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")
        
    from app.services.reconciliation import get_shift_windows
    
    trip_start, trip_end, _, _ = get_shift_windows(db, shift, parsed_date)
    
    # helper for naive vs aware
    def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
        
    # Query all completed cash trips for this driver
    trips = db.exec(
        select(DriverTrip)
        .where(
            DriverTrip.driver_id == driver_id,
            DriverTrip.payment_method == "cash",
            DriverTrip.status == "complete"
        )
    ).all()
    
    trips_to_update = []
    for t in trips:
        if t.booked_at:
            utc_booked = ensure_utc(t.booked_at)
            if trip_start <= utc_booked < trip_end:
                if t.reconciliation_status != "Verified":
                    trips_to_update.append(t)
                    
    # Update trips
    for trip in trips_to_update:
        old_status = trip.reconciliation_status
        old_deposited = trip.deposited_amount
        
        trip.deposited_amount = trip.price or 0.0
        trip.reconciliation_status = "Verified"
        trip.reconciliation_notes = notes or f"Shift manually marked as paid by Admin on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        trip.synced_at = datetime.utcnow()
        db.add(trip)
        
        # Audit logging
        if old_status != "Verified":
            _record_audit_log(db, user.id, "trip", trip.id, "reconciliation_status", old_status, "Verified")
        if old_deposited != trip.deposited_amount:
            _record_audit_log(db, user.id, "trip", trip.id, "deposited_amount", str(old_deposited), str(trip.deposited_amount))
            
    db.commit()
    return {"status": "success", "trips_updated": len(trips_to_update)}


@router.post("/{driver_id}/documents")
async def upload_driver_document(
    driver_id: int,
    document_type: str = Form(...),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Upload and record a driver document as a Base64 Data URL in the database."""
    if not user:
        raise HTTPException(status_code=401)
        
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    try:
        import base64
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        base64_data = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{file.content_type};base64,{base64_data}"
        
        doc = DriverDocument(
            driver_id=driver_id,
            document_type=document_type,
            filename=file.filename,
            content_type=file.content_type,
            file_data=data_url,
            notes=notes
        )
        
        db.add(doc)
        _record_audit_log(db, user.id, "driver", driver.id, "document_upload", "", f"{document_type}: {file.filename}")
        db.commit()
        db.refresh(doc)
        
        return {
            "status": "success",
            "document": {
                "id": doc.id,
                "document_type": doc.document_type,
                "filename": doc.filename,
                "content_type": doc.content_type,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "notes": doc.notes
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.delete("/{driver_id}/documents/{document_id}")
async def delete_driver_document(
    driver_id: int,
    document_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Delete a driver document."""
    if not user:
        raise HTTPException(status_code=401)
        
    doc = db.get(DriverDocument, document_id)
    if not doc or doc.driver_id != driver_id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        doc_info = f"{doc.document_type}: {doc.filename}"
        db.delete(doc)
        _record_audit_log(db, user.id, "driver", driver_id, "document_delete", doc_info, "")
        db.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


