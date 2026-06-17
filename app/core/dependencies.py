import os
from fastapi import Depends, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlmodel import Session, select
from datetime import timezone, datetime

from app.database import get_session
from app.models import User, AuditLog
from app.services.yango import YangoClient

# Global Clients & Tools
yango_client = YangoClient()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Templates Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ==========================================
# AUTHENTICATION HELPERS
# ==========================================

async def get_current_user(db: Session = Depends(get_session), session_id: str = Cookie(None)):
    if not session_id:
        return None
    user = db.exec(select(User).where(User.email == session_id)).first()
    if user and not user.is_active:
        return None
    return user

def _validate_email_domain(email: str):
    """Enforce company email policy."""
    forbidden = ["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com", "@icloud.com"]
    for domain in forbidden:
        if email.lower().endswith(domain):
            raise HTTPException(status_code=400, detail=f"Registration with {domain} is not allowed. Please use a company email.")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format.")

# ==========================================
# AUDIT LOGGING HELPER
# ==========================================

def _record_audit_log(db: Session, user_id: int, target_type: str, target_id: str, field_name: str, old_value: str, new_value: str):
    """Standardized way to record administrative changes."""
    log = AuditLog(
        target_type=target_type,
        target_id=str(target_id),
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        user_id=user_id,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(log)
