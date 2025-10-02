from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, time

class DetectionResponse(BaseModel):
    idDetection: int
    plaga: str  
    prediction_value: str
    plague_percentage: float
    field_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class DetectionCreate(BaseModel):
    image_id: int
    field_id: int
    result: str
    prediction_value: str
    time_initial: str
    time_final: str
    date_detection: str
    plague_percentage: float

class DetectionUpdate(BaseModel):
    result: Optional[str] = None
    prediction_value: Optional[str] = None
    plague_percentage: Optional[float] = None

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    center_x: float
    center_y: float
    width: float
    height: float

class Detection(BaseModel):
    class_name: str
    confidence: float
    bounding_box: BoundingBox

class DetectionResponseBoxes(BaseModel):
    success: bool
    message: str
    detections: List[Detection]
    image_width: int
    image_height: int
    processed_image_base64: Optional[str] = None

class DetectionHistoryResponse(BaseModel):
    id_detection: int
    result: str
    prediction_value: str
    plague_percentage: float
    date_detection: date
    time_initial: time
    time_final: time
    field_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True