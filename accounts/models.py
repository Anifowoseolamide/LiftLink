from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    RIDER = "RIDER"
    DRIVER = "DRIVER"
    ROLE_CHOICES = [(RIDER, "Rider"), (DRIVER, "Driver")]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=RIDER)
    phone = models.CharField(max_length=20, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
