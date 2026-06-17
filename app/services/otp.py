import random
import string
from datetime import timezone, datetime, timedelta
from typing import Dict

# In-memory database mapping phone numbers to active OTP data
# Format: {phone: {"otp": "123456", "expires_at": datetime}}
active_otps: Dict[str, dict] = {}

def generate_otp() -> str:
    """
    Generate a 6-digit numeric verification code.
    """
    return "".join(random.choices(string.digits, k=6))

def normalize_phone_number(phone: str) -> str:
    """
    Standardizes any of the Ethiopian phone formats into canonical +251XXXXXXXXX
    by extracting the last 9 digits.
    """
    if not phone:
        return ""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 9:
        return phone
    return "+251" + digits[-9:]

def get_phone_variants(phone: str) -> list:
    """
    Generates all potential formats (international with plus, local zero, raw international, raw 9-digit)
    of a phone number to search in the database robustly by extracting the last 9 digits.
    """
    if not phone:
        return []
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 9:
        return [phone]
    last_9 = digits[-9:]
    return [
        "+251" + last_9,
        "0" + last_9,
        "251" + last_9,
        last_9
    ]

def format_phone_number(phone: str, format_type: str) -> str:
    """
    Formats any phone number into one of the four target formats by extracting the last 9 digits:
    1. 'canonical' or 'international_with_plus' -> +251911223344
    2. 'international_no_plus' -> 251911223344
    3. 'local_with_zero' -> 0911223344
    4. 'raw_9_digits' -> 911223344
    """
    if not phone:
        return ""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 9:
        return phone
    last_9 = digits[-9:]
    
    if format_type == "international_no_plus":
        return "251" + last_9
    elif format_type == "local_with_zero":
        return "0" + last_9
    elif format_type == "raw_9_digits":
        return last_9
    else:
        return "+251" + last_9



def store_otp(phone: str, otp: str, expire_minutes: int = 5):
    """
    Store an OTP for a normalized phone number with an expiration window.
    """
    phone_norm = normalize_phone_number(phone)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    active_otps[phone_norm] = {
        "otp": otp,
        "expires_at": expires_at
    }

def verify_otp(phone: str, otp: str) -> bool:
    """
    Verify if the OTP matches the stored value and is not expired (using normalized numbers).
    Clears the OTP state upon successful verification to prevent reuse.
    """
    phone_norm = normalize_phone_number(phone)
    if phone_norm not in active_otps:
        return False
        
    otp_data = active_otps[phone_norm]
    
    # Check match
    if otp_data["otp"] != otp:
        return False
        
    # Check expiration
    if datetime.now(timezone.utc) > otp_data["expires_at"]:
        del active_otps[phone_norm]
        return False
        
    # Success: clear OTP to prevent reuse (one-time use)
    del active_otps[phone_norm]
    return True
