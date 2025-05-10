from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model that controls which fields are exposed
    and which fields are read-only.
    
    By default excludes sender and recipient fields from input/output.
    All fields except 'message' are read-only.
    """
    class Meta:
        model = Notification
        fields = [
            'id',
            'message', 
            'is_read',
            'timestamp'
        ] 
        read_only_fields = [
            'id',
            'is_read',
            'timestamp'
        ]