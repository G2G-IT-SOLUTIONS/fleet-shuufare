from datetime import datetime, timezone
import dateutil.parser
from sqlmodel import Session

from app.database import engine
from app.models import SystemConfig, Notification
from app.routers.api_sync import active_syncs, run_bulk_sync_background

# We'll initialize the scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def check_and_run_scheduled_sync():
    """
    Periodic job (e.g. every 15 minutes) that:
    1. Checks if automated sync is enabled.
    2. Compares current time with the last completed bulk sync time.
    3. If the elapsed hours exceed AUTO_SYNC_INTERVAL_HOURS, triggers bulk sync background worker.
    Ensures safe locking, avoiding running during any active manual bulk or individual sync.
    """
    print("[Scheduler] Running schedule check tick...")
    
    try:
        with Session(engine) as db:
            # Load configs
            enabled_conf = db.get(SystemConfig, "AUTO_SYNC_ENABLED")
            is_enabled = enabled_conf.value.lower() == "true" if enabled_conf else True
            
            if not is_enabled:
                # Silently return if disabled
                return
                
            interval_conf = db.get(SystemConfig, "AUTO_SYNC_INTERVAL_HOURS")
            try:
                interval_hours = int(interval_conf.value) if interval_conf else 6
            except Exception:
                interval_hours = 6
                
            last_sync_conf = db.get(SystemConfig, "LAST_BULK_SYNC")
            last_sync_str = last_sync_conf.value if last_sync_conf else None
    except Exception as db_err:
        print(f"[Scheduler] Database reading error during tick: {db_err}")
        return
        
    # Check elapsed time
    should_sync = False
    if not last_sync_str:
        print("[Scheduler] No LAST_BULK_SYNC found. Triggering sync.")
        should_sync = True
    else:
        try:
            # Parse ISO-8601 UTC timestamp safely using dateutil
            last_sync_dt = dateutil.parser.isoparse(last_sync_str)
            # Ensure localized to UTC
            if last_sync_dt.tzinfo is None:
                last_sync_dt = last_sync_dt.replace(tzinfo=timezone.utc)
            else:
                last_sync_dt = last_sync_dt.astimezone(timezone.utc)
                
            now_utc = datetime.now(timezone.utc)
            elapsed_seconds = (now_utc - last_sync_dt).total_seconds()
            elapsed_hours = elapsed_seconds / 3600.0
            
            print(f"[Scheduler] Hours since last completed bulk sync: {elapsed_hours:.2f}h / {interval_hours}h required.")
            if elapsed_hours >= interval_hours:
                should_sync = True
        except Exception as parse_err:
            print(f"[Scheduler] Error parsing LAST_BULK_SYNC '{last_sync_str}': {parse_err}. Resetting to trigger sync.")
            should_sync = True
            
    if not should_sync:
        return
        
    # Check if a bulk sync is already running
    if active_syncs["bulk"]["status"] == "running":
        print("[Scheduler] A bulk sync is already in progress. Skipping scheduled trigger.")
        return
        
    # Check if any individual driver sync is currently running
    drivers_dict = active_syncs.get("drivers", {})
    for d_id, d_sync in drivers_dict.items():
        if d_sync.get("status") == "running" and not d_sync.get("is_bulk"):
            print(f"[Scheduler] Individual sync is running for driver #{d_id}. Deferring scheduled trigger to prevent database locks.")
            return
            
    # Trigger the background bulk sync
    print("[Scheduler] Automated sync interval reached. Triggering bulk background synchronization...")
    try:
        # Await the background worker directly on the main event loop, passing is_scheduled=True
        # This will automatically handle starting, success, and failure notifications.
        await run_bulk_sync_background(is_scheduled=True)
        print("[Scheduler] Automated bulk sync process run completed.")
    except Exception as run_err:
        print(f"[Scheduler] Unexpected error during automated bulk sync job: {run_err}")
