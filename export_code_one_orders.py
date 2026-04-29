import asyncio
import csv
import re
from datetime import datetime
from app.services.yango_client import YangoFleetAsyncClient

# Replicate normalization and Code 1 logic
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

async def main():
    print("Initializing Yango Fleet API Client...")
    yango = YangoFleetAsyncClient()
    
    # Start Date: April 1, 2026
    start_date = "2026-04-01T00:00:00+03:00"
    end_date = datetime.now().strftime("%Y-%m-%dT23:59:59+03:00")
    
    print(f"Fetching completed orders from {start_date} to {end_date}...")
    
    cursor = None
    all_code_one_completed = []
    pages = 0
    total_fetched = 0
    
    while True:
        response = await yango.get_orders(
            booked_at_from=start_date,
            booked_at_to=end_date,
            statuses=["complete"],
            limit=500,  # Max limit
            cursor=cursor
        )
        
        if "error" in response:
            print(f"API Error: {response}")
            break
            
        orders = response.get("orders", [])
        if not orders:
            break
            
        total_fetched += len(orders)
        
        # Filter Code 1
        for o in orders:
            plate = (o.get("car", {}) or {}).get("license", {}).get("number")
            if plate and is_code_one(plate):
                all_code_one_completed.append(o)
                
        cursor = response.get("cursor")
        pages += 1
        print(f"Scanned {pages} pages ({total_fetched} orders processed)... Found {len(all_code_one_completed)} Code 1 matches.")
        
        if not cursor:
            break
            
    print(f"\nScan complete. Writing {len(all_code_one_completed)} records to CSV...")
    
    filename = "code_one_completed_april_to_now.csv"
    
    if not all_code_one_completed:
        print("No records found. Exiting.")
        return

    # Prepare CSV headers
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
            
            writer.writerow([
                order_id, date, driver_id, driver_name, license_plate,
                category, price, address_from
            ])
            
    print(f"Successfully saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())
