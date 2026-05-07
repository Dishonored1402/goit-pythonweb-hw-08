from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactResponse, ContactCreate, ContactUpdate
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    name: str = Query(None), 
    last_name: str = Query(None), 
    email: str = Query(None), 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return await repository_contacts.get_contacts(skip, limit, name, last_name, email, db)

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)

@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, body: ContactUpdate, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(db: Session = Depends(get_db)):
    return await repository_contacts.get_upcoming_birthdays(db)

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return None