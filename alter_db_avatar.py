import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE driver ADD COLUMN avatar_data TEXT;"))
        print("Column avatar_data added successfully.")
    except Exception as e:
        print(f"Error (column might already exist): {e}")
