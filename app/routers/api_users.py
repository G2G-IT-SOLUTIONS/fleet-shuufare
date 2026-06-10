from fastapi import APIRouter, Form, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional

from app.core.dependencies import get_session, get_current_user, pwd_context, _validate_email_domain
from app.models import User
from app.services.otp import normalize_phone_number

router = APIRouter()

@router.post("/")
async def create_user(
    email: str = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    password: str = Form(...),
    phone: Optional[str] = Form(None),
    two_factor_enabled: bool = Form(False),
    db: Session = Depends(get_session),
    admin: User = Depends(get_current_user)
):
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403)
        
    _validate_email_domain(email)
    
    existing = db.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(
        email=email,
        full_name=full_name,
        role=role,
        phone=normalize_phone_number(phone) if phone else None,
        two_factor_enabled=True if role == "admin" else two_factor_enabled,
        hashed_password=pwd_context.hash(password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@router.patch("/{user_id}")
async def update_user_status(
    user_id: int,
    is_active: bool = Form(...),
    role: str = Form(...),
    phone: Optional[str] = Form(None),
    two_factor_enabled: bool = Form(False),
    db: Session = Depends(get_session),
    admin: User = Depends(get_current_user)
):
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403)
    
    target_user = db.get(User, user_id)
    if not target_user:
        raise HTTPException(status_code=404)
        
    target_user.is_active = is_active
    target_user.role = role
    target_user.phone = normalize_phone_number(phone) if phone else None
    target_user.two_factor_enabled = True if role == "admin" else two_factor_enabled
    db.add(target_user)
    db.commit()
    return {"message": "User updated"}

@router.patch("/me/profile")
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
