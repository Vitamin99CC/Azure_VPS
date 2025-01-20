# backend/routers/conversations.py
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ConversationCreate, AttachmentCreate
from ..db_crud import (
    create_conversation,
    get_conversation_by_id,
    get_conversations_by_user,
    create_attachment,
    increment_attachment_count,
    get_attachments_by_conversation
)

router = APIRouter()

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # 如果文件夹不存在则创建

@router.post("/conversations")
def create_new_conversation(
    conversation_data: ConversationCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    # 假设你通过某种方式获取 user_id（例如登录后返回的 user_id）
    conversation = create_conversation(db, user_id=user_id, message=conversation_data.message)
    return {
        "id": conversation.id,
        "message": conversation.message,
        "num_attachments": conversation.num_attachments
    }

@router.get("/conversations/{user_id}")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = get_conversations_by_user(db, user_id=user_id)
    return conversations

@router.post("/conversations/{conversation_id}/attachments")
async def upload_attachment(
    id: int,
    conversation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 在数据库中创建附件记录
    create_attachment(db, id, conversation_id=conversation_id, file_path=str(file_path))
    # 更新对话中的附件数
    new_count = increment_attachment_count(db, conversation)

    return {
        "message": "File uploaded successfully",
        "file_name": file.filename,
        "num_attachments": new_count
    }

@router.get("/conversations/{conversation_id}/attachments")
def list_attachments(conversation_id: int, db: Session = Depends(get_db)):
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    attachments = get_attachments_by_conversation(db, conversation_id)
    return attachments