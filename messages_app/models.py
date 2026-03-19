from django.db import models
from django.conf import settings


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    @staticmethod
    def get_room_name(user_id_1, user_id_2):
        """Deterministic room name for two users."""
        return f"chat_{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}"

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:40]}"
