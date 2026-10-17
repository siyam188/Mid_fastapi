from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
import model
from model import Users
from pydantic import BaseModel,Field
from model import Transactions
from typing import Annotated,Optional,Literal
from datetime import date
from fastapi.responses import JSONResponse
from database import engine, SessionLocal
from router import auth
from router.auth import get_current_user

app=FastAPI()
model.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
class Transaction(BaseModel):
     title: str
     amount: float = Field(gt=0)
     type: Literal["income", "expense"]
     category: str
     date: date

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[date] = None

def get_db():
    db=SessionLocal()
    try:
         yield db
    finally:
        db.close()
db_depends=Annotated[Session,Depends(get_db)]
user_depends = Annotated[dict, Depends(get_current_user)]

@app.get("/")
def read_transactions(db:db_depends,user:user_depends):
     if user is None:
        raise HTTPException(
            status_code=401,detail="User Not Login")

     return db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")).all()

@app.get("/transaction/{transaction_id}")
def read_transaction_id(db:db_depends,transaction_id:int,user:user_depends):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Login"
        )

    transaction = db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    ).filter(
        Transactions.id == transaction_id
    ).first()

    if transaction is not None:
        return transaction

    raise HTTPException(
        status_code=404,
        detail="Not Found"
    )


@app.post('/create')
def transaction_create(db:db_depends,new_transaction:Transaction,user:user_depends):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Login"
        )

    transaction_model = Transactions(
        **new_transaction.model_dump(),
        owner_id=user.get("id")
    )

    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    return JSONResponse(
        status_code=201,
        content={"message": "Create Done"}
    )


@app.put('/edit/{transaction_id}')
def update_transaction(
    db: db_depends,
    transaction_id: int,
    update_transaction: TransactionUpdate,
    user: user_depends
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Login"
        )

    transaction = db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    ).filter(
        Transactions.id == transaction_id
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )

    update_data = update_transaction.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Update Done"}
    )


@app.delete("/delete/{transaction_id}")
def delete_transaction(
    db: db_depends,
    transaction_id: int,
    user: user_depends
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Login"
        )

    transaction = db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    ).filter(
        Transactions.id == transaction_id
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )

    db.delete(transaction)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Deleted Done"}
    )


@app.get("/user")
def users_View_Profile(db: db_depends, user: user_depends):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Login"
        )

    return db.query(Users).filter(
        Users.id == user.get("id")
    ).first()


@app.get("/transactions/filter")
def filter_transactions(
    db: db_depends,
    user: user_depends,
    type: Optional[Literal["income", "expense"]] = None,
    category: Optional[str] = None,
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None
):
    query = db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    )

    if type is not None:
        query = query.filter(
            Transactions.type == type
        )

    if category is not None:
        query = query.filter(
            Transactions.category == category
        )

    if minimum_amount is not None:
        query = query.filter(
            Transactions.amount >= minimum_amount
        )

    if maximum_amount is not None:
        query = query.filter(
            Transactions.amount <= maximum_amount
        )

    return query.all()
