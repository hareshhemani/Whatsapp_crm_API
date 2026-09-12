from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime

def get_or_create_contact(db: Session, phone_number: str, name: str = None):
    contact = db.query(models.Contact).filter(models.Contact.phone_number == phone_number).first()
    if not contact:
        contact = models.Contact(phone_number=phone_number, name=name)
        db.add(contact)
        db.commit()
        db.refresh(contact)
    elif name and not contact.name:
        contact.name = name
        db.commit()
        db.refresh(contact)
    return contact

def store_message(db: Session, contact_id: int, wa_id: str, body: str, direction: str, msg_type: str = "text"):
    message = models.Message(
        contact_id=contact_id,
        wa_id=wa_id,
        body=body,
        direction=direction,
        msg_type=msg_type
    )
    db.add(message)
    # Update contact last seen
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact:
        contact.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    return message
