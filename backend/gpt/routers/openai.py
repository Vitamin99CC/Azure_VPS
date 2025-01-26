# backend/routers/openai_service.py

import os
import base64
import openai
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from ..database import get_db
from ..db_crud import (
    get_conversation_by_id,
    create_conversation,
    create_attachment,
    increment_attachment_count,
    get_attachments_by_conversation
)
from ..db_crud import get_conversations_by_user  # 如果需要
from ..db_model import Conversation, Attachment
from ..schemas import ConversationCreate

router = APIRouter()

# 你可以通过环境变量来管理 API Key，或者通过配置文件等方式。
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

# 这里和你项目中的上传目录一致
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/openai/generate")
async def generate_openai_reply(
    conversation_id: Optional[int] = Form(None),
    user_id: Optional[int] = Form(None),
    user_message: Optional[str] = Form(""),  # 用户本次输入的文本
    files: List[UploadFile] = File([]),      # 最多可上传4个文件/图片
    db: Session = Depends(get_db)
):
    """
    此接口完成以下工作：
    1. 如果 conversation_id 未指定，则新建一个对话；否则取出已存在对话。
    2. 接收本次用户输入（文本 + 最多四个图片）。
    3. 读取该对话的历史消息，构造发送给 OpenAI 的 messages。
    4. 将新的 user_message（含图像）一起发送到 OpenAI Chat Completion 接口，获取回复。
    5. 将回复写入到数据库对应的 conversation。
    6. 返回生成的回复结果给前端。
    """

    # 如果没有指定 conversation_id，就新建一个对话
    if not conversation_id:
        if not user_id:
            raise HTTPException(status_code=400, detail="Must provide user_id when creating a new conversation.")
        # 创建新的对话
        new_conv = create_conversation(db, user_id=user_id, message=user_message)
        conversation_id = new_conv.conv_id
    else:
        # 如果是指定了 conversation_id，就查询数据库验证
        conversation = get_conversation_by_id(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # 处理用户上传的附件（如果有）
    # 注意：这里示例默认所有附件都视为图像并传给 Vision。如果你有文件类型判断逻辑，可自行完善。
    image_urls_for_openai = []
    for upload_file in files[:4]:  # 最多4个
        file_path = UPLOAD_DIR / upload_file.filename
        with open(file_path, "wb") as f:
            f.write(await upload_file.read())

        # 在数据库中保存附件
        create_attachment(
            db,
            id=None,  # 让数据库自动生成主键ID
            conversation_id=conversation_id,
            file_path=str(file_path)
        )
        # 更新对话中的附件数
        increment_attachment_count(db, get_conversation_by_id(db, conversation_id))

        # 这里为了让 OpenAI 能访问该图片，需要有一个可访问的 URL。
        # 如果你有公共存储（如 S3 或公开的静态服务器），可将文件上传并得到公开 URL。
        # 这里为了简化，仅示例“本地静态文件服务器”的用法，假设我们能通过 /uploads/filename 来访问：
        public_url = f"http://YOUR_DOMAIN/uploads/{upload_file.filename}"
        image_urls_for_openai.append(public_url)

    # 取出完整对话的历史信息（消息 + 附件）做上下文
    conversation_history: List[Conversation] = []
    conversation_history = [get_conversation_by_id(db, conversation_id)]  # 简化：仅查这一条
    # 如果你想要过去所有的历史记录，可根据你的逻辑 (e.g. get all messages by conversation_id)
    # 具体可看你的 db 结构和实现

    # 构造要发给 openai 的 messages
    # 假设数据库里只保存了 user 的最初对话(message)和 num_attachments。
    # 如果你要存多轮对话，需要在表里区分 role=“user” / “assistant”，
    # 并按时间顺序读取所有历史消息。
    openai_messages = []

    # 这里随意补充一个 developer/system 提示，也可不加
    openai_messages.append({
        "role": "developer",
        "content": "You are a helpful assistant. You provide text and vision analysis as needed."
    })

    # 1) 放进既有对话中的“用户消息”
    for conv in conversation_history:
        # 先把文字作为一个 user 消息
        if conv.message:
            openai_messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": conv.message
                    }
                ]
            })
        # 再把历史附件(如果需要)，也拼到 messages。若要全部附件做上下文，这里自行处理。
        attachments = get_attachments_by_conversation(db, conv.conv_id)
        for att in attachments:
            # 假设 att.file_path 代表本地文件，转成 public url
            # 这个地址必须保证 openai 能访问到。如果只是内网，可能不行。
            filename = os.path.basename(att.file_path)
            public_url = f"http://YOUR_DOMAIN/uploads/{filename}"
            openai_messages[-1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": public_url,
                    # 如果图像要高分辨率解析，可以设置 detail="high" 或 "low"
                    "detail": "auto"
                }
            })

    # 2) 本次新的 user 消息 + 上传的图片，拼到 messages
    # 如果用户的 text 不为空
    new_user_content = []
    if user_message.strip():
        new_user_content.append({"type": "text", "text": user_message.strip()})
    # 再把本次 upload 的图片，也拼到 content
    for img_url in image_urls_for_openai:
        new_user_content.append({
            "type": "image_url",
            "image_url": {
                "url": img_url,
                "detail": "auto"
            }
        })

    # 只有在新输入里确实有内容时才追加
    if new_user_content:
        openai_messages.append({
            "role": "user",
            "content": new_user_content
        })

    # 调用 OpenAI 的 Chat Completion 接口
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # 你可以换成 gpt-4o-mini 或其他
            messages=openai_messages,
            max_tokens=512,  # 你可根据情况调节
            temperature=0.7
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API call failed: {e}")

    # 获取assistant的回复文本
    assistant_reply_obj = response.choices[0].message  # role="assistant", content=[...]
    # assistant_reply_obj 可能是一个复杂的结构，需要你自行解析
    # 常见是 content=[{ "type": "text", "text": "..."} , ...]
    # 这里假设我们只关心文字部分，简单做一个拼接：
    final_text_reply = ""
    if isinstance(assistant_reply_obj.content, list):
        # 如果 content 是一个数组
        for part in assistant_reply_obj.content:
            if part.get("type") == "text":
                final_text_reply += part.get("text", "")
            # 如果是图像，assistant 也可能返回 image_url
    else:
        # 如果 content 直接是字符串
        final_text_reply = assistant_reply_obj.content

    # 将这条新的 assistant 回复，也保存进数据库(做多轮对话)
    # 这里示例直接复用 create_conversation，也可以建立一个“消息表”来区分每条信息
    new_assistant_conv = create_conversation(db, user_id=user_id or 0, message=final_text_reply)
    # 注意，如果你对数据库结构有更好的设计（比如 conversation 表只存对话元数据，另有 message 表存多条内容），
    # 需要根据你的实际情况保存。

    return {
        "conversation_id": conversation_id,
        "assistant_reply": final_text_reply,
        "openai_raw": response  # 如果想返回完整原始信息可放这里（注意可能泄漏敏感信息）
    }