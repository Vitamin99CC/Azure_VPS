# backend/crud.py
from sqlalchemy.orm import Session
from . import db_model as models

# ========== 用户相关 ==========

def create_user(db: Session, username: str, hashed_password: str):
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# ========== Conversation ==========

def create_conversation(db: Session, user_id: int, message: str):
    db_conversation = models.Conversation(
        user_id=user_id,
        message=message
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.conv_id == conversation_id).first()

def get_conversations_by_user(db: Session, user_id: int):
    return db.query(models.Conversation).filter(models.Conversation.user_id == user_id).all()

# ========== Attachment ==========

def create_attachment(db: Session, id: int, conversation_id: int, file_path: str):
    attachment = models.Attachment(id=id,
        conversation_id=conversation_id,
        file_path=file_path
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def increment_attachment_count(db: Session, conversation: models.Conversation):
    conversation.num_attachments += 1
    db.commit()
    db.refresh(conversation)
    return conversation.num_attachments

def get_attachments_by_conversation(db: Session, conversation_id: int):
    return db.query(models.Attachment).filter(models.Attachment.conversation_id == conversation_id).all()