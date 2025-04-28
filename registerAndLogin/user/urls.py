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
    UploadAvatarView,
    AgentManagementView,
    UserActionLogView,
    SimpleBanView,
    UserSearchView,
    UserLoginRecordView,
    UserListAPIView,
    UserDetailAPIView,
    UserOperationRecordsView,
    UserAbnormalBehaviorsView,
    UserBehaviorStatsView,
    UserBehaviorLogsView,
    AnnouncementView
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
    path('adminGetUsers/', UserManagementView.as_view(), name='user_management'),
    path('adminGetUsersDetail/<int:user_id>/', UserManagementView.as_view(), name='user_detail'),
    path('admin/agent_rating/', AgentRatingView.as_view(), name='agent_rating'),
    path('admin/knowledge_base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('admin/knowledge_base/<int:kb_id>/', KnowledgeBaseView.as_view(), name='knowledge_base_detail'),
    path('admin/ban/<int:user_id>/', SimpleBanView.as_view(), name='simple_ban'),
    path('admin/behavior_logs/', UserActionLogView.as_view(), name='behavior_logs'),
    path('admin/operation_records', UserOperationRecordsView.as_view(), name='admin_operation_records'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('admin/login_records/', UserLoginRecordView.as_view(), name='login_records'),
    path('admin/announcements/', AnnouncementView.as_view(), name='announcements'),
    path('admin/announcements/<int:announcement_id>/', AnnouncementView.as_view(), name='announcement_detail'),
    
    # 新增管理员接口路由
    path('api/admin/user/list/', UserListAPIView.as_view(), name='admin_user_list'),
    path('api/admin/user/<str:user_id>/', UserDetailAPIView.as_view(), name='admin_user_detail'),
    path('admin/abnormal_behaviors', UserAbnormalBehaviorsView.as_view(), name='admin_abnormal_behaviors'),
    path('api/admin/user/behavior_stats/', UserBehaviorStatsView.as_view(), name='admin_behavior_stats'),
    path('api/admin/user/behavior_logs/<str:user_id>/', UserBehaviorLogsView.as_view(), name='admin_behavior_logs'),
]