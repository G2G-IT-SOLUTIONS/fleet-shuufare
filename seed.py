from datetime import date
from sqlmodel import Session
from app.database import create_db_and_tables, engine
from app.models import Driver, ExpectedRevenue

def seed_db():
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check if already seeded
        if session.query(Driver).first():
            print("Database already seeded.")
            return

        print("Seeding drivers...")
        drivers = [
            Driver(yango_driver_id="OP-001", name="Abebe Bikila", phone="+251911000001"),
            Driver(yango_driver_id="OP-002", name="Kenenisa Bekele", phone="+251911000002"),
            Driver(yango_driver_id="OP-003", name="Tirunesh Dibaba", phone="+251911000003"),
            Driver(yango_driver_id="OP-004", name="Haile Gebrselassie", phone="+251911000004"),
        ]
        
        session.add_all(drivers)
        session.commit()
        
        for d in drivers:
            session.refresh(d)
            
        print("Seeding expected revenues for today...")
        today = date.today()
        
        revenues = [
            ExpectedRevenue(driver_id=drivers[0].id, date=today, expected_amount=1500.0),
            ExpectedRevenue(driver_id=drivers[1].id, date=today, expected_amount=2000.0),
            ExpectedRevenue(driver_id=drivers[2].id, date=today, expected_amount=1200.0),
            ExpectedRevenue(driver_id=drivers[3].id, date=today, expected_amount=3000.0),
        ]
        
        session.add_all(revenues)
        session.commit()
        
        print("Seeding complete.")

if __name__ == "__main__":
    seed_db()
