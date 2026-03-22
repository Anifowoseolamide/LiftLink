from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    """POST /api/auth/login  – returns JWT access + refresh tokens and user info."""
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """POST /api/auth/logout  – blacklist the refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /api/auth/profile  – authenticated user's own profile."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


from .models import Review
from .serializers import ReviewSerializer
from bookings.models import Booking

class ReviewCreateView(generics.CreateAPIView):
    """POST /api/auth/reviews/ – Rider rates a driver after a completed ride."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        from rides.models import Ride
        
        ride_id = self.request.data.get("ride")
        try:
            ride = Ride.objects.get(pk=ride_id)
        except Ride.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"ride": "Ride not found."})
            
        if ride.status != Ride.COMPLETED:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"ride": "Can only rate completed rides."})
            
        has_booking = Booking.objects.filter(ride=ride, rider=self.request.user, status=Booking.ACCEPTED).exists()
        if not has_booking:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "You did not participate in this completed ride."})
            
        serializer.save(rider=self.request.user, driver=ride.driver)
        
        from django.db.models import Avg
        avg_rating = Review.objects.filter(driver=ride.driver).aggregate(Avg('rating'))['rating__avg']
        if avg_rating is not None:
            ride.driver.rating = round(avg_rating, 2)
            ride.driver.save(update_fields=['rating'])
