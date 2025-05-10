from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import cloudinary.uploader
from .models import ChatMessage
from .serializers import MessageSerializer
from accounts.models import CustomUser
from .serializers import ProfileSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class MessageListView(generics.ListAPIView):
    """
    API View to retrieve the last 50 messages of a chat room.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]  # Requires authentication

    def get_queryset(self):
        room_name = self.kwargs.get("room_name")
        return ChatMessage.objects.filter(room_name=room_name).order_by("-timestamp")[:50]


class ProfileListView(generics.ListAPIView):
    """
    API View to retrieve all user profiles with error handling.
    """
    queryset = CustomUser.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Failed to fetch user profiles", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MediaUploadView(generics.CreateAPIView):
    """
    API View to upload media files with error handling.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            file = request.data.get("file")
            content_type = file.content_type
            if not file:
                return Response({"error": "No file was submitted"}, status=status.HTTP_400_BAD_REQUEST)
            if content_type.startswith('image/'):
                upload_result = cloudinary.uploader.upload(file)
                file_url = upload_result.get('secure_url')
            elif content_type.startswith('video/'):
                upload_result = cloudinary.uploader.upload_large(file, resource_type="video")
                file_url = upload_result.get('secure_url')
            else:
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"file_url": file_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Failed to upload media", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
