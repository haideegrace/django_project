"""
Django Channels routing configuration.
Maps WebSocket URLs to consumers.
"""

from django.urls import path, re_path
from farm.consumers import FarmDashboardConsumer, NotificationConsumer

websocket_urlpatterns = [
    path('ws/dashboard/', FarmDashboardConsumer.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]
