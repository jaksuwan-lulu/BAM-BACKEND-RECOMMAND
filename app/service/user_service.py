from sqlalchemy.orm import Session
from app.models.models import User, Token, FavoriteHouses  # แก้ไขการ import
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user_data):
    if db.query(User).filter(User.users_email == user_data.email).first():
        return None  # Email already exists
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        users_email=user_data.email,
        users_password=hashed_password,
        users_name=user_data.name,
        users_surname=user_data.surname,
        users_number=user_data.number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_favorite_house(db: Session, user_email: str, id: str):
    favorite = FavoriteHouses(user_email=user_email, id=id)
    db.add(favorite)
    db.commit()
    return favorite

def get_favorites(db: Session, user_email: str):
    return db.query(FavoriteHouses).filter(FavoriteHouses.user_email == user_email).all()

def is_token_blacklisted(db: Session, token_key: str) -> bool:
    blacklist_entry = db.query(Token).filter(Token.token_key == token_key).first()
    return blacklist_entry is not None

def add_token_to_blacklist(db: Session, token_key: str):
    new_blacklist_token = Token(
        token_key=token_key,
        is_logout=False,
        updated_time=datetime.utcnow()
    )
    db.add(new_blacklist_token)
    db.commit()
