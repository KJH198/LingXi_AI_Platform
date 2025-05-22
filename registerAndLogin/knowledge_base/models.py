from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class KnowledgeBase(models.Model):
    """知识库模型"""
    STATUS_CHOICES = (
        ('approved', '审核通过'),
        ('rejected', '拒绝'),
    )
    TYPE_CHOICES = (
        ('text', '文本'),
        ('image', '图片'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)  # text, image
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='knowledge_bases')
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followed_knowledge_bases', blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_knowledge_bases', blank=True)

    def __str__(self):
        return self.name

class KnowledgeBaseFile(models.Model):
    STATUS_CHOICES = (
        ('ready', '已处理完毕'),
        ('processing', '正在处理'),
    )
    
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='knowledge_base_files/')
    filename = models.CharField(max_length=255)
    size = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename 

class KnowledgeBaseComment(models.Model):
    """知识库评论模型"""
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='knowledge_base_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_knowledge_base_comments', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"{self.user.username} 评论了 {self.knowledge_base.name}" 