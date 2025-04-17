from openai import OpenAI

client = OpenAI(
    base_url='https://api.deepseek.com/v1',
    api_key='sk-a57c7e36dd2945308f9934a11fb4e45f'  # 注意实际部署时记得用环境变量管理
)


def chat_with_condition(condition: str, input_text: str) -> bool:
    system_prompt = f"""你是一个判断助手，负责根据输入信息判断是否满足条件。判断条件是：“{condition}”。请只回答“是”或“否”。"""

    response = client.chat.completions.create(
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
    system_prompt = f"""你是一个聚合助手，负责将“{input_text}”按照“{aggregate_field}”求“{aggregate_type}”。输出聚合结果，只输出一个数字"""

    response = client.chat.completions.create(
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
    return aggregate_field + aggregate_type + "是" + reply