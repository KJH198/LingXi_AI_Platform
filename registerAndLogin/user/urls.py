# LingXi_AI_Platform/registerAndLogin/user/urls.py
from django.urls import path
from .views import (
    register,
    user_login,
    update_user_info,
    AdminDashboardView,
    UserManagementView,
    AgentRatingView,
    KnowledgeBaseView,
    AdminLoginView,
    UserFollowingView,
    UserInfoView,
    UpdateUserInfoView,
    UploadAvatarView
)

urlpatterns = [
    path('register', register, name='register'),
    path('login', user_login, name='login_no_slash'),
    path('update_info/', update_user_info, name='update_user_info'),
    path('users/<int:user_id>/following/', UserFollowingView.as_view(), name='user_following'),

    # 个人信息相关路由
    path('user_info/', UserInfoView.as_view(), name='user_info'),
    path('update_info/', UpdateUserInfoView.as_view(), name='update_user_info'),
    path('upload_avatar/', UploadAvatarView.as_view(), name='upload_avatar'),

    # 管理员路由
    path('adminLogin', AdminLoginView.as_view(), name='admin_login'),
    path('adminDashboard', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('adminGetUsers', UserManagementView.as_view(), name='user_management'),
    path('adminGetUsersDetail/<int:user_id>/', UserManagementView.as_view(), name='user_detail'),
    path('admin/agent_rating/', AgentRatingView.as_view(), name='agent_rating'),
    path('admin/knowledge_base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('admin/knowledge_base/<int:kb_id>/', KnowledgeBaseView.as_view(), name='knowledge_base_detail'),
]