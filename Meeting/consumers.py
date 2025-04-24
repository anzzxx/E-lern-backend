import json
import uuid
import traceback
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class MeetingConsumer(AsyncWebsocketConsumer):
    active_rooms = {}  # Class-level dictionary to track room states

    async def connect(self):
        """Handle WebSocket connection with authentication and room management."""
        try:
            self.user = await self.get_user_from_token()
            if not self.user or isinstance(self.user, AnonymousUser):
                print("Unauthorized: No valid user or token")
                await self.close(code=4003)  # Unauthorized
                return

            self.room_name = self.scope['url_route']['kwargs'].get('meeting_id')
            if not self.room_name:
                print("Invalid room: meeting_id not found in scope")
                await self.close(code=4000)  # Invalid room
                return

            self.room_group_name = f'meeting_{self.room_name}'
            self.session_id = str(uuid.uuid4())

            # Initialize or get room
            await self.initialize_room()

            # Handle existing connections from same user
            await self.handle_existing_connections()

            # Register new connection
            await self.register_new_connection()

            await self.accept()
            await self.broadcast_user_list()
            await self.notify_user_joined()

        except Exception as e:
            print(f"Connection error: {e}\n{traceback.format_exc()}")
            await self.close(code=4002)  # Internal error

    async def initialize_room(self):
        """Initialize room structure if it doesn't exist."""
        try:
            if self.room_name not in self.active_rooms:
                self.active_rooms[self.room_name] = {
                    'users': {},
                    'last_user_list': None
                }
        except Exception as e:
            print(f"Error initializing room: {e}")
            raise

    async def handle_existing_connections(self):
        """Close existing connections from the same user."""
        try:
            room = self.active_rooms[self.room_name]
            for channel_name, user_info in list(room['users'].items()):
                if user_info['user_id'] == self.user.id and channel_name != self.channel_name:
                    print(f"Closing duplicate connection for user {self.user.id} on channel {channel_name}")
                    await self.channel_layer.send(
                        channel_name,
                        {
                            "type": "websocket.close",
                            "code": 4001,  # Duplicate connection
                            "reason": "New connection opened"
                        }
                    )
                    del room['users'][channel_name]
        except Exception as e:
            print(f"Error handling existing connections: {e}")
            raise

    async def register_new_connection(self):
        """Register the new connection in the room."""
        try:
            user_info = {
                'channel_name': self.channel_name,
                'username': self.user.username,
                'user_id': self.user.id,
                'session_id': self.session_id
            }
            self.active_rooms[self.room_name]['users'][self.channel_name] = user_info
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"Error registering new connection: {e}")
            raise

    async def disconnect(self, close_code):
        """Clean up on WebSocket disconnection."""
        try:
            if hasattr(self, 'room_name') and self.room_name in self.active_rooms:
                room = self.active_rooms[self.room_name]
                
                if self.channel_name in room['users']:
                    del room['users'][self.channel_name]
                    if not room['users']:
                        del self.active_rooms[self.room_name]
                    else:
                        await self.notify_user_left()
                        await self.broadcast_user_list()

                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"Disconnection error: {e}")

    async def notify_user_joined(self):
        """Notify group about new user joining."""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.user.username,
                    'user_id': self.user.id,
                    'channel_name': self.channel_name
                }
            )
        except Exception as e:
            print(f"Error notifying user joined: {e}")
            raise

    async def notify_user_left(self):
        """Notify group about user leaving."""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.user.username,
                    'user_id': self.user.id,
                    'channel_name': self.channel_name
                }
            )
        except Exception as e:
            print(f"Error notifying user left: {e}")
            raise

    async def broadcast_user_list(self):
        """Send updated user list to all clients in the room."""
        try:
            if self.room_name in self.active_rooms:
                room = self.active_rooms[self.room_name]
                current_users = sorted(
                    (user['channel_name'], user['username'], user['user_id'])
                    for user in room['users'].values()
                )

                if room['last_user_list'] != current_users:
                    room['last_user_list'] = current_users
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_list_update',
                            'users': [
                                {
                                    'channel_name': ch,
                                    'username': uname,
                                    'user_id': uid
                                }
                                for ch, uname, uid in current_users
                            ]
                        }
                    )
        except Exception as e:
            print(f"Error broadcasting user list: {e}")
            raise

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type in ['webrtc_offer', 'webrtc_answer', 'ice_candidate', 'connection_established']:
                target_channel = data.get('target_channel_name')
                if target_channel and target_channel in self.active_rooms[self.room_name]['users']:
                    await self.channel_layer.send(
                        target_channel,
                        {
                            'type': message_type,
                            'sender_channel_name': self.channel_name,
                            'data': data.get('data')
                        }
                    )
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_id': event['user_id'],
            'channel_name': event['channel_name']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_id': event['user_id'],
            'channel_name': event['channel_name']
        }))

    async def user_list_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users']
        }))

    async def webrtc_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'webrtc_offer',
            'sender_channel_name': event['sender_channel_name'],
            'offer': event['data']
        }))

    async def webrtc_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'webrtc_answer',
            'sender_channel_name': event['sender_channel_name'],
            'answer': event['data']
        }))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'sender_channel_name': event['sender_channel_name'],
            'candidate': event['data']
        }))

    async def connection_established(self, event):
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'sender_channel_name': event['sender_channel_name']
        }))

    @database_sync_to_async
    def get_user_from_token(self):
        try:
            query_string = self.scope.get('query_string', b'').decode()
            params = parse_qs(query_string)
            token_key = params.get('token', [None])[0]
            if not token_key:
                print("No token provided in query string")
                return AnonymousUser()
            decoded_token = AccessToken(token_key)
            user = User.objects.get(id=decoded_token['user_id'])
            print(f"Authenticated user: {user.username} (id: {user.id})")
            return user
        except (InvalidToken, TokenError, User.DoesNotExist, KeyError) as e:
            print(f"Authentication error: {e}")
            return AnonymousUser()
        except Exception as e:
            print(f"Unexpected authentication error: {e}")
            return AnonymousUser()