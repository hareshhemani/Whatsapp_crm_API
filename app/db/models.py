from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    tags = Column(String, default="") # Comma-separated tags
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="contact")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    wa_id = Column(String, unique=True, index=True) # WhatsApp Message ID
    body = Column(Text, nullable=True)
    msg_type = Column(String, default="text")
    direction = Column(String) # 'inbound' or 'outbound'
    status = Column(String, default="received") # sent, delivered, read, received
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    contact = relationship("Contact", back_populates="messages")

class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    response = Column(Text)
    action_tag = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
