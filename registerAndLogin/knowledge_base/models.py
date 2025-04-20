from django.db import models
from django.conf import settings

class KnowledgeBase(models.Model):
    STATUS_CHOICES = (
        ('ready', '已处理完毕'),
        ('processing', '正在处理'),
    )
    TYPE_CHOICES = (
        ('text', '文本'),
        ('image', '图片'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)  # text, image
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='knowledge_bases')

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