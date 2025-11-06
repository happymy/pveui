"""操作日志 URL 配置。"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperationLogViewSet, LoginLogViewSet

router = DefaultRouter()
router.register(r'logs', OperationLogViewSet, basename='operation-log')
router.register(r'login-logs', LoginLogViewSet, basename='login-log')

urlpatterns = [
    path('', include(router.urls)),
]

