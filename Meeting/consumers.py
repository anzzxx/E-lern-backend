import json
import uuid
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class MeetingConsumer(AsyncWebsocketConsumer):
    active_rooms = {}
    count=0
    async def connect(self):
        
        try:
            
            self.user = await self.get_user_from_token()
            if not self.user or isinstance(self.user, AnonymousUser):
                await self.close(code=4003)  # Unauthorized
                return

            self.room_name = self.scope['url_route']['kwargs'].get('meeting_id')
            if not self.room_name:
                await self.close(code=4000)  # Invalid room
                return

            self.room_group_name = f'meeting_{self.room_name}'
            self.session_id = str(uuid.uuid4())

            await self.initialize_room()
            await self.register_new_connection()

            await self.accept()
           
            await self.broadcast_user_list()

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close(code=4002)  # Internal error

    async def initialize_room(self):
        if self.room_name not in self.active_rooms:
            self.active_rooms[self.room_name] = {'users': {}, 'last_user_list': None}

    async def register_new_connection(self):
        user_info = {
            'channel_name': self.channel_name,
            'username': self.user.username,
            'user_id': self.user.id,
            'session_id': self.session_id  # Keep session ID but exclude it from user list broadcast
        }
        self.active_rooms[self.room_name]['users'][self.channel_name] = user_info
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_name') and self.room_name in self.active_rooms:
                room = self.active_rooms[self.room_name]
                if self.channel_name in room['users']:
                    del room['users'][self.channel_name]
                    if not room['users']:
                        del self.active_rooms[self.room_name]
                    else:
                        await self.broadcast_user_list()
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"Disconnection error: {e}")

    async def broadcast_user_list(self):
        try:
            if self.room_name in self.active_rooms:
                room = self.active_rooms[self.room_name]

                users = []
                existing_user_ids = set()  # Track existing user IDs to avoid duplicates

                for user in room['users'].values():
                    if user['user_id'] not in existing_user_ids:  # Ensure user isn't already added
                        users.append(
                            {'channel_name': user['channel_name'], 'username': user['username'], 'user_id': user['user_id']}
                        )
                        existing_user_ids.add(user['user_id'])

                await self.channel_layer.group_send(
                    self.room_group_name, {'type': 'user_list_update', 'users': users}
                )
        except Exception as e:
            print(f"Error broadcasting user list: {e}")


    async def user_list_update(self, event):
        await self.send(text_data=json.dumps({'type': 'user_list', 'users': event['users']}))

    async def receive(self, text_data):
        """Handle WebRTC signaling messages (offer, answer, candidate)"""
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type in ['offer', 'answer', 'candidate']:
            await self.channel_layer.group_send(
                self.room_group_name, {'type': 'webrtc_signal', 'data': data}
            )

    async def webrtc_signal(self, event):
        """Forward WebRTC signaling messages to all peers"""
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_user_from_token(self):
        try:
            query_string = self.scope.get('query_string', b'').decode()
            params = parse_qs(query_string)
            token_key = params.get('token', [None])[0]
            if not token_key:
                return AnonymousUser()
            decoded_token = AccessToken(token_key)
            user = User.objects.get(id=decoded_token['user_id'])
            return user
        except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
            return AnonymousUser()
