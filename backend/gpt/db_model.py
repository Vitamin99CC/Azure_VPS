# backend/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = 'conversations'

    conv_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    # 用于统计此对话下的附件数量
    num_attachments = Column(Integer, default=0)

    user = relationship("User", back_populates="conversations")
    attachments = relationship("Attachment", back_populates="conversation")

class Attachment(Base):
    __tablename__ = 'attachments'

    attach_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    file_path = Column(String(255))
    uploaded_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="attachments")