import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"

def create_verification_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # Термін дії токена 24 години
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
