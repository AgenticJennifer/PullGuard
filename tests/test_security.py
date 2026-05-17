import os
from pullguard.security import configure_webhook_secret, verify_signature


def test_verify_valid_signature():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "mysecret"
    configure_webhook_secret()
    payload = b'{"test": "data"}'
    import hmac, hashlib
    expected = "sha256=" + hmac.new(b"mysecret", payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, expected) is True


def test_verify_invalid_signature():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "mysecret"
    configure_webhook_secret()
    payload = b'{"test": "data"}'
    assert verify_signature(payload, "sha256=invalid") is False


def test_verify_missing_header():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "mysecret"
    configure_webhook_secret()
    assert verify_signature(b"{}", None) is False


def test_verify_no_secret_configured():
    if "GITHUB_WEBHOOK_SECRET" in os.environ:
        del os.environ["GITHUB_WEBHOOK_SECRET"]
    configure_webhook_secret()
    assert verify_signature(b"{}", None) is True
