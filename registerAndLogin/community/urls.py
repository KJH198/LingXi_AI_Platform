from django.urls import path
from . import views

urlpatterns = [
    # 现有路由
    path('posts/', views.get_post_list, name='get_post_list'),
    
    # 添加搜索路由
    path('search', views.SearchView.as_view(), name='search'),
    path('agents/hot/', views.HotAgentsView.as_view(), name='hot-agents'),
    path('knowledge-bases/hot/', views.HotKnowledgeBasesView.as_view(), name='hot-knowledge-bases'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/comments/', views.PostCommentsView.as_view(), name='post_comments'),
]