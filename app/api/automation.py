from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from typing import List
from pydantic import BaseModel

router = APIRouter()

class AutomationRuleSchema(BaseModel):
    keyword: str
    response: str = None
    action_tag: str = None
    is_active: bool = True

@router.get("/", response_model=List[AutomationRuleSchema])
def get_rules(db: Session = Depends(get_db)):
    return db.query(models.AutomationRule).all()

@router.post("/")
def create_rule(rule: AutomationRuleSchema, db: Session = Depends(get_db)):
    db_rule = models.AutomationRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule
