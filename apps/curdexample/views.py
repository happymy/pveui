from rest_framework import permissions, filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.viewsets import ActionSerializerMixin
from apps.common.mixins import AuditOwnerPopulateMixin, SoftDeleteMixin
from .models import Example
from .serializers import (
    ExampleListSerializer,
    ExampleDetailSerializer,
    ExampleCreateSerializer,
    ExampleUpdateSerializer,
)


class ExampleViewSet(AuditOwnerPopulateMixin, SoftDeleteMixin, ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = Example.objects.all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated]

    # 兜底
    serializer_class = ExampleDetailSerializer

    # 按动作切换
    list_serializer_class = ExampleListSerializer
    retrieve_serializer_class = ExampleDetailSerializer
    create_serializer_class = ExampleCreateSerializer
    update_serializer_class = ExampleUpdateSerializer
    partial_update_serializer_class = ExampleUpdateSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'owner_organization']
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name', 'price', 'created_at']

