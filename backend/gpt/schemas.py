# backend/schemas.py
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ConversationCreate(BaseModel):
    message: str

class ConversationOut(BaseModel):
    id: int
    message: str
    num_attachments: int

    class Config:
        orm_mode = True

class AttachmentCreate(BaseModel):
    # 如果还需要其他元信息，可以在这里添加
    pass