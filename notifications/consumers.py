# notifications/consumers.py
import json
from urllib.parse import parse_qs
import jwt
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the JWT token from the query string (e.g., ?token=xxx)
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]
        if not token:
            # Reject the connection if no token is provided
            await self.close()
            return

        try:
            # Decode the token using your secret key and expected algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            # Retrieve the user asynchronously (make sure your JWT payload includes the user ID)
            self.user = await sync_to_async(get_user_model().objects.get)(id=user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
            # Close the connection if token is invalid or any error occurs
            print(f"Error: {e}")
            await self.close()
            return

        # Create a unique group name for the user
        self.group_name = f'user_{self.user.id}'
        
        # Add the connection to the user's group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the connection from the user's group on disconnect
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        # Send the notification message to the frontend
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))