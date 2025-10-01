# backend/models/user_model.py
from pydantic import BaseModel, constr
from typing import Optional

# From old schemas.py / auth.py
class UserCreate(BaseModel):
    username: str
    password: constr(min_length=4, max_length=72)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str