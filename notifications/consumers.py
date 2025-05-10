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

        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]
        if not token:
            await self.close()
            return

        try:

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            self.user = await sync_to_async(get_user_model().objects.get)(id=user_id)

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:

            await self.close()
            return

        self.group_name = f'user_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
    
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):

        await self.send(text_data=json.dumps({
            'message': event['message']
        }))