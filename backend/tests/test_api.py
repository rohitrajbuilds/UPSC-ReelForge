from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_topics_returns_list():
    response = client.get("/api/topics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_generate_returns_job_id(monkeypatch):
    response = client.post(
        "/api/generate",
        json={
            "topic": "Directive Principles of State Policy",
            "category": "Polity",
            "duration_seconds": 180,
            "voice": "gtts",
            "include_music": True,
            "include_subtitles": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["job_id"]


def test_history_returns_list():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_config_returns_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.json()["videos_per_day"] >= 1
