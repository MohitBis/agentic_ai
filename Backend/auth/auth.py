import bcrypt
# from database import get_user
import sys
sys.path.append("..")

from backend.auth.database import get_user

def authenticate(username, password):
    """Authenticate user and return role-based access."""
    user = get_user(username)
    print(user)
    
    if not user:
        return {"status": "failed", "message": "User not found"}

    hashed_password = user["password"]
    
    if password == hashed_password:
        return {"status": "success", "role": user["role"]}
    
    return {"status": "failed", "message": "Invalid credentials"}