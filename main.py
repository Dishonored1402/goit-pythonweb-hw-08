from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_
from datetime import datetime, timedelta
from typing import List

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API")

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_contacts(
    name: str = Query(None), 
    last_name: str = Query(None), 
    email: str = Query(None), 
    db: Session = Depends(get_db)
):
    query = db.query(models.Contact)
    if name:
        query = query.filter(models.Contact.first_name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(models.Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(models.Contact.email.ilike(f"%{email}%"))
    return query.all()

@app.get("/contacts/birthdays/", response_model=List[schemas.ContactResponse])
def upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.now().date()
    days_range = []
    for i in range(7):
        current_day = today + timedelta(days=i)
        days_range.append((current_day.month, current_day.day))
    
    all_contacts = db.query(models.Contact).all()
    result = []
    for contact in all_contacts:
        if contact.birthday:
            if (contact.birthday.month, contact.birthday.day) in days_range:
                result.append(contact)
    return result

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, updated_contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in updated_contact.dict().items():
        setattr(db_contact, key, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return None