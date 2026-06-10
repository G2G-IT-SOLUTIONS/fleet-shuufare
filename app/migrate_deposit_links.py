import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db" # Default fallback
if "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.begin() as conn:
        print("Starting migration...")
        
        # 1. Add is_reconciled to TelebirrTransaction
        try:
            conn.execute(text("ALTER TABLE telebirrtransaction ADD COLUMN is_reconciled BOOLEAN DEFAULT FALSE;"))
            print("Added is_reconciled to telebirrtransaction.")
        except Exception as e:
            print(f"telebirrtransaction.is_reconciled might already exist: {e}")

        # 2. Create ReconciliationBatch table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS reconciliationbatch (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR NOT NULL,
                    uploaded_by INTEGER NOT NULL REFERENCES "user"(id),
                    total_transactions INTEGER DEFAULT 0 NOT NULL,
                    total_amount FLOAT DEFAULT 0.0 NOT NULL,
                    drivers_matched INTEGER DEFAULT 0 NOT NULL,
                    trips_reconciled INTEGER DEFAULT 0 NOT NULL,
                    status VARCHAR DEFAULT 'active' NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    reversed_at TIMESTAMP WITHOUT TIME ZONE,
                    reversed_by INTEGER REFERENCES "user"(id)
                );
            """))
            print("Created reconciliationbatch table.")
        except Exception as e:
            print(f"Error creating reconciliationbatch table: {e}")

        # 3. Create DepositTripLink table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS deposittriplink (
                    id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR NOT NULL REFERENCES telebirrtransaction(transaction_id),
                    trip_id VARCHAR NOT NULL REFERENCES drivertrip(id),
                    amount_applied FLOAT NOT NULL,
                    batch_id INTEGER REFERENCES reconciliationbatch(id),
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
                );
            """))
            print("Created deposittriplink table.")
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deposittriplink_transaction_id ON deposittriplink(transaction_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deposittriplink_trip_id ON deposittriplink(trip_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deposittriplink_batch_id ON deposittriplink(batch_id);"))
            print("Created indexes for deposittriplink.")
        except Exception as e:
            # Fallback for SQLite which doesn't support SERIAL
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS reconciliationbatch (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename VARCHAR NOT NULL,
                        uploaded_by INTEGER NOT NULL REFERENCES "user"(id),
                        total_transactions INTEGER DEFAULT 0 NOT NULL,
                        total_amount FLOAT DEFAULT 0.0 NOT NULL,
                        drivers_matched INTEGER DEFAULT 0 NOT NULL,
                        trips_reconciled INTEGER DEFAULT 0 NOT NULL,
                        status VARCHAR DEFAULT 'active' NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        reversed_at TIMESTAMP,
                        reversed_by INTEGER REFERENCES "user"(id)
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS deposittriplink (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_id VARCHAR NOT NULL REFERENCES telebirrtransaction(transaction_id),
                        trip_id VARCHAR NOT NULL REFERENCES drivertrip(id),
                        amount_applied FLOAT NOT NULL,
                        batch_id INTEGER REFERENCES reconciliationbatch(id),
                        created_at TIMESTAMP NOT NULL
                    );
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deposittriplink_transaction_id ON deposittriplink(transaction_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deposittriplink_trip_id ON deposittriplink(trip_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deposittriplink_batch_id ON deposittriplink(batch_id);"))
                print("Created SQLite tables and indexes.")
            except Exception as e2:
                print(f"Error creating SQLite tables: {e2}")
        
        print("Migration complete.")

if __name__ == "__main__":
    run_migration()
