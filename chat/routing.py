from django.urls import re_path
from .consumers import ChatConsumer,DirectChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/chat/direct/(?P<user_id>\w+)/$', DirectChatConsumer.as_asgi()), 
]
