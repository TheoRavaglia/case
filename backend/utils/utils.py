from datetime import datetime
import pandas as pd
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def format_date(date_string: str) -> str:
    """Format date string to YYYY-MM-DD format."""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return date_string

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate that start_date is before end_date."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return start <= end
    except ValueError:
        return False

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def setup_initial_users():
    """Setup initial users with hashed passwords (run once)."""
    users_data = [
        {
            'email': 'admin@company.com',
            'name': 'Admin User',
            'role': 'admin',
            'password': hash_password('admin123')
        },
        {
            'email': 'user@company.com',
            'name': 'Regular User',
            'role': 'user',
            'password': hash_password('user123')
        }
    ]
    
    df = pd.DataFrame(users_data)
    # Get the backend directory (parent of utils folder)
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(current_dir, 'data', 'users.csv')
    df.to_csv(csv_path, index=False)
    print("Initial users created successfully!")

if __name__ == "__main__":
    setup_initial_users()