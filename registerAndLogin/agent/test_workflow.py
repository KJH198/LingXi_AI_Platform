import os
import sys

# 设置 Django 环境变量
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registerAndLogin.settings')  # ← 替换为你的项目名

import django
django.setup()

from agent.models import Workflow
from agent.node import run_workflow_from_output_node

def main():
    workflow = Workflow.objects.get(id=3)  # 你想测试哪个 workflow 自己改 id
    result = run_workflow_from_output_node(workflow)
    print("最终输出节点的运行结果:", result)

if __name__ == "__main__":
    main()
