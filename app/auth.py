from datetime import datetime, timedelta
from jose import jwt
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "supersecretsecrets"
ALGORITHM = "HS256"


def encode_token(customer_id):
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=3),
        "iat": datetime.utcnow(),
        "sub": str(customer_id)   # must be a string
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])  # converts to int
    except Exception as e:
        print("JWT decode error:", repr(e))
        return None


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]
        customer_id = decode_token(token)

        if not customer_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        return func(customer_id, *args, **kwargs)

    return decorated
