from app.schemas import LoginRequest, RegisterRequest, RegisterResponse, TransferResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.ledger import InsufficientFundsException,NotAccountOwnerException ,AccountNotFoundException, transfer , account_getter , get_balance
from fastapi import Depends , FastAPI , Response
from fastapi.middleware.cors import CORSMiddleware
from app.users import login, register , EmailAlreadyExistsException
from app.db import check_connection
from app.database import get_db
from app.schemas import TransferRequest , AccountResponse
from app.dependencies import get_current_user
from app.models import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


@app.get("/health")
def health():
    try:
        db_ok = check_connection()
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "db": db_ok}
@app.post("/transfer", response_model=TransferResponse)
def create_transfer(request: TransferRequest , current_user=Depends(get_current_user), db :Session = Depends(get_db)):
    return transfer(db , request.idempotency_key , request.from_rib , request.to_rib , current_user.id , request.amount , request.description)

@app.post("/register", response_model=RegisterResponse, status_code=201)
def register_user(request: RegisterRequest, db: Session=Depends(get_db)):
    return register(db, request.full_name, request.email, request.password, request.role)

@app.post("/login")
def login_user(request: LoginRequest,response: Response, db: Session = Depends(get_db)):
    signature = login(db, request.email, request.password)
    if signature is not None:
        response.set_cookie(
            key="access_token",
            value=signature,
            httponly=True,
            samesite="lax",
            secure=False
        )
        return {"message":"Login successful"}
    else :
        raise ValueError("Invalid email or password")
    
@app.get("/accounts")
def get_accounts(db:Session=Depends(get_db) ,user = Depends(get_current_user)):
    accounts =  account_getter(db,user)
    return [
        AccountResponse(id=a.id  , rib=a.rib , label=a.label,currency = a.currency , balance= get_balance(db,a.id)) for a in accounts
    ]


@app.get("/me", response_model=RegisterResponse)
def get_me(current_user:User= Depends(get_current_user)):
    return current_user













#exception handlers 

@app.exception_handler(InsufficientFundsException)
def insufficient_funds_exception_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )

@app.exception_handler(ValueError)
def value_error_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )
@app.exception_handler(EmailAlreadyExistsException)
def email_already_exists_exception_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )

@app.exception_handler(NotAccountOwnerException)
def not_account_owner_exception_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )

@app.exception_handler(AccountNotFoundException)
def account_not_found_exception(req,exc):
    return JSONResponse(status_code=404,content={"detail": str(exc)})