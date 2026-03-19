from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "rider", "ride", "seats_booked", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status")
    search_fields = ("rider__username", "ride__origin_name", "ride__destination_name")
