from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field(default='Max')
    last_name: str = Field(default='Somebody')
    email: EmailStr
    phone: str = Field(default='+380441234567')
    born_date: datetime
    add_data: str = Field(default="some text")


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str = None
    email: EmailStr
    phone: str = None
    born_date: datetime = None
    add_data: str = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        orm_mode = True


