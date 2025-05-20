from fastapi.testclient import TestClient
from src.main import app
from infrastructure.jwt_service import create_token

client = TestClient(app)
token = create_token({"sub": "test-user"})


def test_inference_success():
    res = client.post(
        "/infer", headers={"Authorization": f"Bearer {token}"}, json={"text": "hello"}
    )
    assert res.status_code == 200
    assert res.json()["result"] == "olleh"


def test_inference_auth_failure():
    res = client.post(
        "/infer", headers={"Authorization": "Bearer invalid"}, json={"text": "hello"}
    )
    assert res.status_code == 401
