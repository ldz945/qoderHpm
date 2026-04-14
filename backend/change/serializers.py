"""
变更管理 - Serializers
包含：ChangeOrder
"""

from rest_framework import serializers
from .models import ChangeOrder


class ChangeOrderSerializer(serializers.ModelSerializer):
    """变更单序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = ChangeOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ChangeOrderListSerializer(serializers.ModelSerializer):
    """变更单列表序列化器（简化字段）"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = ChangeOrder
        fields = [
            'change_id', 'change_no', 'project', 'project_code', 'project_name',
            'change_type', 'status', 'change_field', 'created_by', 'created_at'
        ]
