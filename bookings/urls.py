from django.urls import path
from .views import BookingCreateView, BookingListView, BookingStatusUpdateView

urlpatterns = [
    path("", BookingListView.as_view(), name="booking-list"),
    path("create/", BookingCreateView.as_view(), name="booking-create"),
    path("<int:pk>/status/", BookingStatusUpdateView.as_view(), name="booking-status"),
]
