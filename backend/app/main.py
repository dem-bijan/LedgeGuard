from app.schemas import LoginRequest, RegisterRequest, RegisterResponse, TransferResponse , TransferRequest , AccountResponse , PendingTransferResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.ledger import InsufficientFundsException , AccountFlaggedException , FlaggedRecepientException,NotAccountOwnerException ,PendingTransferNotCancellableException,AccountNotFoundException 
from app.ledger import get_account_by_id  ,cancel_pending_transfer,get_pending_transfers_for_user ,sweeper  ,transfer , account_getter , get_balance
from fastapi import Depends , FastAPI , Response
from fastapi.middleware.cors import CORSMiddleware
from app.users import login, register , EmailAlreadyExistsException
from app.db import check_connection
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, PendingTransfer
import uuid

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
@app.post("/transfer", response_model=TransferResponse | PendingTransferResponse)
def create_transfer(request: TransferRequest , current_user=Depends(get_current_user), db :Session = Depends(get_db) , ):
    sweeper(db , current_user.id)
    result =  transfer(db , request.idempotency_key , request.from_rib , request.to_rib , current_user.id , request.amount , request.description ,confirm_flagged_recipient=request.confirm_flagged_recipient)
    if isinstance(result , PendingTransfer):
        pending_response = PendingTransferResponse(id=result.id, to_rib=get_account_by_id(db, result.to_account_id).rib, idempotency_key=result.idempotency_key, description=result.description, status=result.status, execute_at=result.execute_at, amount=result.amount)
        return JSONResponse(status_code=202 , content=pending_response.model_dump(mode="json"))
    return JSONResponse(status_code=201,content=TransferResponse.model_validate(result).model_dump(mode="json") )

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
    sweeper(db ,user.id)
    accounts =  account_getter(db,user)
    return [
        AccountResponse(id=a.id  , rib=a.rib , label=a.label,currency = a.currency , balance= get_balance(db,a.id)) for a in accounts
    ]


@app.get("/me", response_model=RegisterResponse)
def get_me(current_user:User= Depends(get_current_user)):
    return current_user

@app.get("/pending-transfers",response_model=list[PendingTransferResponse])
def get_pending_transfers(db:Session=Depends(get_db), user = Depends(get_current_user)):
    transfers = get_pending_transfers_for_user(db , user.id)
    return [
        PendingTransferResponse(id=pt.id ,to_rib=get_account_by_id(db,pt.to_account_id).rib, idempotency_key=pt.idempotency_key ,description= pt.description ,status=pt.status ,execute_at=pt.execute_at ,amount=pt.amount) for pt in transfers
        ]


@app.post("/pending-transfers/{pending_transfer_id}/cancel", response_model=PendingTransferResponse)
def cancel_transaction_by_id(pending_transfer_id:uuid.UUID,db:Session =Depends(get_db)  ,user=Depends(get_current_user)):
    pt = cancel_pending_transfer(db ,pending_transfer_id , user.id )
    return PendingTransferResponse(id=pt.id, to_rib=get_account_by_id(db, pt.to_account_id).rib, idempotency_key=pt.idempotency_key, description=pt.description, status=pt.status, execute_at=pt.execute_at, amount=pt.amount)














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

@app.exception_handler(PendingTransferNotCancellableException)
def pending_transfer_not_cancellable(req,exc):
    return JSONResponse(status_code=409 , content={"detail":str(exc)})

@app.exception_handler(FlaggedRecepientException)
def failed_for_flagging_reason(req,exc):
    return JSONResponse(status_code=428 , content={"detail":str(exc)})

@app.exception_handler(AccountFlaggedException)
def failed_for_being_flagged(req,exc):
    return JSONResponse(status_code=403 , content={"detail":str(exc)})