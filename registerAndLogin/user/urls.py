# LingXi_AI_Platform/registerAndLogin/user/urls.py
from django.urls import path
from user.views import register, user_login, update_user_info
from .admin_views import (
    AdminDashboardView,
    UserListView,
    UserBanView,
    AgentRatingView,
    KnowledgeBaseView
)

urlpatterns = [
    path('register', register, name='register'),
    path('login', user_login, name='login_no_slash'),
    path('update_info/', update_user_info, name='update_user_info'),
    path('admin/dashboard', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users', UserListView.as_view(), name='user_list'),
    path('admin/users/<int:user_id>/ban', UserBanView.as_view(), name='user_ban'),
    path('admin/ratings', AgentRatingView.as_view(), name='agent_ratings'),
    path('admin/knowledge', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('admin/knowledge/<int:kb_id>', KnowledgeBaseView.as_view(), name='knowledge_base_detail'),
]
