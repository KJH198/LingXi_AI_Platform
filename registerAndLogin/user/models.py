# LingXi_AI_Platform/registerAndLogin/user/models.py
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
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_admin = models.BooleanField(default=False, verbose_name='是否为管理员')
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True,
                                       verbose_name='关注')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
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

    @property
    def is_staff(self):
        return self.is_admin

    def follow(self, user):
        """关注用户"""
        if user != self:
            self.following.add(user)
            return True
        return False

    def unfollow(self, user):
        """取消关注用户"""
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
        if not self.is_active:
            return True
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
        ('logout', '登出'),
        ('create_agent', '创建智能体'),
        ('edit_agent', '编辑智能体'),
        ('delete_agent', '删除智能体'),
        ('follow', '关注用户'),
        ('unfollow', '取消关注'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_logs', verbose_name='用户')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='行为类型')
    target_id = models.IntegerField(blank=True, null=True, verbose_name='目标ID')
    target_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='目标类型')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    user_agent = models.CharField(max_length=255, blank=True, null=True, verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '用户行为日志'
        verbose_name_plural = '用户行为日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} {self.get_action_display()} at {self.created_at}'

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
    model_id = models.CharField(max_length=100, verbose_name='模型ID')
    workflow_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='工作流ID')
    knowledge_bases = models.ManyToManyField('knowledge_base.KnowledgeBase', blank=True, verbose_name='知识库')
    views = models.IntegerField(default=0, verbose_name='浏览量')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    comments = models.IntegerField(default=0, verbose_name='评论数')

    class Meta:
        verbose_name = '已发布智能体'
        verbose_name_plural = '已发布智能体'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} (by {self.creator.username})'