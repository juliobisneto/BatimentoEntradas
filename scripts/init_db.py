"""
Initialize Database
Creates all tables in the database
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, settings
from app.models.user import User
from app.models.payment_method import PaymentMethod
from app.models.transaction import TransactionModel

def init_database():
    """Create all tables in the database"""
    print("="*60)
    print("INITIALIZING DATABASE")
    print("="*60)
    print(f"Database URL: {settings.database_url[:50]}...")
    print()
    
    try:
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        print()
        
        # List created tables
        print("Tables created:")
        for table in Base.metadata.sorted_tables:
            print(f"  • {table.name}")
        
        print()
        print("="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Run 'python scripts/create_admin.py' to create admin user")
        print("2. Run 'python init_payment_methods.py' to add payment methods")
        print()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()



