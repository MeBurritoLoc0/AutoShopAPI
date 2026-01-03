import jwt
from datetime import datetime, timezone, timedelta

SECERET_KEY = "super secret secrets"

def encode_token(user_id):
    payload = {
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(tz=timezone.utc),
        "sub": user_id,
    }
    return jwt.encode(payload, SECERET_KEY, algorithm="HS256")