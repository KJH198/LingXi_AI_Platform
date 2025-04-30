import os
from dotenv import load_dotenv
from openai import OpenAI

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

def chat_with_condition(condition: str, input_text: str) -> bool:
    if isinstance(input_text, list):
        input_text = "\n".join(map(str, input_text))

    system_prompt = f"""你是一个判断助手，负责根据输入信息判断是否满足条件。判断条件是：“{condition}”。请只回答“是”或“否”。"""

    response = deepseek.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]
    )

    reply = response.choices[0].message.content.strip()
    print(condition)
    print(reply)
    return reply.startswith("是")

def chat_with_aggregate(aggregate_type: str, aggregate_field: str, input_text: str):
    if isinstance(input_text, list):
        input_text = "\n".join(map(str, input_text))
    print(input_text)
    system_prompt = f"""你是一个聚合助手，负责将“{input_text}”按照“{aggregate_field}”求“{aggregate_type}”。输出聚合结果，只输出一个数字"""

    response = deepseek.chat.completions.create(
        model="deepseek-chat",
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

def call_llm(model_type: str, system_prompt: str, input_text: str) -> str:
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

    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    if isinstance(input_text, list):
        input_text = "\n".join(map(str, input_text))
    if isinstance(system_prompt, list):
        system_prompt = "\n".join(map(str, system_prompt))

    # print(client)
    # print(model)
    # print(input_text)
    # print(system_prompt)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]
    )
    reply = response.choices[0].message.content.strip()
    # print(reply)
    return reply
