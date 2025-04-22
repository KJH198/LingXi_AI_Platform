from django.db import models
from django.conf import settings

class Agent(models.Model):
    user_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)  # 需要确保智能体名称对每个用户唯一
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Workflow(models.Model):
    user_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    structure = models.JSONField(default=dict)
    name = models.CharField(max_length=255)  # 需要确保工作流名称对每个用户唯一

    def __str__(self):
        return self.name

class Node(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    node_id = models.CharField(max_length=100)
    node_type = models.CharField(max_length=50)
    node_data = models.JSONField(default=dict)
    predecessors = models.JSONField(default=list)  # 保存前驱节点 id
    successors = models.JSONField(default=list)    # 保存后继节点 id
    # 需要补充data

class UserActionLog(models.Model):
    """用户行为日志模型"""
    ACTION_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create_agent', '创建智能体'),
        ('delete_agent', '删除智能体'),
        ('create_workflow', '创建工作流'),
        ('delete_workflow', '删除工作流'),
        ('execute_workflow', '执行工作流'),
        ('admin_action', '管理员操作'),
        ('other', '其他')
    ]

    user_id = models.CharField(max_length=255, verbose_name='用户ID')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name='行为类型')
    action_detail = models.JSONField(default=dict, verbose_name='行为详情')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(null=True, blank=True, verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '用户行为日志'
        verbose_name_plural = '用户行为日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} - {self.get_action_type_display()} - {self.created_at}'