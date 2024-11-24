from pymongo import MongoClient

def get_database():
    # ใช้ MongoClient พร้อม username และ password ใน URL
    client = MongoClient("mongodb://root:1234@localhost:27017/?authSource=admin")
    return client['bamAssetsRecommendation']
