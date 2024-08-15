from typing import Optional, List
from datetime import datetime, timedelta, date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas import ContactCreate
from src.database.models import Contact, User


def create_contact(contact_data: ContactCreate, db: Session) -> Contact:
    existing_contact = db.query(Contact).filter(Contact.email == contact_data.email).first()
    if existing_contact:
        raise HTTPException(status_code=400, detail="Contact with this email already exists.")

    birthday = None
    if contact_data.birthday:
        try:
            birthday = datetime.strptime(contact_data.birthday, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    new_contact = Contact(
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        email=contact_data.email,
        phone_number=contact_data.phone_number,
        birthday=birthday,
        additional_info=contact_data.additional_info
    )

    try:
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create contact.")
    if new_contact.birthday:
        new_contact.birthday = new_contact.birthday.strftime('%Y-%m-%d')

    return new_contact


def get_contacts(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[Contact]:
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).offset(skip).limit(limit).all()
    return contacts


def get_contact(db: Session, contact_id: int, current_user: User) -> Optional[Contact]:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    return contact


def update_contact(db: Session, contact_id: int, contact_data: dict, current_user: User) -> Optional[Contact]:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if contact:
        for key, value in contact_data.items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int, current_user: User):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if db_contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this contact")
    db.delete(db_contact)
    db.commit()
    return db_contact

def format_date(d: date) -> str:
    return d.strftime('%Y-%m-%d') if d else None

def search_contacts(db: Session, name: Optional[str] = None, email: Optional[str] = None) -> List[Contact]:
    query = db.query(Contact)
    if name:
        query = query.filter(Contact.first_name.ilike(f"%{name}%") | Contact.last_name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    contacts = query.all()
    for contact in contacts:
        contact.birthday = format_date(contact.birthday)
    return contacts


def get_contacts_birthday_soon(db: Session, days: int = 7) -> List[Contact]:
    today = datetime.today().date()
    end_date = today + timedelta(days=days)
    contacts = (
        db.query(Contact)
        .filter(Contact.birthday >= today, Contact.birthday <= end_date)
        .all()
    )
    for contact in contacts:
        if contact.birthday:
            contact.birthday = contact.birthday.strftime('%Y-%m-%d')
    return contacts
