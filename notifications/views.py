from django.shortcuts import get_list_or_404
from rest_framework.permissions import BasePermission
from rest_framework.generics import CreateAPIView,ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification, CustomUser
from .serializers import NotificationSerializer
from accounts.models import CustomUser
from rest_framework.response import Response
from rest_framework import status

class IsStaffOnly(BasePermission):
    """
    Custom permission to allow only staff members to create notifications.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class NotificationCreateView(CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsStaffOnly]

    def perform_create(self, serializer):
        """
        Override this method to create multiple notifications
        for multiple recipients.
        """
        sender = self.request.user
        recipient_ids = self.request.data.get("recipients", [])  # Expecting a list of user IDs

        recipients = CustomUser.objects.filter(is_active=True)
        
        notifications = [
            Notification(sender=sender, recipient=recipient, message=self.request.data["message"])
            for recipient in recipients
        ]

        Notification.objects.bulk_create(notifications)  # Create multiple notifications efficientlycla



class UnreadNotificationsView(ListAPIView):
    """
    API view to retrieve all unread notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns only unread notifications for the authenticated user.
        """
        return Notification.objects.filter(recipient=self.request.user, is_read=False)
        
class MarkAllNotificationsReadView(UpdateAPIView):
    """
    API view to mark all notifications as read for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Marks all notifications as read for the authenticated user.
        """
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        count = notifications.update(is_read=True)  # Bulk update

        return Response(
            {"message": f"{count} notifications marked as read."},
            status=status.HTTP_200_OK
        )        