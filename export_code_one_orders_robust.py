import asyncio
import csv
import re
from datetime import datetime
import httpx

# We will hit the API directly to implement infinite backoff for bulk export
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YANGO_API_KEY")
CLIENT_ID = os.getenv("YANGO_CLIENT_ID")
PARK_ID = os.getenv("YANGO_PARK_ID")
BASE_URL = "https://fleet-api.yango.tech"

homoglyph_map = {
    'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'Н': 'H', 'К': 'K', 
    'М': 'M', 'О': 'O', 'Р': 'P', 'Т': 'T', 'Х': 'X', 'У': 'Y'
}

def normalize_plate(p: str):
    if not p: return ""
    clean = re.sub(r'[^A-Z0-9\u0400-\u04FF]', '', p.upper())
    return "".join(homoglyph_map.get(c, c) for c in clean)

def is_code_one(plate: str):
    norm = normalize_plate(plate)
    if not norm: return False
    match = re.search(r'(\d)[A-Z]', norm)
    return bool(match and match.group(1) == '1')

async def fetch_page(client, cursor, start_date, end_date):
    url = f"{BASE_URL}/v1/parks/orders/list"
    headers = {
        "X-API-Key": API_KEY,
        "X-Client-ID": CLIENT_ID,
        "X-Park-ID": PARK_ID,
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": {
            "park": {
                "id": PARK_ID,
                "order": {
                    "booked_at": {
                        "from": start_date,
                        "to": end_date
                    },
                    "statuses": ["complete"]
                }
            }
        },
        "limit": 500
    }
    if cursor:
        payload["cursor"] = cursor

    while True:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            if response.status_code == 429:
                print("Rate limited. Sleeping for 10 seconds...")
                await asyncio.sleep(10)
                continue
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Request failed ({e}). Sleeping 10s and retrying...")
            await asyncio.sleep(10)

async def main():
    print("Starting robust Yango Export for Code 1...")
    
    start_date = "2026-04-01T00:00:00+03:00"
    end_date = datetime.now().strftime("%Y-%m-%dT23:59:59+03:00")
    
    cursor = None
    all_code_one_completed = []
    pages = 0
    total_fetched = 0
    
    async with httpx.AsyncClient() as client:
        while True:
            data = await fetch_page(client, cursor, start_date, end_date)
            
            orders = data.get("orders", [])
            if not orders:
                break
                
            total_fetched += len(orders)
            
            # Filter Code 1
            for o in orders:
                plate = (o.get("car", {}) or {}).get("license", {}).get("number")
                if plate and is_code_one(plate):
                    all_code_one_completed.append(o)
                    
            cursor = data.get("cursor")
            pages += 1
            print(f"Scanned {pages} pages ({total_fetched} orders processed)... Found {len(all_code_one_completed)} Code 1 matches.")
            
            if not cursor:
                break
                
            # Nice and easy on the API
            await asyncio.sleep(1)
            
    filename = "code_one_completed_april_to_now.csv"
    
    headers = [
        "Order ID", "Date", "Driver ID", "Driver Name", "Plate", 
        "Category", "Price", "Address"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for o in all_code_one_completed:
            order_id = o.get("id", "")
            date = o.get("ended_at", "")
            driver_profile = o.get("driver_profile", {}) or {}
            driver_id = driver_profile.get("id", "")
            driver_name = driver_profile.get("name", "")
            car = o.get("car", {}) or {}
            license_plate = (car.get("license", {}) or {}).get("number", "")
            category = o.get("category", "")
            price = str(o.get("price", "0"))
            address_from = (o.get("address_from", {}) or {}).get("address", "")
            
            writer.writerow([order_id, date, driver_id, driver_name, license_plate, category, price, address_from])
            
    print(f"Successfully saved all {len(all_code_one_completed)} records to {filename}")

if __name__ == "__main__":
    asyncio.run(main())
