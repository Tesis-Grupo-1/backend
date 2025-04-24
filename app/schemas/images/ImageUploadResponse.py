from pydantic import BaseModel

class ImageUploadResponse(BaseModel):
    id_image: int
    name: str
    url_image: str
    #upload_Date: str

    class Config:
        from_attributes = True 