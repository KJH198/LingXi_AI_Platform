from .models import Node, Workflow
import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


AGENT_CACHE = {}  # 你可以按用户 ID、会话 ID、agent_id 等作为 key

def set_agent(agent_id: int, user_id: int, agent):
    agent_key = (agent_id, user_id)
    AGENT_CACHE[agent_key] = agent

def get_agent(agent_id: int,user_id: int):
    agent_key = (agent_id, user_id)
    if agent_key in AGENT_CACHE:
        return AGENT_CACHE[agent_key]
    else:
        raise RuntimeError(f"No agent found for key: {agent_key}")

class Agent:
    def __init__(self, agent_id, user_id, workflow, general_model=None, knowledge_bases=None):
        self.agent_id = agent_id
        self.user_id = user_id
        self.workflow = workflow  # 可以是节点构成的DAG或列表
        self.general_model = general_model
        self.knowledge_bases = knowledge_bases or {}

        # 输入输出上下文
        self.static_inputs = {}
        self.pending_inputs = {}
        self.results = {}
        self.node_dict = {}

        self.global_count = 0  # 如果你有计数需求
        self.is_outer_agent = True

    def check_next_input(self):
        if self.pending_inputs:
            next_input_name = next(iter(self.pending_inputs))
            return {
                'hasNextInput': True,
                'nextInputName': next_input_name
            }
        else:
            return {
                'hasNextInput': False
            }

    def start_preview(self):
        nodes = Node.objects.filter(workflow=self.workflow, node_type='input')
        flag = nodes.exists()
        if not flag:  # 没有静态输入，直接调工作流
            print("reset")
            from agent.workflow import run_workflow_from_output_node
            run_workflow_from_output_node(self)

        return {
            'code': 200,
            'message': '预览模式启动成功',
            'data': {}
        }

@csrf_exempt
def check_next_input(request):
    if request.method == 'GET':
        try:
            agent_id = request.GET.get('agent_id')
            user_id = request.GET.get('userId')
            agent = get_agent(agent_id, user_id)
            result = agent.check_next_input()
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def start_preview(request):
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'message': '只支持 POST 请求',
            'data': {}
        }, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('userId')
        # agent_id = data.get('agent_id')
        agent_id = 0 #暂时把id传成0
        workflow_id = data.get('workflow_id')
        model_id = data.get('model_id')
        knowledge_bases = data.get('knowledge_bases', [])

        workflow = Workflow.objects.get(id=workflow_id)
        general_model = select_model(model_id)
        agent = Agent(agent_id, user_id, workflow, general_model, knowledge_bases)
        set_agent(agent_id,user_id, agent)  # ✅ 保存到缓存
        result = agent.start_preview()
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': {}
        }, status=500)

def select_model(model_id):
    if model_id == 'claude-3':
        model = "claude-3-5-haiku-20241022"

    elif model_id == 'gpt-4':
        model = "gpt-4o"

    elif model_id == 'deepseek':
        model = "deepseek-chat"

    else:
        model = "qwen-turbo"
    return model