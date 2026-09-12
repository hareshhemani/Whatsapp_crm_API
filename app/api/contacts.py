from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.services import crm
from typing import List
from pydantic import BaseModel
from datetime import datetime
import csv
import io

router = APIRouter()

class MessageSchema(BaseModel):
    id: int
    body: str
    direction: str
    timestamp: datetime
    msg_type: str

    class Config:
        from_attributes = True

class ContactSchema(BaseModel):
    id: int
    phone_number: str
    name: str = None
    tags: str
    last_seen: datetime = None

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    phone_number: str
    name: str = None
    tags: str = ""

@router.get("/", response_model=List[ContactSchema])
def get_contacts(db: Session = Depends(get_db)):
    return db.query(models.Contact).filter(models.Contact.is_deleted == False).all()

@router.post("/", response_model=ContactSchema)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    # Clean phone number
    clean_phone = "".join(filter(str.isdigit, contact.phone_number))
    if not clean_phone:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    db_contact = crm.get_or_create_contact(db, clean_phone, contact.name)
    if contact.tags:
        db_contact.tags = contact.tags
        db.commit()
    
    return db_contact
@router.get("/{contact_id}/messages", response_model=List[MessageSchema])
def get_chat_history(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return db.query(models.Message).filter(models.Message.contact_id == contact_id).order_by(models.Message.timestamp.asc()).all()

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Soft delete
    contact.is_deleted = True
    db.commit()
    return {"status": "success"}

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file with 'phone' and optional 'name' and 'tags' columns.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file")
    
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        count = 0
        for row in reader:
            # Try different common column names
            phone = row.get('phone') or row.get('phone_number') or row.get('mobile')
            if not phone:
                continue
            
            # Clean phone number (keep only digits)
            clean_phone = "".join(filter(str.isdigit, phone))
            if not clean_phone:
                continue
                
            name = row.get('name') or row.get('full_name')
            tags = row.get('tags') or ""
            
            # Create or update contact
            contact = crm.get_or_create_contact(db, clean_phone, name)
            if tags:
                contact.tags = tags
                db.commit()
                
            count += 1
            
        return {"status": "success", "message": f"{count} contacts processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
