from django.urls import path
from .views import RideListCreateView, RideDetailView, RideStartView, RideCompleteView

urlpatterns = [
    path("", RideListCreateView.as_view(), name="ride-list-create"),
    path("<int:pk>/", RideDetailView.as_view(), name="ride-detail"),
    path("<int:pk>/start/", RideStartView.as_view(), name="ride-start"),
    path("<int:pk>/complete/", RideCompleteView.as_view(), name="ride-complete"),
]
