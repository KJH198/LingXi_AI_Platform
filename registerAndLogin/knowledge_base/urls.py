from django.urls import path
from . import views

urlpatterns = [
    path('fetch_knowledgebases/', views.KnowledgeBaseListView.as_view(), name='knowledge-base-list'),
    path('create_knowledgebase/', views.KnowledgeBaseCreateView.as_view(), name='knowledge-base-create'),
    path('knowledgebase/<str:knowledgeBaseId>/upload/', views.KnowledgeBaseUploadView.as_view(), name='knowledge-base-upload'),
    path('knowledgebase/<str:kb_id>/delete/', views.KnowledgeBaseDeleteView.as_view(), name='knowledge-base-delete'),
] 