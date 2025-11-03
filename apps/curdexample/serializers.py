from apps.common.serializers import BaseModelSerializer
from .models import Example


class ExampleListSerializer(BaseModelSerializer):
    class Meta:
        model = Example
        fields = ['id', 'name', 'price', 'is_active']


class ExampleDetailSerializer(BaseModelSerializer):
    class Meta:
        model = Example
        fields = '__all__'


class ExampleCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Example
        fields = ['name', 'description', 'price', 'is_active', 'owner_organization', 'remark']


class ExampleUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Example
        fields = ['name', 'description', 'price', 'is_active', 'owner_organization', 'remark']


