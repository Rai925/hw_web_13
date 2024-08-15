from datetime import timedelta
from pathlib import Path
from typing import Callable, Awaitable
from fastapi import Request, FastAPI, Depends, HTTPException, status, Security, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.schemas import EmailRequest
from src.auths.auth import create_access_token, create_refresh_token, get_email_from_refresh_token, get_current_user, \
    Hash, get_email_from_access_token
from src.database.db import get_db
from src.database.models import User
from src.routes.router import router, hash_handler
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

conf = ConnectionConfig(
    MAIL_USERNAME="example@meta.ua",
    MAIL_PASSWORD="secretPassword",
    MAIL_FROM="example@meta.ua",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Example email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter



app.include_router(router)

class UserModel(BaseModel):
    username: str
    password: str

fm = FastMail(conf)

@app.post("/send-email")
def send_email(request: EmailRequest):
    message = MessageSchema(
        subject="Email Verification",
        recipients=[request.recipient_email],
        body=f"Click on the link to verify your email: {request.verification_link}",
        subtype="plain"
    )
    try:
        fm.send_message(message)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: UserModel, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    exist_user = db.query(User).filter(User.email == body.username).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    new_user = User(email=body.username, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = create_access_token(data={"sub": new_user.email}, expires_delta=timedelta(hours=24))
    verification_link = f"http://localhost/verify-email?token={verification_token}"

    message = MessageSchema(
        subject="Email Verification",
        recipients=[new_user.email],
        body=f"Please verify your email: {verification_link}",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return {"email": new_user.email,
            "message": "User registered successfully. Please check your email to verify your account."}

@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = get_email_from_access_token(token)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}

@app.post("/login")
def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.username).first()
    if not user or not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.get('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = get_email_from_refresh_token(token)
    user = db.query(User).filter(User.email == email).first()

    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = create_access_token(data={"sub": email})
    refresh_token = create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.get("/")
def root(): return {"message": "Hello World"}

@app.get("/secret")
def read_item(current_user: User = Depends(get_current_user)):
    return {"message": "Secret route", "owner": current_user.email}
