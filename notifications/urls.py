from django.urls import path
from .views import *
urlpatterns = [
    path('create/', NotificationCreateView.as_view(), name='notification-create'),
    path('unread/', UnreadNotificationsView.as_view(), name='unread-notifications'),
    path("mark-read/", MarkAllNotificationsReadView.as_view(), name="mark-read-notifications"),
   
]