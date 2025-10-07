from pydantic import BaseModel

class ImageUploadResponse(BaseModel):
    id_image: int
    image_path: str
    porcentaje_plaga: float
    #upload_Date: str

    class Config:
        from_attributes = True 