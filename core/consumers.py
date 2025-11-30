import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']
        
        room_users = self.room_name.split('_')
        receiver_id = int(room_users[0]) if int(room_users[1]) == sender.id else int(room_users[1])

        await self.save_message(sender.id, receiver_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': sender.username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender_username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        from .models import Chat, User  # Import models here
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        Chat.objects.create(sender=sender, receiver=receiver, message=message)
