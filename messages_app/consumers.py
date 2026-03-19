import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket: ws/chat/<room_name>/

    room_name format: chat_<uid_low>_<uid_high>  (use Message.get_room_name())
    Clients must connect with a valid JWT via query param: ?token=<access_token>
    """

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive a message from WebSocket client."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        event = data.get("event")
        if event != "send_message":
            return

        sender = self.scope.get("user")
        if sender is None or not sender.is_authenticated:
            await self.send(text_data=json.dumps({"error": "Unauthenticated."}))
            return

        content = data.get("content", "").strip()
        receiver_id = data.get("receiver_id")

        if not content or not receiver_id:
            return

        # Persist message
        message = await self._save_message(sender, receiver_id, content)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message["id"],
                "sender_id": sender.id,
                "sender_name": sender.get_full_name() or sender.username,
                "content": content,
                "timestamp": message["timestamp"],
            },
        )

    async def chat_message(self, event):
        """Forward group message to WebSocket client."""
        await self.send(text_data=json.dumps({
            "event": "receive_message",
            "message_id": event["message_id"],
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "content": event["content"],
            "timestamp": event["timestamp"],
        }))

    @database_sync_to_async
    def _save_message(self, sender, receiver_id, content):
        from .models import Message
        from accounts.models import User
        try:
            receiver = User.objects.get(pk=receiver_id)
        except User.DoesNotExist:
            raise ValueError("Receiver not found.")
        msg = Message.objects.create(sender=sender, receiver=receiver, content=content)
        return {"id": msg.id, "timestamp": msg.timestamp.isoformat()}
