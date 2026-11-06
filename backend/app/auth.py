import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY")


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))



def create_access_token(data:dict , expires_minuts: int=30) -> str :
    to_encode = data.copy()
    expire =datetime.datetime.now(datetime.timezone.utc)+ datetime.timedelta(minutes=expires_minuts)
    to_encode["exp"] = expire
    return jwt.encode(to_encode , SECRET_KEY,algorithm="HS256")


def decode_access_token(token:str) -> dict :
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


