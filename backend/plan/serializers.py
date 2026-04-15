"""
计划管理 - Serializers
包含：PlanTask, ResourcePlan, ResourceReserve, PlanVersion
"""

from rest_framework import serializers
from .models import PlanTask, ResourcePlan, ResourceReserve, PlanVersion


class PlanTaskSerializer(serializers.ModelSerializer):
    """计划任务序列化器"""
    parent_task_id = serializers.PrimaryKeyRelatedField(
        source='parent_task',
        queryset=PlanTask.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = PlanTask
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PlanTaskTreeSerializer(serializers.ModelSerializer):
    """计划任务树形序列化器（用于展示WBS结构）"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = PlanTask
        fields = [
            'plan_task_id', 'project', 'parent_task', 'task_name', 'task_level',
            'pre_task_code', 'logic_relation', 'department', 'task_owner',
            'authorized_owner', 'planned_start_date', 'planned_end_date',
            'workload_days', 'task_status', 'has_deliverable', 'is_hour_task',
            'acceptance_item', 'remark', 'phase', 'progress_percent',
            'include_weekend', 'version', 'sort_order', 'children',
            'created_at', 'updated_at'
        ]
    
    def get_children(self, obj):
        children = obj.children.all()
        return PlanTaskTreeSerializer(children, many=True).data


class ResourcePlanSerializer(serializers.ModelSerializer):
    """资源计划序列化器"""
    
    class Meta:
        model = ResourcePlan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ResourceReserveSerializer(serializers.ModelSerializer):
    """资源预占序列化器"""
    
    class Meta:
        model = ResourceReserve
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PlanVersionSerializer(serializers.ModelSerializer):
    """计划版本序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    project_manager = serializers.CharField(source='project.pm', read_only=True)
    version = serializers.CharField(source='version_no', read_only=True)
    
    class Meta:
        model = PlanVersion
        fields = [
            'version_id', 'version_no', 'version', 'version_name', 'status',
            'is_current', 'publish_date', 'published_by', 'remark',
            'created_by', 'created_at', 'updated_at', 'project',
            'project_code', 'project_name', 'project_manager'
        ]
        read_only_fields = ['created_at', 'updated_at']
