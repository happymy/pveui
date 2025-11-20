"""客服系统 URL。"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GuestSessionViewSet,
    GuestMessageViewSet,
    guest_session_init,
    guest_message_send,
    guest_message_history,
)

router = DefaultRouter()
router.register(r'sessions', GuestSessionViewSet, basename='cs-session')
router.register(r'messages', GuestMessageViewSet, basename='cs-message')

urlpatterns = [
    path('', include(router.urls)),
    path('guest/session/', guest_session_init, name='guest-session-init'),
    path('guest/messages/', guest_message_send, name='guest-message-send'),
    path('guest/messages/history/', guest_message_history, name='guest-message-history'),
]


