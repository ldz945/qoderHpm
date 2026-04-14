"""
项目管理 - Serializers
包含：Project, ProjectTask, ProjectMember, ActualHour
"""

from rest_framework import serializers
from .models import Project, ProjectTask, ProjectMember, ActualHour


class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器"""
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """项目列表序列化器（简化字段）"""
    
    class Meta:
        model = Project
        fields = [
            'project_id', 'project_code', 'project_name', 'version',
            'project_type', 'status', 'pm', 'am', 'contract_amount',
            'health_status', 'created_at'
        ]


class ProjectTaskSerializer(serializers.ModelSerializer):
    """项目任务序列化器"""
    
    class Meta:
        model = ProjectTask
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectMemberSerializer(serializers.ModelSerializer):
    """项目成员序列化器"""
    employee_name = serializers.CharField(source='employee.employee_name', read_only=True)
    department = serializers.CharField(source='employee.department', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ActualHourSerializer(serializers.ModelSerializer):
    """实际工时序列化器"""
    
    class Meta:
        model = ActualHour
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
