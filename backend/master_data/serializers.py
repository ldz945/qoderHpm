"""
主数据管理 - Serializers
包含：Employee, Resource, PriceHeader, PriceLine
"""

from rest_framework import serializers
from .models import Employee, Resource, PriceHeader, PriceLine


class EmployeeSerializer(serializers.ModelSerializer):
    """员工序列化器"""
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ResourceSerializer(serializers.ModelSerializer):
    """资源序列化器"""
    
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PriceLineSerializer(serializers.ModelSerializer):
    """价格表明细序列化器"""
    
    class Meta:
        model = PriceLine
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PriceLineNestedSerializer(serializers.ModelSerializer):
    """价格表明细嵌套序列化器（用于PriceHeader详情）"""
    
    class Meta:
        model = PriceLine
        fields = ['line_id', 'resource_type', 'resource_code', 'price', 'unit', 'created_at', 'updated_at']


class PriceHeaderSerializer(serializers.ModelSerializer):
    """价格表头序列化器"""
    lines = PriceLineNestedSerializer(many=True, read_only=True, source='lines')
    
    class Meta:
        model = PriceHeader
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PriceHeaderListSerializer(serializers.ModelSerializer):
    """价格表头列表序列化器（不包含lines）"""
    
    class Meta:
        model = PriceHeader
        fields = ['header_id', 'version_name', 'version_no', 'currency', 'effective_from', 'effective_to', 'status', 'created_at', 'updated_at']
