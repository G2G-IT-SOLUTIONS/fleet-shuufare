from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List
from datetime import date, datetime, timezone
import uuid

from app.database import create_db_and_tables, get_session
from app.models import Driver, ExpectedRevenue, TelebirrTransaction, ReconciliationRecord, Order
from app.services.yango import YangoClient

app = FastAPI(title="FLOS - Telebirr Integration Simulator")
yango_client = YangoClient()

# Setting up Jinja2 templates
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ==========================================
# FRONTEND VIEWS
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, search: str = None, db: Session = Depends(get_session)):
    """Main operations dashboard."""
    # Fetch drivers and their latest reconciliation record
    statement = select(Driver)
    if search:
        statement = statement.where(
            (Driver.name.ilike(f"%{search}%")) | 
            (Driver.operator_id.ilike(f"%{search}%")) |
            (Driver.phone.ilike(f"%{search}%"))
        )
    drivers = db.exec(statement).all()
    
    # We will compute reconciliation on the fly for today for simplicity, 
    # or just show the records. Let's show today's expected vs actual.
    today = date.today()
    dashboard_data = []
    
    for d in drivers:
        expected = db.exec(
            select(ExpectedRevenue).where(ExpectedRevenue.driver_id == d.id, ExpectedRevenue.date == today)
        ).first()
        
        actual_txs = db.exec(
            select(TelebirrTransaction).where(TelebirrTransaction.driver_id == d.id)
        ).all()
        # Filter for today
        actual_today = sum([tx.amount for tx in actual_txs if tx.timestamp.date() == today])
        
        expected_amt = expected.expected_amount if expected else 0.0
        
        # Calculate status manually for dashboard view
        if expected_amt == 0 and actual_today == 0:
            status = "No Activity"
            color = "gray"
        elif actual_today == expected_amt:
            status = "Verified"
            color = "green"
        elif actual_today == 0:
            status = "Missing Deposit"
            color = "red"
        elif actual_today < expected_amt:
            status = "Partial Deposit"
            color = "orange"
        else:
            status = "Excess Deposit"
            color = "blue"
            
        dashboard_data.append({
            "driver": d,
            "expected": expected_amt,
            "actual": actual_today,
            "status": status,
            "color": color
        })
        
    # KPI Calculations
    total_expected = sum(item["expected"] for item in dashboard_data)
    total_actual = sum(item["actual"] for item in dashboard_data)
    total_drivers = len(dashboard_data)
    reconciled_drivers = sum(1 for item in dashboard_data if item["status"] == "Verified")
    exceptions_count = sum(1 for item in dashboard_data if item["status"] in ["Missing Deposit", "Partial Deposit", "Excess Deposit"])
    reconciliation_rate = (reconciled_drivers / total_drivers * 100) if total_drivers > 0 else 0
    
    kpis = {
        "total_expected": total_expected,
        "total_actual": total_actual,
        "total_drivers": total_drivers,
        "reconciled_drivers": reconciled_drivers,
        "exceptions_count": exceptions_count,
        "reconciliation_rate": reconciliation_rate,
        "unreconciled_drivers": total_drivers - reconciled_drivers
    }
        
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={
            "data": dashboard_data,
            "today": today,
            "kpis": kpis
        }
    )

@app.get("/simulator", response_class=HTMLResponse)
async def simulator_view(request: Request, db: Session = Depends(get_session)):
    """UI to mock a deposit."""
    drivers = db.exec(select(Driver)).all()
    return templates.TemplateResponse(
        request=request,
        name="simulator.html", 
        context={
            "drivers": drivers
        }
    )

@app.get("/exceptions", response_class=HTMLResponse)
async def exceptions_view(request: Request, db: Session = Depends(get_session)):
    """View only drivers with reconciliation discrepancies and summary stats."""
    drivers = db.exec(select(Driver)).all()
    today = date.today()
    exceptions_data = []
    
    total_reconciled_val = 0
    total_unreconciled_val = 0
    missing_count = 0
    partial_count = 0
    excess_count = 0
    
    for d in drivers:
        expected = db.exec(
            select(ExpectedRevenue).where(ExpectedRevenue.driver_id == d.id, ExpectedRevenue.date == today)
        ).first()
        
        actual_txs = db.exec(
            select(TelebirrTransaction).where(TelebirrTransaction.driver_id == d.id)
        ).all()
        actual_today = sum([tx.amount for tx in actual_txs if tx.timestamp.date() == today])
        
        expected_amt = expected.expected_amount if expected else 0.0
        
        if expected_amt == 0 and actual_today == 0:
            continue 
        
        if actual_today != expected_amt:
            if actual_today == 0:
                status, color = "Missing Deposit", "red"
                missing_count += 1
            elif actual_today < expected_amt:
                status, color = "Partial Deposit", "orange"
                partial_count += 1
            else:
                status, color = "Excess Deposit", "blue"
                excess_count += 1
            
            total_unreconciled_val += (expected_amt - actual_today)
                
            exceptions_data.append({
                "driver": d,
                "expected": expected_amt,
                "actual": actual_today,
                "status": status,
                "color": color
            })
        else:
            total_reconciled_val += actual_today
            
    reconciliation_rate = (total_reconciled_val / (total_reconciled_val + abs(total_unreconciled_val)) * 100) if (total_reconciled_val + abs(total_unreconciled_val)) > 0 else 100
            
    return templates.TemplateResponse(
        request=request,
        name="exceptions.html", 
        context={
            "data": exceptions_data,
            "today": today,
            "kpis": {
                "missing_count": missing_count,
                "partial_count": partial_count,
                "excess_count": excess_count,
                "total_drivers": len(drivers),
                "reconciliation_rate": reconciliation_rate
            }
        }
    )

@app.get("/orders", response_class=HTMLResponse)
async def orders_view(request: Request, search: str = None, db: Session = Depends(get_session), page: int = 1):
    """View completed orders cached in the database with search."""
    limit = 50
    offset = (page - 1) * limit
    
    statement = select(Order).order_by(Order.ended_at.desc())
    if search:
        statement = statement.where(
            (Order.driver_name.ilike(f"%{search}%")) | 
            (Order.driver_id.ilike(f"%{search}%")) |
            (Order.id.ilike(f"%{search}%"))
        )
        
    orders = db.exec(statement.offset(offset).limit(limit)).all()
    
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "orders": orders,
            "page": page
        }
    )

@app.get("/internal-drivers", response_class=HTMLResponse)
async def internal_drivers_view(request: Request, search: str = None, db: Session = Depends(get_session)):
    """View dedicated only to internal drivers."""
    statement = select(Driver).where(Driver.driver_type == "internal")
    if search:
        statement = statement.where(
            (Driver.name.ilike(f"%{search}%")) | 
            (Driver.operator_id.ilike(f"%{search}%")) |
            (Driver.phone.ilike(f"%{search}%"))
        )
    drivers = db.exec(statement).all()
    
    return templates.TemplateResponse(
        request=request,
        name="internal_drivers.html",
        context={"drivers": drivers}
    )

@app.get("/drivers/{driver_id}", response_class=HTMLResponse)
async def driver_detail_view(request: Request, driver_id: int, db: Session = Depends(get_session)):
    """Deep dive into a specific driver's performance and reconciliation."""
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    # Get all transactions
    transactions = db.exec(
        select(TelebirrTransaction).where(TelebirrTransaction.driver_id == driver.id).order_by(TelebirrTransaction.timestamp.desc())
    ).all()
    
    # Get all reconciliation records
    reconciliations = db.exec(
        select(ReconciliationRecord).where(ReconciliationRecord.driver_id == driver.id).order_by(ReconciliationRecord.date.desc())
    ).all()
    
    # Calculate KPIs
    total_expected = sum([r.expected_amount for r in reconciliations])
    total_actual = sum([r.actual_amount for r in reconciliations])
    variance = total_expected - total_actual
    compliance = (total_actual / total_expected * 100) if total_expected > 0 else 100
    
    # Get today's expected revenue
    today_expected = db.exec(
        select(ExpectedRevenue).where(ExpectedRevenue.driver_id == driver.id, ExpectedRevenue.date == date.today())
    ).first()
    
    return templates.TemplateResponse(
        request=request,
        name="driver_detail.html",
        context={
            "driver": driver,
            "transactions": transactions,
            "reconciliations": reconciliations,
            "kpis": {
                "total_expected": total_expected,
                "total_actual": total_actual,
                "variance": variance,
                "compliance": compliance,
                "today_expected": today_expected.expected_amount if today_expected else 0.0
            }
        }
    )

# ==========================================
# API ENDPOINTS
# ==========================================

from pydantic import BaseModel

class WebhookPayload(BaseModel):
    transaction_id: str
    amount: float
    sender_identifier: str
    merchant_id: str
    timestamp: datetime
    status: str

@app.post("/api/telebirr/webhook")
async def telebirr_webhook(payload: WebhookPayload, db: Session = Depends(get_session)):
    """Simulates receiving a webhook from Telebirr when a driver deposits."""
    # 1. Store transaction
    tx = TelebirrTransaction(
        transaction_id=payload.transaction_id,
        amount=payload.amount,
        sender_identifier=payload.sender_identifier,
        merchant_id=payload.merchant_id,
        timestamp=payload.timestamp,
        status=payload.status
    )
    
    # 2. Attribution: Try to find driver by operator ID or phone
    driver = db.exec(
        select(Driver).where(
            (Driver.operator_id == payload.sender_identifier) | 
            (Driver.phone == payload.sender_identifier)
        )
    ).first()
    
    if driver:
        tx.driver_id = driver.id
        
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    return {"message": "Transaction recorded and attributed", "transaction": tx}


@app.post("/api/simulator/deposit")
async def simulate_deposit(
    driver_id: int = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_session)
):
    """Called from our simulator UI to trigger the webhook logic."""
    driver = db.get(Driver, driver_id)
    if not driver:
        return {"error": "Driver not found"}
        
    # Create fake webhook payload
    payload = WebhookPayload(
        transaction_id=f"TB-{uuid.uuid4().hex[:8].upper()}",
        amount=amount,
        sender_identifier=driver.operator_id,
        merchant_id="G2G-MERCHANT-001",
        timestamp=datetime.utcnow(),
        status="success"
    )
    
    # Call the webhook function directly for simulation
    await telebirr_webhook(payload, db)
    
    # Redirect back to simulator with success
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/simulator?success=true", status_code=303)

@app.post("/api/sync/yango")
async def sync_yango_data(db: Session = Depends(get_session)):
    """Sync drivers and calculate expected revenue from Yango orders."""
    try:
        # 1. Sync Drivers
        yango_drivers = await yango_client.get_drivers()
        batch_size = 500
        for i in range(0, len(yango_drivers), batch_size):
            batch = yango_drivers[i:i + batch_size]
            for yd in batch:
                profile = yd.get("driver_profile", {})
                y_id = profile.get("id")
                name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Unknown"
                phones = profile.get("phones", [])
                phone = phones[0] if phones else None
                
                # Check if exists
                driver = db.exec(select(Driver).where(Driver.operator_id == y_id)).first()
                if not driver:
                    driver = Driver(operator_id=y_id, name=name, phone=phone)
                    db.add(driver)
                else:
                    driver.name = name
                    driver.phone = phone
            db.commit()

        # 2. Sync Orders for Today to calculate ExpectedRevenue
        today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
        today_end = datetime.combine(date.today(), datetime.max.time()).replace(tzinfo=timezone.utc)
        
        yango_orders = await yango_client.get_all_completed_orders(date_from=today_start, date_to=today_end)
        
        # 3. Cache Orders in DB
        for o in yango_orders:
            o_id = o.get("id")
            profile = o.get("driver_profile", {})
            d_id = profile.get("id")
            
            # Convert Yango timestamp
            ended_at_str = o.get("ended_at", "")
            try:
                # Yango uses 2019-08-08T11:58:01+03:00 format
                ended_at = datetime.fromisoformat(ended_at_str)
            except:
                ended_at = datetime.utcnow()
                
            # Upsert Order
            db_order = db.get(Order, o_id)
            if not db_order:
                db_order = Order(
                    id=o_id,
                    short_id=o.get("short_id", 0),
                    status=o.get("status", ""),
                    price=float(o.get("price", 0)),
                    payment_method=o.get("payment_method", ""),
                    driver_id=d_id,
                    driver_name=profile.get("name", "Unknown"),
                    ended_at=ended_at
                )
                db.add(db_order)
            else:
                db_order.status = o.get("status", "")
                db_order.price = float(o.get("price", 0))

        # Calculate sums per driver for ExpectedRevenue
        revenue_map = {}
        for o in yango_orders:
            d_id = o.get("driver_profile", {}).get("id")
            if not d_id: continue
            
            if o.get("payment_method") != "cash":
                continue
                
            price = float(o.get("price", 0))
            revenue_map[d_id] = revenue_map.get(d_id, 0) + price
            
        # Update ExpectedRevenue table
        for y_id, amount in revenue_map.items():
            driver = db.exec(select(Driver).where(Driver.operator_id == y_id)).first()
            if not driver: continue
            
            exp_rev = db.exec(select(ExpectedRevenue).where(
                ExpectedRevenue.driver_id == driver.id, 
                ExpectedRevenue.date == date.today()
            )).first()
            
            if not exp_rev:
                exp_rev = ExpectedRevenue(driver_id=driver.id, date=date.today(), expected_amount=amount)
                db.add(exp_rev)
            else:
                exp_rev.expected_amount = amount
                
        db.commit()
        return {"message": "Sync completed", "drivers_synced": len(yango_drivers), "orders_processed": len(yango_orders)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/drivers/update-type")
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

@app.post("/api/reconciliation/run")
async def run_reconciliation(target_date: date = None, db: Session = Depends(get_session)):
    """Batch job to reconcile expected vs actual for a given day."""
    if not target_date:
        target_date = date.today()
        
    drivers = db.exec(select(Driver)).all()
    results = []
    
    for d in drivers:
        expected = db.exec(
            select(ExpectedRevenue).where(ExpectedRevenue.driver_id == d.id, ExpectedRevenue.date == target_date)
        ).first()
        
        expected_amt = expected.expected_amount if expected else 0.0
        
        actual_txs = db.exec(
            select(TelebirrTransaction).where(TelebirrTransaction.driver_id == d.id)
        ).all()
        actual_amt = sum([tx.amount for tx in actual_txs if tx.timestamp.date() == target_date])
        
        if expected_amt == 0 and actual_amt == 0:
            continue # No activity to reconcile
            
        if actual_amt == expected_amt:
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
    return {"message": f"Reconciliation ran for {target_date}", "records_processed": len(results)}
