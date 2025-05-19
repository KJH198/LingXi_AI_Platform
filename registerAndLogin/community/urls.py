from django.urls import path
from . import views

urlpatterns = [
    # 现有路由
    path('posts/', views.get_post_list, name='get_post_list'),
    
    # 添加搜索路由
    path('search', views.SearchView.as_view(), name='search'),
    path('agents/hot/', views.HotAgentsView.as_view(), name='hot-agents'),
    path('agents/open/', views.OpenAgentsView.as_view(), name='open-agents'),
    path('knowledge-bases/hot/', views.HotKnowledgeBasesView.as_view(), name='hot-knowledge-bases'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/comments/', views.PostCommentsView.as_view(), name='post_comments'),
    path('recent-edited', views.UserRecentEditedView.as_view(), name='user_recent_edited'),
    # 在urlpatterns列表中添加以下路由
    path('favorites/posts', views.UserFavoritePostsView.as_view(), name='user_favorite_posts'),
]