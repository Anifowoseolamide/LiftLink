"""
WebSocket URL routing for RideShare Lagos.
"""

from django.urls import path
from messages_app.consumers import ChatConsumer
from tracking.consumers import TrackingConsumer

websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
    path("ws/tracking/<int:ride_id>/", TrackingConsumer.as_asgi()),
]
