from .models import Node, Workflow
from knowledge_base.models import KnowledgeBaseFile
from agent.llm import chat_with_condition, chat_with_aggregate, call_llm
import types

import websockets
import asyncio
import json
import time
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

static_inputs = {}  # 全局变量，保存所有静态输入
pending_inputs = {}  # 全局变量，存等待中的动态输入
global_count = 0
agent_id = None
workflow_id = None
general_model = None
knowledge_bases = None
results = {}


class BaseNode:
    def __init__(self, node: Node):
        self.node = node
        self.id = node.node_id
        self.type = node.node_type
        self.data = node.node_data
        self.predecessors = node.predecessors
        self.successors = node.successors

    async def run(self, inputs, node_dict, handle, count):
        raise NotImplementedError("Each node must implement its own run method.")

class InputNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.name = node.node_data.get('name', 'input')

    def run(self, inputs, node_dict, handle, count):
        print(f"读取静态输入: {self.name}")

        # 从全局 static_inputs 字典取出对应输入
        if self.name in static_inputs:
            static_input = static_inputs[self.name]
            print(f"静态输入 {self.name}: {static_input}")
            return static_input
        else:
            print(f"未找到静态输入 {self.name}，返回默认空字符串")
            return ''


@csrf_exempt
def submit_static_inputs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            inputs = data.get('inputs', [])
            print(inputs)

            # 存储静态输入到内存中
            for item in inputs:
                name = item.get('name')
                value = item.get('value')
                if name is not None:
                    static_inputs[name] = value

            # 获取工作流对象
            workflow = Workflow.objects.get(id=workflow_id, user_id=request.user.id)

            # 调用工作流执行函数
            run_workflow_from_output_node(workflow)

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


class DynamicInputNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.name = node.node_data.get('name', 'dynamic-input')

    def run(self, inputs, node_dict, handle, count):
        print(f"等待前端输入: {self.name}")

        # 第一步：通知前端需要输入
        asyncio.run(send_dynamic_request_to_frontend(self.name))

        # 第二步：创建线程事件，并记录在 pending_inputs 中
        event = threading.Event()
        pending_inputs[self.name] = (event, None)

        # 第三步：等待事件被 set，或超时
        if not event.wait(timeout=60):  # 最多等待30秒
            print("等待输入超时！")
            pending_inputs.pop(self.name, None)
            return None

        # 第四步：事件已 set，获取输入值
        _, value = pending_inputs.pop(self.name)
        print(f"收到前端输入: {value}")
        return value

@csrf_exempt
def submit_dynamic_input(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        input_name = data.get('input')
        input_value = data.get('variables')
        print(f"收到动态输入: {input_name} = {input_value}")

        if input_name in pending_inputs:
            event, _ = pending_inputs[input_name]
            pending_inputs[input_name] = (event, input_value)
            event.set()  # 唤醒等待线程
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'error': 'Input not pending'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


class OutputNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.name = node.node_data.get('name', 'output')

    def run(self, inputs, node_dict, handle, count):
        print(inputs)
        asyncio.run(send_output_to_frontend(self.name, inputs, count))
        return inputs


class MonitorNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.name = node.node_data.get('name', 'monitor')

    def run(self, inputs, node_dict, handle, count):
        asyncio.run(send_output_to_frontend(self.name, inputs, count))
        return inputs


async def send_output_to_frontend(node_name: str, output: any, count):
    channel_layer = get_channel_layer()
    payload = {
        "type": "output",
        "node_name": node_name,
        "output": output
    }
    # print(f"是否传往前端？")
    # print(f"golbal_count:", global_count)
    # print(f"count", count)
    if count == global_count:
        try:
            await channel_layer.group_send(
                "node_output",
                {
                    "type": "node.output",
                    "message": payload
                }
            )
            print(f"成功发送输出到前端: {node_name} : {output}")
        except Exception as e:
            print(f"发送输出到前端失败: {e}")



async def send_dynamic_request_to_frontend(node_name: str):
    channel_layer = get_channel_layer()
    payload = {
        "node_name": node_name,
        "type": "request_input"
    }
    try:
        await channel_layer.group_send(
            "node_output",
            {
                "type": "node.output",
                "message": payload
            }
        )
        print(f"成功动态输入需求到前端: {node_name}")
    except Exception as e:
        print(f"发送动态输入需求到前端失败: {e}")


class CodeNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.code_content = node.node_data.get('codeContent', '')

    def run(self, inputs, node_dict, handle, count):
        print(inputs)
        try:
            # 准备执行环境
            local_env = {}
            # 执行用户代码
            exec(self.code_content, {}, local_env)

            # 找出用户写的函数（第一个是 function 的变量）
            user_func = None
            for val in local_env.values():
                if isinstance(val, types.FunctionType):
                    user_func = val
                    break

            if user_func is None:
                raise ValueError("未检测到用户定义的函数")

            # 执行用户函数
            result = user_func(inputs)

            return result

        except Exception as e:
            return f"执行代码节点时出错：{e}"


class SelectorNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.if_condition = node.node_data.get('ifCondition', '')
        self.else_if_conditions = node.node_data.get('elseIfConditions', [])
        self.else_condition = node.node_data.get('elseCondition', '')

    @staticmethod
    def get_source_handle(source_id, target_node):
        for pred in target_node.predecessors:
            if pred['source'] == source_id:
                return pred.get('sourceHandle')
        return None  # fallback

    def run(self, inputs, node_dict, handle, count):
        # print(handle)
        if isinstance(inputs, list):
            input_text = "\n".join(map(str, inputs))  # 将列表转换为字符串，每个元素换行
        else:
            input_text = str(inputs)  # 直接转换字符串

        matched = False
        if chat_with_condition(self.if_condition, input_text, general_model):
            matched = 'if'
        elif self.else_if_conditions:
            for idx, cond in enumerate(self.else_if_conditions):
                if chat_with_condition(cond, input_text, general_model):
                    matched = f'elseif-{idx}'
                    break
        if not matched:
            matched = 'else'

        for suc in self.successors:
            target_id = suc['target']
            source_handle = self.get_source_handle(self.id, node_dict[target_id])
            # print(source_handle)

            cache_key = (self.id, source_handle)
            if source_handle == matched:
                results[cache_key] = input_text  # 分支命中，传值
            else:
                results[cache_key] = None  # 分支未命中，传空

        cache_key = (self.id, handle)
        return results[cache_key]


class LoopNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.loop_type = node.node_data.get('loopType', '')
        self.loop_count = node.node_data.get('loopCount', '')
        self.loop_condition = node.node_data.get('loopCondition', '')

    def run(self, inputs, node_dict, handle, count):
        return inputs


class IntentNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, handle, count):
        # print(inputs)
        return inputs


class BatchNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.loop_type = 'fixed'
        self.loop_count = 1
        self.inputs = ''

    def run(self, inputs, node_dict, handle, count):
        self.inputs = inputs
        # print("批处理")
        # print(inputs)
        return inputs
        # ⚠️ 可用于并发/批量处理


class AggregateNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.aggregate_type = node.node_data.get('aggregateType', '')
        self.aggregate_field = node.node_data.get('aggregateField', '')

    def run(self, inputs, node_dict, handle, count):
        if isinstance(inputs, list):
            input_text = "\n".join(map(str, inputs))  # 将列表转换为字符串，每个元素换行
        else:
            input_text = str(inputs)  # 直接转换字符串
        return chat_with_aggregate(self.aggregate_type, self.aggregate_field, input_text, general_model)


class LLMNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.llm_model = node.node_data.get('llmModel', '')
        self.llm_prompt = node.node_data.get('llmPrompt', '')
        self.llm_knowledge = send_kb_files_to_llm(knowledge_bases) if knowledge_bases else ""
        self.llm_messages = [
            {"role": "system", "content": self.llm_prompt + self.llm_knowledge},
        ]

    def run(self, inputs, node_dict, handle, count):
        input_text = inputs
        if isinstance(input_text, list):
            input_text = "\n".join(map(str, input_text))
        self.llm_messages.append({"role": "user", "content": input_text})
        reply = call_llm(self.llm_model, self.llm_messages)
        self.llm_messages.append({"role": "assistant", "content": reply})
        return reply


class WorkflowNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, handle, count):
        return inputs


node_type_map = {
    "input": InputNode,
    "dynamic-input": DynamicInputNode,
    "output": OutputNode,
    "code": CodeNode,
    "selector": SelectorNode,
    "loop": LoopNode,
    "intent": IntentNode,
    "batch": BatchNode,
    "aggregate": AggregateNode,
    "llm": LLMNode,
    "workflow": WorkflowNode,
    "monitor": MonitorNode,
}


def build_node_instance(node_model_instance):
    node_type = node_model_instance.node_type
    NodeClass = node_type_map.get(node_type)
    if NodeClass is None:
        raise ValueError(f"未知的节点类型: {node_type}")

    return NodeClass(node_model_instance)


def execute_node(node_id, node_dict, count, source_handle=None, is_loop=False):
    cache_key = (node_id, source_handle)
    if cache_key in results:
        print("在result里")
        print(results[cache_key])
        return results[cache_key]

    if count != global_count:
        # print(f"count:", count)
        # print(f"global_count:", global_count)
        return

    node_instance = node_dict[node_id]
    inputs = []
    normal_preds = []
    loop_pred = None
    pred_output = ''

    if node_instance.type == 'batch' or node_instance.type == 'loop':
        for pred in node_instance.predecessors:
            pred_id = pred['source']
            pred_node = node_dict[pred_id]
            is_loop = any(
                succ['target'] == node_id and (
                            succ['targetHandle'] == 'batch-exit' or succ['targetHandle'] == 'loop-exit')
                for succ in pred_node.successors
            )
            if is_loop:
                loop_pred = pred
            else:
                normal_preds.append(pred)
    else:
        normal_preds = node_instance.predecessors

    for pred in normal_preds:
        pred_id = pred['source']
        pred_handle = pred['sourceHandle']  # 这个 pred 是当前节点的一个输入来源
        pred_output = execute_node(pred_id, node_dict, count, pred_handle, is_loop)  # 只要其中一个分支的输出
        inputs.append(pred_output)

    if inputs == [None]:
        return None
    output = node_instance.run(inputs, node_dict, source_handle, count)

    if loop_pred and node_instance.type == 'loop':
        if node_instance.loop_type == 'fixed':
            for i in range(node_instance.loop_count):
                output = execute_loop(loop_pred['source'], node_dict, output, count)
        else:
            loop_counter = 0
            while chat_with_condition(node_instance.loop_condition, output, general_model) and loop_counter < 100:  # 防止死循环
                output = execute_loop(loop_pred['source'], node_dict, output, count)
                loop_counter += 1

    if loop_pred and node_instance.type == 'batch':
        output = execute_batch(loop_pred['source'], node_dict, output, count)

    if not is_loop:
        results[cache_key] = output
    return output


def execute_batch(current_id, node_dict, inputs, count):
    if count != global_count:
        # print(f"count:", count)
        # print(f"global_count:", global_count)
        return
    current_node = node_dict[current_id]

    for pred in current_node.predecessors:
        pred_id = pred['source']
        pred_handle = pred['sourceHandle']
        if pred_handle == 'batch-entry':
            # 找到批处理入口，使用 inputs 执行该入口节点
            # print(f"[Entry] 执行 {current_node.type} {current_id}")
            outputs = []
            for single_input in inputs:
                # print("这是一条输入")
                # print(single_input)
                if single_input is None:
                    output = None
                else:
                    output = current_node.run(single_input, node_dict, pred_handle, count)
                outputs.append(output)
            return outputs

        else:
            # 先递归执行上一个节点（一路向上）
            prev_output = execute_batch(pred_id, node_dict, inputs, count)
            # 再用上一个节点的输出执行当前节点
            # print(f"[Loop Step] 执行 {current_node.type} {current_id}")
            outputs = []
            for single_prev_input in prev_output:
                # print("这是一条输入")
                # print(single_prev_input)
                if single_prev_input is None:
                    output = None
                else:
                    output = current_node.run(single_prev_input, node_dict, pred_handle, count)
                outputs.append(output)
            return outputs

    return None


def execute_loop(current_id, node_dict, inputs, count):
    if count != global_count:
        # print(f"count:", count)
        # print(f"global_count:", global_count)
        return
    current_node = node_dict[current_id]

    for pred in current_node.predecessors:
        pred_id = pred['source']
        pred_handle = pred['sourceHandle']

        if pred_handle == 'loop-entry':
            # 找到批处理入口，使用 inputs 执行该入口节点
            print(f"[Entry] 执行 {current_node.type} {current_id}")
            output = current_node.run(inputs, node_dict, pred_handle, count)
            if len(current_node.predecessors) > 1:  # 有不止一个前驱
                normal_inputs = []
                for normal_pred in current_node.predecessors:
                    normal_pred_id = normal_pred['source']
                    normal_pred_handle = normal_pred['sourceHandle']
                    if normal_pred_handle != 'loop-entry':  # 遍历其余前驱
                        print(f"normal_pred:", normal_pred)
                        normal_pred_output = execute_node(normal_pred_id, node_dict, count, normal_pred_handle, True)
                        normal_inputs.append(normal_pred_output)
                        output = current_node.run(normal_inputs, node_dict, normal_pred_handle, count)
            print(output)
            return output
        else:
            # 先递归执行上一个节点（一路向上）
            prev_output = execute_loop(pred_id, node_dict, inputs, count)

            # 再用上一个节点的输出执行当前节点
            print(f"[Loop Step] 执行 {current_node.type} {current_id}")
            output = current_node.run(prev_output, node_dict, pred_handle, count)
            print(output)
            return output

    return None  # fallback：未找到入口


def run_workflow_from_output_node(workflow):
    """
    从输出节点开始执行整个工作流
    :param output_node_id: 最终输出节点的 ID
    :param node_list: 所有 BaseNode 实例的列表
    :return: 最终输出节点的运行结果
    """
    global global_count
    global_count += 1
    # 加载所有节点，并创建实例
    node_dict = {
        node.node_id: build_node_instance(node)
        for node in Node.objects.filter(workflow=workflow)
    }

    # print(node_dict)

    # 初始化一个结果缓存字典
    global results
    results = {}

    # 找到类型为 output 的节点
    output_nodes = Node.objects.filter(workflow=workflow, node_type='output')

    final_result = {}

    # 遍历所有输出节点
    for output_node in output_nodes:
        output_node_id = output_node.node_id

        # 获取前驱连接的 sourceHandle，假设每个 output 节点有一个前驱
        source_handle = output_node.predecessors[0].get('sourceHandle')

        # 递归执行
        result = execute_node(output_node_id, node_dict, global_count, source_handle, False)

        # 保存结果
        final_result[output_node_id] = result

    return final_result


@csrf_exempt
def check_next_input(request):
    if request.method == 'GET':
        try:
            # 检查是否有待处理的动态输入
            if pending_inputs:
                # 获取第一个待处理的输入
                next_input_name = next(iter(pending_inputs))
                return JsonResponse({
                    'hasNextInput': True,
                    'nextInputName': next_input_name
                })
            else:
                return JsonResponse({
                    'hasNextInput': False
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def start_preview(request):
    global agent_id, workflow_id, general_model, knowledge_bases
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'message': '只支持 POST 请求',
            'data': {}
        }, status=405)

    try:
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        workflow_id = data.get('workflow_id')
        model_id = data.get('model_id')
        knowledge_bases = data.get('knowledge_bases', [])

        workflow = Workflow.objects.get(id=workflow_id)
        nodes = Node.objects.filter(workflow=workflow, node_type='input')
        general_model = select_model(model_id)

        flag = False
        for node in nodes:
            node_type = node.node_type
            if node_type == 'input':
                flag = True
                break
        if flag is False:  # 没有静态输入，直接调工作流
            print("reset")
            run_workflow_from_output_node(workflow)

        return JsonResponse({
            'code': 200,
            'message': '预览模式启动成功',
            'data': {}  # 有具体返回内容可以填进来
        })

    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': {}
        }, status=500)

def send_kb_files_to_llm(knowledge_bases):
    # 取出这些知识库下的所有文件
    # print(f"knowledge_base:", knowledge_bases)
    files = KnowledgeBaseFile.objects.filter(knowledge_base_id__in=knowledge_bases)
    # print(f"files:",files)
    # 读取文件内容
    all_text = ''
    for f in files:
        file_path = f.file.path
        # print(f"filepath:",file_path)
        with open(file_path, 'r', encoding='utf-8') as file_obj:
            content = file_obj.read()
            all_text += f"\n--- 文件: {f.filename} ---\n" + content
    # print(f"all_text:", all_text)
    return all_text

def select_model(model_id):
    if model_id == 'claude-3':
        model = "claude-3-5-haiku-20241022"

    elif model_id == 'gpt-4':
        model = "gpt-4o"

    else:
        model = "qwen-turbo"
    return model