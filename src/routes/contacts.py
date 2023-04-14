from datetime import datetime, timedelta
from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.model import Contact
from src.schemas import ContactResponse, ContactModel

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], name="Get contacts")
async def get_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(email=body.email).first()
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is exists")
    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactResponse, name="Get contact by id")
async def get_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, name="Update contact by id")
async def update_contact_by_id(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone = body.phone
    contact.born_date = body.born_date
    contact.add_data = body.add_data
    db.commit()
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, name="Remove contact by id")
async def remove_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(contact)
    db.commit()
    return contact


@router.get("/search/{find_item}",
            response_model=List[ContactResponse],
            name="Find contact by first_name, last_name, email")
async def get_search(find_item: str, db: Session = Depends(get_db)):
    result = []
    if find_item:
        contacts_f_name = db.query(Contact).filter(Contact.first_name.like(f'%{find_item}%')).all()
        if contacts_f_name:
            result.extend(contacts_f_name)
        contacts_l_name = db.query(Contact).filter(Contact.last_name.like(f'%{find_item}%')).all()
        if contacts_l_name:
            result.extend(contacts_l_name)
        contacts_email = db.query(Contact).filter(Contact.email.like(f'%{find_item}%')).all()
        if contacts_email:
            result.extend(contacts_email)
        result = list(set(result))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result


@router.get("/birthday/", response_model=List[ContactResponse], name="Birthday in 7 days")
async def birthday_7(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    result = []
    today = datetime.now()
    for contact in contacts:
        if contact.born_date.month > today.month:
            contact_birthday = datetime(year=today.year, month=contact.born_date.month, day=contact.born_date.day)
        elif contact.born_date.month < today.month:
            contact_birthday = datetime(year=today.year+1, month=contact.born_date.month, day=contact.born_date.day)
        else:
            if contact.born_date.day > today.day:
                contact_birthday = datetime(year=today.year, month=contact.born_date.month, day=contact.born_date.day)
            else:
                contact_birthday = datetime(year=today.year+1, month=contact.born_date.month, day=contact.born_date.day)
        delta = contact_birthday - today
        if delta <= timedelta(days=7):
            result.append(contact)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result
