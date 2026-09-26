from fastapi import FastAPI, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import User, Transaction
from database import engine, sessionLocal
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, Literal
from datetime import date
from router import auth, admin
import models
from router.auth import get_current_user


app = FastAPI()

class TransactionCreate(BaseModel):
        id : int
        title : str
        amount : float = Field(gt=0,lt=500001)
        type : Literal["income","expense"]
        category : str
        Transaction_date : date

class TransactionUpdate(BaseModel):
        title : Optional[str] = Field(default=None)
        amount : Optional[float] = Field(default=None)
        type : Optional[Literal["income","expense"]] = Field(default=None)
        category : Optional[str] = Field(default=None)
        Transaction_date: Optional[date] = Field(default=None)



models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.post('/transactions')
def create_trensaction(user : user_dependency, db : db_dependency, new_transaction : TransactionCreate):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')
    
    transaction_model = Transaction(**new_transaction.model_dump(), owner_id = user.get('id'))
    db.add(transaction_model)
    db.commit()

    return {"id": new_transaction.id,"title": new_transaction.title,"amount": new_transaction.amount,"type": new_transaction.type,"category": new_transaction.category,"Transaction_date": str(new_transaction.Transaction_date), "owner_id": user.get('id')}


@app.get('/transactions')
def all_transaction(user : user_dependency, db : db_dependency):

        if user is None:
              raise HTTPException(status_code=404, detail='Faield Authenticated')

        return db.query(Transaction).filter(Transaction.owner_id == user.get('id')).all()

@app.get('/transactions/filter')
def Transaction_Filtering(user : user_dependency, db : db_dependency, type : Optional[str] = None, category : Optional[str] = None, minimum_amount : Optional[float] = None, maximum_amount : Optional[float] = None):
    
    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    query = db.query(Transaction).filter(Transaction.owner_id == user.get('id'))

    if type is not None:
        query = query.filter(Transaction.type == type)

    if category is not None:
        query = query.filter(Transaction.category == category)

    if minimum_amount is not None:
        query = query.filter(Transaction.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(Transaction.amount <= maximum_amount)

    return query.all()



@app.get('/transactions/{transaction_id}')
def read_specfice_transaction(user : user_dependency, db : db_dependency, transaction_id : int):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')
    
    spacific_transaction = db.query(Transaction).filter(Transaction.owner_id == user.get('id')).filter(Transaction.id == transaction_id).first()

    if spacific_transaction is not None:
        return spacific_transaction
    else:
        raise HTTPException(status_code=404, detail=" No transaction Found!")


@app.put('/transactions/{transaction_id}')
def update_transaction(user : user_dependency, db : db_dependency, transaction_id : int, update_transaction : TransactionUpdate):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    transaction = db.query(Transaction).filter(Transaction.owner_id == user.get('id')).filter(Transaction.id == transaction_id).first()

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found!")

    update_data = update_transaction.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(transaction,key,value)

    db.commit()

    return JSONResponse(status_code=200, content={'message': 'Transaction Update successfully!'})


@app.delete('/transactions/{transactions_id}')
def delete_transactions(user : user_dependency, db : db_dependency, transactions_id : int):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    trensact = db.query(Transaction).filter(Transaction.owner_id == user.get('id')).filter(Transaction.id == transactions_id).first()

    if trensact is None:
        raise HTTPException(status_code=404, detail="Transaction Not found!")

    db.query(Transaction).filter(Transaction.owner_id == user.get('id')).filter(Transaction.id == transactions_id).delete()

    db.commit()
    return JSONResponse(status_code=200, content={'massage' : 'Transactions delete successfully!'})

