"""
项目验收模块 - Serializers
包含：Acceptance
"""

from rest_framework import serializers
from .models import Acceptance


class AcceptanceSerializer(serializers.ModelSerializer):
    """验收单序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = Acceptance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AcceptanceListSerializer(serializers.ModelSerializer):
    """验收单列表序列化器（简化字段）"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = Acceptance
        fields = [
            'acceptance_id', 'acceptance_no', 'project', 'project_code', 'project_name',
            'acceptance_type', 'acceptance_status', 'acceptance_phase', 
            'acceptance_date', 'created_by', 'created_at'
        ]
