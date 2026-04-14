"""
接口模块 - Serializers
包含：InterfaceLog
"""

from rest_framework import serializers
from .models import InterfaceLog


class InterfaceLogSerializer(serializers.ModelSerializer):
    """接口日志序列化器"""
    
    class Meta:
        model = InterfaceLog
        fields = '__all__'
        read_only_fields = ['created_at', 'request_time']


class InterfaceLogListSerializer(serializers.ModelSerializer):
    """接口日志列表序列化器（简化字段）"""
    
    class Meta:
        model = InterfaceLog
        fields = [
            'log_id', 'service_code', 'service_name', 'direction',
            'request_status', 'request_time', 'process_time'
        ]
