from app.database import engine, Base
import app.models  # Registers models with Base

if __name__ == "__main__":
    print("Creating database tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")