from django.urls import re_path
from . import consumers
websocket_urlpatterns = [
    re_path('api/ws/', consumers.GatewayConsumer.as_asgi()),
]