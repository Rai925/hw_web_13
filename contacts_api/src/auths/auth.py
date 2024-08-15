from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.database.db import get_db
from src.database.models import User


class TokenData(BaseModel):
    email: Optional[str] = None


def get_email_from_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
        return token_data.email
    except JWTError:
        return None


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_verification_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def send_verification_email(email: str, token: str):
    sender_email = "your_email@example.com"
    receiver_email = email
    password = "your_email_password"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Email Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    verification_link = f"http://your-domain.com/verify-email/?token={token}"
    html = f"""
    <html>
    <body>
        <p>Thank you for registering! Please verify your email by clicking the link below:</p>
        <a href="{verification_link}">Verify Email</a>
    </body>
    </html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


def get_email_from_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'access_token':
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
