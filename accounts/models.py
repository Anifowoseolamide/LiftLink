from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    RIDER = "RIDER"
    DRIVER = "DRIVER"
    ROLE_CHOICES = [(RIDER, "Rider"), (DRIVER, "Driver")]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=RIDER)
    is_driver_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class Review(models.Model):
    ride = models.ForeignKey("rides.Ride", on_delete=models.CASCADE, related_name="reviews")
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="given_reviews")
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_reviews")
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("ride", "rider")

    def __str__(self):
        return f"{self.rating} stars for {self.driver} by {self.rider}"
