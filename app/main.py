from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api import webhook, messages, contacts, automation, templates, analytics
from app.db.database import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="WhatsApp CRM + Automation API")

# Include routers
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
app.include_router(automation.router, prefix="/automation", tags=["Automation"])
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
