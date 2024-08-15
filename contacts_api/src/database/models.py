from sqlalchemy import Column, Integer, String, ForeignKey, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import Boolean

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birthday = Column(Date, nullable=True)
    additional_info = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    username = Column(String(50))
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar_url = Column(String, nullable=True)
    refresh_token = Column(String(255), nullable=True)
    contacts = relationship("Contact", back_populates="user")
