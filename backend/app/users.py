
from sqlalchemy.exc import IntegrityError

from app.models import User
from app.auth import create_access_token, hash_password, verify_password


def register(session , full_name , email , password , role) -> User:
    stmt = session.query(User).filter_by(email=email).first()
    if stmt:
        raise EmailAlreadyExistsException("Email already exists")
    hashed_password = hash_password(password)
    user = User(full_name=full_name, email=email, hashed_password=hashed_password, role=role)
    session.add(user)
    try :
        session.commit()
    except IntegrityError:
        session.rollback()
        raise EmailAlreadyExistsException("Error occurred while registering user")
    return user

def login(session , email , password) :
    user = session.query(User).filter_by(email=email).first()
    if user and verify_password(password, user.hashed_password):
        jwt_token = create_access_token({"sub": str(user.id), "role": user.role})
        return jwt_token



class EmailAlreadyExistsException(Exception):
    pass

