import os
from openai import OpenAI

def generate_llm_response(user_message, api_key, model="deepseek-chat"):
    """
    调用DeepSeek API生成LLM响应 - 使用OpenAI SDK
    
    Args:
        user_message: 用户输入的消息
        api_key: DeepSeek API密钥
        model: 使用的模型名称，默认deepseek-chat
        
    Returns:
        str: LLM生成的响应或错误信息
    """
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        print(f"[backend.chat_engine] 调用DeepSeek API处理消息：{user_message[:50]}...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个聊天伙伴，用自然口语化的方式回应，内容简洁，像真人聊天一样。请确保你的回答只能使用中文，绝对不能包含任何英文单词或字母。"},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )
        
        # 解析API响应
        bot_response = response.choices[0].message.content
        print(f"[backend.chat_engine] API响应成功: {bot_response[:50]}...")
        return bot_response
    except Exception as e:
        # 处理异常情况
        print(f"[backend.chat_engine] 生成响应时出错: {str(e)}")
        return f"生成响应时出错: {str(e)}"