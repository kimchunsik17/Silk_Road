import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, User
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
        
        room_users_ids = [int(uid) for uid in self.room_name.split('_')]
        # Determine the receiver_id by finding the user_id in room_users_ids that is not the sender.id
        receiver_id = next((uid for uid in room_users_ids if uid != sender.id), None)
        
        if receiver_id is None:
            # This case should ideally not happen if room_name always contains two distinct user IDs
            print(f"Error: Could not determine receiver_id from room_name: {self.room_name} for sender: {sender.id}")
            return # Or raise an exception

        await self.save_message(sender.id, receiver_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender.id,
                'sender_username': sender.username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender_username']
        sender_id = event['sender_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username,
            'sender_id': sender_id
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        Chat.objects.create(sender=sender, receiver=receiver, message=message)
