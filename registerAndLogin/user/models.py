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
    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

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