import sys
from pathlib import Path

from sqlalchemy import text

from app.database import engine, get_db

#----------------------------------------------------------------------------#


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))


def test_connection():
    print("Testing connection...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()
            print("Engine connected successfully")

            db = next(get_db())
            try: 
                res = db.execute(text("SELECT 1;"))
                print("get_db) session working.)")
                print("🎉🎉🎉🎉🎉🎉")
            finally:
                db.close()

            print("Checkpoint passed! App can connect to DB.")

    except Exception as e:
        print(f"Connection failed: {e}")
        print("😡😡😡😡😡😡😡😡😡")

if __name__ == "__main__":
    test_connection()