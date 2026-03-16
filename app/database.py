from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./batimento_entradas.db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Frontend URL for CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Supabase (optional)
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # Debug mode
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Fix for Render PostgreSQL URLs (postgres:// -> postgresql://)
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Database engine configuration
# SQLite requires check_same_thread=False for FastAPI
# PostgreSQL doesn't need this parameter
connect_args = {}
if "sqlite" in database_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug  # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

