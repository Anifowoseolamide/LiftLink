from django.contrib import admin
from .models import Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id", "driver", "origin_name", "destination_name", "departure_time", "available_seats", "status")
    list_filter = ("status",)
    search_fields = ("origin_name", "destination_name", "driver__username")
    ordering = ("departure_time",)
