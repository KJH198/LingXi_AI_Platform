# LingXi_AI_Platform/registerAndLogin/user/models.py
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class MyUserManager(BaseUserManager):
    def create_user(self, username, password, phone_number, email=None):
        if not username:
            raise ValueError('Users must have an username')
        if not phone_number:
            raise ValueError('Users must have a phone number')
        user = self.model(
            username=username,
            phone_number=phone_number,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, phone_number, email=None):
        user = self.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            email=email
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=30, verbose_name='用户名')
    phone_number = models.CharField(max_length=15, unique=True, verbose_name='手机号码')
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name='邮箱地址')
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='个人简介')
    avatar = models.URLField(max_length=255, blank=True, null=True, verbose_name='头像URL')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    is_admin = models.BooleanField(default=False, verbose_name='是否为管理员')
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True,
                                       verbose_name='关注')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='最后一次看公告的时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    online_duration = models.DurationField(default=timezone.timedelta, verbose_name='今日在线时长')
    login_times = models.IntegerField(default=0, verbose_name='今日登录次数')
    unexpected_operation_times = models.IntegerField(default=0, verbose_name='今日异常操作次数')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='最后登录IP地址')
    ban_type = models.CharField(
        max_length=20,
        choices=[
            ('light', '轻度违规'),
            ('medium', '中度违规'),
            ('severe', '严重违规'),
            ('permanent', '永久封禁')
        ],
        blank=True,
        null=True,
        verbose_name='封禁类型'
    )
    ban_reason = models.TextField(max_length=500, blank=True, null=True, verbose_name='封禁原因')
    ban_until = models.DateTimeField(null=True, blank=True, verbose_name='封禁截止时间')

    objects = MyUserManager()

    USERNAME_FIELD = 'phone_number'

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def follow(self, user):
        """关注用户"""
        if user != self:
            self.following.add(user)
            return True
        return False

    def unfollow(self, user):
        """取消关注用户"""
        if not self.is_following(user):
            raise ValueError("还未关注该用户")
        self.following.remove(user)
        return True

    def is_following(self, user):
        """检查是否已关注用户"""
        return self.following.filter(id=user.id).exists()

    def get_following_count(self):
        """获取关注数"""
        return self.following.count()

    def get_followers_count(self):
        """获取粉丝数"""
        return self.followers.count()

    def is_banned(self):
        """检查用户是否被封禁"""
        if self.ban_until and self.ban_until > timezone.now():
            return True
        return False

    def get_ban_info(self):
        """获取封禁信息"""
        if not self.is_banned():
            return None
        return {
            'reason': self.ban_reason,
            'until': self.ban_until
        }
    # 重写 save 方法
    def save(self, *args, **kwargs):
        # 确保 online_duration 只保留整数秒
        if self.online_duration:
            self.online_duration = timedelta(seconds=int(self.online_duration.total_seconds()))
        super().save(*args, **kwargs)

class AIAgent(models.Model):
     """智能体模型"""
     STATUS_CHOICES = [
         ('pending', '待审核'),
         ('approved', '已通过'),
         ('rejected', '已拒绝'),
     ]
     
     name = models.CharField(max_length=100, verbose_name='智能体名称')
     description = models.TextField(verbose_name='描述')
     creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_agents', verbose_name='创建者')
     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
     review_notes = models.TextField(blank=True, null=True, verbose_name='审核意见')
     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
     updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
     is_active = models.BooleanField(default=True, verbose_name='是否激活')

     class Meta:
         verbose_name = '智能体'
         verbose_name_plural = '智能体'
         ordering = ['-created_at']

     def __str__(self):
         return f'{self.name} (by {self.creator.username})'

class AgentReview(models.Model):
    """智能体审核记录"""
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name='reviews', verbose_name='智能体')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_reviews', verbose_name='审核员')
    decision = models.CharField(max_length=20, choices=[('approve', '通过'), ('reject', '拒绝')], verbose_name='审核决定')
    notes = models.TextField(blank=True, null=True, verbose_name='审核意见')
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name='审核时间')

    class Meta:
        verbose_name = '智能体审核记录'
        verbose_name_plural = '智能体审核记录'
        ordering = ['-reviewed_at']

    def __str__(self):
        return f'{self.agent.name} review by {self.reviewer.username}'

class UserActionLog(models.Model):
    """用户行为日志"""
    ACTION_CHOICES = [
        ('login', '登录'),
        ('login_failed', '登录失败'),
        ('logout', '登出'),
        ('register', '注册'),
        ('update_profile', '更新个人信息'),
        ('publish_agent', '发布智能体'),
        ('create_agent', '创建智能体'),
        ('edit_agent', '编辑智能体'),
        ('delete_agent', '删除智能体'),
        ('create_post', '发帖'),
        ('delete_post', '删除帖'),
        ('edit_agent', '编辑智能体'),
        ('delete_agent', '删除智能体'),
        ('follow', '关注用户'),
        ('unfollow', '取消关注'),
        ('like_post', '点赞帖子'),
        ('comment_post', '评论帖子'),
        ('unlike_post', '取消点赞'),
        ('favorite_post', '收藏帖子'),
        ('unfavorite_post', '取消收藏'),
        ('delete_post_comment', '删除评论'),
    ]
    
    Type_CHOICES = [
        ('agent', '智能体'),
        ('post', '帖子'),
        ('comment', '评论'),
        ('post_comment', '评论'),
        ('knowledge_base', '知识库'),
        ('user', '用户'),
        ('other', '其他')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_logs', verbose_name='用户')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='行为类型')
    target_id = models.IntegerField(blank=True, null=True, verbose_name='目标ID')
    target_type = models.CharField(max_length=50, blank=True, choices=Type_CHOICES, null=True, verbose_name='目标类型')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '用户行为日志'
        verbose_name_plural = '用户行为日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} {self.get_action_display()} at {self.created_at}'

class AbnormalBehavior(models.Model):
    """用户异常行为记录"""
    ABNORMAL_TYPES = [
        ('frequent_login', '频繁登录'),
        ('frequent_failed_login', '频繁登录失败'),
        ('long_online_duration', '超长时间在线'),
        ('login_ip_change', '异地登录'),
        ('suspicious_activity', '可疑操作'),
        ('content_violation', '内容违规'),
        ('spam', '垃圾信息'),
        ('other', '其他异常')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abnormal_behaviors', verbose_name='用户')
    abnormal_time = models.DateTimeField(auto_now_add=True, verbose_name='异常时间')
    abnormal_type = models.CharField(max_length=50, choices=ABNORMAL_TYPES, verbose_name='异常类型')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    is_handled = models.BooleanField(default=False, verbose_name='是否已处理')
    handled_at = models.DateTimeField(blank=True, null=True, verbose_name='处理时间')
    handled_notes = models.TextField(blank=True, null=True, verbose_name='处理意见')

    class Meta:
        verbose_name = '异常行为记录'
        verbose_name_plural = '异常行为记录'
        ordering = ['-abnormal_time']

    def __str__(self):
        return f'{self.user.username} {self.get_abnormal_type_display()} at {self.abnormal_time}'

class Announcement(models.Model):
    """系统公告模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('withdrawn', '已撤回'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    publishTime = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')

    class Meta:
        verbose_name = '系统公告'
        verbose_name_plural = '系统公告'
        ordering = ['-publishTime']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
    
class PublishedAgent(models.Model):
    """已发布的智能体模型"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='智能体名称')
    description = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_agents', verbose_name='创建者')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    review_notes = models.TextField(blank=True, null=True, verbose_name='审核意见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    model_id = models.CharField(max_length=100, verbose_name='模型ID', default='模型999')
    workflow_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='工作流ID')
    knowledge_bases = models.ManyToManyField('knowledge_base.KnowledgeBase', blank=True, verbose_name='知识库')
    views = models.IntegerField(default=0, verbose_name='浏览量')
    likes = models.ManyToManyField(User, related_name='liked_agents', blank=True, verbose_name='点赞用户')
    comments = models.IntegerField(default=0, verbose_name='评论数')
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name='头像URL')
    followers = models.ManyToManyField(User, related_name='followed_agents', blank=True, verbose_name='关注者')
    is_OpenSource = models.BooleanField(default=False, verbose_name='是否开源')

    class Meta:
        verbose_name = '已发布智能体'
        verbose_name_plural = '已发布智能体'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} (by {self.creator.username})'

class AgentComment(models.Model):
    """智能体评论"""
    agent = models.ForeignKey(PublishedAgent, on_delete=models.CASCADE, related_name='agent_comments', verbose_name='智能体')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_comments', verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    likes = models.ManyToManyField(User, related_name='liked_agent_comments', blank=True, verbose_name='点赞用户')

    class Meta:
        verbose_name = '智能体评论'
        verbose_name_plural = '智能体评论'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 评论了 {self.agent.name}'
    
class AgentDraft(models.Model):
    """智能体草稿模型"""
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_drafts', verbose_name='创建者')
    name = models.CharField(max_length=100, verbose_name='智能体名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name='头像URL')
    model_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='模型ID')
    workflow_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='工作流ID')
    knowledge_bases = models.ManyToManyField('knowledge_base.KnowledgeBase', blank=True, verbose_name='知识库')
    model_params = models.JSONField(default=dict, blank=True, verbose_name='模型参数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '智能体草稿'
        verbose_name_plural = '智能体草稿'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} (草稿 by {self.creator.username})'