from datetime import datetime
from app.database.database import get_database

db = get_database()  # ใช้ฟังก์ชัน get_database()

# คลาสสำหรับการจัดการ FavoriteHouses
class FavoriteHouses:
    def __init__(self, email, house_id):
        self.email = email
        self.house_id = house_id

    def save(self):
        favorite_houses_collection = db['favorite']
        favorite_houses_collection.insert_one({
            "email": self.email,
            "house_id": self.house_id
        })

    @staticmethod
    def find_by_user_email(user_email):
        favorite_houses_collection = db['favorite']
        return list(favorite_houses_collection.find({"email": user_email}))

# คลาสสำหรับการจัดการ HouseList (ใช้ collection preProcessed_500)
class HouseList:
    @staticmethod
    def find_all():
        return list(db['preProcessed_500'].find())

    @staticmethod
    def find_by_id(house_id):
        return db['preProcessed_500'].find_one({"id": house_id})

# คลาสสำหรับการจัดการ VisitedPages
class VisitedPages:
    def __init__(self, email, house_id):
        self.email = email
        self.house_id = house_id
        self.timestamp = datetime.utcnow()

    def save(self):
        visited_pages_collection = db['visited_pages']
        visited_pages_collection.insert_one({
            "email": self.email,
            "house_id": self.house_id,
            "timestamp": self.timestamp
        })

    @staticmethod
    def find_by_user_email(user_email):
        visited_pages_collection = db['visited_pages']
        return list(visited_pages_collection.find({"email": user_email}))

# คลาสสำหรับการจัดการ BlacklistToken
class BlacklistToken:
    def __init__(self, token_key, is_logout=False):
        self.token_key = token_key
        self.is_logout = is_logout
        self.updated_time = datetime.utcnow()

    def save(self):
        blacklist_token_collection = db['blacklist_token']
        blacklist_token_collection.insert_one({
            "token_key": self.token_key,
            "is_logout": self.is_logout,
            "updated_time": self.updated_time
        })

    @staticmethod
    def find_by_token_key(token_key):
        blacklist_token_collection = db['blacklist_token']
        return blacklist_token_collection.find_one({"token_key": token_key})

# คลาสสำหรับการจัดการ User
class User:
    def __init__(self, email, password, name, surname, number):
        self.email = email
        self.password = password
        self.name = name
        self.surname = surname
        self.number = number

    def save(self):
        users_collection = db['users']
        users_collection.insert_one({
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "surname": self.surname,
            "number": self.number
        })

    @staticmethod
    def find_by_email(email):
        users_collection = db['users']
        return users_collection.find_one({"email": email})
