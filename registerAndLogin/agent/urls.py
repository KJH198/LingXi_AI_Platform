# agents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建新的路由器用于知识库相关的URL
knowledge_router = DefaultRouter()
knowledge_router.register(r'knowledge-bases', views.KnowledgeBaseViewSet, basename='knowledge-base')
knowledge_router.register(r'documents', views.DocumentViewSet, basename='document')
knowledge_router.register(r'agent-knowledge-bases', views.AgentKnowledgeBaseViewSet, basename='agent-knowledge-base')

urlpatterns = [
    path('workflowSave/', views.WorkflowSaveView.as_view(), name='workflow-save'),
    path('workflowGet/', views.WorkflowRetrieveView.as_view(), name='workflow-get'),
    # 添加知识库相关的URL
    path('knowledge/', include(knowledge_router.urls)),
]