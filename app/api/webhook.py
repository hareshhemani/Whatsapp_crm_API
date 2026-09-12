from fastapi import APIRouter, Request, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import crm, automation
import logging

router = APIRouter()
logger = logging.getLogger("webhook")

import os
from dotenv import load_dotenv

load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "your_verify_token_here")
@router.get("/")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Verification endpoint for Meta Webhook setup.
    """
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/")
async def handle_notification(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming notifications from WhatsApp (Meta).
    """
    payload = await request.json()
    logger.info(f"Received webhook: {payload}")
    
    if "entry" in payload:
        for entry in payload["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Handle Contacts info if available
                contacts_info = value.get("contacts", [])
                contact_names = {c["wa_id"]: c["profile"]["name"] for c in contacts_info if "profile" in c}

                if "messages" in value:
                    for message in value["messages"]:
                        from_number = message.get("from")
                        msg_body = message.get("text", {}).get("body")
                        msg_id = message.get("id")
                        msg_type = message.get("type")
                        
                        # Get or Create Contact
                        name = contact_names.get(from_number)
                        contact = crm.get_or_create_contact(db, from_number, name)
                        
                        # Store Message
                        crm.store_message(
                            db, 
                            contact_id=contact.id, 
                            wa_id=msg_id, 
                            body=msg_body, 
                            direction="inbound", 
                            msg_type=msg_type
                        )
                        
                        # Process Automation (Step 5)
                        await automation.process_automation(db, contact, msg_body)
                        
                        print(f"Stored and processed message from {from_number}: {msg_body}")
    
    return {"status": "ok"}
