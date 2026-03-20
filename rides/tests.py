from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from .models import Ride

class RidePermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rider_user = User.objects.create_user(
            username="rider", 
            password="password123", 
            role=User.RIDER
        )
        self.driver_user = User.objects.create_user(
            username="driver", 
            password="password123", 
            role=User.DRIVER
        )
        self.ride = Ride.objects.create(
            driver=self.driver_user,
            origin_name="Lekki",
            destination_name="Ikeja",
            departure_time="2026-03-25T08:00:00Z",
            total_seats=4,
            available_seats=4,
            price_per_seat=1000
        )
        self.list_url = reverse("ride-list-create")
        self.detail_url = reverse("ride-detail", kwargs={"pk": self.ride.pk})

    def test_list_rides_unauthenticated(self):
        """Test that listing rides requires authentication."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ride_detail_unauthenticated(self):
        """Test that viewing ride details requires authentication."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_rides_authenticated(self):
        """Test that authenticated users can list rides."""
        self.client.force_authenticate(user=self.rider_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_ride_as_rider_fails(self):
        """Test that riders cannot offer rides."""
        self.client.force_authenticate(user=self.rider_user)
        data = {
            "origin_name": "Test Origin",
            "destination_name": "Test Destination",
            "departure_time": "2026-03-25T08:00:00Z",
            "total_seats": 3,
            "price_per_seat": "500.00",
            "vehicle_details": {"make": "Toyota", "model": "Corolla", "plate": "ABC-123"},
            "origin_coords": {"lat": 6.4, "lng": 3.4},
            "destination_coords": {"lat": 6.6, "lng": 3.3}
        }
        response = self.client.post(self.list_url, data, format="json")
        if response.status_code == 400:
            print(f"RIDER FAIL TEST 400: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "Only drivers can publish rides.")

    def test_offer_ride_as_driver_success(self):
        """Test that drivers can offer rides."""
        self.client.force_authenticate(user=self.driver_user)
        data = {
            "origin_name": "Test Origin",
            "destination_name": "Test Destination",
            "departure_time": "2026-03-25T08:00:00Z",
            "total_seats": 3,
            "price_per_seat": "500.00",
            "vehicle_details": {"make": "Toyota", "model": "Corolla", "plate": "ABC-123"},
            "origin_coords": {"lat": 6.4, "lng": 3.4},
            "destination_coords": {"lat": 6.6, "lng": 3.3}
        }
        response = self.client.post(self.list_url, data, format="json")
        if response.status_code == 400:
            print(f"DRIVER SUCCESS TEST 400: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
