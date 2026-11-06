from app.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, TransferResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.ledger import InsufficientFundsException, transfer
from fastapi import Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users import login, register , EmailAlreadyExistsException
from app.db import check_connection
from app.database import get_db
from app.schemas import TransferRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    try:
        db_ok = check_connection()
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "db": db_ok}
@app.post("/transfer", response_model=TransferResponse)
def create_transfer(request: TransferRequest , db :Session = Depends(get_db)):
    return transfer(db , request.idempotency_key , request.from_account_id , request.to_account_id , request.amount , request.description)

@app.post("/register", response_model=RegisterResponse, status_code=201)
def register_user(request: RegisterRequest, db: Session=Depends(get_db)):
    return register(db, request.full_name, request.email, request.password, request.role)

@app.post("/login", response_model=LoginResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    signature = login(db, request.email, request.password)
    if signature:
        return {"access_token": signature}
    else:
        raise ValueError("Invalid email or password")

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