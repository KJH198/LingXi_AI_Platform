# LingXi_AI_Platform/registerAndLogin/user/urls.py
from django.urls import path
from .views import (
    register,
    user_login,
    update_user_info,
    AdminDashboardView,
    UserManagementView,
    AgentRatingView,
    KnowledgeBaseView
)

urlpatterns = [
    path('register', register, name='register'),
    path('login', user_login, name='login_no_slash'),
    path('update_info/', update_user_info, name='update_user_info'),
    
    # 管理员路由
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', UserManagementView.as_view(), name='user_management'),
    path('admin/users/<int:user_id>/', UserManagementView.as_view(), name='user_detail'),
    path('admin/agent_rating/', AgentRatingView.as_view(), name='agent_rating'),
    path('admin/knowledge_base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('admin/knowledge_base/<int:kb_id>/', KnowledgeBaseView.as_view(), name='knowledge_base_detail'),
]