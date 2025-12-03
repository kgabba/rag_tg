import bcrypt
import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY=os.getenv('SECRET_KEY')


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_jwt(data: dict, expires_minutes: int = 60):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
