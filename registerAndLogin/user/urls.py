# LingXi_AI_Platform/registerAndLogin/user/urls.py
from django.urls import path
from .views import register, user_login, update_user_info

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('update_info/', update_user_info, name='update_user_info'),
]