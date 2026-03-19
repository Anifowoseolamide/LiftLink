from django.urls import path
from .views import ConversationHistoryView

urlpatterns = [
    path("<int:other_user_id>/", ConversationHistoryView.as_view(), name="message-history"),
]
