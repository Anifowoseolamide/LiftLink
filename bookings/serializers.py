from rest_framework import serializers
from django.db import transaction
from .models import Booking
from rides.models import Ride
from accounts.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    rider = UserSerializer(read_only=True)
    ride_id = serializers.PrimaryKeyRelatedField(
        queryset=Ride.objects.all(), source="ride", write_only=True
    )
    ride_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id", "rider", "ride_id", "ride_info",
            "seats_booked", "status", "payment_status", "created_at",
        )
        read_only_fields = ("id", "rider", "status", "payment_status", "created_at", "ride_info")

    def get_ride_info(self, obj):
        from rides.serializers import RideSerializer
        return RideSerializer(obj.ride, context=self.context).data

    def validate(self, attrs):
        ride: Ride = attrs["ride"]
        seats = attrs.get("seats_booked", 1)
        if ride.available_seats < seats:
            raise serializers.ValidationError(
                {"seats_booked": f"Only {ride.available_seats} seat(s) available."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        ride: Ride = validated_data["ride"]
        seats = validated_data.get("seats_booked", 1)
        # Lock row to prevent double-booking
        ride = Ride.objects.select_for_update().get(pk=ride.pk)
        if ride.available_seats < seats:
            raise serializers.ValidationError(
                {"seats_booked": "Not enough seats (concurrent booking conflict)."}
            )
        ride.available_seats -= seats
        ride.save(update_fields=["available_seats"])
        validated_data["rider"] = self.context["request"].user
        return super().create(validated_data)


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "status")
