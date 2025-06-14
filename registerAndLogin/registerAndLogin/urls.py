"""
URL configuration for registerAndLogin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import AgentDetailView, KnowledgeBaseDetailView, AgentCommentView, AgentCommentLikeView, \
    AgentFollowView, KnowledgeBaseFollowView, AgentLikeView, AgentCommentReplyView, KnowledgeBaseLikeView, \
    KnowledgeBaseCommentView, AgentRestoreView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('agent/', include('agent.urls')),
    path('knowledge_base/', include('knowledge_base.urls')),
    path('community/', include('community.urls')),

    path('agent/<int:agentId>/detail/', AgentDetailView.as_view(), name='agent_detail'),
    path('agent/<int:agentId>/comment/', AgentCommentView.as_view(), name='agent_comment'),
    path('agent/<int:agentId>/follow/', AgentFollowView.as_view(), name='agent_follow_alt'),
    path('agent/<int:agentId>/like/', AgentLikeView.as_view(), name='agent_like'),
    path('agent/restore/', AgentRestoreView.as_view(), name='agent_restore'),
    path('comment/<int:commentId>/like/', AgentCommentLikeView.as_view(), name='agent_comment_like'),
    path('comment/<int:commentId>/reply/', AgentCommentReplyView.as_view(), name='agent_comment_reply'),
    path('knowledge-base/<int:kbId>/detail/', KnowledgeBaseDetailView.as_view(), name='knowledge_base_detail'),
    path('knowledge-base/<int:kbId>/follow/', KnowledgeBaseFollowView.as_view(), name='knowledge_base_follow_alt'),
    path('knowledge-base/<int:kbId>/like/', KnowledgeBaseLikeView.as_view(), name='knowledge_base_like'),
    path('knowledge-base/<int:kbId>/comment/', KnowledgeBaseCommentView.as_view(), name='knowledge_base_comment'),
]

# 开发环境下添加静态文件URL配置
if settings.DEBUG:
    # 处理静态文件
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # 处理assets目录下的文件
    urlpatterns += [
        re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0] / 'assets'}),
        re_path(r'^$', serve, {'path': 'index.html', 'document_root': settings.STATICFILES_DIRS[0]}),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





