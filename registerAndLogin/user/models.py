# LingXi_AI_Platform/registerAndLogin/user/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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
    username = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    ban_until = models.DateTimeField(null=True, blank=True)
    ban_reason = models.CharField(max_length=200, blank=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class AgentRating(models.Model):
    """智能体评分模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    agent_id = models.CharField(max_length=36)  # 智能体UUID
    rating = models.PositiveSmallIntegerField()  # 1-5星评分
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'agent_id')  # 每个用户对每个智能体只能评价一次

    def __str__(self):
        return f"{self.user.username}对智能体{self.agent_id}的{self.rating}星评价"