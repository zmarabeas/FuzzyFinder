import pytest
from backend.server import app

@pytest.fixture

def client():
    app.config.update({
        "TESTING": True,
    })
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_available_detectors(client):
    response = client.get('/available-detectors')
    assert response.status_code == 200
    data = response.get_json()
    assert "detectors" in data
    assert isinstance(data["detectors"], list)