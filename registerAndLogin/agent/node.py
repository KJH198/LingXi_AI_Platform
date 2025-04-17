from .models import Node
from agent.llm import chat_with_condition, chat_with_aggregate


class BaseNode:
    def __init__(self, node: Node):
        self.node = node
        self.id = node.node_id
        self.type = node.node_type
        self.data = node.node_data
        self.predecessors = node.predecessors
        self.successors = node.successors

    def run(self, inputs, node_dict, results, handle):
        raise NotImplementedError("Each node must implement its own run method.")

class InputNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.input_type = "文本"  # 暂未传入，先这么设吧
        self.default_value = "家里来了十只猫"

    def run(self, inputs, node_dict, results, handle):
        return self.default_value


class OutputNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, results, handle):
        return inputs


class CodeNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, results, handle):
        code = self.data.get("code", "")
        print(f"[CodeNode] 执行代码块:\n{code}")
        # ⚠️ 后期可加 exec 安全沙箱执行逻辑


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

    def run(self, inputs, node_dict, results, handle):
        # print(handle)
        if isinstance(inputs, list):
            input_text = "\n".join(map(str, inputs))  # 将列表转换为字符串，每个元素换行
        else:
            input_text = str(inputs)  # 直接转换字符串

        matched = False
        if chat_with_condition(self.if_condition, input_text):
            matched = 'if'
        elif self.else_if_conditions:
            for idx, cond in enumerate(self.else_if_conditions):
                if chat_with_condition(cond, input_text):
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
                results[cache_key] = ""  # 分支未命中，传空

        cache_key = (self.id, handle)
        return results[cache_key]


class LoopNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, results, handle):
        loop_count = self.data.get("count", 1)
        print(f"[LoopNode] 循环执行 {loop_count} 次")
        # ⚠️ 可迭代执行其 successors


class IntentNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, results, handle):
        intent = self.data.get("intent", "unknown")
        print(f"[IntentNode] 识别意图: {intent}")
        # ⚠️ 可嵌入意图识别模块


class BatchNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)

    def run(self, inputs, node_dict, results, handle):
        items = self.data.get("items", [])
        print(f"[BatchNode] 批处理 {len(items)} 个元素")
        # ⚠️ 可用于并发/批量处理


class AggregateNode(BaseNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.aggregate_type = node.node_data.get('aggregateType', '')
        self.aggregate_field = node.node_data.get('aggregateField', '')

    def run(self, inputs, node_dict, results, handle):
        if isinstance(inputs, list):
            input_text = "\n".join(map(str, inputs))  # 将列表转换为字符串，每个元素换行
        else:
            input_text = str(inputs)  # 直接转换字符串
        return chat_with_aggregate(self.aggregate_type, self.aggregate_field, input_text)


node_type_map = {
    "input": InputNode,
    "output": OutputNode,
    "code": CodeNode,
    "selector": SelectorNode,
    "loop": LoopNode,
    "intent": IntentNode,
    "batch": BatchNode,
    "aggregate": AggregateNode,
}

def build_node_instance(node_model_instance):
    node_type = node_model_instance.node_type
    NodeClass = node_type_map.get(node_type)
    if NodeClass is None:
        raise ValueError(f"未知的节点类型: {node_type}")

    return NodeClass(node_model_instance)

def execute_node(node_id, node_dict, results, source_handle=None):
    # 判断是否已经执行过该节点（考虑 handle）
    cache_key = (node_id, source_handle)
    if cache_key in results:
        return results[cache_key]

    node_instance = node_dict[node_id]
    inputs = []

    for pred in node_instance.predecessors:
        pred_id = pred['source']
        pred_handle = pred['sourceHandle']  # 这个 pred 是当前节点的一个输入来源
        pred_output = execute_node(pred_id, node_dict, results, pred_handle) # 只要其中一个分支的输出
        inputs.append(pred_output)

    output = node_instance.run(inputs, node_dict, results, source_handle)
    results[cache_key] = output
    return output

def run_workflow_from_output_node(workflow):
    """
    从输出节点开始执行整个工作流
    :param output_node_id: 最终输出节点的 ID
    :param node_list: 所有 BaseNode 实例的列表
    :return: 最终输出节点的运行结果
    """
    # 加载所有节点，并创建实例
    node_dict = {
        node.node_id: build_node_instance(node)
        for node in Node.objects.filter(workflow=workflow)
    }

    # print(node_dict)

    # 初始化一个结果缓存字典
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
        result = execute_node(output_node_id, node_dict, results, source_handle)

        # 保存结果
        final_result[output_node_id] = result

    return final_result