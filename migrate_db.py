import asyncio
from sqlalchemy import text
from app.db.session import engine

async def migrate():
    async with engine.begin() as conn:
        print("Starting DB migration...")
        
        # 1. Rename 'status' to 'work_status' if it exists
        try:
            await conn.execute(text("ALTER TABLE driver RENAME COLUMN status TO work_status;"))
            print("Renamed 'status' to 'work_status'.")
        except Exception as e:
            print(f"Could not rename 'status' (might already be renamed): {e}")

        # 2. Add new columns
        columns = [
            ("phones", "TEXT"),
            ("employment_type", "TEXT"),
            ("car_id", "TEXT"),
            ("car_brand_model", "TEXT"),
            ("plate", "TEXT"),
            ("license_number", "TEXT"),
            ("license_expiry", "TEXT"),
            ("license_issue_date", "TEXT"),
            ("license_country", "TEXT"),
            ("tin", "TEXT"),
            ("experience_date", "TEXT"),
            ("balance_limit", "FLOAT DEFAULT 0.0"),
            ("hired_at", "TEXT")
        ]
        
        for col_name, col_type in columns:
            try:
                await conn.execute(text(f"ALTER TABLE driver ADD COLUMN {col_name} {col_type};"))
                print(f"Added column '{col_name}'.")
            except Exception as e:
                print(f"Could not add column '{col_name}' (might already exist): {e}")

        print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate())
