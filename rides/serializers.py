from rest_framework import serializers
from .models import Ride
from accounts.serializers import UserSerializer


class RideSerializer(serializers.ModelSerializer):
    driver = UserSerializer(read_only=True)
    driver_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Ride
        fields = (
            "id", "driver", "driver_id",
            "origin_name", "destination_name",
            "origin_coords", "destination_coords",
            "departure_time", "total_seats", "available_seats",
            "price_per_seat", "vehicle_details", "status",
            "created_at",
        )
        read_only_fields = ("id", "driver", "available_seats", "status", "created_at")

    def create(self, validated_data):
        # available_seats defaults to total_seats on creation
        validated_data["available_seats"] = validated_data["total_seats"]
        return super().create(validated_data)
