from rest_framework import serializers
from .models import Ride
from accounts.serializers import UserSerializer


class RideSerializer(serializers.ModelSerializer):
    driver = UserSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = (
            "id", "driver",
            "origin_name", "destination_name",
            "origin_coords", "destination_coords",
            "departure_time", "total_seats", "available_seats",
            "price_per_seat", "instant_book", "vehicle_details", "status",
            "created_at",
        )
        read_only_fields = ("id", "driver", "available_seats", "status", "created_at")

    def create(self, validated_data):
        # Extract driver if passed in save(driver=...) or Meta
        driver = validated_data.pop("driver", None)
        # Handle available_seats default
        total_seats = validated_data.get("total_seats", 1)
        validated_data["available_seats"] = total_seats
        
        return Ride.objects.create(driver=driver, **validated_data)
