from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ImageUploadResponse(BaseModel):
    id_image: int
    image_path: str
    porcentaje_plaga: float
    #upload_Date: str

    class Config:
        from_attributes = True 

class ImageResponse(BaseModel):
    id_image: int
    image_path: str
    porcentaje_plaga: float
    created_at: datetime
    is_validated: bool
    is_false_positive: bool
    validated_at: Optional[datetime] = None
    detection_id: int

    class Config:
        from_attributes = True

class ImageValidation(BaseModel):
    is_false_positive: bool

class DetectionImagesResponse(BaseModel):
    detection_id: int
    field_name: str
    detection_date: str
    total_images: int
    validated_images: int
    false_positives: int
    images: List[ImageResponse]

    class Config:
        from_attributes = True