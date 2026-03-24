from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()
    total_trips = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "username", "first_name", "last_name", "email", "phone",
            "role", "driver_verification_status", "rating", "avatar_url",
            "wallet_balance", "total_trips",
        )
        read_only_fields = ("id", "driver_verification_status", "rating", "wallet_balance", "total_trips")

    def get_wallet_balance(self, obj):
        try:
            return str(obj.wallet.balance)
        except Exception:
            return "0.00"

    def get_total_trips(self, obj):
        if obj.role == User.DRIVER:
            return obj.offered_rides.filter(status="COMPLETED").count()
        else:
            from bookings.models import Booking
            return Booking.objects.filter(rider=obj, status=Booking.COMPLETED).count()


class DriverPublicSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the nested driver object in Rides."""
    total_trips = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "rating", "avatar_url",
                  "driver_verification_status", "total_trips")

    def get_total_trips(self, obj):
        return obj.offered_rides.filter(status="COMPLETED").count()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "phone", "role", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        from django.db import transaction
        from wallet.models import Wallet, Transaction
        import uuid
        
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            
            # Create a wallet and add welcome bonus
            Wallet.objects.create(user=user, balance=5000.00)
            
            # Record the welcome bonus transaction
            Transaction.objects.create(
                user=user,
                transaction_type=Transaction.DEPOSIT,
                amount=5000.00,
                reference=f"WELCOME-{uuid.uuid4().hex[:10].upper()}",
                status=Transaction.SUCCESS,
                meta={"note": "Welcome Bonus"}
            )
            
        return user


from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("id", "ride", "rating", "comment", "created_at", "reviewer_name")

    def get_reviewer_name(self, obj):
        return obj.rider.get_full_name() or obj.rider.username
