"""
计划管理 - Serializers
包含：PlanTask, ResourcePlan, ResourceReserve, PlanVersion
"""

from rest_framework import serializers
from .models import PlanTask, PlanTaskDependency, ResourcePlan, ResourceReserve, PlanVersion


def _build_legacy_dependency_fields(task):
    first_dep = task.successor_dependencies.order_by('sort_order', 'dependency_id').first()
    if not first_dep:
        return '', 'FS'
    return str(first_dep.predecessor_task_id), first_dep.logic_relation or 'FS'


def sync_task_dependencies(task, dependencies_payload):
    """Replace incoming dependencies of a task and return normalized rows."""
    if dependencies_payload is None:
        return

    normalized = []
    seen = set()
    for index, item in enumerate(dependencies_payload):
        predecessor_id = item.get('predecessor_task_id')
        if predecessor_id in (None, '', 0, '0'):
            continue
        try:
            predecessor_id = int(predecessor_id)
        except (TypeError, ValueError):
            continue
        if predecessor_id <= 0 or predecessor_id == task.plan_task_id:
            continue

        dedup_key = predecessor_id
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        logic_relation = item.get('logic_relation') or 'FS'
        lag_days = item.get('lag_days') or 0
        sort_order = item.get('sort_order', index)
        normalized.append({
            'predecessor_task_id': predecessor_id,
            'logic_relation': logic_relation,
            'lag_days': lag_days,
            'sort_order': sort_order,
        })

    PlanTaskDependency.objects.filter(successor_task=task).delete()
    dependency_rows = []
    for row in normalized:
        try:
            predecessor_task = PlanTask.objects.get(
                pk=row['predecessor_task_id'],
                project_id=task.project_id,
            )
        except PlanTask.DoesNotExist:
            continue

        dependency_rows.append(
            PlanTaskDependency(
                successor_task=task,
                predecessor_task=predecessor_task,
                logic_relation=row['logic_relation'],
                lag_days=row['lag_days'],
                sort_order=row['sort_order'],
            )
        )

    if dependency_rows:
        PlanTaskDependency.objects.bulk_create(dependency_rows)

    # 同步旧字段，保证历史页面和接口继续可用
    pre_task_code, logic_relation = _build_legacy_dependency_fields(task)
    PlanTask.objects.filter(pk=task.pk).update(
        pre_task_code=pre_task_code,
        logic_relation=logic_relation,
    )


class PlanTaskSerializer(serializers.ModelSerializer):
    """计划任务序列化器"""
    parent_task_id = serializers.PrimaryKeyRelatedField(
        source='parent_task',
        queryset=PlanTask.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    dependencies = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = PlanTask
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        deps = instance.successor_dependencies.order_by('sort_order', 'dependency_id')
        data['dependencies'] = [
            {
                'dependency_id': dep.dependency_id,
                'predecessor_task_id': dep.predecessor_task_id,
                'successor_task_id': dep.successor_task_id,
                'logic_relation': dep.logic_relation,
                'lag_days': float(dep.lag_days),
                'sort_order': dep.sort_order,
            }
            for dep in deps
        ]
        return data

    def create(self, validated_data):
        dependencies = validated_data.pop('dependencies', None)
        task = super().create(validated_data)

        if dependencies is None and task.pre_task_code not in (None, '', 0, '0'):
            dependencies = [{
                'predecessor_task_id': task.pre_task_code,
                'logic_relation': task.logic_relation or 'FS',
                'lag_days': 0,
                'sort_order': 0,
            }]

        sync_task_dependencies(task, dependencies)
        return PlanTask.objects.get(pk=task.pk)

    def update(self, instance, validated_data):
        dependencies = validated_data.pop('dependencies', None)
        task = super().update(instance, validated_data)

        # 旧协议仅传 pre_task_code 时，自动映射为单依赖
        if dependencies is None and 'pre_task_code' in validated_data:
            raw_pre = validated_data.get('pre_task_code')
            if raw_pre not in (None, '', 0, '0'):
                dependencies = [{
                    'predecessor_task_id': raw_pre,
                    'logic_relation': validated_data.get('logic_relation') or task.logic_relation,
                    'lag_days': 0,
                    'sort_order': 0,
                }]
            else:
                dependencies = []

        sync_task_dependencies(task, dependencies)
        return PlanTask.objects.get(pk=task.pk)


class PlanTaskTreeSerializer(serializers.ModelSerializer):
    """计划任务树形序列化器（用于展示WBS结构）"""
    children = serializers.SerializerMethodField()
    dependencies = serializers.SerializerMethodField()

    class Meta:
        model = PlanTask
        fields = [
            'plan_task_id', 'project', 'parent_task', 'task_name', 'task_level',
            'pre_task_code', 'logic_relation', 'department', 'task_owner',
            'authorized_owner', 'planned_start_date', 'planned_end_date',
            'workload_days', 'task_status', 'has_deliverable', 'is_hour_task',
            'acceptance_item', 'remark', 'phase', 'progress_percent',
            'baseline_start_date', 'baseline_end_date',
            'include_weekend', 'version', 'sort_order', 'dependencies', 'children',
            'created_at', 'updated_at'
        ]
    
    def get_children(self, obj):
        children = obj.children.all()
        return PlanTaskTreeSerializer(children, many=True).data

    def get_dependencies(self, obj):
        deps = obj.successor_dependencies.order_by('sort_order', 'dependency_id')
        return [
            {
                'dependency_id': dep.dependency_id,
                'predecessor_task_id': dep.predecessor_task_id,
                'successor_task_id': dep.successor_task_id,
                'logic_relation': dep.logic_relation,
                'lag_days': float(dep.lag_days),
                'sort_order': dep.sort_order,
            }
            for dep in deps
        ]


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
