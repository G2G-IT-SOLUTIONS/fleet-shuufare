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

    async def _post_with_retry(self, client, url, payload, max_retries=7):
        for i in range(max_retries):
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
                if i == max_retries - 1:
                    raise
                import asyncio
                await asyncio.sleep(2 ** i)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429: # Too Many Requests
                    if i == max_retries - 1:
                        raise
                    
                    # Check for Retry-After header
                    retry_after = e.response.headers.get("Retry-After")
                    import asyncio
                    if retry_after and retry_after.isdigit():
                        sleep_time = int(retry_after) + 1
                    else:
                        # Fallback to aggressive exponential backoff for 429s
                        sleep_time = (2 ** (i + 2)) + 1 
                    
                    await asyncio.sleep(sleep_time)
                else:
                    # For other HTTP errors like 400, 401, 404, fail immediately
                    raise
        return None

    # Minimal field set — only what we need. Keeps pages small and fast.
    _DRIVER_FIELDS = {
        "car": [],
        "park": [],
        "current_status": [],
        "account": [],
        "driver_profile": ["id", "first_name", "last_name", "phones", "work_status"]
    }

    # Full field set for profile card
    _FULL_DRIVER_FIELDS = {
        "car": ["id", "brand", "model", "number", "color", "year", "callsign"],
        "park": ["id", "name"],
        "current_status": ["status", "status_updated_at"],
        "account": ["balance", "currency"],
        "driver_profile": [
            "id", "first_name", "last_name", "middle_name", 
            "phones", "work_status", "created_date", 
            "work_rule_id", "provider_config_id"
        ]
    }

    async def get_driver_profile_v2(self, yango_driver_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed contractor profile from Yango v2 endpoint."""
        url = f"{self.base_url}/v2/parks/contractors/driver-profile"
        params = {"contractor_profile_id": yango_driver_id}
        headers = {
            "X-API-Key": self.api_key,
            "X-Client-ID": self.client_id,
            "X-Park-ID": self.park_id
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"V2 Profile Error: {e}")
            return None

    async def get_driver_profile(self, yango_driver_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single driver's full profile from Yango."""
        url = f"{self.base_url}/v1/parks/driver-profiles/list"
        
        # Strategy 1: Exact ID filter
        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                    "driver_profile": {"id": [yango_driver_id]}
                }
            },
            "fields": self._FULL_DRIVER_FIELDS
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await self._post_with_retry(client, url, payload)
                if response:
                    data = response.json()
                    profiles = data.get("driver_profiles", [])
                    if profiles:
                        return profiles[0]
                
                # Strategy 2: Text search fallback (sometimes ID filter is finicky)
                payload_search = {
                    "query": {"park": {"id": self.park_id}},
                    "text": yango_driver_id,
                    "fields": self._FULL_DRIVER_FIELDS
                }
                response = await self._post_with_retry(client, url, payload_search)
                if response:
                    data = response.json()
                    profiles = data.get("driver_profiles", [])
                    # Verify it's the right one
                    for p in profiles:
                        if p.get("driver_profile", {}).get("id") == yango_driver_id:
                            return p
            except Exception as e:
                print(f"Error in get_driver_profile v1: {e}")
                    
        return None

    async def get_car_profile(self, car_id: str) -> Optional[Dict[str, Any]]:
        """Fetch car details from Yango."""
        url = f"{self.base_url}/v1/parks/cars/list"
        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                    "car": {"id": [car_id]}
                }
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await self._post_with_retry(client, url, payload)
                if response:
                    data = response.json()
                    cars = data.get("cars", [])
                    return cars[0] if cars else None
            except Exception as e:
                print(f"Error fetching car {car_id}: {e}")
        return None

    async def get_driver_balance(self, yango_driver_id: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time balance for a driver using the dedicated balances endpoint."""
        url = f"{self.base_url}/v1/parks/driver-profiles/balances/list"
        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                    "driver_profile": {"ids": [yango_driver_id]}
                }
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await self._post_with_retry(client, url, payload)
                if response:
                    data = response.json()
                    balances = data.get("balances", [])
                    return balances[0] if balances else None
            except Exception as e:
                print(f"Error fetching balance for {yango_driver_id}: {e}")
        return None

    async def search_drivers(self, text: str) -> List[Dict[str, Any]]:
        """
        Use Yango's native full-text search to find drivers
        by name, phone, or operator ID.
        """
        url = f"{self.base_url}/v1/parks/driver-profiles/list"
        
        clean_text = text.strip()
        query_park = {"id": self.park_id}
        
        # Check if it's an exact 32-character hex ID
        id_candidate = clean_text.replace("-", "")
        if len(id_candidate) == 32 and all(c in "0123456789abcdefABCDEF" for c in id_candidate):
            query_park["driver_profile"] = {"id": [id_candidate]}

        payload = {
            "query": {
                "park": query_park,
                "text": clean_text
            },
            "fields": self._DRIVER_FIELDS,
            "limit": 50,
            "offset": 0
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await self._post_with_retry(client, url, payload)
                if response:
                    data = response.json()
                    return data.get("driver_profiles", [])
            except Exception as e:
                print(f"Search Drivers Error: {e}")
            return []

    async def get_drivers(self, updated_since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Full paginated sync of ALL drivers (working + not_working + fired).
        If updated_since is provided, performs a fast Delta Sync using updated_at.
        """
        url = f"{self.base_url}/v1/parks/driver-profiles/list"
        all_drivers: List[Dict[str, Any]] = []
        offset = 0
        limit = 1000  # API max

        async with httpx.AsyncClient(timeout=90.0) as client:
            while True:
                query_park: Dict[str, Any] = {
                    "id": self.park_id
                }
                
                if updated_since:
                    query_park["updated_at"] = {
                        "from": updated_since.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    
                payload = {
                    "query": {
                        "park": query_park
                    },
                    "fields": self._DRIVER_FIELDS,
                    "sort_order": [{"field": "driver_profile.created_date", "direction": "asc"}],
                    "limit": limit,
                    "offset": offset
                }

                response = await self._post_with_retry(client, url, payload)
                data = response.json()
                drivers = data.get("driver_profiles", [])

                if not drivers:
                    break

                all_drivers.extend(drivers)

                # If we got fewer than the limit, we've hit the last page
                if len(drivers) < limit:
                    break

                offset += limit
                
                # Throttle to respect API rate limits (57 requests for 57k drivers)
                import asyncio
                await asyncio.sleep(1.5)

        return all_drivers

    async def get_drivers_paginated(self, offset: int = 0, limit: int = 1000, cursor_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Single-page driver fetch — used internally for streaming sync.
        Uses updated_at filtering as a cursor to bypass Yango's 10,000 offset limit.
        """
        url = f"{self.base_url}/v1/parks/driver-profiles/list"
        query_park = {"id": self.park_id}
        
        if cursor_date:
            query_park["updated_at"] = {"from": cursor_date}
            
        payload = {
            "query": {
                "park": query_park
            },
            "fields": self._DRIVER_FIELDS,
            "sort_order": [{"field": "updated_at", "direction": "asc"}],
            "limit": limit,
            "offset": offset
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await self._post_with_retry(client, url, payload)
            return response.json()

    async def get_all_completed_orders(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, driver_profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
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
                if driver_profile_id:
                    query_park["driver_profile"] = {"id": driver_profile_id}
                
                payload = {
                    "query": {"park": query_park},
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
                    
                # Throttle to respect API rate limits
                import asyncio
                await asyncio.sleep(1.5)
                    
        return all_orders

    async def get_order_transactions(self, order_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch financial transactions for a list of order IDs.
        Chunks the requests into batches of 100 to respect Yango's API limits.
        """
        if not order_ids:
            return []
            
        url = f"{self.base_url}/v2/parks/orders/transactions/list"
        all_transactions = []
        
        # Split order_ids into chunks of 100 (Yango API max limit)
        batch_size = 100
        for i in range(0, len(order_ids), batch_size):
            chunk = order_ids[i:i + batch_size]
            payload = {
                "query": {
                    "park": {
                        "id": self.park_id,
                        "order": {
                            "ids": chunk
                        }
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    response = await self._post_with_retry(client, url, payload)
                    data = response.json()
                    transactions = data.get("transactions", [])
                    all_transactions.extend(transactions)
                except Exception as e:
                    print(f"Error fetching transactions for batch: {e}")
            
            # Short sleep to prevent rate limiting
            import asyncio
            await asyncio.sleep(0.5)
            
        return all_transactions

    async def get_orders_page(
        self, 
        cursor: str = None, 
        limit: int = 100, 
        date_from=None, 
        date_to=None,
        driver_profile_id: str = None,
        order_ids: List[str] = None,
        short_ids: List[int] = None
    ):
        """
        Fetch a SINGLE page of completed orders (one API call — fast).
        Supports deep scanning by specific IDs.
        Returns (orders_list, next_cursor).
        """
        url = f"{self.base_url}/v1/parks/orders/list"
        query_park = {"id": self.park_id}
        order_query = {"statuses": ["complete"]}
        
        if date_from:
            order_query["booked_at"] = {
                "from": date_from.isoformat(),
                "to": date_to.isoformat() if date_to else None
            }
            
        if order_ids:
            order_query["ids"] = order_ids
            
        if short_ids:
            order_query["short_ids"] = short_ids
            
        query_park["order"] = order_query
        
        if driver_profile_id:
            query_park["driver_profile"] = {"id": driver_profile_id}
            
        payload = {"query": {"park": query_park}, "limit": limit}
        if cursor:
            payload["cursor"] = cursor
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await self._post_with_retry(client, url, payload)
                if not response:
                    return [], None
                data = response.json()
                return data.get("orders", []), data.get("cursor")
            except Exception as e:
                print(f"Error fetching orders page: {e}")
                return [], None

    async def get_driver_profile(self, yango_driver_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full driver profile from Yango v2 API."""
        url = f"{self.base_url}/v2/parks/contractors/driver-profile"
        params = {"contractor_profile_id": yango_driver_id}
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception:
                return None

    async def get_driver_orders(self, yango_driver_id: str, days_back: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent orders for a specific driver by their Yango yango_driver_id."""
        url = f"{self.base_url}/v1/parks/orders/list"
        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc)
        date_from = now - timedelta(days=days_back)

        payload = {
            "query": {
                "park": {
                    "id": self.park_id,
                    "order": {
                        "booked_at": {
                            "from": date_from.isoformat(),
                            "to": now.isoformat()
                        }
                    },
                    "driver_profile": {"id": yango_driver_id}
                }
            },
            "limit": limit
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await self._post_with_retry(client, url, payload)
                data = response.json()
                return data.get("orders", [])
            except Exception:
                return []

    async def get_all_driver_orders(self, yango_driver_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Fetch ALL orders for a specific driver using cursor pagination."""
        url = f"{self.base_url}/v1/parks/orders/list"
        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc)
        date_from = now - timedelta(days=days_back)
        
        all_orders = []
        cursor = None
        limit = 500

        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                payload = {
                    "query": {
                        "park": {
                            "id": self.park_id,
                            "order": {
                                "statuses": ["complete"],
                                "booked_at": {
                                    "from": date_from.isoformat(),
                                    "to": now.isoformat()
                                }
                            },
                            "driver_profile": {"id": yango_driver_id}
                        }
                    },
                    "limit": limit
                }
                if cursor:
                    payload["cursor"] = cursor
                    
                try:
                    response = await self._post_with_retry(client, url, payload)
                    if not response:
                        break
                    data = response.json()
                    orders = data.get("orders", [])
                    if not orders:
                        break
                        
                    all_orders.extend(orders)
                    
                    cursor = data.get("cursor")
                    if not cursor:
                        break
                        
                    import asyncio
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"Error fetching all orders for {yango_driver_id}: {e}")
                    break
                    
        return all_orders

    async def get_order_track(self, order_id: str) -> List[Dict[str, Any]]:
        """Fetch GPS telemetry track for a specific order."""
        url = f"{self.base_url}/v1/parks/orders/track"
        params = {"order_id": order_id, "park_id": self.park_id}
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json().get("track", [])
                return []
            except Exception:
                return []

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
            "query": {"park": query_park},
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
