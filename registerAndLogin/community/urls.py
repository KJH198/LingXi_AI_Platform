from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.get_post_list, name='get_post_list'),
] 