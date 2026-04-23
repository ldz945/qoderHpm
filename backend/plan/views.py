"""
计划管理 - Views
包含：PlanTaskViewSet, ResourcePlanViewSet, ResourceReserveViewSet, PlanVersionViewSet
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.utils import IntegrityError
from .models import PlanTask, PlanTaskCategory, ResourcePlan, ResourceReserve, PlanVersion
from .serializers import (
    PlanTaskSerializer, 
    PlanTaskTreeSerializer,
    PlanTaskCategorySerializer,
    sync_task_dependencies,
    ResourcePlanSerializer,
    ResourceReserveSerializer, 
    PlanVersionSerializer
)


class PlanTaskViewSet(viewsets.ModelViewSet):
    """计划任务视图集"""
    queryset = PlanTask.objects.prefetch_related('successor_dependencies').all()
    required_permissions = {
        'list': ['plan.task.read'],
        'retrieve': ['plan.task.read'],
        'create': ['plan.task.write'],
        'update': ['plan.task.write'],
        'partial_update': ['plan.task.write'],
        'destroy': ['plan.task.write'],
        'batch_update': ['plan.task.batch_update'],
    }
    filterset_fields = [
        'project', 'phase', 'task_status', 'task_level', 
        'is_hour_task', 'parent_task', 'version'
    ]
    search_fields = ['task_name', 'department', 'task_owner']
    ordering_fields = ['task_level', 'planned_start_date', 'created_at', 'sort_order']
    ordering = ['sort_order', 'plan_task_id']
    
    def get_serializer_class(self):
        if self.request.query_params.get('tree', 'false').lower() == 'true':
            return PlanTaskTreeSerializer
        return PlanTaskSerializer

    @action(detail=False, methods=['post'], url_path='batch-update')
    def batch_update(self, request):
        """
        批量更新任务（用于甘特图拖拽/拉伸/排序操作）
        请求体：{ "tasks": [ { "plan_task_id": 1, "planned_start_date": "2024-01-01", ... }, ... ] }
        """
        tasks_data = request.data.get('tasks', [])
        if not tasks_data:
            return Response({'detail': '任务列表为空'}, status=status.HTTP_400_BAD_REQUEST)

        updated_ids = []
        errors = []
        for task_data in tasks_data:
            task_id = task_data.get('plan_task_id')
            if not task_id:
                errors.append({'error': '缺少 plan_task_id', 'data': task_data})
                continue
            try:
                task = PlanTask.objects.get(pk=task_id)
                # 只更新允许的字段
                allowed_fields = [
                    'planned_start_date', 'planned_end_date', 'workload_days',
                    'sort_order', 'parent_task_id', 'phase', 'progress_percent',
                    'task_name', 'pre_task_code', 'logic_relation', 'task_level',
                    'baseline_start_date', 'baseline_end_date'
                ]
                for field in allowed_fields:
                    if field not in task_data:
                        continue
                    value = task_data[field]
                    if field == 'parent_task_id':
                        # 甘特图根任务通常传 0，这里统一转为 NULL
                        if value in (0, '0', '', None):
                            value = None
                    setattr(task, field, value)

                if bool(task.baseline_start_date) != bool(task.baseline_end_date):
                    raise ValueError('基线开始日期和基线结束日期必须同时填写或同时清空')
                if task.baseline_start_date and task.baseline_end_date and task.baseline_end_date < task.baseline_start_date:
                    raise ValueError('基线结束日期不能早于基线开始日期')

                task.save()

                # 新协议：每个任务可提交多条前置依赖
                if 'dependencies' in task_data:
                    sync_task_dependencies(task, task_data.get('dependencies'))
                # 旧协议兼容：仅单条 pre_task_code/logic_relation
                elif 'pre_task_code' in task_data:
                    raw_pre = task_data.get('pre_task_code')
                    if raw_pre in (None, '', 0, '0'):
                        sync_task_dependencies(task, [])
                    else:
                        sync_task_dependencies(task, [{
                            'predecessor_task_id': raw_pre,
                            'logic_relation': task_data.get('logic_relation') or task.logic_relation,
                            'lag_days': 0,
                            'sort_order': 0,
                        }])

                updated_ids.append(task_id)
            except PlanTask.DoesNotExist:
                errors.append({'error': f'任务 {task_id} 不存在', 'plan_task_id': task_id})
            except (IntegrityError, ValueError, TypeError) as exc:
                errors.append({'error': str(exc), 'plan_task_id': task_id})

        return Response({
            'updated': updated_ids,
            'errors': errors,
            'message': f'成功更新 {len(updated_ids)} 条任务'
        })


class PlanTaskCategoryViewSet(viewsets.ModelViewSet):
    """计划任务类别字典视图集"""
    queryset = PlanTaskCategory.objects.all()
    serializer_class = PlanTaskCategorySerializer
    required_permissions = {
        'list': ['master_data.department.read'],
        'retrieve': ['master_data.department.read'],
        'create': ['master_data.department.write'],
        'update': ['master_data.department.write'],
        'partial_update': ['master_data.department.write'],
        'destroy': ['master_data.department.write'],
    }
    filterset_fields = ['category_type', 'enabled']
    search_fields = ['category_value']
    ordering_fields = ['category_type', 'sort_order', 'category_value', 'created_at']
    ordering = ['category_type', 'sort_order', 'category_id']


class ResourcePlanViewSet(viewsets.ModelViewSet):
    """资源计划视图集"""
    queryset = ResourcePlan.objects.all()
    serializer_class = ResourcePlanSerializer
    required_permissions = {
        'list': ['plan.task.read'],
        'retrieve': ['plan.task.read'],
        'create': ['plan.task.write'],
        'update': ['plan.task.write'],
        'partial_update': ['plan.task.write'],
        'destroy': ['plan.task.write'],
    }
    filterset_fields = [
        'project', 'task', 'resource_type', 'resource_code', 'status'
    ]
    search_fields = ['resource_name', 'resource_code']
    ordering_fields = ['planned_start_date', 'resource_code', 'created_at']
    ordering = ['resource_code']


class ResourceReserveViewSet(viewsets.ModelViewSet):
    """资源预占视图集"""
    queryset = ResourceReserve.objects.all()
    serializer_class = ResourceReserveSerializer
    required_permissions = {
        'list': ['plan.task.read'],
        'retrieve': ['plan.task.read'],
        'create': ['plan.task.write'],
        'update': ['plan.task.write'],
        'partial_update': ['plan.task.write'],
        'destroy': ['plan.task.write'],
    }
    filterset_fields = [
        'project', 'resource_type', 'resource_code', 
        'reserve_status', 'project_short_code'
    ]
    search_fields = ['resource_name', 'resource_code', 'project_short_code']
    ordering_fields = ['reserve_start_time', 'resource_code', 'created_at']
    ordering = ['-reserve_start_time']


class PlanVersionViewSet(viewsets.ModelViewSet):
    """计划版本视图集"""
    queryset = PlanVersion.objects.select_related('project').all()
    serializer_class = PlanVersionSerializer
    required_permissions = {
        'list': ['plan.version.read'],
        'retrieve': ['plan.version.read'],
        'create': ['plan.version.write'],
        'update': ['plan.version.write'],
        'partial_update': ['plan.version.write'],
        'destroy': ['plan.version.write'],
    }
    filterset_fields = ['project', 'status', 'is_current']
    search_fields = ['version_no', 'version_name']
    ordering_fields = ['version_no', 'publish_date', 'created_at']
    ordering = ['-is_current', '-version_no']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        project_code = params.get('project_code')
        project_manager = params.get('project_manager')
        status = params.get('status')

        if project_code:
            queryset = queryset.filter(project__project_code__icontains=project_code)
        if project_manager:
            queryset = queryset.filter(project__pm__icontains=project_manager)
        if status:
            queryset = queryset.filter(status=status.upper())

        return queryset
