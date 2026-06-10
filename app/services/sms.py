import httpx
import os
from sqlmodel import Session

from app.database import engine
from app.models import SystemConfig
from app.services.otp import format_phone_number

async def send_sms(phone: str, message: str) -> str:
    """
    Sends an SMS message to a phone number using the configured playSMS gateway.
    Queries the database for SMS_GATEWAY_PHONE_FORMAT and formats the outgoing phone number dynamically.
    """
    url = os.getenv("PLAYSMS_URL")
    user = os.getenv("PLAYSMS_USER")
    token = os.getenv("PLAYSMS_TOKEN")
    
    if not url or not user or not token:
        print("[SMS Service] PlaySMS configuration missing from environment variables.")
        return "CONFIG_ERROR"
        
    # Query database for the expected phone number format
    format_type = "canonical"
    try:
        with Session(engine) as db:
            config = db.get(SystemConfig, "SMS_GATEWAY_PHONE_FORMAT")
            if config:
                format_type = config.value
    except Exception as db_err:
        print(f"[SMS Service] Error reading SMS_GATEWAY_PHONE_FORMAT from DB (falling back to canonical): {db_err}")
        
    formatted_phone = format_phone_number(phone, format_type)
    print(f"[SMS Service] Formatted phone number from '{phone}' to '{formatted_phone}' using format type '{format_type}'")
        
    params = {
        "app": "ws",
        "op": "pv",
        "u": user,
        "h": token,
        "to": formatted_phone,
        "msg": message,
        "nofooter": "1"
    }
    
    try:
        # verify=False behaves like rejectUnauthorized=False in Node's HTTPS agent
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            print(f"[SMS Service] SMS successfully sent to {formatted_phone}: {response.text}")
            return response.text
    except Exception as e:
        print(f"[SMS Service] Error sending SMS to {formatted_phone}: {e}")
        raise e

