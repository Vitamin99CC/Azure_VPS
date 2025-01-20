# backend/main.py
from fastapi import FastAPI
from .database import Base, engine
from .db_model import User, Conversation, Attachment

# 路由导入
from .routers import users, conversations

# 创建所有数据库表（如果数据库还没建表，会自动建）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My Backend Service",
    description="FastAPI Backend with Users, Conversations, and Attachments",
    version="1.0.0"
)

# 注册路由
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(conversations.router, prefix="", tags=["Conversations"])