import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from .models import ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        self.user = await self.get_user_from_token()

        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close()  # Reject the connection if authentication fails
            return

        # Extract room name from URL
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = f'chat_{self.room_name}'  # Define room group name
        print(self.room_group_name, "group")

        # Add the channel to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages."""
        if not self.user or isinstance(self.user, AnonymousUser):
            return  # Ignore messages from unauthenticated users

        try:
            data = json.loads(text_data)
            message = data.get('message')
            file_url = data.get('file')
        except json.JSONDecodeError:
            return  # Ignore invalid JSON messages

        if message:
            # Save message to database
            await self.save_message(self.user, self.room_name, message, file_url)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'file_url': file_url,
                    'username': self.user.username
                }
            )

    async def chat_message(self, event):
        """Sends messages to WebSocket clients."""
        message = event.get('message', '').strip()
        file_url = event.get('fileMessage', '').strip()

        if message or file_url:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'file_url': event['file_url'],
                'username': event['username']
            }))

    @database_sync_to_async
    def save_message(self, user, room_name, message, file_url):
        """Stores a message in the database."""
        ChatMessage.objects.create(user=user, room_name=room_name, message=message, file_url=file_url)

    @database_sync_to_async
    def get_previous_messages(self):
        """Retrieves the last 10 messages for the chat room."""
        messages = ChatMessage.objects.filter(room_name=self.room_name).order_by('-timestamp')[:10]
        return [
            {
                'message': msg.message,
                'file_url': msg.file_url,
                'username': msg.user.username,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for msg in messages
        ]

    @database_sync_to_async
    def get_user_from_token(self):
        """Extracts the user from the JWT token."""
        query_string = self.scope['query_string'].decode()
        params = dict(q.split('=') for q in query_string.split('&') if '=' in q)
        token_key = params.get('token')

        if not token_key:
            return AnonymousUser()  # No token provided

        try:
            decoded_token = AccessToken(token_key)  # Decode the JWT token
            user_id = decoded_token['user_id']  # Extract user ID
            return User.objects.get(id=user_id)  # Get the user from DB
        except Exception as e:
            return AnonymousUser()  # Return anonymous if invalid


class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection for direct chat."""
        self.user = await self.get_user_from_token()
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close()  # Reject the connection if authentication fails
            return

        # Extract recipient ID from URL
        self.recipient_id = self.scope['url_route']['kwargs'].get('user_id')

        # Generate consistent group name for the user pair
        user_ids = sorted([str(self.user.id), str(self.recipient_id)])
        self.room_group_name = f'direct_{user_ids[0]}_{user_ids[1]}'

        # Add the channel to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages for direct chat."""
        if not self.user or isinstance(self.user, AnonymousUser):
            return  # Ignore messages from unauthenticated users

        try:
            data = json.loads(text_data)
            message = data.get('message')
        except json.JSONDecodeError:
            return  # Ignore invalid JSON messages

        if message:
            # Save message to database
            await self.save_message(self.user, self.room_group_name, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.user.username
                }
            )

    async def chat_message(self, event):
        """Sends messages to WebSocket clients."""
        print(f"Sending message to User {self.user.id}: {event['message']}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @database_sync_to_async
    def save_message(self, user, room_name, message):
        """Stores a message in the database."""
        ChatMessage.objects.create(user=user, room_name=room_name, message=message)

    @database_sync_to_async
    def get_user_from_token(self):
        """Extracts the user from the JWT token."""
        query_string = self.scope['query_string'].decode()
        params = dict(q.split('=') for q in query_string.split('&') if '=' in q)
        token_key = params.get('token')

        if not token_key:
            return AnonymousUser()  # No token provided

        try:
            decoded_token = AccessToken(token_key)  # Decode the JWT token
            user_id = decoded_token['user_id']  # Extract user ID
            return User.objects.get(id=user_id)  # Get the user from DB
        except Exception as e:
            return AnonymousUser()
