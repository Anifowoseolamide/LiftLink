from rest_framework import generics, permissions
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer


class ConversationHistoryView(generics.ListAPIView):
    """GET /api/messages/<other_user_id>/ – Retrieve chat history between two users."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        other_id = self.kwargs["other_user_id"]
        me = self.request.user
        qs = Message.objects.filter(
            Q(sender=me, receiver_id=other_id) | Q(sender_id=other_id, receiver=me)
        ).select_related("sender", "receiver")
        # Mark incoming messages as read
        qs.filter(receiver=me, read_status=False).update(read_status=True)
        return qs
