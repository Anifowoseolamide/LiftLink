from django.db import models
from django.conf import settings
from rides.models import Ride


class Booking(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
        (COMPLETED, "Completed"),
    ]

    PAY_PENDING = "PENDING"
    PAY_ESCROWED = "ESCROWED"
    PAY_RELEASED = "RELEASED"
    PAY_REFUNDED = "REFUNDED"
    PAYMENT_STATUS_CHOICES = [
        (PAY_PENDING, "Pending"),
        (PAY_ESCROWED, "Escrowed"),
        (PAY_RELEASED, "Released"),
        (PAY_REFUNDED, "Refunded"),
    ]

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="bookings")
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    seats_booked = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAY_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.pk} – {self.rider} on {self.ride}"
