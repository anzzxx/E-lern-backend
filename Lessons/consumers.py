import json
import logging
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db.models import Prefetch
from .models import CourseComment

User = get_user_model()
logger = logging.getLogger(__name__)

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        self.user = await self.get_user_from_token()
    
        if not self.user or isinstance(self.user, AnonymousUser):
            logger.warning(f"Authentication failed for token: {self.scope.get('query_string')}")
            await self.close(code=4001, reason="Authentication failed")
            return

        self.course_id = self.scope['url_route']['kwargs']['lesson_id']
        self.room_group_name = f'chat_{self.course_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_previous_messages()

    async def disconnect(self, close_code):
        """Leave room group."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages with reply support."""
        if not self.user or isinstance(self.user, AnonymousUser):
            return

        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            reply_to = text_data_json.get('replyTo')
            reply_to_username = text_data_json.get('replyToUsername')
            reply_to_message = text_data_json.get('replyToMessage')
            
            if not message or not isinstance(message, str):
                return
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            return

        # Extract mentions
        mentions = []
        words = message.split()
        for word in words:
            if word.startswith('@') and len(word) > 1:
                username = word[1:]
                if await self.user_exists(username):
                    mentions.append(username)

        # Save message to database
        chat_message = await self.save_message(
            user=self.user,
            message=message,
            course_id=self.course_id,
            reply_to=reply_to,
            mentions=mentions
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': str(chat_message.id),
                'message': message,
                'username': self.user.username,
                'avatar': self.user.profile_picture.url if hasattr(self.user, 'profile_picture') and self.user.profile_picture else '',
                'mentions': mentions,
                'replyTo': reply_to,
                'replyToUsername': reply_to_username,
                'replyToMessage': reply_to_message,
                'created_at': chat_message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        """Send message to WebSocket with all metadata."""
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'username': event['username'],
            'avatar': event['avatar'],
            'mentions': event['mentions'],
            'replyTo': event.get('replyTo'),
            'replyToUsername': event.get('replyToUsername'),
            'replyToMessage': event.get('replyToMessage'),
            'created_at': event.get('created_at'),
        }))

    @database_sync_to_async
    def get_user_from_token(self):
        """Extracts user from JWT token."""
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token_key = params.get('token', [None])[0]

        if not token_key:
            logger.warning("No token provided in query string")
            return AnonymousUser()

        try:
            decoded_token = AccessToken(token_key)
            user_id = decoded_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.error(f"Token validation failed: {str(e)}")
            return AnonymousUser()

    @database_sync_to_async
    def user_exists(self, username):
        """Check if a user with the given username exists."""
        return User.objects.filter(username=username).exists()

    @database_sync_to_async
    def save_message(self, user, message, course_id, reply_to=None, mentions=None):
        """Save message to database with reply and mention info."""
        reply_to_obj = None
        if reply_to:
            try:
                reply_to_obj = CourseComment.objects.get(id=reply_to)
            except CourseComment.DoesNotExist:
                logger.warning(f"Reply-to comment with ID {reply_to} does not exist")
                pass

        return CourseComment.objects.create(
            user=user,
            course_id=course_id,
            message=message,
            reply_to=reply_to_obj,
            mentions=mentions or []
        )

    @database_sync_to_async
    def get_previous_messages(self, limit=50):
        """Retrieve previous messages from database with related objects prefetched."""
        messages = CourseComment.objects.filter(
            course_id=self.course_id
        ).select_related('user').prefetch_related(
            Prefetch('reply_to', queryset=CourseComment.objects.select_related('user'))
        ).order_by('-created_at')[:limit]
        
        return list(messages[::-1])  # Reverse to get oldest first

    async def send_previous_messages(self):
        """Send previous messages to the newly connected client."""
        messages = await self.get_previous_messages()
        
        for message in messages:
            reply_to_username = None
            reply_to_message = None
            reply_to_id = None
            
            if message.reply_to:
                try:
                    reply_to_id = str(message.reply_to.id)
                    reply_to_username = message.reply_to.user.username if message.reply_to.user else None
                    reply_to_message = message.reply_to.message if message.reply_to else None
                except AttributeError as e:
                    logger.error(f"Error accessing reply_to fields: {str(e)}")
                    reply_to_id = None
                    reply_to_username = None
                    reply_to_message = None

            await self.send(text_data=json.dumps({
                'id': str(message.id),
                'message': message.message,
                'username': message.user.username,
                'avatar': message.user.profile_picture.url if hasattr(message.user, 'profile_picture') and message.user.profile_picture else '',
                'mentions': message.mentions,
                'replyTo': reply_to_id,
                'replyToUsername': reply_to_username,
                'replyToMessage': reply_to_message,
                'created_at': message.created_at.isoformat(),
            }))