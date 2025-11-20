from django.contrib import admin
from .models import GuestSession, GuestMessage


@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'nickname', 'app_id', 'status', 'assigned_to', 'last_message_at']
    list_filter = ['app_id', 'status']
    search_fields = ['session_id', 'nickname', 'visitor_id', 'contact']
    readonly_fields = ['session_id', 'secret_token', 'last_message', 'last_message_at']


@admin.register(GuestMessage)
class GuestMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender_type', 'message_type', 'is_read', 'created_at']
    list_filter = ['sender_type', 'message_type', 'is_read']
    search_fields = ['session__session_id', 'content']
    readonly_fields = ['session', 'sender', 'sender_type', 'message_type', 'content']


