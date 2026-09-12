from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db import models
from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_messages = db.query(models.Message).count()
    total_contacts = db.query(models.Contact).count()
    inbound_count = db.query(models.Message).filter(models.Message.direction == "inbound").count()
    outbound_count = db.query(models.Message).filter(models.Message.direction == "outbound").count()
    
    return {
        "total_messages": total_messages,
        "total_contacts": total_contacts,
        "inbound": inbound_count,
        "outbound": outbound_count
    }

@router.get("/export-contacts")
def export_contacts(db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Phone", "Name", "Tags", "Last Seen"])
    
    for c in contacts:
        writer.writerow([c.id, c.phone_number, c.name, c.tags, c.last_seen])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"}
    )
