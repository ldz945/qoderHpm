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
    overallProgress = serializers.SerializerMethodField()
    actualAmount = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'project_id', 'project_code', 'project_name', 'version',
            'project_type', 'status', 'pm', 'am', 'contract_amount',
            'health_status', 'created_at', 'overallProgress', 'actualAmount'
        ]

    def get_overallProgress(self, obj):
        tasks_manager = getattr(obj, 'plan_tasks', None)
        if tasks_manager is None:
            return 0
        tasks = list(tasks_manager.all())
        if not tasks:
            return 0

        weighted_sum = 0.0
        total_weight = 0.0
        plain_sum = 0.0
        plain_count = 0

        for task in tasks:
            progress = float(task.progress_percent or 0)
            progress = max(0.0, min(100.0, progress))
            workload = float(task.workload_days or 0)

            plain_sum += progress
            plain_count += 1

            if workload > 0:
                weighted_sum += progress * workload
                total_weight += workload

        if total_weight > 0:
            return round(weighted_sum / total_weight, 2)
        if plain_count > 0:
            return round(plain_sum / plain_count, 2)
        return 0

    def get_actualAmount(self, obj):
        # 当前模型未维护项目实际金额，先返回 0，避免前端显示为空
        return 0


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
    role = serializers.CharField(source='project_role', required=False, default='')
    is_core = serializers.BooleanField(required=False, default=False)
    source = serializers.CharField(source='person_source', required=False, default='')
    employee_id = serializers.IntegerField(write_only=True, required=False)
    project_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ProjectMember
        fields = [
            'member_id', 'project', 'project_id', 'employee', 'employee_id', 'employee_code',
            'employee_name', 'department', 'role', 'is_core', 'source',
            'resource_code', 'effective_from', 'effective_to',
            'is_core_member', 'project_role', 'person_source',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'employee_code', 'employee_name', 'department']
        extra_kwargs = {
            'employee': {'required': False, 'read_only': True},
            'project': {'required': False, 'read_only': True},
            'is_core_member': {'required': False},
            'project_role': {'required': False},
            'person_source': {'required': False},
        }

    def create(self, validated_data):
        employee_id = validated_data.pop('employee_id', None)
        project_id = validated_data.pop('project_id', None)
        is_core = validated_data.pop('is_core', False)
        if project_id:
            validated_data['project_id'] = project_id
        if employee_id:
            from master_data.models import Employee
            emp = Employee.objects.get(pk=employee_id)
            validated_data['employee'] = emp
            validated_data['employee_code'] = emp.employee_code
            validated_data['department'] = emp.department
        validated_data['is_core_member'] = 'Y' if is_core else 'N'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_core = validated_data.pop('is_core', None)
        validated_data.pop('employee_id', None)
        if is_core is not None:
            validated_data['is_core_member'] = 'Y' if is_core else 'N'
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['is_core'] = instance.is_core_member == 'Y'
        return ret


class ActualHourSerializer(serializers.ModelSerializer):
    """实际工时序列化器"""
    
    class Meta:
        model = ActualHour
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
