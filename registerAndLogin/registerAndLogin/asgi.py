"""
ASGI config for registerAndLogin project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from agent.consumers import NodeOutputConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registerAndLogin.settings')

# 获取Django的ASGI应用
django_asgi_app = get_asgi_application()

# WebSocket路由配置
websocket_urlpatterns = [
    re_path(r'ws/node_output/$', NodeOutputConsumer.as_asgi()),
]

# 组合HTTP和WebSocket路由
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
