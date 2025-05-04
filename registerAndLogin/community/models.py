from django.db import models
from knowledge_base.models import KnowledgeBase
from user.models import PublishedAgent,User


class Post(models.Model):
    """帖子模型"""
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)  # 添加收藏数字段
    comment_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='active')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '帖子'
        verbose_name_plural = '帖子'

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '帖子图片'
        verbose_name_plural = '帖子图片'

    def __str__(self):
        return f"{self.post.title}的图片"

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = '帖子点赞'
        verbose_name_plural = '帖子点赞'

    def __str__(self):
        return f"{self.user.username}点赞了{self.post.title}"

class PostFavorite(models.Model):
    """帖子收藏模型"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # 确保用户不能重复收藏同一个帖子
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.post.title}"

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '帖子评论'
        verbose_name_plural = '帖子评论'

    def __str__(self):
        return f"{self.user.username}评论了{self.post.title}"

class PostAgent(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    agent = models.ForeignKey(PublishedAgent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'agent')
        verbose_name = '帖子-智能体关联'
        verbose_name_plural = '帖子-智能体关联'

    def __str__(self):
        return f"{self.post.title}关联了{self.agent.agent_name}"

class PostKnowledgeBase(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'knowledge_base')
        verbose_name = '帖子-知识库关联'
        verbose_name_plural = '帖子-知识库关联'

    def __str__(self):
        return f"{self.post.title}关联了{self.knowledge_base.name}"
