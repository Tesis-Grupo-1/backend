from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    lastname: str
    date_register: Optional[datetime] = datetime.now()