# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

# Custom signal for bulk create
bulk_create_done = Signal()

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, **kwargs):
    """
    Signal handler to send a notification to the user when a single Notification instance is created.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.user.id}',  # Send to the user's specific group
        {
            'type': 'send_notification',
            'message': instance.message
        }
    )

def handle_bulk_create(sender, instances, **kwargs):
    """
    Signal handler to process bulk-created Notification instances.
    """
    channel_layer = get_channel_layer()
    for instance in instances:
        print(f"Handling bulk-created instance: {instance}")
        # Send a notification for each bulk-created instance
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.recipient.id}',  # Send to the user's specific group
            {
                'type': 'send_notification',
                'message': instance.message
            }
        )

# Connect the bulk_create_done signal to the handle_bulk_create handler
bulk_create_done.connect(handle_bulk_create, sender=Notification)