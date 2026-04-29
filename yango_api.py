"""
YANGO Fleet API Client
Save this as yango_api.py
"""

import requests
import uuid
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Enums and Data Classes
# ============================================================================

class OrderStatus(str, Enum):
    DRIVING = "driving"
    WAITING = "waiting"
    TRANSPORTING = "transporting"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TransactionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAIL = "fail"


@dataclass
class Location:
    lat: float
    lon: float
    address: Optional[str] = None


@dataclass
class TrackPoint:
    tracked_at: str
    location: Location
    speed: float
    order_status: str
    direction: int
    distance: float


# ============================================================================
# YANGO API Client
# ============================================================================

class YangoFleetAPI:
    """
    YANGO Fleet API Client
    """
    
    BASE_URL = "https://fleet-api.yango.tech"
    
    def __init__(self, api_key: str, client_id: str, park_id: str):
        self.api_key = api_key
        self.client_id = client_id
        self.park_id = park_id
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "X-Client-ID": self.client_id,
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make API request with error handling"""
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = kwargs.pop("headers", {})
        if "X-Park-ID" not in headers:
            headers["X-Park-ID"] = self.park_id
        kwargs["headers"] = headers
        
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code == 429:
            raise Exception("Rate limit exceeded. Please wait before retrying.")
        
        response.raise_for_status()
        
        return response.json() if response.content else {}
    
    # ========================================================================
    # Orders API
    # ========================================================================
    
    def get_orders_list(self, park_id: str, booked_at_from: Optional[str] = None,
                       booked_at_to: Optional[str] = None, statuses: Optional[List[str]] = None,
                       limit: int = 100, cursor: str = "") -> Dict:
        """Retrieve filtered list of orders"""
        body = {
            "query": {
                "park": {
                    "id": park_id,
                    "order": {}
                }
            },
            "limit": limit,
            "cursor": cursor
        }
        
        if booked_at_from or booked_at_to:
            body["query"]["park"]["order"]["booked_at"] = {}
            if booked_at_from:
                body["query"]["park"]["order"]["booked_at"]["from"] = booked_at_from
            if booked_at_to:
                body["query"]["park"]["order"]["booked_at"]["to"] = booked_at_to
        
        if statuses:
            body["query"]["park"]["order"]["statuses"] = statuses
        
        response = self._request(
            "POST",
            "/v1/parks/orders/list",
            json=body,
            headers={"X-Park-ID": None}
        )
        
        return response
    
    def get_all_orders(self, park_id: str, booked_at_from: str, 
                      booked_at_to: str, statuses: Optional[List[str]] = None,
                      limit: int = 100) -> List[Dict]:
        """Get all orders using pagination"""
        all_orders = []
        cursor = ""
        
        while True:
            response = self.get_orders_list(
                park_id=park_id,
                booked_at_from=booked_at_from,
                booked_at_to=booked_at_to,
                statuses=statuses,
                limit=limit,
                cursor=cursor
            )
            
            all_orders.extend(response.get("orders", []))
            cursor = response.get("cursor", "")
            
            if not cursor:
                break
        
        return all_orders
    
    def get_order_track(self, order_id: str, park_id: str) -> List[TrackPoint]:
        """Retrieve GPS track for an order"""
        response = self._request(
            "POST",
            f"/v1/parks/orders/track?order_id={order_id}&park_id={park_id}",
            headers={"X-Park-ID": None}
        )
        
        track_points = []
        for point in response.get("track", []):
            track_points.append(TrackPoint(
                tracked_at=point["tracked_at"],
                location=Location(
                    lat=point["location"]["lat"],
                    lon=point["location"]["lon"]
                ),
                speed=point["speed"],
                order_status=point["order_status"],
                direction=point.get("direction", 0),
                distance=point["distance"]
            ))
        
        return track_points
    
    # ========================================================================
    # Driver/Courier API
    # ========================================================================
    
    def get_driver_profiles_list(self, park_id: str, statuses: Optional[List[str]] = None,
                                 limit: int = 100, offset: int = 0) -> Dict:
        """Retrieve filtered list of driver profiles"""
        body = {
            "query": {
                "park": {
                    "id": park_id
                }
            },
            "limit": limit,
            "offset": offset
        }
        
        if statuses:
            body["query"]["park"]["driver_profile"] = {"statuses": statuses}
        
        response = self._request("POST", "/v1/parks/driver-profiles/list", json=body)
        return response
    
    def get_all_driver_profiles(self, park_id: str, statuses: Optional[List[str]] = None,
                               limit: int = 100) -> List[Dict]:
        """Get all driver profiles using pagination"""
        all_couriers = []
        offset = 0
        
        while True:
            response = self.get_driver_profiles_list(
                park_id=park_id,
                statuses=statuses,
                limit=limit,
                offset=offset
            )
            
            all_couriers.extend(response.get("driver_profiles", []))
            
            if offset + limit >= response.get("total", 0):
                break
            
            offset += limit
        
        return all_couriers
    
    def get_driver_profile(self, contractor_profile_id: str) -> Dict:
        """Get single driver profile details"""
        response = self._request(
            "GET",
            f"/v2/parks/contractors/driver-profile?contractor_profile_id={contractor_profile_id}"
        )
        return response
    
    def get_blocked_balance(self, contractor_id: str) -> Dict:
        """Get blocked balance breakdown for a courier"""
        response = self._request(
            "GET",
            f"/v1/parks/contractors/blocked-balance?contractor_id={contractor_id}"
        )
        return response
    
    def get_available_for_payout(self, contractor_id: str) -> Dict:
        """Calculate available balance for payout"""
        blocked = self.get_blocked_balance(contractor_id)
        profile = self.get_driver_profile(contractor_id)
        
        total_balance = float(blocked.get("balance", 0))
        blocked_balance = float(blocked.get("blocked_balance", 0))
        available = total_balance - blocked_balance
        
        return {
            "total_balance": blocked.get("balance", "0"),
            "blocked": blocked.get("blocked_balance", "0"),
            "available": str(available),
            "breakdown": blocked.get("details", {})
        }
    
    # ========================================================================
    # Transactions API
    # ========================================================================
    
    def get_transaction_categories(self, park_id: str) -> List[Dict]:
        """Get available transaction categories"""
        response = self._request(
            "POST",
            "/v2/parks/transactions/categories/list",
            json={"park_id": park_id}
        )
        return response.get("categories", [])
    
    def get_driver_transactions(self, park_id: str, driver_profile_id: str,
                               event_at_from: str, event_at_to: str,
                               category_ids: Optional[List[str]] = None,
                               limit: int = 100, cursor: str = "") -> Dict:
        """Get transaction history for a specific driver"""
        body = {
            "query": {
                "park": {
                    "id": park_id,
                    "driver_profile": {
                        "id": driver_profile_id
                    },
                    "transaction": {
                        "event_at": {
                            "from": event_at_from,
                            "to": event_at_to
                        }
                    }
                }
            },
            "limit": limit,
            "cursor": cursor
        }
        
        if category_ids:
            body["query"]["park"]["transaction"]["category_ids"] = category_ids
        
        response = self._request(
            "POST",
            "/v2/parks/driver-profiles/transactions/list",
            json=body
        )
        return response
    
    def get_all_driver_transactions(self, park_id: str, driver_profile_id: str,
                                   event_at_from: str, event_at_to: str,
                                   category_ids: Optional[List[str]] = None,
                                   limit: int = 100) -> List[Dict]:
        """Get all driver transactions using pagination"""
        all_transactions = []
        cursor = ""
        
        while True:
            response = self.get_driver_transactions(
                park_id=park_id,
                driver_profile_id=driver_profile_id,
                event_at_from=event_at_from,
                event_at_to=event_at_to,
                category_ids=category_ids,
                limit=limit,
                cursor=cursor
            )
            
            all_transactions.extend(response.get("transactions", []))
            cursor = response.get("cursor", "")
            
            if not cursor:
                break
        
        return all_transactions