import httpx
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class YangoClient:
    def __init__(self):
        self.base_url = os.getenv("YANGO_BASE_URL", "https://fleet-api.yango.tech")
        self.api_key = os.getenv("YANGO_API_KEY")
        self.client_id = os.getenv("YANGO_CLIENT_ID")
        self.park_id = os.getenv("YANGO_PARK_ID")
        
        self.headers = {
            "X-API-Key": self.api_key,
            "X-Client-ID": self.client_id,
            "Content-Type": "application/json",
            "Accept-Language": "en"
        }

    async def get_drivers(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/parks/driver-profiles/list"
        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                    "driver_profile": {
                        "work_status": ["working"]
                    }
                }
            },
            "limit": 1000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("driver_profiles", [])

    async def get_completed_orders(self, driver_id: Optional[str] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/parks/orders/list"
        
        query_park = {"id": self.park_id}
        order_query = {"statuses": ["complete"]}
        
        if date_from:
            order_query["booked_at"] = {"from": date_from.isoformat(), "to": date_to.isoformat() if date_to else None}
        
        query_park["order"] = order_query
        
        if driver_id:
            query_park["driver_profile"] = {"id": driver_id}
            
        payload = {
            "query": {
                "park": query_park
            },
            "limit": limit,
            "cursor": "" # Some APIs use cursor instead of offset, but the docs show limit/cursor/offset
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
