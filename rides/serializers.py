from rest_framework import serializers
from .models import Ride
from accounts.serializers import DriverPublicSerializer


class RideSerializer(serializers.ModelSerializer):
    driver = DriverPublicSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = (
            "id", "driver",
            "origin_name", "destination_name",
            "origin_coords", "destination_coords",
            "departure_time", "end_time", "total_seats", "available_seats",
            "price_per_seat", "instant_book", "vehicle_details", "status",
            "created_at",
        )
        read_only_fields = ("id", "driver", "available_seats", "status", "created_at")

    def create(self, validated_data):
        driver = validated_data.pop("driver", None)
        total_seats = validated_data.get("total_seats", 1)
        validated_data["available_seats"] = total_seats
        return Ride.objects.create(driver=driver, **validated_data)
