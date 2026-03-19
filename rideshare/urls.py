"""
Root URL configuration for RideShare Lagos.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/", include("accounts.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Core resources
    path("api/rides/", include("rides.urls")),
    path("api/bookings/", include("bookings.urls")),
    # Wallet & payments
    path("api/wallet/", include("wallet.urls")),
    # Messaging (REST history)
    path("api/messages/", include("messages_app.urls")),
    # Notifications
    path("api/notifications/", include("notifications.urls")),
]
