from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_hello_endpoint():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}


def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text
