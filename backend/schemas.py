from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chatbot schemas
class ChatbotCreate(BaseModel):
    name: str
    instagram_account_id: str
    instagram_username: Optional[str] = None
    access_token: str


class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    instagram_username: Optional[str] = None
    access_token: Optional[str] = None
    is_active: Optional[bool] = None


class ChatbotResponse(BaseModel):
    id: int
    name: str
    instagram_account_id: str
    instagram_username: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Keyword schemas
class KeywordCreate(BaseModel):
    trigger: str
    response: str
    chatbot_id: int


class KeywordUpdate(BaseModel):
    trigger: Optional[str] = None
    response: Optional[str] = None
    is_active: Optional[bool] = None


class KeywordResponse(BaseModel):
    id: int
    trigger: str
    response: str
    is_active: bool
    chatbot_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Message schemas
class MessageResponse(BaseModel):
    id: int
    sender_id: str
    sender_username: Optional[str]
    message_text: str
    bot_response: Optional[str]
    matched_keyword: Optional[str]
    timestamp: datetime
    chatbot_id: int
    
    class Config:
        from_attributes = True


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str


# Instagram webhook
class InstagramWebhook(BaseModel):
    object: str
    entry: List[dict]
