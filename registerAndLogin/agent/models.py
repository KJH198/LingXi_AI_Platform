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

# 知识库相关模型
class KnowledgeBase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='knowledge_bases')
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('text', '文本'),
        ('pdf', 'PDF'),
        ('markdown', 'Markdown'),
        ('code', '代码'),
    )

    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    content = models.TextField()
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)  # 存储文档的元数据，如作者、标签等

    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    embedding = models.JSONField(null=True)  # 存储文档块的向量嵌入
    chunk_index = models.IntegerField()  # 块在文档中的位置
    metadata = models.JSONField(default=dict)  # 存储块的元数据

    class Meta:
        ordering = ['chunk_index']

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"

class AgentKnowledgeBase(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='knowledge_bases')
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)  # 知识库优先级
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['agent', 'knowledge_base']
        ordering = ['-priority']

    def __str__(self):
        return f"{self.agent.name} - {self.knowledge_base.name}"