from django.urls import path
from . import views

urlpatterns = [
    # 现有路由
    path('posts/', views.get_post_list, name='get_post_list'),
    
    # 添加搜索路由
    path('search', views.SearchView.as_view(), name='search'),
]