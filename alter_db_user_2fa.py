import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    sqlite_file_name = "database.db"
    DATABASE_URL = f"sqlite:///{sqlite_file_name}"
else:
    if "postgresql+asyncpg" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

print(f"Connecting to database: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    is_sqlite = engine.dialect.name == "sqlite"
    table_name = "user" if is_sqlite else '"user"'
    
    try:
        column_type = "INTEGER DEFAULT 0" if is_sqlite else "BOOLEAN DEFAULT FALSE"
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN two_factor_enabled {column_type};"))
        print("Column 'two_factor_enabled' added successfully to user table.")
    except Exception as e:
        print(f"Error (column might already exist): {e}")
