# backend/app/db/repositories.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Client (For Storage)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# SQLAlchemy Engine (For PostgreSQL)
# Replace 'postgres://' with 'postgresql://' if necessary for SQLAlchemy
db_url = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()