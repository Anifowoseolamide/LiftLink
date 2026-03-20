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
        qs = Ride.objects.filter(status=Ride.PENDING).select_related("driver")
        params = self.request.query_params

        origin = params.get("origin")
        destination = params.get("destination")
        date = params.get("date")          # format: YYYY-MM-DD
        seats = params.get("seats")

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
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != User.DRIVER:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only drivers can publish rides.")
        serializer.save(driver=self.request.user)


class RideDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PATCH / DELETE /api/rides/<pk>/"""
    serializer_class = RideSerializer
    queryset = Ride.objects.all()

    permission_classes = [permissions.IsAuthenticated]
