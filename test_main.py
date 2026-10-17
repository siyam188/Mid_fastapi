
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_transactions():
    response = client.get("/")

    assert response.status_code == 401 or response.status_code == 200


def test_get_specific_transaction():
    response = client.get("/transaction/1")

    assert response.status_code in [401, 404, 200]


def test_create_transaction():
    transaction = {
        "title": "Test Salary",
        "amount": 1000,
        "type": "income",
        "category": "Salary",
        "date": "2026-10-17"
    }

    response = client.post("/create", json=transaction)

    assert response.status_code in [401, 201]

def test_update_transaction():
    update_data = {
        "title": "Updated Salary",
        "amount": 1500
    }

    response = client.put("/edit/1", json=update_data)

    assert response.status_code in [401, 404, 200]



def test_delete_transaction():
    response = client.delete("/delete/1")

    assert response.status_code in [401, 404, 200]
