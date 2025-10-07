from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import time, timedelta, date, datetime

class DetectionResponse(BaseModel):
    id_detection: int
    prediction_value: str
    plague_percentage: float
    field_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DetectionCreate(BaseModel):
    field_id: int
    result: str
    prediction_value: str
    time_initial: str
    time_final: str
    date_detection: str
    plague_percentage: float
    image_ids: List[int]  

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
    id: int
    field_id: int
    user_id: int
    detection_date: date
    affected_percentage: float
    result: str
    prediction_value: str
    time_initial: time
    time_final: time
    field_name: str | None = "Campo desconocido"
    plant_count: int = 0  # 👈 nuevo campo

    @field_validator('time_initial', 'time_final', mode='before')
    def convert_timedelta(cls, v):
        if isinstance(v, timedelta):
            total_seconds = int(v.total_seconds())
            h = (total_seconds // 3600) % 24
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            return time(h, m, s)
        return v

    @model_validator(mode='before')
    def normalize_fields(cls, data):
        base = data.__dict__.copy() if hasattr(data, '__dict__') else dict(data)

        # Asignar campos equivalentes
        base["id"] = base.get("id_detection")
        base["detection_date"] = base.get("date_detection")
        base["affected_percentage"] = base.get("plague_percentage")

        # Nombre del campo
        field_obj = getattr(data, "field", None) if hasattr(data, "field") else data.get("field")
        if field_obj and hasattr(field_obj, "name"):
            base["field_name"] = field_obj.name
        else:
            base.setdefault("field_name", "Campo desconocido")

        # 👇 Contar imágenes asociadas al campo (si está prefetch_related)
        images = getattr(data, "images", None) or base.get("images")
        if images:
            base["plant_count"] = len(images)
        else:
            base["plant_count"] = 0

        return base

    model_config = {"from_attributes": True}