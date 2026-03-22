from rest_framework import generics, filters, permissions
from .models import Ride
from .serializers import RideSerializer
from accounts.models import User


class RideListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/rides/  – List rides (filter by origin, destination, date, seats).
    POST /api/rides/  – Publish a new ride (DRIVER only).
    """
    serializer_class = RideSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        qs = Ride.objects.filter(status=Ride.PENDING, departure_time__gte=timezone.now()).select_related("driver")
        params = self.request.query_params

        origin = params.get("origin")
        destination = params.get("destination")
        date = params.get("date")          # format: YYYY-MM-DD
        seats = params.get("seats")
        max_price = params.get("max_price")
        is_verified_driver = params.get("is_verified_driver")
        instant_book = params.get("instant_book")

        if origin:
            qs = qs.filter(origin_name__icontains=origin)
        if destination:
            qs = qs.filter(destination_name__icontains=destination)
        if date:
            qs = qs.filter(departure_time__date=date)
        if seats:
            try:
                qs = qs.filter(available_seats__gte=int(seats))
            except (ValueError, TypeError):
                pass
        if max_price:
            try:
                qs = qs.filter(price_per_seat__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        if is_verified_driver and is_verified_driver.lower() in ("true", "1"):
            qs = qs.filter(driver__driver_verification_status=User.VERIFICATION_ACTIVE)
        if instant_book and instant_book.lower() in ("true", "1"):
            qs = qs.filter(instant_book=True)
            
        return qs

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        if self.request.user.role != User.DRIVER:
            raise PermissionDenied("Only drivers can publish rides.")
        if self.request.user.driver_verification_status != User.VERIFICATION_ACTIVE:
            raise PermissionDenied("Your driver profile must be verified before publishing rides.")
        serializer.save(driver=self.request.user)


class RideDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PATCH / DELETE /api/rides/<pk>/"""
    serializer_class = RideSerializer
    queryset = Ride.objects.all()

    permission_classes = [permissions.IsAuthenticated]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

class RideStartView(APIView):
    """POST /api/rides/<pk>/start/ – Driver starts the ride."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk, driver=request.user)
        except Ride.DoesNotExist:
            return Response({"detail": "Ride not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
            
        if ride.status != Ride.PENDING:
            return Response({"detail": "Only PENDING rides can be started."}, status=status.HTTP_400_BAD_REQUEST)
            
        ride.status = Ride.ACTIVE
        ride.save(update_fields=['status'])
        return Response({"detail": "Ride started.", "status": ride.status})

class RideCompleteView(APIView):
    """POST /api/rides/<pk>/complete/ – Driver completes the ride and releases escrow."""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        from django.db.models import F
        from wallet.models import Wallet, EscrowRecord
        from bookings.models import Booking
        
        try:
            ride = Ride.objects.select_for_update().get(pk=pk, driver=request.user)
        except Ride.DoesNotExist:
            return Response({"detail": "Ride not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
            
        if ride.status != Ride.ACTIVE:
            return Response({"detail": "Only ACTIVE rides can be completed."}, status=status.HTTP_400_BAD_REQUEST)
            
        ride.status = Ride.COMPLETED
        ride.save(update_fields=['status'])
        
        # Release Escrow
        accepted_bookings = Booking.objects.filter(ride=ride, status=Booking.ACCEPTED)
        
        for booking in accepted_bookings:
            try:
                escrow = EscrowRecord.objects.select_for_update().get(booking=booking, status=EscrowRecord.Status.HELD)
                driver_wallet, _ = Wallet.objects.get_or_create(user=ride.driver)
                
                driver_wallet.balance = F('balance') + escrow.amount
                driver_wallet.save(update_fields=['balance'])
                
                escrow.status = EscrowRecord.Status.RELEASED
                escrow.save(update_fields=['status'])
                
            except EscrowRecord.DoesNotExist:
                continue
                
        return Response({"detail": "Ride completed and funds released.", "status": ride.status})
