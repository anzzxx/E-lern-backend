from django.db import models
from accounts.models import CustomUser


class CustomManager(models.Manager):
    """
    Custom manager that extends bulk_create functionality to send a signal
    after bulk creation is complete.
    """
    def bulk_create(self, objs, **kwargs):
        """
        Perform bulk create operation and send signal when complete.
        
        Args:
            objs: List of model instances to create
            **kwargs: Additional arguments for bulk_create
            
        Returns:
            List of created model instances
        """
        # Perform the bulk create operation
        created_objs = super().bulk_create(objs, **kwargs)
        
        # Send custom signal after bulk create is done
        from .signals import bulk_create_done  # Import here to avoid circular imports
        bulk_create_done.send(
            sender=self.model,
            instances=created_objs
        )
        
        return created_objs


class Notification(models.Model):
   
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="received_notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = CustomManager()

    def __str__(self):
        """String representation of the notification."""
        return f"{self.sender} -> {self.recipient}: {self.message[:20]}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'