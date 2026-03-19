import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket: ws/tracking/<ride_id>/

    The Driver sends GPS location updates; all connected Riders in the same
    ride room receive them in real-time.

    Expected payload from driver:
        {"event": "location_update", "lat": 6.5244, "lng": 3.3792}

    Broadcast payload to riders:
        {"event": "driver_location", "lat": ..., "lng": ..., "ride_id": ...}
    """

    async def connect(self):
        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]
        self.room_group_name = f"tracking_{self.ride_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("event") != "location_update":
            return

        lat = data.get("lat")
        lng = data.get("lng")

        if lat is None or lng is None:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "driver_location",
                "lat": lat,
                "lng": lng,
                "ride_id": self.ride_id,
            },
        )

    async def driver_location(self, event):
        await self.send(text_data=json.dumps({
            "event": "driver_location",
            "lat": event["lat"],
            "lng": event["lng"],
            "ride_id": event["ride_id"],
        }))
