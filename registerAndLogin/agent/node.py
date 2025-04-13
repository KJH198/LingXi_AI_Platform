from .models import Node

class BaseNode:
    def __init__(self, node: Node):
        self.node = node
        self.id = node.node_id
        self.type = node.node_type
        self.data = node.data        # 暂时没有传入，之后补充
        self.predecessors = node.predecessors
        self.successors = node.successors

    def run(self):
        raise NotImplementedError("Each node must implement its own run method.")

class InputNode(BaseNode):
    def run(self):
        label = self.data.get("label", "input")
        print(f"[InputNode] 收集输入: {label}")


class OutputNode(BaseNode):
    def run(self):
        print(f"[OutputNode] 输出数据: {self.data}")


class CodeNode(BaseNode):
    def run(self):
        code = self.data.get("code", "")
        print(f"[CodeNode] 执行代码块:\n{code}")
        # ⚠️ 后期可加 exec 安全沙箱执行逻辑


class SelectorNode(BaseNode):
    def run(self):
        conditions = self.data.get("conditions", [])
        print(f"[SelectorNode] 执行选择逻辑，条件列表: {conditions}")
        # ⚠️ 可根据条件决定走哪个 successor


class LoopNode(BaseNode):
    def run(self):
        loop_count = self.data.get("count", 1)
        print(f"[LoopNode] 循环执行 {loop_count} 次")
        # ⚠️ 可迭代执行其 successors


class IntentNode(BaseNode):
    def run(self):
        intent = self.data.get("intent", "unknown")
        print(f"[IntentNode] 识别意图: {intent}")
        # ⚠️ 可嵌入意图识别模块


class BatchNode(BaseNode):
    def run(self):
        items = self.data.get("items", [])
        print(f"[BatchNode] 批处理 {len(items)} 个元素")
        # ⚠️ 可用于并发/批量处理


class AggregateNode(BaseNode):
    def run(self):
        variables = self.data.get("variables", [])
        print(f"[AggregateNode] 聚合变量: {variables}")
        # ⚠️ 聚合上下文中的多个变量为一个输出


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