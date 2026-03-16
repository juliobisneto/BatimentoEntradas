"""
Create Admin User
Creates the default admin user for the system
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    """Create default admin user"""
    db = SessionLocal()
    
    print("="*60)
    print("CREATING ADMIN USER")
    print("="*60)
    print()
    
    try:
        # Admin credentials
        admin_email = "admin@admin.com"
        admin_password = "123admin123"
        admin_name = "Admin"
        
        # Check if admin already exists
        existing_user = db.query(User).filter(User.email == admin_email).first()
        
        if existing_user:
            print(f"⚠️  Admin user '{admin_email}' already exists.")
            response = input("Do you want to recreate it? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
            
            db.delete(existing_user)
            db.commit()
            print("Old admin user deleted.")
            print()
        
        # Create new admin user
        print("Creating admin user...")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print(f"Name: {admin_name}")
        print()
        
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            name=admin_name,
            email=admin_email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("="*60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY!")
        print("="*60)
        print()
        print("Login credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
        print()
        print("⚠️  IMPORTANT: Change the admin password after first login!")
        print()
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()


