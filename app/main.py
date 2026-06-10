from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import select

from app.database import create_db_and_tables, get_session
from app.models import User, SystemConfig
from app.core.dependencies import pwd_context

# Import routers
from app.routers import auth, views, api_drivers, api_yango, api_users, api_sync, api_system

app = FastAPI(title="FLOS - Telebirr Integration Simulator")

# Static files not currently used in this project
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Create default admin if not exists
    with next(get_session()) as db:
        admin = db.exec(select(User).where(User.email == "admin@shuufare.com")).first()
        if not admin:
            hashed_pwd = pwd_context.hash("admin123")
            admin = User(email="admin@shuufare.com", hashed_password=hashed_pwd, full_name="System Admin", role="admin")
            db.add(admin)
            
        # Seed default configs
        default_configs = [
            {"key": "DRIVER_SYNC_LOOKBACK_DAYS", "value": "7", "description": "Delta sync lookback window for driver profiles", "data_type": "int"},
            {"key": "LATEST_ORDERS_SYNC_DAYS", "value": "1", "description": "Lookback window for syncing orders for a specific driver", "data_type": "int"},
            {"key": "DEEP_SCAN_MAX_DAYS", "value": "365", "description": "Maximum search timeframe for Deep Scan orders lookup", "data_type": "int"},
            {"key": "AUTO_SYNC_ENABLED", "value": "true", "description": "Enable automated background order syncing", "data_type": "string"},
            {"key": "AUTO_SYNC_INTERVAL_HOURS", "value": "6", "description": "Interval in hours between automated background runs", "data_type": "int"},
            {"key": "RECONCILE_ENFORCE_TIME_SEQUENCE", "value": "true", "description": "If enabled, automatic reconciliation will only match Telebirr deposits with trips completed before the deposit timestamp", "data_type": "string"},
            {"key": "SMS_GATEWAY_PHONE_FORMAT", "value": "canonical", "description": "Phone number format expected by the SMS gateway ('canonical' for +251..., 'international_no_plus' for 251..., 'local_with_zero' for 09..., 'raw_9_digits' for 9...)", "data_type": "string"},
            {"key": "SHIFT_DAY_START", "value": "06:00", "description": "Start time for the Day Shift (Format HH:MM)", "data_type": "string"},
            {"key": "SHIFT_DAY_END", "value": "18:00", "description": "End time for the Day Shift (Format HH:MM)", "data_type": "string"},
            {"key": "SHIFT_NIGHT_START", "value": "18:00", "description": "Start time for the Night Shift (Format HH:MM)", "data_type": "string"},
            {"key": "SHIFT_NIGHT_END", "value": "06:00", "description": "End time for the Night Shift (Format HH:MM)", "data_type": "string"}
        ]
        
        for conf in default_configs:
            if not db.get(SystemConfig, conf["key"]):
                db.add(SystemConfig(**conf))
                
        db.commit()

    # Start automated background synchronization scheduler
    try:
        from app.services.scheduler import scheduler, check_and_run_scheduled_sync
        scheduler.add_job(check_and_run_scheduled_sync, "interval", minutes=15, id="scheduled_sync_check")
        scheduler.start()
        print("[Startup] Background synchronization scheduler started successfully.")
    except Exception as sched_err:
        print(f"[Startup] Error starting scheduler: {sched_err}")

@app.on_event("shutdown")
def on_shutdown():
    try:
        from app.services.scheduler import scheduler
        scheduler.shutdown()
        print("[Shutdown] Background scheduler shut down cleanly.")
    except Exception as shutdown_err:
        print(f"[Shutdown] Error during background scheduler shutdown: {shutdown_err}")

# Register Routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(views.router, tags=["Frontend Views"])
app.include_router(api_drivers.router, prefix="/api/drivers", tags=["Drivers API"])
app.include_router(api_yango.router, prefix="/api/yango", tags=["Yango API"])
app.include_router(api_users.router, prefix="/api/users", tags=["Users API"])
app.include_router(api_sync.router, prefix="/api", tags=["Sync & Reconciliation API"]) # handles /api/sync/* and /api/reconciliation/* and /api/telebirr/*
app.include_router(api_system.router, prefix="/api", tags=["System API"]) # handles /api/notifications/* and /api/configs/* and /api/me
