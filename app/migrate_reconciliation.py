from app.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        print("Starting migration...")
        conn.execute(text('ALTER TABLE drivertrip ADD COLUMN IF NOT EXISTS deposited_amount FLOAT DEFAULT 0.0'))
        conn.execute(text("ALTER TABLE drivertrip ADD COLUMN IF NOT EXISTS reconciliation_status VARCHAR DEFAULT 'Pending'"))
        conn.execute(text('ALTER TABLE drivertrip ADD COLUMN IF NOT EXISTS reconciliation_notes TEXT'))
        conn.commit()
        print("✅ Migration successful: Columns added to drivertrip table.")

if __name__ == "__main__":
    run_migration()
