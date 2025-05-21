from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.main import app
from infrastructure.jwt_service import create_token

client = TestClient(app)

# Create a valid token with 1-hour expiry
valid_token = create_token(
    {"sub": "test-user", "exp": datetime.utcnow() + timedelta(hours=1)}
)

# Create an expired token
expired_token = create_token(
    {"sub": "test-user", "exp": datetime.utcnow() - timedelta(hours=1)}
)


def test_inference_success():
    """Test successful inference with valid JWT token."""
    response = client.post(
        "/infer",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"text": "hello"},
    )
    assert response.status_code == 200
    assert response.json().get("data") == {"result": "olleh"}


def test_inference_auth_failure_invalid_token():
    """Test inference request with an invalid token."""
    response = client.post(
        "/infer",
        headers={"Authorization": "Bearer invalid_token"},
        json={"text": "hello"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_inference_auth_failure_missing_token():
    """Test inference request with missing token."""
    response = client.post("/infer", json={"text": "hello"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_inference_auth_failure_expired_token():
    """Test inference request with expired token."""
    response = client.post(
        "/infer",
        headers={"Authorization": f"Bearer {expired_token}"},
        json={"text": "hello"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
