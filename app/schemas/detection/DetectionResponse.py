from pydantic import BaseModel
from typing import List, Optional

class DetectionResponse(BaseModel):
    idDetection: int
    plaga: bool  
    prediction_value: float  

    class Config:
        from_attributes = True

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