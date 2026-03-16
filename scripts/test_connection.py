"""
Test Database and Services Connection
Verifies all connections are working properly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, settings, SessionLocal
from app.services.storage import is_storage_enabled
from sqlalchemy import text

def test_database_connection():
    """Test database connection"""
    print("="*60)
    print("TESTING DATABASE CONNECTION")
    print("="*60)
    print(f"Database URL: {settings.database_url[:50]}...")
    print()
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Database connection successful!")
        
        # Check tables
        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """) if 'sqlite' in settings.database_url else text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname='public' 
                ORDER BY tablename
            """))
            
            tables = [row[0] for row in result]
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  • {table}")
            else:
                print("⚠️  No tables found. Run 'python scripts/init_db.py' to create them.")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_supabase_storage():
    """Test Supabase storage connection"""
    print()
    print("="*60)
    print("TESTING SUPABASE STORAGE")
    print("="*60)
    
    if not settings.supabase_url or not settings.supabase_key:
        print("⚠️  Supabase not configured (optional)")
        print("   Set SUPABASE_URL and SUPABASE_KEY to enable file storage")
        return True
    
    print(f"Supabase URL: {settings.supabase_url[:50]}...")
    print()
    
    try:
        if is_storage_enabled():
            print("✅ Supabase storage is configured and ready!")
        else:
            print("❌ Supabase storage is configured but not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase storage error: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print()
    print("="*60)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("="*60)
    print()
    
    vars_to_check = {
        "DATABASE_URL": settings.database_url[:50] + "...",
        "SECRET_KEY": settings.secret_key[:20] + "...",
        "FRONTEND_URL": settings.frontend_url,
        "SUPABASE_URL": settings.supabase_url or "(not set)",
        "SUPABASE_KEY": "(set)" if settings.supabase_key else "(not set)",
        "DEBUG": str(settings.debug)
    }
    
    for var, value in vars_to_check.items():
        print(f"  {var}: {value}")
    
    print()
    
    # Check for production readiness
    warnings = []
    if settings.secret_key == "dev-secret-key-change-in-production":
        warnings.append("SECRET_KEY is using default value! Change it in production!")
    
    if settings.frontend_url == "http://localhost:3000" and "postgres" in settings.database_url:
        warnings.append("FRONTEND_URL seems to be localhost but using production database")
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
    else:
        print("✅ All environment variables look good!")
    
    return len(warnings) == 0

def main():
    """Run all tests"""
    print()
    print("🔍 RUNNING CONNECTION TESTS")
    print()
    
    results = {
        "Database": test_database_connection(),
        "Supabase Storage": test_supabase_storage(),
        "Environment": test_environment_variables()
    }
    
    print()
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test}: {status}")
    
    print()
    
    if all(results.values()):
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())



