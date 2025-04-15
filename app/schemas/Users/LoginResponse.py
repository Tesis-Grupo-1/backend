# app/schemas/users.py

from pydantic import BaseModel

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
