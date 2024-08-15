from dataclasses import Field
from datetime import datetime
from typing import Optional

from fastapi_mail import ConnectionConfig
from pydantic import BaseModel, EmailStr, constr, HttpUrl
from dotenv import load_dotenv
import os
load_dotenv()

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: Optional[str] = None
    additional_info: Optional[str] = None


class ContactUpdate(ContactCreate):
    pass


class ContactResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    birthday: Optional[str] = None
    additional_info: Optional[str] = None



class UserModel(BaseModel):
    username: constr(min_length=5, max_length=16)
    email: EmailStr
    password: constr(min_length=6, max_length=16)


class UserUpdate(BaseModel):
    avatar_url: HttpUrl


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    detail: str = "User successfully created"


class EmailRequest(BaseModel):
    recipient_email: EmailStr
    verification_link: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmailSettings(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    MAIL_FROM_NAME: str = "Your App Name"


conf = ConnectionConfig(
    MAIL_USERNAME="your_email@example.com",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.example.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM_NAME="Your App Name"
)
