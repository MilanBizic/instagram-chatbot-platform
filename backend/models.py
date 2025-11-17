from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Admin user model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chatbots = relationship("Chatbot", back_populates="owner")


class Chatbot(Base):
    """Chatbot model - one per Instagram account"""
    __tablename__ = "chatbots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    instagram_account_id = Column(String, unique=True, nullable=False)
    instagram_username = Column(String)
    access_token = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="chatbots")
    
    # Relationships
    keywords = relationship("Keyword", back_populates="chatbot", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chatbot", cascade="all, delete-orphan")


class Keyword(Base):
    """Keyword-based responses"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    trigger = Column(String, nullable=False)  # Keyword koji triggeruje odgovor
    response = Column(Text, nullable=False)   # Automatski odgovor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"))
    chatbot = relationship("Chatbot", back_populates="keywords")


class Message(Base):
    """Log svih poruka"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, nullable=False)  # Instagram user ID
    sender_username = Column(String)
    message_text = Column(Text, nullable=False)
    bot_response = Column(Text)
    matched_keyword = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"))
    chatbot = relationship("Chatbot", back_populates="messages")
