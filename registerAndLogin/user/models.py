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
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

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