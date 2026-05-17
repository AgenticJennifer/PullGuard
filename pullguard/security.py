from __future__ import annotations
import hmac
import hashlib
import os


WEBHOOK_SECRET: bytes | None = None


def configure_webhook_secret() -> None:
    global WEBHOOK_SECRET
    raw = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if raw:
        WEBHOOK_SECRET = raw.encode()
    else:
        WEBHOOK_SECRET = None


def verify_signature(payload_bytes: bytes, signature_header: str | None) -> bool:
    if not WEBHOOK_SECRET:
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
