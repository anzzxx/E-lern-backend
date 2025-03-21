from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Message sender
    room_name = models.CharField(max_length=255)  # Chat room name
    message = models.TextField(blank=True,null=True)  # Message content
    file_url=models.CharField(blank=True,null=True,max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    class Meta:
        ordering = ["timestamp"]  # Order messages by time

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"
