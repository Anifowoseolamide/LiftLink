from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingSerializer, BookingStatusSerializer
from rides.models import Ride


class BookingCreateView(generics.CreateAPIView):
    """POST /api/bookings/ – Rider creates a booking."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(rider=self.request.user)


class BookingListView(generics.ListAPIView):
    """GET /api/bookings/ – List current user's bookings (as rider or driver)."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Drivers see bookings for their rides; riders see their own bookings
        if user.role == "DRIVER":
            return Booking.objects.filter(ride__driver=user).select_related("rider", "ride")
        return Booking.objects.filter(rider=user).select_related("rider", "ride")


class BookingStatusUpdateView(APIView):
    """PATCH /api/bookings/<pk>/status/ – Driver accepts or rejects a booking."""
    permission_classes = [permissions.IsAuthenticated]

    from django.db import transaction
    
    @transaction.atomic
    def patch(self, request, pk):
        from django.db.models import F
        from wallet.models import Wallet, EscrowRecord
        
        try:
            booking = Booking.objects.select_related("ride__driver", "rider").select_for_update().get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        is_rider = request.user == booking.rider
        is_driver = request.user == booking.ride.driver

        if not (is_driver or is_rider):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        allowed = [Booking.ACCEPTED, Booking.REJECTED, Booking.CANCELLED, Booking.COMPLETED]
        if new_status not in allowed:
            return Response({"detail": f"Status must be one of: {', '.join(allowed)}."}, status=status.HTTP_400_BAD_REQUEST)

        if is_rider and new_status != Booking.CANCELLED:
            return Response({"detail": "Riders can only CANCEL their bookings."}, status=status.HTTP_403_FORBIDDEN)

        if is_driver and new_status not in [Booking.ACCEPTED, Booking.REJECTED]:
            return Response({"detail": "Drivers can only ACCEPT or REJECT bookings."}, status=status.HTTP_403_FORBIDDEN)

        old_status = booking.status
        booking.status = new_status

        # If rejecting / cancelling, restore available seats and handle funds
        if new_status in [Booking.REJECTED, Booking.CANCELLED] and old_status in [Booking.PENDING, Booking.ACCEPTED]:
            ride = Ride.objects.select_for_update().get(pk=booking.ride_id)
            ride.available_seats = F('available_seats') + booking.seats_booked
            ride.save(update_fields=["available_seats"])
            
            try:
                escrow = EscrowRecord.objects.select_for_update().get(booking=booking, status=EscrowRecord.Status.HELD)
                
                from django.utils import timezone
                from datetime import timedelta
                
                is_late_cancel = (
                    is_rider and
                    new_status == Booking.CANCELLED and
                    old_status == Booking.ACCEPTED and
                    (ride.departure_time - timezone.now() < timedelta(hours=2))
                )
                
                if is_late_cancel:
                    penalty = escrow.amount / 2
                    refund = escrow.amount - penalty
                    
                    rider_wallet = Wallet.objects.select_for_update().get(user=booking.rider)
                    rider_wallet.balance = F('balance') + refund
                    rider_wallet.save(update_fields=['balance'])
                    
                    driver_wallet, _ = Wallet.objects.get_or_create(user=ride.driver)
                    driver_wallet.balance = F('balance') + penalty
                    driver_wallet.save(update_fields=['balance'])
                    
                    escrow.status = EscrowRecord.Status.REFUNDED
                    escrow.save(update_fields=['status'])
                else:
                    wallet = Wallet.objects.select_for_update().get(user=booking.rider)
                    wallet.balance = F('balance') + escrow.amount
                    wallet.save(update_fields=['balance'])
                    
                    escrow.status = EscrowRecord.Status.REFUNDED
                    escrow.save(update_fields=['status'])
                    
            except (EscrowRecord.DoesNotExist, Wallet.DoesNotExist):
                pass

        booking.save(update_fields=["status"])
        serializer = BookingStatusSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
