import hashlib
import hmac

from app.config import settings


def hash_api_key(raw_key: str) -> str:
    secret = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(secret, raw_key.encode("utf-8"), hashlib.sha256).hexdigest()


def get_api_key_prefix(raw_key: str) -> str:
    return raw_key[:8]


def secure_compare(value: str, expected: str) -> bool:
    return hmac.compare_digest(value, expected)
