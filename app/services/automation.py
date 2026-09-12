from sqlalchemy.orm import Session
from app.db import models
from app.services import whatsapp, crm
import logging

logger = logging.getLogger("automation")

async def process_automation(db: Session, contact: models.Contact, message_body: str):
    """
    Checks incoming messages against rules and sends auto-replies or updates tags.
    """
    if not message_body:
        return

    # Normalize message for matching
    text = message_body.lower().strip()
    
    # Fetch active rules
    rules = db.query(models.AutomationRule).filter(models.AutomationRule.is_active == True).all()
    
    for rule in rules:
        if rule.keyword.lower() in text:
            logger.info(f"Rule matched: {rule.keyword} for contact {contact.phone_number}")
            
            # Send auto-reply if response exists
            if rule.response:
                result = await whatsapp.send_text_message(contact.phone_number, rule.response)
                # Store auto-reply in DB
                wa_id = result.get("messages", [{}])[0].get("id", "automation_reply")
                crm.store_message(
                    db,
                    contact_id=contact.id,
                    wa_id=wa_id,
                    body=rule.response,
                    direction="outbound",
                    msg_type="text"
                )
            
            # Update tags if action_tag exists
            if rule.action_tag:
                current_tags = contact.tags.split(",") if contact.tags else []
                if rule.action_tag not in current_tags:
                    current_tags.append(rule.action_tag)
                    contact.tags = ",".join(filter(None, current_tags))
                    db.commit()
            
            # For now, stop at first match (can be improved)
            break
