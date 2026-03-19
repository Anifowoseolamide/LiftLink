from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "content_preview", "timestamp", "read_status")
    list_filter = ("read_status",)
    search_fields = ("sender__username", "receiver__username", "content")

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = "Content"
