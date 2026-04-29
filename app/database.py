import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to SQLite if no URL is provided
    sqlite_file_name = "database.db"
    DATABASE_URL = f"sqlite:///{sqlite_file_name}"
    connect_args = {"check_same_thread": False}
else:
    # If using PostgreSQL with psycopg2, we need to ensure the driver is correct
    # The .env currently has postgresql+asyncpg, but we are using sync sessions.
    if "postgresql+asyncpg" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    connect_args = {}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
