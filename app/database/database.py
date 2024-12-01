import logging
from pymongo import MongoClient

# ตั้งค่าระดับของ logging
logging.basicConfig(level=logging.INFO)

def get_database():
    try:
        # logging.info("Connecting to MongoDB...")
        client = MongoClient("mongodb://root:1234@localhost:27017/?authSource=admin")
        # logging.info("Successfully connected to MongoDB")
        return client["bamAssetsRecommendation"]
    except Exception as e:
        # logging.error(f"Failed to connect to MongoDB: {e}")
        raise
