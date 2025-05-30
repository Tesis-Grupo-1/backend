from pydantic import BaseModel

class DetectionResponse(BaseModel):
    idDetection: int
    plaga: bool  
    prediction_value: float  

    class Config:
        from_attributes = True
