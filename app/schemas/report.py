from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportBase(BaseModel):
    title: str
    content: str

class ReportCreate(ReportBase):
    field_id: int
    detection_id: int

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ReportResponse(ReportBase):
    id: int
    user_id: int
    field_id: int
    detection_id: int
    ai_generated_content: Optional[str] = None
    pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReportGenerateRequest(BaseModel):
    field_id: int
    detection_id: int
    title: str
    additional_notes: Optional[str] = None
