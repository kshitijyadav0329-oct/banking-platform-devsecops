from fastapi.testclient import TestClient

from application.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_accounts():
    response = client.get("/api/accounts")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_existing_account():
    response = client.get("/api/accounts/1001")

    assert response.status_code == 200
    assert response.json()["customer_name"] == "John Doe"


def test_get_nonexistent_account():
    response = client.get("/api/accounts/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"