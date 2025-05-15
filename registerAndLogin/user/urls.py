# LingXi_AI_Platform/registerAndLogin/user/urls.py
from django.urls import path
from .views import (
    AdminBanView,
    AdminChangeAgentSataus,
    AdminChangeKBSataus,
    AdminGetAgents,
    AdminGetKB,
    AdminUnbanView,
    CheckAnnouncements,
    CreateAnnouncement,
    DeleteAnnouncement,
    EditAnnouncement,
    GetAnnouncements,
    OpenAgentView,
    Update,
    UseAgentView,
    UserFollowedAgentsView,
    UserGetAnnouncements,
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
    UserSearchView,
    UserLoginRecordView,
    UserListAPIView,
    UserDetailAPIView,
    UserOperationRecordsView,
    UserAbnormalBehaviorsView,
    UserBehaviorStatsView,
    UserBehaviorLogsView,
    AgentPublishView,
    UserAgentListView,
    UserKnowledgeBaseListView,
    PostCreateView,
    PostImageUploadView,
    user_logout,
    PostLikeView,
    PostFavoriteView,
    PostCommentView,
    AgentFollowView,
    KnowledgeBaseFollowView,
    AgentDetailView,
    KnowledgeBaseDetailView,
    AgentEditDetailView,
    AgentUpdateView,
    AgentCommentView,
    AgentCommentLikeView,
    AgentLikeView,
    AgentCommentReplyView,
    KnowledgeBaseLikeView,
    KnowledgeBaseCommentView,
    AgentRestoreView,
    UserFollowView,
    AgentDeleteView,
    AgentDraftView,
    UserProfileView, 
    UserPostsView, 
    UserPublicAgentsView, 
    UserPublicKnowledgeBasesView, 
)

urlpatterns = [
    path('register', register, name='register'),
    path('login', user_login, name='login_no_slash'),
    path('update_info/', update_user_info, name='update_user_info'),
    path('follow/<int:user_id>/', UserFollowingView.as_view(), name='user_following'),

    # 个人信息相关路由
    path('user_info/', UserInfoView.as_view(), name='user_info'),
    path('update_info/', UpdateUserInfoView.as_view(), name='update_user_info'),
    path('upload_avatar/', UploadAvatarView.as_view(), name='upload_avatar'),
    path('<str:user_id>/profile/', UserProfileView.as_view(), name='user_profile'),
    path('<str:user_id>/posts/', UserPostsView.as_view(), name='user_posts'),
    path('<str:user_id>/agents/', UserPublicAgentsView.as_view(), name='user_public_agents'),
    path('<str:user_id>/knowledge-bases/', UserPublicKnowledgeBasesView.as_view(), name='user_public_knowledge_bases'),

    # 管理员路由
    path('adminLogin', AdminLoginView.as_view(), name='admin_login'),
    path('adminDashboard', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('adminGetUsers', UserManagementView.as_view(), name='user_management'),
    path('adminGetUsersDetail/<int:user_id>/', UserManagementView.as_view(), name='user_detail'),
    path('admin/agent_rating/', AgentRatingView.as_view(), name='agent_rating'),
    path('admin/knowledge_base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('admin/knowledge_base/<int:kb_id>/', KnowledgeBaseView.as_view(), name='knowledge_base_detail'),
    path('admin/behavior_logs/', UserActionLogView.as_view(), name='behavior_logs'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    
    path('agent/publish', AgentPublishView.as_view(), name='agent-publish'),
    path('api/admin/user/<str:user_id>/', UserDetailAPIView.as_view(), name='admin_user_detail'),
    path('api/admin/user/behavior_stats/', UserBehaviorStatsView.as_view(), name='admin_behavior_stats'),
    path('api/admin/user/behavior_logs/<str:user_id>/', UserBehaviorLogsView.as_view(), name='admin_behavior_logs'),
    
    # 管理员封禁与解封用户
    path('admin/banUser/<int:user_id>', AdminBanView.as_view(), name='ban'),
    path('admin/unbanUser/<int:user_id>', AdminUnbanView.as_view(), name='unban'),
    
    # 管理员发布、修改和删除公告
    path('admin/GetAnnouncements', GetAnnouncements.as_view(), name='announcement_list'),
    path('admin/CreateAnnouncement', CreateAnnouncement.as_view(), name='create_announcement'),
    path('admin/EditAnnouncement/<int:announcement_id>', EditAnnouncement.as_view(), name='update_announcement'),
    path('admin/DeleteAnnouncement/<int:announcement_id>', DeleteAnnouncement.as_view(), name='delete_announcement'),
    
    # 验证是否需要提醒用户看公告以及更新最后一次看公告的时间
    path('GetAnnouncements', UserGetAnnouncements.as_view(), name='announcement_list2'),
    path('user/checkAnnouncements/<int:user_id>', CheckAnnouncements.as_view(), name='check_announcement'),
    path('user/update/<int:user_id>', Update.as_view(), name='user_update'),
    
    # 统计用户登录时长
    path('logout/<str:user_id>', user_logout, name='user_logout'),
    
    # 登录数据列表和搜索、操作记录数据列表和搜索、异常行为数据列表和搜索 
    path('admin/login_records', UserLoginRecordView.as_view(), name='login_records'),
    path('admin/operation_records', UserOperationRecordsView.as_view(), name='admin_operation_records'),
    path('admin/abnormal_behaviors', UserAbnormalBehaviorsView.as_view(), name='admin_abnormal_behaviors'),
    
    path('admin/login_records/<int:user_id>', UserLoginRecordView.as_view(), name='login_records2'),
    path('admin/operation_records/<int:user_id>', UserOperationRecordsView.as_view(), name='admin_operation_records2'),
    path('admin/abnormal_behaviors/<int:user_id>', UserAbnormalBehaviorsView.as_view(), name='admin_abnormal_behaviors2'),
    
    # 获取智能体列表和搜索、审核智能体
    path('admin/agents/list', AdminGetAgents.as_view(), name='agent_list'),
    path('admin/agents/list/<int:agent_id>', AdminGetAgents.as_view(), name='agent_search'),
    path('admin/changeAgentSataus/<int:agent_id>', AdminChangeAgentSataus.as_view(), name='agent_list'),
    
    # 获取知识库列表和搜索、审核知识库
    path('admin/knowledgebases', AdminGetKB.as_view(), name='kb_list'),
    path('admin/knowledgebases/<int:kb_id>', AdminGetKB.as_view(), name='kb_search'),
    path('admin/changeKBSataus/<int:kb_id>', AdminChangeKBSataus.as_view(), name='kb_list'),
    
    # 智能体互用和开源
    path('useAgent/<str:agent_id>/', UseAgentView.as_view(), name='agent_edit_detail'),
    path('OpenAgent/<str:agent_id>/', OpenAgentView.as_view(), name='open_agent'),
    path('followed/agents', UserFollowedAgentsView.as_view(), name='agent_detail'),
    
    # 智能体和知识库相关路由
    path('agents/list', UserAgentListView.as_view(), name='user_agent_list'),
    path('knowledge-bases/list/', UserKnowledgeBaseListView.as_view(), name='user_knowledge_base_list'),
    path('agent/<str:agent_id>/edit-detail/', AgentEditDetailView.as_view(), name='agent_edit_detail'),
    path('agent/<str:agent_id>/update/', AgentUpdateView.as_view(), name='agent_update'),
    
    # 帖子相关路由
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/upload-images/', PostImageUploadView.as_view(), name='post_image_upload'),
    path('like/post/<int:postId>/', PostLikeView.as_view(), name='post_like'),
    path('favorite/post/<int:postId>/', PostFavoriteView.as_view(), name='post_favorite'),
    path('comment/post/<int:postId>/', PostCommentView.as_view(), name='post_comment'),
    
    # 关注相关路由
    path('follow/agent/<int:agentId>/', AgentFollowView.as_view(), name='agent_follow'),
    path('follow/knowledge-base/<int:kbId>/', KnowledgeBaseFollowView.as_view(), name='knowledge_base_follow'),

    path('knowledge-base/<int:kbId>/like/', KnowledgeBaseLikeView.as_view(), name='knowledge_base_like'),
    path('knowledge-base/<int:kbId>/comment/', KnowledgeBaseCommentView.as_view(), name='knowledge_base_comment'),

    path('follow/<str:userId>/', UserFollowView.as_view(), name='user_follow'),

    path('agent/<str:agent_id>/delete', AgentDeleteView.as_view(), name='agent_delete'),
    path('agent/draft', AgentDraftView.as_view(), name='agent_draft_create_or_list'),
    path('agent/draft/<int:draft_id>', AgentDraftView.as_view(), name='agent_draft_detail_or_delete'),
]