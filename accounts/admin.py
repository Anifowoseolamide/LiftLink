from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "driver_verification_status", "phone", "rating", "is_staff")
    list_filter = ("role", "driver_verification_status", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("RideShare Info", {"fields": ("role", "driver_verification_status", "phone", "rating", "avatar_url")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RideShare Info", {"fields": ("role", "driver_verification_status", "phone")}),
    )
