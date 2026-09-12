from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services import whatsapp, crm
from app.db.database import get_db
from typing import List, Optional

router = APIRouter()

class TemplateVariable(BaseModel):
    type: str = "text"
    text: str

class TemplateRequest(BaseModel):
    to: str
    template_name: str
    language_code: str = "en_US"
    variables: Optional[List[str]] = None

class BroadcastRequest(BaseModel):
    template_name: str
    language_code: str = "en_US"
    tag_filter: Optional[str] = None

@router.post("/send")
async def send_template(request: TemplateRequest, db: Session = Depends(get_db)):
    """
    Sends a WhatsApp template message with dynamic variables.
    """
    components = []
    if request.variables:
        body_params = [{"type": "text", "text": v} for v in request.variables]
        components.append({
            "type": "body",
            "parameters": body_params
        })

    try:
        result = await whatsapp.send_template_message(
            to=request.to,
            template_name=request.template_name,
            language_code=request.language_code,
            components=components
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store in DB
        wa_id = result.get("messages", [{}])[0].get("id", "template_sent")
        contact = crm.get_or_create_contact(db, request.to)
        crm.store_message(
            db,
            contact_id=contact.id,
            wa_id=wa_id,
            body=f"Template: {request.template_name}",
            direction="outbound",
            msg_type="template"
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
def template_info():
    """
    Instructions on how to create and use templates.
    """
    return {
        "instructions": "1. Go to Meta Business Suite -> All Tools -> WhatsApp Manager -> Message Templates. 2. Create a template and wait for approval. 3. Use the approved name in this API. 4. Use {{1}}, {{2}} in the template body to inject variables via this API.",
        "example_payload": {
            "to": "919876543210",
            "template_name": "hello_world",
            "variables": ["John", "Monday"]
        }
    }

@router.post("/broadcast")
async def broadcast_template(request: BroadcastRequest, db: Session = Depends(get_db)):
    """
    Broadcast a template to multiple contacts.
    """
    query = db.query(models.Contact).filter(models.Contact.is_deleted == False)
    if request.tag_filter:
        query = query.filter(models.Contact.tags.contains(request.tag_filter))
    
    contacts = query.all()
    if not contacts:
        return {"status": "error", "message": "No contacts found matching the filter"}

    results = []
    for contact in contacts:
        try:
            res = await whatsapp.send_template_message(
                to=contact.phone_number,
                template_name=request.template_name,
                language_code=request.language_code
            )
            # Store in DB
            wa_id = res.get("messages", [{}])[0].get("id", "broadcast_sent")
            crm.store_message(
                db,
                contact_id=contact.id,
                wa_id=wa_id,
                body=f"Broadcast: {request.template_name}",
                direction="outbound",
                msg_type="template"
            )
            results.append({"phone": contact.phone_number, "status": "sent", "id": wa_id})
        except Exception as e:
            results.append({"phone": contact.phone_number, "status": "error", "message": str(e)})

    return {"status": "completed", "processed": len(contacts), "results": results}
