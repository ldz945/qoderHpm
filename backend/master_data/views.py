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
    filterset_fields = ['employee_code', 'department', 'source', 'is_external']
    search_fields = ['employee_name', 'employee_code', 'department']
    ordering_fields = ['employee_code', 'employee_name', 'created_at']
    ordering = ['employee_code']


class ResourceViewSet(viewsets.ModelViewSet):
    """资源视图集"""
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_fields = ['resource_code', 'resource_type', 'enabled']
    search_fields = ['resource_name', 'resource_code', 'short_name']
    ordering_fields = ['resource_code', 'resource_name', 'created_at']
    ordering = ['resource_code']


class PriceHeaderViewSet(viewsets.ModelViewSet):
    """价格表头视图集"""
    queryset = PriceHeader.objects.all()
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
    filterset_fields = ['header', 'resource_type', 'resource_code']
    ordering_fields = ['resource_code', 'created_at']
    ordering = ['resource_code']
