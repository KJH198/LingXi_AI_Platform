# LingXi_AI_Platform/registerAndLogin/user/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import register, user_login, update_user_info, AdminView

router = DefaultRouter()
router.register(r'admin', AdminView, basename='admin')

urlpatterns = [
    path('register', register, name='register'),
    path('login', user_login, name='login_no_slash'),
    path('update_info/', update_user_info, name='update_user_info'),
] + router.urls