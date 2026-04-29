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

    async def _post_with_retry(self, client, url, payload, max_retries=3):
        for i in range(max_retries):
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
                if i == max_retries - 1:
                    raise
                import asyncio
                await asyncio.sleep(2 ** i) # Exponential backoff
        return None

    async def get_drivers(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/parks/driver-profiles/list"
        all_drivers = []
        offset = 0
        limit = 1000
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                payload = {
                    "query": {
                        "park": {
                            "id": self.park_id,
                            "driver_profile": {
                                "work_status": ["working"]
                            }
                        }
                    },
                    "limit": limit,
                    "offset": offset
                }
                
                response = await self._post_with_retry(client, url, payload)
                data = response.json()
                drivers = data.get("driver_profiles", [])
                
                if not drivers:
                    break
                    
                all_drivers.extend(drivers)
                if len(drivers) < limit:
                    break
                    
                offset += limit
                
        return all_drivers

    async def get_all_completed_orders(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/parks/orders/list"
        all_orders = []
        cursor = None
        limit = 500
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                query_park = {"id": self.park_id}
                order_query = {"statuses": ["complete"]}
                
                if date_from:
                    order_query["booked_at"] = {"from": date_from.isoformat(), "to": date_to.isoformat() if date_to else None}
                
                query_park["order"] = order_query
                
                payload = {
                    "query": {
                        "park": query_park
                    },
                    "limit": limit
                }
                if cursor:
                    payload["cursor"] = cursor
                
                response = await self._post_with_retry(client, url, payload)
                data = response.json()
                orders = data.get("orders", [])
                
                if not orders:
                    break
                    
                all_orders.extend(orders)
                
                # Check for next cursor
                cursor = data.get("cursor")
                if not cursor:
                    break
                    
        return all_orders

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
