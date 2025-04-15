from pydantic import BaseModel

class UserResponse(BaseModel):
    id_user: int
    email: str
    name: str
    lastname: str
    password: str
    
    class Config:
        from_attributes = True