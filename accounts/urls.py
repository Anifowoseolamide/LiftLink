from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, ReviewCreateView, ReviewListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("reviews/", ReviewCreateView.as_view(), name="auth-reviews-create"),
    path("reviews/<int:user_id>/", ReviewListView.as_view(), name="auth-reviews-list"),
]
