import os
from dotenv import load_dotenv
from openai import OpenAI
import base64

load_dotenv()  # 加载 .env 文件

deepseek = OpenAI(
    base_url='https://api.deepseek.com/v1',
    api_key=os.getenv('DEEPSEEK_API_KEY')
)

qwen = OpenAI(
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=os.getenv('QWEN_API_KEY')
)

chatgpt = OpenAI(
    base_url='https://yibuapi.com/v1',
    api_key=os.getenv('CHATGPT_API_KEY')
)

claude = chatgpt

def chat_with_condition(condition: str, input_text: str, model) -> bool:
    if isinstance(input_text, list):
        input_text = "\n".join(map(str, input_text))

    system_prompt = f"""你是一个判断助手，负责根据输入信息判断是否满足条件。判断条件是：“{condition}”。请只回答“是”或“否”。"""

    client = select_client(model)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]
    )

    reply = response.choices[0].message.content.strip()
    print(condition)
    print(reply)
    return reply.startswith("是")

def chat_with_aggregate(aggregate_type: str, aggregate_field: str, input_text: str, model):
    if isinstance(input_text, list):
        input_text = "\n".join(map(str, input_text))
    print(input_text)
    system_prompt = f"""你是一个聚合助手，负责将“{input_text}”按照“{aggregate_field}”求“{aggregate_type}”。输出聚合结果，只输出一个数字"""

    client = select_client(model)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]
    )

    reply = response.choices[0].message.content.strip()
    print(aggregate_type)
    print(aggregate_field)
    print(reply)
    return reply

def deal_with_photo(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": "请总结图片内容"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]
    }]

    try:
        response = qwen.chat.completions.create(
            model="qwen-vl-plus",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("图片解析异常：", e)
        return "图片解析失败"


def call_llm(model_type: str, messages) -> str:
    if model_type == 'claude-3':
        model = "claude-3-5-haiku-20241022"
        client = claude

    elif model_type == 'gpt-3.5-turbo':
        model = "gpt-3.5-turbo"
        client = chatgpt

    elif model_type == 'gpt-4':
        model = "gpt-4o"
        client = chatgpt

    elif model_type == 'Qwen':
        model = "qwen-turbo"
        client = qwen

    elif model_type == 'deepseek':
        model = "deepseek-chat"
        client = deepseek

    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # print(client)
    # print(model)
    # print(input_text)
    # print(system_prompt)
    print("message",messages)
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    # print(reply)
    return reply

def select_client(model):
    if model == 'claude-3-5-haiku-20241022':
        client = claude
    elif model == 'gpt-4o':
        client = chatgpt
    elif model == 'deepseek-chat':
        client = deepseek
    else:
        client = qwen
    return client