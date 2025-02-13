from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv("../config/auth.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "jenkins_ai"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

def get_user(username):
    """Retrieve user details from MongoDB."""
    user = users_collection.find_one({"username": username}, {"_id": 0})  # Exclude `_id`
    return user if user else None