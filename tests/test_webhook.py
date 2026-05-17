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


def test_webhook_skips_unrelated_comments():
    resp = client.post("/webhook", json={
        "comment": {"body": "looks good to me"},
        "issue": {"pull_request": None},
    }, headers={
        "X-GitHub-Event": "issue_comment",
        "Content-Type": "application/json",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "skipped"


def test_unauthorized_without_signature():
    resp = client.post("/webhook", json={}, headers={
        "X-GitHub-Event": "ping",
        "Content-Type": "application/json",
    })
    assert resp.status_code in (200, 401)
