from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select, func
from datetime import datetime
from typing import Optional

from app.models import User, SystemConfig, Notification
from app.services.otp import normalize_phone_number
from app.core.dependencies import get_session, get_current_user

router = APIRouter()

@router.post("/configs/update")
async def update_configs(request: Request, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login", status_code=303)
    
    form = await request.form()
    for key, value in form.items():
        config = db.get(SystemConfig, key)
        if config:
            config.value = str(value)
            config.updated_at = datetime.utcnow()
            db.add(config)
            
    db.commit()
    return RedirectResponse(url="/settings/configs?success=1", status_code=303)

@router.get("/notifications")
async def get_notifications(db: Session = Depends(get_session)):
    """Fetch recent unread notifications."""
    unread_count = db.exec(select(func.count(Notification.id)).where(Notification.is_read == False)).first() or 0
    recent = db.exec(
        select(Notification)
        .order_by(Notification.created_at.desc())
        .limit(5)
    ).all()
    
    return {
        "unread_count": unread_count,
        "notifications": recent
    }

@router.post("/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: int, db: Session = Depends(get_session)):
    notif = db.get(Notification, notif_id)
    if notif:
        notif.is_read = True
        db.add(notif)
        db.commit()
    return {"status": "success"}

@router.post("/notifications/read-all")
async def mark_all_notifications_read(db: Session = Depends(get_session)):
    unread = db.exec(select(Notification).where(Notification.is_read == False)).all()
    for n in unread:
        n.is_read = True
        db.add(n)
    db.commit()
    return {"status": "success"}

@router.patch("/me")
async def update_my_profile(
    full_name: str = Form(...),
    phone: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    two_factor_enabled: bool = Form(False),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401)
        
    user.full_name = full_name
    user.phone = normalize_phone_number(phone) if phone else None
    user.two_factor_enabled = True if user.role == "admin" else two_factor_enabled
    if password:
        user.hashed_password = pwd_context.hash(password)
        
    db.add(user)
    db.commit()
    return {"message": "Profile updated"}
