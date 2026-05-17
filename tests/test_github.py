from pullguard.github import GitHubClient


def test_init_no_token():
    client = GitHubClient(token="test-token")
    assert client.token == "test-token"
    assert "Authorization" in client.headers


def test_init_from_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "env-token")
    client = GitHubClient()
    assert client.token == "env-token"
