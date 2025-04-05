from django.urls import path, include
from user.admin_urls import urlpatterns as admin_urls

urlpatterns = [
    path('admin/', include((admin_urls, 'admin'), namespace='admin')),
]