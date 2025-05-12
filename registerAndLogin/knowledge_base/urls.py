from django.urls import path
from . import views

urlpatterns = [
    path('fetch_knowledgebases/', views.KnowledgeBaseListView.as_view(), name='knowledge-base-list'),
    path('create_knowledgebase/', views.KnowledgeBaseCreateView.as_view(), name='knowledge-base-create'),
    path('knowledgebase/<str:knowledgeBaseId>/', views.KnowledgeBaseDetailView.as_view(), name='knowledge-base-detail'),
    path('knowledgebase/<str:knowledgeBaseId>/upload/', views.KnowledgeBaseUploadView.as_view(), name='knowledge-base-upload'),
    path('knowledgebase/<str:knowledgeBaseId>/file/<int:fileId>/content/', views.FileContentView.as_view(), name='file-content'),
    path('delete_knowledgebase/<str:knowledgeBaseId>/', views.KnowledgeBaseDeleteView.as_view(), name='knowledge-base-delete'),
    path('knowledgebase/<str:knowledgeBaseId>/delete_file/<int:fileId>/', views.FileDeleteView.as_view(), name='file-delete'),
    
    path('my-list', views.MyKnowledgeBaseListView.as_view(), name='my-knowledge-base-list'),
    path('knowledgebase/<str:knowledgeBaseId>/upload_url/', views.KnowledgeBaseUrlUploadView.as_view(), name='knowledge-base-upload-url'),
]