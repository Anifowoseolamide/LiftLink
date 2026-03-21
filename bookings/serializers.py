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
        from django.db.models import F
        from wallet.models import Wallet, EscrowRecord
        
        ride: Ride = validated_data["ride"]
        seats = validated_data.get("seats_booked", 1)
        
        # Lock row to prevent double-booking
        ride = Ride.objects.select_for_update().get(pk=ride.pk)
        if ride.available_seats < seats:
            raise serializers.ValidationError(
                {"seats_booked": "Not enough seats (concurrent booking conflict)."}
            )
            
        rider = self.context["request"].user
        amount = ride.price_per_seat * seats
        
        # Access and lock wallet
        try:
            wallet = Wallet.objects.select_for_update().get(user=rider)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"detail": "Wallet not found for this user."})
            
        if wallet.balance < amount:
            raise serializers.ValidationError({"detail": "Insufficient wallet balance."})
            
        # Deduct from wallet
        wallet.balance = F('balance') - amount
        wallet.save(update_fields=['balance'])
        
        # Decrease available seats
        ride.available_seats = F('available_seats') - seats
        ride.save(update_fields=["available_seats"])
        
        validated_data["rider"] = rider
        booking = super().create(validated_data)
        
        # Hold in escrow
        EscrowRecord.objects.create(
            booking=booking,
            amount=amount,
            status=EscrowRecord.Status.HELD
        )
        
        return booking

class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "status")
