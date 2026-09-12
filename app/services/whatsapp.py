import httpx
import os
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}"

async def send_text_message(to: str, text: str):
    """
    Sends a text message using the Meta WhatsApp Business API.
    """
    url = f"{BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()

async def send_template_message(to: str, template_name: str, language_code: str = "en_US", components: list = None):
    """
    Sends a template message. (Used in later steps)
    """
    url = f"{BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code}
        }
    }
    if components:
        payload["template"]["components"] = components
        
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()

async def send_media_message(to: str, media_url: str, media_type: str = "image"):
    """
    Sends a media message (image/document) via URL.
    """
    url = f"{BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": media_type,
        media_type: {"link": media_url}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()
