from datetime import datetime, timedelta
from sqlalchemy import or_, extract
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate

async def get_contacts(skip: int, limit: int, name: str, last_name: str, email: str, db: Session):
    query = db.query(Contact)
    if name:
        query = query.filter(Contact.first_name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.offset(skip).limit(limit).all()

async def create_contact(body: ContactCreate, db: Session):
    existing_contact = db.query(Contact).filter(Contact.email == body.email).first()
    if existing_contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactUpdate, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact

async def get_upcoming_birthdays(db: Session):
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    
    contacts = db.query(Contact).all()
    upcoming = []
    for contact in contacts:
        if contact.birthday:
            try:
                bday_this_year = contact.birthday.replace(year=today.year)
            except ValueError:
                bday_this_year = contact.birthday.replace(year=today.year, day=28)
                
            if today <= bday_this_year <= next_week:
                upcoming.append(contact)
    return upcoming

async def get_contact(contact_id: int, db: Session):
    return db.query(Contact).filter(Contact.id == contact_id).first()

async def remove_contact(contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact