from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services import whatsapp, crm
from app.db.database import get_db

router = APIRouter()

class MessageRequest(BaseModel):
    to: str
    text: str

class MediaRequest(BaseModel):
    to: str
    media_url: str
    media_type: str = "image"

@router.post("/send")
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Endpoint to send a manual message from the CRM dashboard.
    """
    try:
        result = await whatsapp.send_text_message(request.to, request.text)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store in DB
        wa_id = result.get("messages", [{}])[0].get("id", "unknown")
        contact = crm.get_or_create_contact(db, request.to)
        crm.store_message(
            db, 
            contact_id=contact.id, 
            wa_id=wa_id, 
            body=request.text, 
            direction="outbound"
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-media")
async def send_media(request: MediaRequest, db: Session = Depends(get_db)):
    """
    Endpoint to send media (image/document) from the CRM.
    """
    try:
        result = await whatsapp.send_media_message(request.to, request.media_url, request.media_type)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store in DB
        wa_id = result.get("messages", [{}])[0].get("id", "media_sent")
        contact = crm.get_or_create_contact(db, request.to)
        crm.store_message(
            db, 
            contact_id=contact.id, 
            wa_id=wa_id, 
            body=f"Sent {request.media_type}: {request.media_url}", 
            direction="outbound",
            msg_type=request.media_type
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
