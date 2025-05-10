from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    room_name = models.CharField(max_length=255)
    message = models.TextField(blank=True,null=True) 
    file_url=models.CharField(blank=True,null=True,max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"
