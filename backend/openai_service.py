# openai_service.py
import os
from openai import OpenAI
from typing import List, Dict, Any

# 在环境变量或配置文件中存储你的 API Key，避免写死在代码中
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY")

# 初始化客户端
client = OpenAI(api_key=OPENAI_API_KEY)


def create_chat_completion(
    messages: List[Dict[str, Any]],
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    封装对OpenAI Chat Completions接口的调用。
    :param messages: 聊天消息列表，每条消息包含 role 和 content 等字段
    :param model: 选择的OpenAI模型
    :param temperature: 生成温度，越高输出越随机
    :param max_tokens: 最大生成长度
    :return: 返回模型生成的文本
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # OpenAI 返回的结构中，生成文本在 choices[0] 下
    # 这里直接返回第一个回答
    return response.choices[0].message.content


def create_image_analysis(
    messages: List[Dict[str, Any]],
    model: str = "gpt-4o-mini",
    max_tokens: int = 300
) -> str:
    """
    封装对带有Vision能力的OpenAI模型的调用。
    :param messages: 聊天消息列表，可能包含image_url
    :param model: Vision模型名称，如 gpt-4o-mini, gpt-4o
    :param max_tokens: 最大生成长度
    :return: 返回模型生成的文本
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content