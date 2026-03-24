from django.db import models
from django.conf import settings


class Ride(models.Model):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACTIVE, "Active"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offered_rides",
    )
    origin_name = models.CharField(max_length=255)
    destination_name = models.CharField(max_length=255)
    origin_coords = models.JSONField(default=dict, blank=True)       # {"lat": ..., "lng": ...}
    destination_coords = models.JSONField(default=dict, blank=True)
    departure_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    total_seats = models.PositiveIntegerField(default=1)
    available_seats = models.PositiveIntegerField(default=1)
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    instant_book = models.BooleanField(default=False)
    vehicle_details = models.JSONField(default=dict, blank=True)     # {"make": ..., "model": ..., "plate": ...}
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.origin_name} → {self.destination_name} ({self.departure_time:%Y-%m-%d %H:%M})"
