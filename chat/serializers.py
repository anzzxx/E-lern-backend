from rest_framework import serializers
from .models import ChatMessage
from accounts.models import CustomUser
class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'sender_name','room_name','is_read', 'timestamp','message','file_url']
        read_only_fields = ['id', 'timestamp','sender_name']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "profile_picture"]
        read_only_fields = ["email"]
