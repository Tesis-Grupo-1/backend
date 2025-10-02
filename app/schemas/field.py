from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FieldBase(BaseModel):
    name: str
    size_hectares: float
    location: str
    description: Optional[str] = None

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    size_hectares: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None

class FieldResponse(FieldBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
