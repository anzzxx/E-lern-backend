
from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "room_name", "message", "is_read", "timestamp")
    list_filter = ("is_read", "timestamp")
    search_fields = ("user__username", "room_name", "message")
    ordering = ("-timestamp",)
