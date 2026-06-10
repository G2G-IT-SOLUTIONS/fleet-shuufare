from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user, yango_client
from app.models import User

router = APIRouter()

@router.get("/search-drivers")
async def yango_live_search(q: str = "", user: User = Depends(get_current_user)):
    """Live full-text search against Yango API — bypasses local DB entirely."""
    if not user:
        raise HTTPException(status_code=401)
    if len(q.strip()) < 2:
        return []
    try:
        profiles = await yango_client.search_drivers(text=q.strip())
        results = []
        for yd in profiles:
            profile = yd.get("driver_profile", {})
            phones = profile.get("phones", [])
            results.append({
                "yango_driver_id": profile.get("id"),
                "name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Unknown",
                "phone": phones[0] if phones else None,
                "work_status": profile.get("work_status"),
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drivers/{yango_driver_id}")
async def get_yango_driver_live(yango_driver_id: str, user: User = Depends(get_current_user)):
    """Fetch live data (v1 + v2 + balance) for a specific driver from Yango API."""
    if not user:
        raise HTTPException(status_code=401)
        
    v1_profile = await yango_client.get_driver_profile(yango_driver_id)
    v2_profile = await yango_client.get_driver_profile_v2(yango_driver_id)
    live_balance = await yango_client.get_driver_balance(yango_driver_id)
    
    if not v1_profile and not v2_profile:
        raise HTTPException(status_code=404, detail="Driver not found in Yango")
        
    if v2_profile and v2_profile.get("car_id"):
        if not v1_profile or not v1_profile.get("car") or not v1_profile.get("car", {}).get("brand"):
            car_details = await yango_client.get_car_profile(v2_profile["car_id"])
            if car_details:
                if not v1_profile: v1_profile = {}
                v1_profile["car"] = car_details

    if live_balance:
        if not v1_profile: v1_profile = {}
        if "account" not in v1_profile: v1_profile["account"] = {}
        bal = live_balance.get("total_balance") or live_balance.get("balance")
        if bal is not None:
            v1_profile["account"]["balance"] = bal
            v1_profile["account"]["currency"] = live_balance.get("currency") or "ETB"

    return {
        "v1": v1_profile or {},
        "v2": v2_profile or {}
    }
