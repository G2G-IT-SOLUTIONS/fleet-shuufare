from fastapi import APIRouter, Request, Form, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, or_
from datetime import datetime
from pydantic import BaseModel

from app.core.dependencies import get_session, pwd_context, templates
from app.models import User
from app.services.sms import send_sms
from app.services.otp import generate_otp, store_otp, verify_otp, normalize_phone_number, get_phone_variants

class SendOTPPayload(BaseModel):
    phone: str

class VerifyOTPPayload(BaseModel):
    phone: str
    otp: str

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
async def login_submit(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session)
):
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)
    
    if not user.is_active:
        return RedirectResponse(url="/login?error=Account deactivated", status_code=303)
        
    is_2fa_required = user.two_factor_enabled
    if is_2fa_required:
        if not user.phone:
            return RedirectResponse(url="/login?error=2FA is required for your account, but no phone number is registered. Please contact an administrator.", status_code=303)
            
        # Generate and store OTP
        otp = generate_otp()
        store_otp(user.phone, otp)
        
        try:
            await send_sms(user.phone, f"Your verification code is {otp}. Do not share this OTP.")
        except Exception as sms_err:
            print(f"Failed to send 2FA SMS: {sms_err}")
            
        # Redirect to /login-2fa with temp cookie
        response = RedirectResponse(url="/login-2fa", status_code=303)
        response.set_cookie(key="2fa_pending_email", value=user.email, httponly=True, path="/", max_age=300) # 5 minutes
        return response

    # Update last login
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    # Set simple cookie session
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_id", value=user.email, httponly=True, path="/")
    return response

@router.get("/login-2fa", response_class=HTMLResponse)
async def login_2fa_page(request: Request, db: Session = Depends(get_session)):
    pending_email = request.cookies.get("2fa_pending_email")
    if not pending_email:
        return RedirectResponse(url="/login?error=Session expired. Please sign in again.", status_code=303)
    
    user = db.exec(select(User).where(User.email == pending_email)).first()
    if not user or not user.phone:
        return RedirectResponse(url="/login?error=No phone number registered for this account.", status_code=303)
        
    error = request.query_params.get("error", "")
    return templates.TemplateResponse(
        request=request,
        name="login_2fa.html",
        context={"phone": user.phone, "error": error}
    )

@router.post("/login-2fa")
async def login_2fa_submit(
    request: Request,
    response: Response,
    otp: str = Form(...),
    db: Session = Depends(get_session)
):
    pending_email = request.cookies.get("2fa_pending_email")
    if not pending_email:
        return RedirectResponse(url="/login?error=Session expired. Please sign in again.", status_code=303)
        
    user = db.exec(select(User).where(User.email == pending_email)).first()
    if not user or not user.is_active:
        return RedirectResponse(url="/login?error=Account inactive or not found.", status_code=303)
        
    if not user.phone:
        return RedirectResponse(url="/login?error=No phone number registered.", status_code=303)
        
    if not verify_otp(user.phone, otp):
        return RedirectResponse(url="/login-2fa?error=Invalid or expired verification code.", status_code=303)
        
    # OTP verified! Establish full session
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_id", value=user.email, httponly=True, path="/")
    response.delete_cookie(key="2fa_pending_email", path="/")
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_id", path="/")
    return response

@router.post("/send-otp")
async def send_otp_endpoint(
    payload: SendOTPPayload,
    db: Session = Depends(get_session)
):
    phone = payload.phone.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required.")
        
    # Look up user by phone number variants robustly
    variants = get_phone_variants(phone)
    user = db.exec(select(User).where(or_(*(User.phone == v for v in variants)))).first()
    if not user:
        raise HTTPException(status_code=404, detail="Phone number is not registered with any user account.")
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated.")
        
    otp = generate_otp()
    store_otp(user.phone, otp)
    
    try:
        # Send SMS via PlaySMS
        await send_sms(phone, f"Your verification code is {otp}. Do not share this OTP.")
        return {
            "success": True,
            "otp": otp,  # kept for testing/dev just like express code
            "message": "Verification code sent successfully."
        }
    except Exception as sms_err:
        # Fallback if SMS service fails but return OTP for testing purposes
        return {
            "success": True,
            "otp": otp,
            "message": f"Verification code generated (SMS gateway error: {sms_err})"
        }

@router.post("/verify-otp")
async def verify_otp_endpoint(
    response: Response,
    payload: VerifyOTPPayload,
    db: Session = Depends(get_session)
):
    phone = payload.phone.strip()
    otp = payload.otp.strip()
    
    if not phone or not otp:
        raise HTTPException(status_code=400, detail="Phone number and verification code are required.")
        
    # Verify OTP
    if not verify_otp(phone, otp):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")
        
    # Retrieve user robustly by phone number variants
    variants = get_phone_variants(phone)
    user = db.exec(select(User).where(or_(*(User.phone == v for v in variants)))).first()
    if not user or not user.is_active:
         raise HTTPException(status_code=404, detail="User account not found or deactivated.")
         
    # Update last login
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    # Set session cookie to user email
    response.set_cookie(key="session_id", value=user.email, httponly=True, path="/")
    return {"success": True, "message": "Logged in successfully."}

