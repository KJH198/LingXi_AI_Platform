from .models import Node, Workflow
from knowledge_base.models import KnowledgeBaseFile
from user.models import PublishedAgent
from agent.llm import chat_with_condition, chat_with_aggregate, deal_with_photo, call_llm
from agent.agent import get_agent, Agent, select_model
from pathlib import Path
import types
import fitz
import re
import websockets
import asyncio
import json
import time
import threading
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from docx import Document  # 处理 docx


class BaseNode:
    def __init__(self, node: Node, agent):
        self.node = node
        self.id = node.node_id
        self.type = node.node_type
        self.data = node.node_data
        self.predecessors = node.predecessors
        self.successors = node.successors
        self.agent = agent

    async def run(self, inputs, handle, count):
        raise NotImplementedError("Each node must implement its own run method.")

class InputNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.name = node.node_data.get('name', 'input')

    def run(self, inputs, handle, count):
        print(f"读取静态输入: {self.name}")

        # 从全局 static_inputs 字典取出对应输入
        if self.name in self.agent.static_inputs:
            static_input = self.agent.static_inputs[self.name]
            print(f"静态输入 {self.name}: {static_input}")
            return static_input
        else:
            print(f"未找到静态输入 {self.name}，返回默认空字符串")
            return ''


@csrf_exempt
def submit_static_inputs(request, workflow_id0 = None):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            user_id = data.get('userId')
            agent_id = 0
            agent = get_agent(agent_id, user_id)
            inputs = data.get('inputs', [])
            print(inputs)

            # 存储静态输入到内存中
            for item in inputs:
                name = item.get('name')
                value = item.get('value')
                if name is not None:
                    agent.static_inputs[name] = value

            # 获取工作流对象
            # 如果没有传入 workflow_id，则使用全局变量
            if workflow_id0 is not None:
                agent.workflow = Workflow.objects.get(id=workflow_id0)

            # 调用工作流执行函数
            run_workflow_from_output_node(agent)

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


class DynamicInputNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.name = node.node_data.get('name', 'dynamic-input')

    def run(self, inputs, handle, count):
        print(f"等待前端输入: {self.name}")

        # 第一步：通知前端需要输入
        asyncio.run(send_dynamic_request_to_frontend(self.name))

        # 第二步：创建线程事件，并记录在 pending_inputs 中
        event = threading.Event()
        self.agent.pending_inputs[self.name] = (event, None)

        # 第三步：等待事件被 set，或超时
        if not event.wait(timeout=60):  # 最多等待30秒
            print("等待输入超时！")
            self.agent.pending_inputs.pop(self.name, None)
            return None

        # 第四步：事件已 set，获取输入值
        _, value = self.agent.pending_inputs.pop(self.name)
        print(f"收到前端输入: {value}")
        return value

@csrf_exempt
def submit_dynamic_input(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        input_name = data.get('input')
        input_value = data.get('variables')
        user_id = data.get('userId')
        agent_id = 0
        agent = get_agent(agent_id, user_id)
        print(f"收到动态输入: {input_name} = {input_value}")

        if input_name in agent.pending_inputs:
            event, _ = agent.pending_inputs[input_name]
            agent.pending_inputs[input_name] = (event, input_value)
            event.set()  # 唤醒等待线程
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'error': 'Input not pending'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


class OutputNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.name = node.node_data.get('name', 'output')

    def run(self, inputs, handle, count):
        # print(inputs)
        # print(f"[运行智能体] agent_id={self.agent.agent_id}, is_outer_agent={self.agent.is_outer_agent}")
        if self.agent.is_outer_agent:
            asyncio.run(send_output_to_frontend(self.name, inputs, self.agent, count))
        return inputs


class MonitorNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.name = node.node_data.get('name', 'monitor')

    def run(self, inputs, handle, count):
        asyncio.run(send_output_to_frontend(self.name, inputs, self.agent, count))
        return inputs


async def send_output_to_frontend(node_name: str, output: any, agent, count):
    channel_layer = get_channel_layer()
    payload = {
        "type": "output",
        "node_name": node_name,
        "output": output
    }
    # print(f"是否传往前端？")
    # print(f"golbal_count:", global_count)
    # print(f"count", count)
    if count == agent.global_count:
        try:
            await channel_layer.group_send(
                "node_output",
                {
                    "type": "node.output",
                    "message": payload,
                    "userId": agent.user_id
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
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.code_content = node.node_data.get('codeContent', '')

    def run(self, inputs, handle, count):
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
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.if_condition = node.node_data.get('ifCondition', '')
        self.else_if_conditions = node.node_data.get('elseIfConditions', [])
        self.else_condition = node.node_data.get('elseCondition', '')

    @staticmethod
    def get_source_handle(source_id, target_node):
        for pred in target_node.predecessors:
            if pred['source'] == source_id:
                return pred.get('sourceHandle')
        return None  # fallback

    def run(self, inputs, handle, count):
        # print(handle)
        if isinstance(inputs, list):
            input_text = "\n".join(map(str, inputs))  # 将列表转换为字符串，每个元素换行
        else:
            input_text = str(inputs)  # 直接转换字符串

        matched = False
        if chat_with_condition(self.if_condition, input_text, self.agent.general_model):
            matched = 'if'
        elif self.else_if_conditions:
            for idx, cond in enumerate(self.else_if_conditions):
                if chat_with_condition(cond, input_text, self.agent.general_model):
                    matched = f'elseif-{idx}'
                    break
        if not matched:
            matched = 'else'

        for suc in self.successors:
            target_id = suc['target']
            source_handle = self.get_source_handle(self.id, self.agent.node_dict[target_id])
            # print(source_handle)

            cache_key = (self.id, source_handle)
            if source_handle == matched:
                self.agent.results[cache_key] = input_text  # 分支命中，传值
            else:
                self.agent.results[cache_key] = None  # 分支未命中，传空

        cache_key = (self.id, handle)
        return self.agent.results[cache_key]


class LoopNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.loop_type = node.node_data.get('loopType', '')
        self.loop_count = node.node_data.get('loopCount', '')
        self.loop_condition = node.node_data.get('loopCondition', '')

    def run(self, inputs, handle, count):
        return inputs


class BatchNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.loop_type = 'fixed'
        self.loop_count = 1
        self.inputs = ''

    def run(self, inputs, handle, count):
        self.inputs = inputs
        # print("批处理")
        # print(inputs)
        return inputs
        # ⚠️ 可用于并发/批量处理


class AggregateNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.aggregate_type = node.node_data.get('aggregateType', '')
        self.aggregate_field = node.node_data.get('aggregateField', '')

    def run(self, inputs, handle, count):
        if isinstance(inputs, list):
            input_text = "\n".join(map(str, inputs))  # 将列表转换为字符串，每个元素换行
        else:
            input_text = str(inputs)  # 直接转换字符串
        return chat_with_aggregate(self.aggregate_type, self.aggregate_field, input_text, self.agent.general_model)


class LLMNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.llm_model = node.node_data.get('llmModel', '')
        self.llm_prompt = node.node_data.get('llmPrompt', '')
        if agent.is_outer_agent:
            self.llm_knowledge = send_kb_files_to_llm(self.agent.knowledge_bases) if self.agent.knowledge_bases else ""
        else:
            self.llm_knowledge = send_kb_files_to_llm(
                self.agent.knowledge_bases.all()) if self.agent.knowledge_bases.exists() else ""
        self.llm_messages = [
            {"role": "system", "content": self.llm_prompt + self.llm_knowledge},
        ]

    def run(self, inputs, handle, count):
        input_text = inputs
        if isinstance(input_text, list):
            input_text = "\n".join(map(str, input_text))
        self.llm_messages.append({"role": "user", "content": input_text})
        reply = call_llm(self.llm_model, self.llm_messages)
        self.llm_messages.append({"role": "assistant", "content": reply})
        return reply


class AgentNode(BaseNode):
    def __init__(self, node: Node, agent):
        super().__init__(node, agent)
        self.inner_agent_id = node.node_data.get('AgentID')
        self.internal_to_external_id = {} # {内部输入节点名：外部输入节点id}
        self.external_id_to_inputs = {} # {外部输入节点id：输入内容}
        self.internal_id_to_outputs = {} # {内部输出节点id：输出内容}
        self.internal_to_outputs = {} # {内部输出节点名：输出内容}

    @staticmethod
    def get_source_handle(source_id, target_node):
        for pred in target_node.predecessors:
            if pred['source'] == source_id:
                return pred.get('sourceHandle')
        return None  # fallback

    def run(self, inputs, handle, count):
        # 从数据库加载 inner_agent 的信息，并构建 Agent 实例
        if self.inner_agent_id:
            try:
                agent_model = PublishedAgent.objects.get(id=self.inner_agent_id)
                workflow = Workflow.objects.get(id=agent_model.workflow_id)

                self.inner_agent = Agent(
                    agent_id=agent_model.id,
                    user_id=self.agent.user_id,
                    workflow=workflow,
                    general_model=select_model(agent_model.model_id),
                    knowledge_bases=agent_model.knowledge_bases,
                )
                print(f"智能体节点输入：",inputs)
                self.inner_agent.static_inputs={}  # {内部输入节点名：输入内容}
                self.inner_agent.pending_inputs={}
                self.inner_agent.results={}
                self.inner_agent.global_count=0
                self.inner_agent.is_outer_agent=False  # 明确标记为内部智能体

                print(f"[调试] 智能体节点 {self.id} 开始执行 run()")

                # 1. 找到当前智能体节点对象（本身）
                current_node = self.agent.node_dict[self.id]

                # 2. 获取所有前驱节点 ID（这些是外部传进来的数据来源）
                predecessors = current_node.predecessors or []  # list of dicts
                input_node_ids = [pred["source"] for pred in predecessors]

                # 3. 遍历这些前驱节点，找到连向当前智能体节点的 targetHandle（输入名）
                self.internal_to_external_id = {}  # 清空

                for pred_id in input_node_ids:
                    pred_node = self.agent.node_dict.get(pred_id)
                    if not pred_node:
                        continue

                    # 在 pred_node.successors 中查找连到当前 workflow 的那条边
                    for succ in pred_node.successors:
                        if succ["target"] == self.id:
                            raw_name = succ["targetHandle"]  # 例如 input-内部输入1
                            match = re.match(r'^[a-zA-Z]+-(.+)', raw_name)
                            if not match:
                                continue
                            cleaned_name = match.group(1)  # 内部输入1
                            self.internal_to_external_id[cleaned_name] = pred_id
                            break

                # print("\n[调试] self.internal_to_external_id（内部输入名 → 外部输入节点ID）:")
                # for internal_name, external_id in self.internal_to_external_id.items():
                #     print(f"  {internal_name}  -->  {external_id}")
                #
                # print("\n[调试] self.external_id_to_inputs（外部输入节点ID → 输入内容）:")
                # for external_id, input_value in self.external_id_to_inputs.items():
                #     print(f"  {external_id}  -->  {input_value}")

                self.inner_agent.static_inputs = {
                    internal_name: self.external_id_to_inputs[external_id]
                    for internal_name, external_id in self.internal_to_external_id.items()
                    if external_id in self.external_id_to_inputs  # 安全判断，防止缺失
                }

                # print(f"[调试] 构造 inner_agent.static_inputs: {self.inner_agent.static_inputs}")
                # print(f"[运行智能体] agent_id={self.inner_agent.agent_id}, is_outer_agent={self.inner_agent.is_outer_agent}")

                self.internal_id_to_outputs = run_workflow_from_output_node(self.inner_agent)
                for internal_id in self.internal_id_to_outputs:
                    internal_output_node = self.inner_agent.node_dict[internal_id]
                    internal_name = internal_output_node.node.node_data.get('name')
                    self.internal_to_outputs[internal_name] = self.internal_id_to_outputs[internal_id]

                for suc in self.successors:
                    target_id = suc['target']
                    source_handle = self.get_source_handle(self.id, self.agent.node_dict[target_id])
                    # print(source_handle)
                    raw_name = source_handle # 例如 input-内部输入1
                    match = re.match(r'^[a-zA-Z]+-(.+)', raw_name)
                    if not match:
                        continue
                    cleaned_name = match.group(1)  # 内部输入1

                    cache_key = (self.id, source_handle)
                    self.agent.results[cache_key] = self.internal_to_outputs[cleaned_name]

                cache_key = (self.id, handle)
                return self.agent.results[cache_key]

            except Exception as e:
                traceback.print_exc()
                print(f"无法加载内部智能体 {self.inner_agent_id}：{e}")
                self.inner_agent = None
        else:
            self.inner_agent = None



node_type_map = {
    "input": InputNode,
    "dynamic-input": DynamicInputNode,
    "output": OutputNode,
    "code": CodeNode,
    "selector": SelectorNode,
    "loop": LoopNode,
    "batch": BatchNode,
    "aggregate": AggregateNode,
    "llm": LLMNode,
    "workflow": AgentNode,
    "monitor": MonitorNode,
}


def build_node_instance(node_model_instance, agent):
    node_type = node_model_instance.node_type
    NodeClass = node_type_map.get(node_type)
    if NodeClass is None:
        raise ValueError(f"未知的节点类型: {node_type}")

    return NodeClass(node_model_instance, agent)


def execute_node(node_id, count, source_handle=None, agent=None, is_loop=False):
    cache_key = (node_id, source_handle)
    if cache_key in agent.results:
        print("在result里")
        print(agent.results[cache_key])
        return agent.results[cache_key]

    if count != agent.global_count:
        # print(f"count:", count)
        # print(f"global_count:", global_count)
        return

    node_instance = agent.node_dict[node_id]
    inputs = []
    normal_preds = []
    loop_pred = None
    pred_output = ''

    if node_instance.type == 'batch' or node_instance.type == 'loop':
        for pred in node_instance.predecessors:
            pred_id = pred['source']
            pred_node = agent.node_dict[pred_id]
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
        pred_output = execute_node(pred_id, count, pred_handle, agent, is_loop)  # 只要其中一个分支的输出
        inputs.append(pred_output)
        if node_instance.type == 'workflow':
            node_instance.external_id_to_inputs[pred_id] = pred_output

    if inputs == [None]:
        return None
    output = node_instance.run(inputs, source_handle, count)

    if node_instance.type == 'workflow':
        print("智能体节点的输出：",output)

    if loop_pred and node_instance.type == 'loop':
        if node_instance.loop_type == 'fixed':
            for i in range(node_instance.loop_count):
                output = execute_loop(loop_pred['source'], output, agent, count)
        else:
            loop_counter = 0
            while chat_with_condition(node_instance.loop_condition, output, agent.general_model) and loop_counter < 100:  # 防止死循环
                output = execute_loop(loop_pred['source'], output, agent, count)
                loop_counter += 1

    if loop_pred and node_instance.type == 'batch':
        output = execute_batch(loop_pred['source'], output, agent, count)

    if not is_loop:
        agent.results[cache_key] = output
    return output


def execute_batch(current_id, inputs, agent, count):
    if count != agent.global_count:
        # print(f"count:", count)
        # print(f"global_count:", global_count)
        return
    current_node = agent.node_dict[current_id]

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
                    output = current_node.run(single_input, pred_handle, count)
                outputs.append(output)
            return outputs

        else:
            # 先递归执行上一个节点（一路向上）
            prev_output = execute_batch(pred_id, inputs, agent, count)
            # 再用上一个节点的输出执行当前节点
            # print(f"[Loop Step] 执行 {current_node.type} {current_id}")
            outputs = []
            for single_prev_input in prev_output:
                # print("这是一条输入")
                # print(single_prev_input)
                if single_prev_input is None:
                    output = None
                else:
                    output = current_node.run(single_prev_input, pred_handle, count)
                outputs.append(output)
            return outputs

    return None


def execute_loop(current_id, inputs, agent, count):
    if count != agent.global_count:
        # print(f"count:", count)
        # print(f"global_count:", global_count)
        return
    current_node = agent.node_dict[current_id]

    for pred in current_node.predecessors:
        pred_id = pred['source']
        pred_handle = pred['sourceHandle']

        if pred_handle == 'loop-entry':
            # 找到批处理入口，使用 inputs 执行该入口节点
            print(f"[Entry] 执行 {current_node.type} {current_id}")
            output = current_node.run(inputs, pred_handle, count)
            if len(current_node.predecessors) > 1:  # 有不止一个前驱
                normal_inputs = []
                for normal_pred in current_node.predecessors:
                    normal_pred_id = normal_pred['source']
                    normal_pred_handle = normal_pred['sourceHandle']
                    if normal_pred_handle != 'loop-entry':  # 遍历其余前驱
                        print(f"normal_pred:", normal_pred)
                        normal_pred_output = execute_node(normal_pred_id, count, normal_pred_handle, agent, True)
                        normal_inputs.append(normal_pred_output)
                        output = current_node.run(normal_inputs, normal_pred_handle, count)
            print(output)
            return output
        else:
            # 先递归执行上一个节点（一路向上）
            prev_output = execute_loop(pred_id, inputs, agent, count)

            # 再用上一个节点的输出执行当前节点
            print(f"[Loop Step] 执行 {current_node.type} {current_id}")
            output = current_node.run(prev_output, pred_handle, count)
            print(output)
            return output

    return None  # fallback：未找到入口


def run_workflow_from_output_node(agent):
    """
    从输出节点开始执行整个工作流
    :param output_node_id: 最终输出节点的 ID
    :param node_list: 所有 BaseNode 实例的列表
    :return: 最终输出节点的运行结果
    """
    agent.global_count += 1
    workflow = agent.workflow
    # 加载所有节点，并创建实例
    agent.node_dict = {
        node.node_id: build_node_instance(node, agent)
        for node in Node.objects.filter(workflow=workflow)
    }

    # print(node_dict)

    # 找到类型为 output 的节点
    output_nodes = Node.objects.filter(workflow=workflow, node_type='output')

    final_result = {}

    # 遍历所有输出节点
    for output_node in output_nodes:
        output_node_id = output_node.node_id

        # 获取前驱连接的 sourceHandle，假设每个 output 节点有一个前驱
        source_handle = output_node.predecessors[0].get('sourceHandle')

        # 递归执行
        result = execute_node(output_node_id, agent.global_count, source_handle, agent, False)

        # 保存结果
        final_result[output_node_id] = result

    return final_result

def send_kb_files_to_llm(knowledge_bases):
    # 取出这些知识库下的所有文件
    # print(f"knowledge_base:", knowledge_bases)
    files = KnowledgeBaseFile.objects.filter(knowledge_base_id__in=knowledge_bases)
    # print(f"files:",files)
    # 读取文件内容
    all_text = ''
    for f in files:
        file_path = f.file.path
        suffix = Path(file_path).suffix.lower()
        print(f"suffix:", suffix)

        # 根据文件后缀判断处理方式
        if suffix in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as file_obj:
                content = file_obj.read()
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            content = deal_with_photo(file_path)
        elif suffix == '.pdf':
            content = deal_with_pdf(file_path)
        elif suffix == '.docx':
            content = deal_with_docx(file_path)
        else:
            content = f"[不支持的文件类型：{suffix}]"

        all_text += f"\n--- 文件: {f.filename} ---\n{content}"
        print(all_text)
    return all_text

def deal_with_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def deal_with_docx(file_path):
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])