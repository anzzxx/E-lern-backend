from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'timestamp']  # Exclude sender & recipient from input
        read_only_fields = ['id', 'is_read', 'timestamp']
