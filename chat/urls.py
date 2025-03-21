from django.urls import path
from .views import *

urlpatterns = [
    path("<str:room_name>/messages/", MessageListView.as_view(), name="chat-messages"),
    path("profiles/", ProfileListView.as_view(), name="user-profiles"),
    path("upload/", MediaUploadView.as_view(), name="media-upload"),
]