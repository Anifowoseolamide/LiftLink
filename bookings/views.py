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

    def patch(self, request, pk):
        try:
            booking = Booking.objects.select_related("ride__driver").get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only the driver of the ride can update the booking status
        if booking.ride.driver != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        allowed = [Booking.ACCEPTED, Booking.REJECTED, Booking.CANCELLED, Booking.COMPLETED]
        if new_status not in allowed:
            return Response(
                {"detail": f"Status must be one of: {', '.join(allowed)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = booking.status
        booking.status = new_status

        # If rejecting / cancelling, restore available seats
        if new_status in [Booking.REJECTED, Booking.CANCELLED] and old_status == Booking.ACCEPTED:
            booking.ride.available_seats += booking.seats_booked
            booking.ride.save(update_fields=["available_seats"])

        booking.save(update_fields=["status"])

        serializer = BookingStatusSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
