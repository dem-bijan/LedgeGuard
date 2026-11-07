from fastapi import Depends, HTTPException , Cookie
import jwt
from app.auth import decode_access_token
from app.models import User
from app.database import get_db
from sqlalchemy.orm import Session




def get_current_user(access_token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if access_token is None :
            raise HTTPException(status_code=401,detail="Not authenticated")
        
    try:
        payload= decode_access_token(access_token) 
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid/Expired token")
    user_id = payload.get("sub") 
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user



def require_role(role:str):
    def check_role(current_user: User= Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403,detail="Not authorized for this action")
        return current_user
    return check_role