from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignup(BaseModel):
    name: str
    class_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    name: str
    class_name: str
    email: str
