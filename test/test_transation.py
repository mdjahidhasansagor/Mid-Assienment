from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import sessionLocal
from models import Transaction


def override_get_current_user():
    return {
        'id' : 1,
        'username' : 'testuser'
    }


def test_transaction():
    db = sessionLocal()

    # remove old test data if its exist
    db.query(Transaction).filter(Transaction.id == 99).delete()

    Transact = Transaction(
        id = 99,
        title = 'Testing',
        amount = '100000',
        type = 'income',
        category = "Food",
        Transaction_date = "2026-09-25",
        owner_id = 1
    )

    db.add(Transact)
    db.commit()


app.dependency_overrides[get_current_user] = override_get_current_user


def test_treasaction_read():
    response = client.get('transactions')
    assert response.status_code == status.HTTP_200_OK


def test_read_specific_transaction():
    response = client.get('/transactions/99')
    assert response.status_code == status.HTTP_200_OK


def test_create_transaction():

    db = sessionLocal()

    # remove old test data if its exist
    db.query(Transaction).filter(Transaction.id == 0).delete()
    db.commit()


    request_data = {
        "id": 0,
        "title": "string",
        "amount": 10000,
        "type": "income",
        "category": "Food",
        "Transaction_date": "2026-09-25"
    }
    
    response = client.post('/transactions', json=request_data)
    assert response.status_code == status.HTTP_200_OK


def test_update_transaction():

    request_data = {
        "title": "Updated"
}
    response = client.put('/transactions/99', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Transaction Update successfully!'}



def test_delete_transaction():

    response = client.delete('/transactions/99')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'massage' : 'Transactions delete successfully!'}