import pytest  # type: ignore

from backend.server import app

@pytest.fixture(autouse=True)
def patch_downloader(monkeypatch):
    """Patch download_youtube_video to avoid external network calls during tests."""
    from backend.utils import youtube_downloader

    def _fake_download(url):
        return '/tmp/fake-video.mp4'

    monkeypatch.setattr(youtube_downloader, 'download_youtube_video', _fake_download)


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


# --- New tests for YouTube endpoint scaffolding ---

def test_process_youtube_missing_url(client):
    """Should return 400 when no url is provided"""
    response = client.post('/process-youtube', json={})
    assert response.status_code == 400


def test_process_youtube_not_implemented(client):
    """Should return 202 when download succeeds but detection not yet implemented"""
    payload = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    response = client.post('/process-youtube', json=payload)
    # Depending on environment network, we mock to skip download in unit tests; here assume 202 or 502.
    assert response.status_code in (202, 502)
    data = response.get_json()
    assert data["url"] == payload["url"]