from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, func, or_, and_
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from app.core.dependencies import get_session, get_current_user, templates, yango_client
from app.models import User, Driver, DriverTrip, SystemConfig, TelebirrTransaction, ReconciliationBatch, DepositTripLink, ReconciliationRecord
from app.services.reconciliation import get_shift_windows

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    search: str = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
    page: int = 1,
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """Main dashboard showing high-level trip reconciliation KPIs."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # 1. Driver Stats
    total_internal_drivers = db.exec(select(func.count(Driver.id)).where(Driver.driver_type == "internal")).first() or 0
    total_drivers = db.exec(select(func.count(Driver.id))).first() or 0
    
    # 2. Financial Stats (Global Cash Trips)
    total_expected_cash = db.exec(
        select(func.sum(DriverTrip.price))
        .where(DriverTrip.payment_method == "cash", DriverTrip.status == "complete")
    ).first() or 0.0
    
    total_reconciled_cash = db.exec(
        select(func.sum(DriverTrip.deposited_amount))
        .where(DriverTrip.payment_method == "cash", DriverTrip.status == "complete")
    ).first() or 0.0
    
    today_expected_cash = db.exec(
        select(func.sum(DriverTrip.price))
        .where(
            DriverTrip.payment_method == "cash", 
            DriverTrip.status == "complete",
            DriverTrip.booked_at >= today_start
        )
    ).first() or 0.0
    
    total_exceptions = db.exec(
        select(func.count(DriverTrip.id))
        .where(
            DriverTrip.payment_method == "cash", 
            DriverTrip.status == "complete",
            DriverTrip.reconciliation_status != "Verified"
        )
    ).first() or 0

    # 3. Compliance Distribution (Doughnut Chart)
    status_counts_raw = db.exec(
        select(DriverTrip.reconciliation_status, func.count(DriverTrip.id))
        .where(DriverTrip.payment_method == "cash", DriverTrip.status == "complete")
        .group_by(DriverTrip.reconciliation_status)
    ).all()
    compliance_dist = {status: count for status, count in status_counts_raw}

    # 4. Exception Trend (Bar Chart - Last 14 Days)
    fourteen_days_ago = today - timedelta(days=14)
    trend_raw = db.exec(
        select(func.date(DriverTrip.booked_at), func.count(DriverTrip.id))
        .where(
            DriverTrip.payment_method == "cash", 
            DriverTrip.status == "complete",
            DriverTrip.reconciliation_status != "Verified",
            DriverTrip.booked_at >= fourteen_days_ago
        )
        .group_by(func.date(DriverTrip.booked_at))
        .order_by(func.date(DriverTrip.booked_at))
    ).all()
    
    # Fill gaps for trend data
    exception_trend = []
    for i in range(14):
        d = fourteen_days_ago + timedelta(days=i+1)
        d_str = d.strftime('%Y-%m-%d')
        count = next((c for date_obj, c in trend_raw if str(date_obj) == d_str), 0)
        exception_trend.append({"date": d.strftime('%b %d'), "count": count})

    kpis = {
        "total_drivers": total_drivers,
        "total_internal_drivers": total_internal_drivers,
        "total_expected_cash": total_expected_cash,
        "total_reconciled_cash": total_reconciled_cash,
        "today_expected_cash": today_expected_cash,
        "total_exceptions": total_exceptions,
        "reconciliation_rate": (total_reconciled_cash / total_expected_cash * 100) if total_expected_cash > 0 else 100.0,
        "compliance_dist": compliance_dist,
        "exception_trend": exception_trend
    }
        
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={
            "kpis": kpis,
            "today": today,
            "user": user
        }
    )

@router.get("/settings/users", response_class=HTMLResponse)
async def settings_users(request: Request, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or user.role != 'admin': 
        return RedirectResponse(url="/", status_code=303)
    
    users = db.exec(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(
        request=request, 
        name="settings/users.html", 
        context={"users": users, "user": user}
    )

@router.get("/settings/roles", response_class=HTMLResponse)
async def settings_roles(request: Request, user: User = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="settings/roles.html", context={"user": user})

@router.get("/settings/configs", response_class=HTMLResponse)
async def settings_configs(request: Request, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login", status_code=303)
    configs = db.exec(select(SystemConfig).where(~SystemConfig.key.like("LAST_%"))).all()
    return templates.TemplateResponse(request=request, name="settings/configs.html", context={"configs": configs, "user": user})

@router.get("/exceptions", response_class=HTMLResponse)
async def exceptions_view(
    request: Request, 
    date_from: str = None, 
    date_to: str = None, 
    status: str = None,
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """View trips with reconciliation discrepancies with filtering."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    today = date.today()
    
    # 1. Build Query
    statement = select(DriverTrip).where(DriverTrip.payment_method == "cash", DriverTrip.status == "complete")
    
    if date_from:
        df = datetime.fromisoformat(date_from)
        statement = statement.where(DriverTrip.booked_at >= df)
    if date_to:
        dt = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59)
        statement = statement.where(DriverTrip.booked_at <= dt)
    
    if status:
        if status == "Missing Deposit":
            statement = statement.where(DriverTrip.reconciliation_status.in_(["Missing Deposit", "Pending"]))
        else:
            statement = statement.where(DriverTrip.reconciliation_status == status)
    else:
        statement = statement.where(DriverTrip.reconciliation_status != "Verified")
        
    statement = statement.order_by(DriverTrip.booked_at.desc())
    
    exception_trips = db.exec(statement).all()
    
    # 2. Fetch driver info and links
    driver_ids = {t.driver_id for t in exception_trips}
    drivers = db.exec(select(Driver).where(Driver.id.in_(driver_ids))).all() if driver_ids else []
    driver_map = {d.id: d for d in drivers}
    
    trip_ids = [t.id for t in exception_trips]
    links = db.exec(select(DepositTripLink).where(DepositTripLink.trip_id.in_(trip_ids))).all() if trip_ids else []
    
    from collections import defaultdict
    links_map = defaultdict(list)
    for link in links:
        links_map[link.trip_id].append({
            "transaction_id": link.transaction_id,
            "amount_applied": link.amount_applied
        })
    
    # 3. Summary Stats
    global_total_expected = db.exec(select(func.sum(DriverTrip.price)).where(DriverTrip.payment_method == "cash", DriverTrip.status == "complete")).first() or 0.0
    global_total_actual = db.exec(select(func.sum(DriverTrip.deposited_amount)).where(DriverTrip.payment_method == "cash", DriverTrip.status == "complete")).first() or 0.0
    
    verified_count = db.exec(select(func.count(DriverTrip.id)).where(DriverTrip.payment_method == "cash", DriverTrip.reconciliation_status == "Verified")).first() or 0
    missing_count = db.exec(select(func.count(DriverTrip.id)).where(DriverTrip.payment_method == "cash", DriverTrip.reconciliation_status.in_(["Missing Deposit", "Pending"]))).first() or 0
    partial_count = db.exec(select(func.count(DriverTrip.id)).where(DriverTrip.payment_method == "cash", DriverTrip.reconciliation_status == "Partial Deposit")).first() or 0
    
    # 4. Format data
    exceptions_data = []
    for t in exception_trips:
        driver = driver_map.get(t.driver_id)
        if not driver: continue
        
        display_status = t.reconciliation_status
        if display_status == "Pending" and t.booked_at and t.booked_at.date() < today:
            display_status = "Missing Deposit"
            
        color = "red" if display_status == "Missing Deposit" else "orange" if display_status == "Partial Deposit" else "blue"
            
        exceptions_data.append({
            "id": t.id,
            "short_id": t.short_id,
            "driver": driver,
            "expected": t.price or 0.0,
            "actual": t.deposited_amount,
            "status": display_status,
            "notes": t.reconciliation_notes,
            "color": color,
            "date": t.booked_at.strftime('%Y-%m-%d %H:%M') if t.booked_at else "—",
            "links": links_map[t.id]
        })
        
    reconciliation_rate = (global_total_actual / global_total_expected * 100) if global_total_expected > 0 else 100.0
    
    # 5. Fetch batches
    batches = db.exec(select(ReconciliationBatch).order_by(ReconciliationBatch.created_at.desc())).all()
            
    return templates.TemplateResponse(
        request=request,
        name="exceptions.html", 
        context={
            "data": exceptions_data,
            "filters": {"date_from": date_from, "date_to": date_to, "status": status},
            "kpis": {
                "total_expected": global_total_expected,
                "total_actual": global_total_actual,
                "verified_count": verified_count,
                "missing_count": missing_count,
                "partial_count": partial_count,
                "reconciliation_rate": reconciliation_rate
            },
            "batches": batches,
            "user": user
        }
    )

@router.get("/orders", response_class=HTMLResponse)
async def orders_view(
    request: Request,
    cursor: str = None,
    search: str = None,
    days: int = 1,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Fetch one page of completed orders directly from Yango API."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    now = datetime.now(timezone.utc)
    date_from = datetime.combine((now - timedelta(days=days - 1)).date(), datetime.min.time()).replace(tzinfo=timezone.utc)
    date_to = now

    search_kwargs = {
        "cursor": cursor,
        "limit": 20,
        "date_from": date_from,
        "date_to": date_to
    }
    
    is_deep_scan = False
    all_orders = []
    next_cursor = None
    
    if search:
        s = search.strip()
        deep_scan_limit_conf = db.get(SystemConfig, "DEEP_SCAN_MAX_DAYS")
        deep_scan_limit = int(deep_scan_limit_conf.value) if deep_scan_limit_conf else 365
        
        if len(s.replace("-", "")) == 32 and all(c in "0123456789abcdefABCDEF" for c in s.replace("-", "")):
            driver = db.exec(select(Driver).where(Driver.yango_driver_id == s)).first()
            if driver:
                search_kwargs["driver_profile_id"] = s
                is_deep_scan = True
            else:
                search_kwargs["order_ids"] = [s]
                search_kwargs["date_from"] = now - timedelta(days=deep_scan_limit)
                search_kwargs["date_to"] = now
                is_deep_scan = True
        elif s.isdigit() and len(s) < 10:
            search_kwargs["short_ids"] = [int(s)]
            search_kwargs["date_from"] = now - timedelta(days=deep_scan_limit)
            search_kwargs["date_to"] = now
            is_deep_scan = True
        else:
            driver = db.exec(select(Driver).where(
                or_(Driver.name.ilike(f"%{s}%"), Driver.phone.ilike(f"%{s}%"))
            )).first()
            if driver:
                search_kwargs["driver_profile_id"] = driver.yango_driver_id
                is_deep_scan = True

    raw_orders, next_cursor = await yango_client.get_orders_page(**search_kwargs)

    # Map Yango profile IDs to local database Driver IDs
    yango_profile_ids = {o.get("driver_profile", {}).get("id") for o in raw_orders if o.get("driver_profile", {}).get("id")}
    driver_id_map = {}
    if yango_profile_ids:
        drivers = db.exec(select(Driver).where(Driver.yango_driver_id.in_(yango_profile_ids))).all()
        driver_id_map = {d.yango_driver_id: d.id for d in drivers}

    def parse_order(o, idx):
        profile = o.get("driver_profile") or {}
        addr = o.get("address_from") or {}
        ended_raw = o.get("ended_at") or o.get("booked_at") or ""
        try:
            ended_dt = datetime.fromisoformat(ended_raw.replace("Z", "+00:00"))
        except Exception:
            ended_dt = None
        try:
            price = float(o.get("price") or 0)
        except (ValueError, TypeError):
            price = 0.0
            
        profile_id = profile.get("id")
        internal_driver_id = driver_id_map.get(profile_id) if profile_id else None
        
        return {
            "seq": idx,
            "id": o.get("id", ""),
            "short_id": o.get("short_id", ""),
            "driver_name": profile.get("name") or (
                f"{profile.get('first_name','')} {profile.get('last_name','')}".strip()
            ) or "Unknown",
            "driver_id": internal_driver_id,
            "payment_method": o.get("payment_method", ""),
            "price": price,
            "status": o.get("status", ""),
            "ended_at": ended_dt,
            "address_from": addr.get("address") if isinstance(addr, dict) else None,
        }

    all_orders = [parse_order(o, i + 1) for i, o in enumerate(raw_orders)]

    if search and not is_deep_scan:
        s = search.strip().lower()
        all_orders = [
            o for o in all_orders
            if s in o["id"].lower()
            or s in str(o["short_id"])
            or s in o["driver_name"].lower()
        ]

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "orders": all_orders,
            "next_cursor": next_cursor,
            "cursor": cursor,
            "search": search or "",
            "days": days,
            "total_count": len(all_orders),
            "user": user
        }
    )

@router.get("/drivers", response_class=HTMLResponse)
async def drivers_view(
    request: Request, 
    search: str = None, 
    date_from: str = None,
    date_to: str = None,
    shift: str = None,
    payment_status: str = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """View dedicated only to managed drivers with aggregated totals."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    trip_conditions = [
        (Driver.id == DriverTrip.driver_id),
        (DriverTrip.payment_method == "cash"),
        (DriverTrip.status == "complete"),
        or_(
            Driver.reconciliation_start_date == None,
            DriverTrip.booked_at >= Driver.reconciliation_start_date
        )
    ]
    
    if date_from:
        df = datetime.fromisoformat(date_from)
        trip_conditions.append(DriverTrip.booked_at >= df)
    if date_to:
        dt = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59)
        trip_conditions.append(DriverTrip.booked_at <= dt)

    statement = (
        select(
            Driver,
            func.coalesce(func.sum(DriverTrip.price), 0.0).label("total_expected"),
            func.coalesce(func.sum(DriverTrip.deposited_amount), 0.0).label("total_actual")
        )
        .outerjoin(DriverTrip, and_(*trip_conditions))
        .where(Driver.driver_type == "internal")
        .group_by(Driver.id)
    )

    if search:
        statement = statement.where(
            (Driver.name.ilike(f"%{search}%")) | 
            (Driver.yango_driver_id.ilike(f"%{search}%")) |
            (Driver.phone.ilike(f"%{search}%"))
        )
        
    if shift:
        statement = statement.where(Driver.shift == shift)

    # Fetch results from database
    results = db.exec(statement).all()
    
    # Fetch all Telebirr transaction sums grouped by driver_id to calculate real-time ledger balances efficiently
    tx_stmt = select(TelebirrTransaction.driver_id, func.sum(TelebirrTransaction.amount)).where(TelebirrTransaction.driver_id != None).group_by(TelebirrTransaction.driver_id)
    tx_sums = {driver_id: total_amount for driver_id, total_amount in db.exec(tx_stmt).all()}
    
    drivers_data = []
    for driver, expected, actual in results:
        total_deposited_ledger = tx_sums.get(driver.id, 0.0)
        ledger_balance = total_deposited_ledger - expected
        
        if ledger_balance < -0.01:
            ledger_status = "Outstanding"
            ledger_color = "red"
        elif ledger_balance > 0.01:
            ledger_status = "Prepaid"
            ledger_color = "green"
        else:
            ledger_status = "Settled"
            ledger_color = "gray"
            
        drivers_data.append({
            "driver": driver,
            "expected": expected,
            "actual": actual,
            "variance": actual - expected,
            "ledger_deposited": total_deposited_ledger,
            "ledger_balance": ledger_balance,
            "ledger_status": ledger_status,
            "ledger_color": ledger_color
        })
        
    # Apply payment status filtering in Python
    if payment_status == "paid":
        drivers_data = [d for d in drivers_data if d["ledger_balance"] >= -0.01]
    elif payment_status == "partial":
        drivers_data = [d for d in drivers_data if d["ledger_balance"] < -0.01 and d["ledger_deposited"] > 0]
    elif payment_status == "pending":
        drivers_data = [d for d in drivers_data if d["ledger_balance"] < -0.01 and d["ledger_deposited"] == 0]
        
    # Apply sorting in Python
    reverse_sort = (sort_dir == "desc")
    if sort_by == "expected":
        drivers_data.sort(key=lambda x: x["expected"], reverse=reverse_sort)
    elif sort_by == "actual":
        drivers_data.sort(key=lambda x: x["actual"], reverse=reverse_sort)
    elif sort_by == "unpaid":
        drivers_data.sort(key=lambda x: x["expected"] - x["actual"], reverse=reverse_sort)
    elif sort_by == "ledger":
        drivers_data.sort(key=lambda x: x["ledger_balance"], reverse=reverse_sort)
    else: # Default by name
        drivers_data.sort(key=lambda x: x["driver"].name.lower(), reverse=reverse_sort)
        
    return templates.TemplateResponse(
        request=request,
        name="internal_drivers.html",
        context={
            "drivers_data": drivers_data, 
            "filters": {
                "search": search or "",
                "date_from": date_from or "",
                "date_to": date_to or "",
                "shift": shift or "",
                "payment_status": payment_status or "",
                "sort_by": sort_by,
                "sort_dir": sort_dir
            },
            "user": user
        }
    )

@router.get("/drivers/{driver_id}", response_class=HTMLResponse)
async def driver_detail_view(request: Request, driver_id: int, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """Deep dive into a specific driver's performance and reconciliation."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
        
    transactions = db.exec(
        select(TelebirrTransaction).where(TelebirrTransaction.driver_id == driver.id).order_by(TelebirrTransaction.timestamp.desc())
    ).all()
    
    db_trips = db.exec(
        select(DriverTrip).where(DriverTrip.driver_id == driver.id).order_by(DriverTrip.booked_at.desc())
    ).all()
    
    # Filter trips based on reconciliation start date
    start_date = driver.reconciliation_start_date
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        valid_trips = [t for t in db_trips if t.booked_at and ensure_utc(t.booked_at) >= start_datetime]
    else:
        valid_trips = db_trips
        start_datetime = None
    
    # Fetch links early to determine manual direct cash payments vs matched bank transactions
    trip_ids = [t.id for t in db_trips]
    links = []
    if trip_ids:
        links = db.exec(select(DepositTripLink).where(DepositTripLink.trip_id.in_(trip_ids))).all()
    linked_trip_ids = {l.trip_id for l in links}
    
    total_expected = sum([t.price for t in valid_trips if t.price and t.payment_method == "cash"])
    
    # Total actual deposited is the total successful telebirr deposits + manual direct cash payments (no bank link)
    manual_cash_payments = sum([t.deposited_amount for t in valid_trips if t.id not in linked_trip_ids and t.deposited_amount])
    total_deposited_ledger = sum([tx.amount for tx in transactions]) + manual_cash_payments
    ledger_balance = total_deposited_ledger - total_expected
    
    if ledger_balance < -0.01:
        ledger_status = "Outstanding"
        ledger_color = "red"
    elif ledger_balance > 0.01:
        ledger_status = "Prepaid"
        ledger_color = "green"
    else:
        ledger_status = "Settled"
        ledger_color = "gray"
        
    # Maintain compatibility with existing UI metrics
    total_actual = sum([t.deposited_amount for t in valid_trips if t.payment_method == "cash"])
    variance = total_actual - total_expected
    compliance = (total_actual / total_expected * 100) if total_expected > 0 else 100.0
    
    today = date.today()
    today_expected = sum([t.price for t in db_trips if t.price and t.payment_method == "cash" and t.booked_at and t.booked_at.date() == today])
    total_made = sum([t.price for t in db_trips if t.price])

    yango_profile = await yango_client.get_driver_profile(driver.yango_driver_id)
        
    # Dynamic daily shift-aware reconciliations over the last 30 days
    today_local = (datetime.utcnow() + timedelta(hours=3)).date()
    dynamic_reconciliations = []
    for i in range(30):
        target_date = today_local - timedelta(days=i)
        
        trip_start, trip_end, deposit_start, deposit_end = get_shift_windows(db, driver.shift, target_date)
        
        if start_datetime and trip_end <= start_datetime:
            continue
            
        # Cash trips in shift trip window
        day_trips = [t for t in db_trips if t.payment_method == "cash" and t.status == "complete" and t.booked_at and ensure_utc(t.booked_at) >= trip_start and ensure_utc(t.booked_at) < trip_end]
        if start_datetime:
            day_trips = [t for t in day_trips if ensure_utc(t.booked_at) >= start_datetime]
            
        day_expected = sum([t.price for t in day_trips if t.price])
        
        # Telebirr transactions in shift deposit window
        day_txs = [tx for tx in transactions if tx.timestamp and ensure_utc(tx.timestamp) >= deposit_start and ensure_utc(tx.timestamp) < deposit_end]
        day_actual_txs = sum([tx.amount for tx in day_txs])
        
        # Consider physical cash payments directly mapped to trips
        day_trip_deposits = sum([t.deposited_amount for t in day_trips if t.deposited_amount])
        day_actual = max(day_actual_txs, day_trip_deposits)
        
        # Skip empty days unless it's today
        if day_expected == 0 and day_actual == 0 and target_date != today_local:
            continue
            
        day_balance = day_actual - day_expected
        
        # All trips in shift are Verified -> Shift is Verified
        if len(day_trips) > 0 and all(t.reconciliation_status == "Verified" for t in day_trips):
            day_status = "Verified"
            if day_balance < 0:
                day_balance = 0.0
        elif abs(day_balance) < 0.01:
            day_status = "Verified"
        elif day_actual == 0:
            day_status = "Missing Deposit"
        elif day_actual < day_expected:
            day_status = "Partial Deposit"
        else:
            day_status = "Excess Deposit"
            
        dynamic_reconciliations.append({
            "date": target_date,
            "expected_amount": day_expected,
            "actual_amount": day_actual,
            "balance": day_balance,
            "status": day_status,
            "trips_count": len(day_trips),
            "txs_count": len(day_txs)
        })
        
    return templates.TemplateResponse(
        request=request,
        name="driver_detail.html",
        context={
            "driver": driver,
            "transactions": transactions,
            "db_trips": db_trips,
            "links": links,
            "yango_profile": yango_profile,
            "reconciliations": dynamic_reconciliations,
            "ledger": {
                "total_expected": total_expected,
                "total_deposited": total_deposited_ledger,
                "balance": ledger_balance,
                "status": ledger_status,
                "color": ledger_color
            },
            "kpis": {
                "total_expected": total_expected,
                "total_actual": total_actual,
                "variance": variance,
                "compliance": compliance,
                "today_expected": today_expected,
                "total_made": total_made
            },
            "user": user
        }
    )

@router.get("/users", response_class=HTMLResponse)
async def user_management_page(request: Request, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or user.role != "admin":
        return RedirectResponse(url="/", status_code=303)
    users = db.exec(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(request=request, name="user_management.html", context={"users": users, "user": user})

@router.get("/profile", response_class=HTMLResponse)
async def user_profile_page(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="user_profile.html", context={"user": user})

@router.get("/maps", response_class=HTMLResponse)
async def maps_view(
    request: Request,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """View presenting real-time driver tracking on an interactive map."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    statement = select(Driver).where(Driver.driver_type == "internal").order_by(Driver.name)
    drivers = db.exec(statement).all()
    
    return templates.TemplateResponse(
        request=request,
        name="maps.html",
        context={
            "drivers": drivers,
            "user": user
        }
    )
