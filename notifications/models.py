# models.py
from django.db import models
from accounts.models import CustomUser

class CustomManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        # Perform the bulk create operation
        created_objs = super(CustomManager, self).bulk_create(objs, **kwargs)
        
        # Send a custom signal after bulk create is done
        from .signals import bulk_create_done  # Import the signal here to avoid circular imports
        bulk_create_done.send(sender=self.model, instances=created_objs)
        
        return created_objs

class Notification(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_notifications")
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = CustomManager()

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.message[:20]}"