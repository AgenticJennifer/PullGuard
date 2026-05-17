from pullguard.webhook import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_webhook_skips_non_pr():
    resp = client.post("/webhook", json={}, headers={
        "X-GitHub-Event": "issues",
        "Content-Type": "application/json",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "skipped"
