from app.database import engine
from app.models import SQLModel
from sqlalchemy import text

def reset_database():
    try:
        # Drop all tables managed by SQLModel
        SQLModel.metadata.drop_all(engine)
        print("Successfully dropped all SQLModel tables.")
        
        # As an extra measure to ensure a clean slate, let's execute a CASCADE drop on the public schema
        # and recreate it, in case there are lingering sequences or tables not caught by drop_all.
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE;"))
            conn.execute(text("CREATE SCHEMA public;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
            print("Successfully recreated public schema.")
            
        # Recreate all tables
        SQLModel.metadata.create_all(engine)
        print("Successfully recreated all tables.")
        
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
