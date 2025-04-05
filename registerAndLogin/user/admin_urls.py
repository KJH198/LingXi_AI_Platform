from django.urls import path
from .admin_views import (
    AdminDashboardView,
    UserListView,
    UserBanView,
    AgentRatingView,
    KnowledgeBaseView
)

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/ban/', UserBanView.as_view(), name='user-ban'),
    path('ratings/', AgentRatingView.as_view(), name='agent-ratings'),
    path('knowledge/', KnowledgeBaseView.as_view(), name='knowledge-base'),
    path('knowledge/<int:kb_id>/', KnowledgeBaseView.as_view(), name='knowledge-base-detail'),
    path('users/<int:user_id>/ban-status/', UserBanStatusView.as_view(), name='user-ban-status'),
]