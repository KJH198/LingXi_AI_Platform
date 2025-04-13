from django.db import models
from django.conf import settings

class Agent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agents')
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique=True)  # 智能体名称唯一？
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Workflow(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='workflows', null=True, blank=True) #暂时允许为空
    created_at = models.DateTimeField(auto_now_add=True)
    structure = models.JSONField(default=dict)
    name = models.CharField(max_length=255, unique=True)  # 确保工作流名称唯一

    def __str__(self):
        return self.name

class Node(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    node_id = models.CharField(max_length=100)
    node_type = models.CharField(max_length=50)
    predecessors = models.JSONField(default=list)  # 保存前驱节点 id
    successors = models.JSONField(default=list)    # 保存后继节点 id
    # 需要补充data