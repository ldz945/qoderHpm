"""
主数据管理 - Views
包含：EmployeeViewSet, ResourceViewSet, PriceHeaderViewSet, PriceLineViewSet
"""

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Resource, PriceHeader, PriceLine
from .serializers import (
    EmployeeSerializer, 
    ResourceSerializer, 
    PriceHeaderSerializer, 
    PriceHeaderListSerializer,
    PriceLineSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """员工视图集"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    required_permissions = {
        'list': ['master_data.employee.read'],
        'retrieve': ['master_data.employee.read'],
        'create': ['master_data.employee.write'],
        'update': ['master_data.employee.write'],
        'partial_update': ['master_data.employee.write'],
        'destroy': ['master_data.employee.write'],
    }
    filterset_fields = ['employee_code', 'department', 'source', 'is_external']
    search_fields = ['employee_name', 'employee_code', 'department']
    ordering_fields = ['employee_code', 'employee_name', 'created_at']
    ordering = ['employee_code']


class ResourceViewSet(viewsets.ModelViewSet):
    """资源视图集"""
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    required_permissions = {
        'list': ['master_data.resource.read'],
        'retrieve': ['master_data.resource.read'],
        'create': ['master_data.resource.write'],
        'update': ['master_data.resource.write'],
        'partial_update': ['master_data.resource.write'],
        'destroy': ['master_data.resource.write'],
    }
    filterset_fields = ['resource_code', 'resource_type', 'enabled']
    search_fields = ['resource_name', 'resource_code', 'short_name']
    ordering_fields = ['resource_code', 'resource_name', 'created_at']
    ordering = ['resource_code']


class PriceHeaderViewSet(viewsets.ModelViewSet):
    """价格表头视图集"""
    queryset = PriceHeader.objects.all()
    required_permissions = {
        'list': ['master_data.price.read'],
        'retrieve': ['master_data.price.read'],
        'create': ['master_data.price.write'],
        'update': ['master_data.price.write'],
        'partial_update': ['master_data.price.write'],
        'destroy': ['master_data.price.write'],
    }
    filterset_fields = ['version_name', 'currency', 'status']
    search_fields = ['version_name']
    ordering_fields = ['version_no', 'created_at']
    ordering = ['-version_no']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PriceHeaderListSerializer
        return PriceHeaderSerializer


class PriceLineViewSet(viewsets.ModelViewSet):
    """价格表明细视图集"""
    queryset = PriceLine.objects.all()
    serializer_class = PriceLineSerializer
    required_permissions = {
        'list': ['master_data.price.read'],
        'retrieve': ['master_data.price.read'],
        'create': ['master_data.price.write'],
        'update': ['master_data.price.write'],
        'partial_update': ['master_data.price.write'],
        'destroy': ['master_data.price.write'],
    }
    filterset_fields = ['header', 'resource_type', 'resource_code']
    ordering_fields = ['resource_code', 'created_at']
    ordering = ['resource_code']
