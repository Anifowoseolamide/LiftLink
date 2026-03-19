from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """GET /api/notifications/ – list all notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(APIView):
    """PATCH /api/notifications/<pk>/read/ – mark a notification as read."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        n.read = True
        n.save(update_fields=["read"])
        return Response(NotificationSerializer(n).data)


def send_notification(user, title, body):
    """Utility: create a Notification record for a user (called from any app)."""
    return Notification.objects.create(user=user, title=title, body=body)
