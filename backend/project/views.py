"""
项目管理 - Views
包含：ProjectViewSet, ProjectTaskViewSet, ProjectMemberViewSet, ActualHourViewSet
"""

from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, ProjectTask, ProjectMember, ActualHour
from .serializers import (
    ProjectSerializer, 
    ProjectListSerializer,
    ProjectTaskSerializer, 
    ProjectMemberSerializer, 
    ActualHourSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """项目视图集"""
    queryset = Project.objects.prefetch_related('plan_tasks').all()
    required_permissions = {
        'list': ['project.read', 'execution.read'],
        'retrieve': ['project.read', 'execution.read'],
        'create': ['project.create'],
        'update': ['project.update'],
        'partial_update': ['project.update'],
        'destroy': ['project.delete'],
    }
    filterset_fields = [
        'project_code', 'project_type', 'status', 'pm', 
        'project_level', 'am', 'health_status'
    ]
    search_fields = ['project_code', 'project_name', 'pm', 'customer_name']
    ordering_fields = ['project_code', 'created_at', 'contract_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        # Support partial match for project_code and project_name
        project_code = params.get('project_code')
        project_name = params.get('project_name')

        if project_code:
            queryset = queryset.filter(project_code__icontains=project_code)
        if project_name:
            queryset = queryset.filter(project_name__icontains=project_name)

        # 数据范围隔离：项目经理只能看到自己负责的项目
        from hpm.permissions import get_visible_project_ids
        visible = get_visible_project_ids(self.request.user)
        if visible is not None:
            queryset = queryset.filter(project_id__in=visible)

        return queryset

    def get_required_permissions(self, request):
        action = getattr(self, 'action', None)
        base = self.required_permissions.get(action) or self.required_permissions.get('*') or []
        if action == 'partial_update':
            data = request.data or {}
            if 'status' in data:
                return ['project.status.update']
            if 'pm' in data:
                # 修改项目经理需要更高权限（PMO 或超管），项目经理本身无此权限
                return ['project.pm.update']
        return base


class ProjectTaskViewSet(viewsets.ModelViewSet):
    """项目任务视图集"""
    queryset = ProjectTask.objects.all()
    serializer_class = ProjectTaskSerializer
    required_permissions = {
        'list': ['execution.detail.read'],
        'retrieve': ['execution.detail.read'],
        'create': ['execution.progress.write'],
        'update': ['execution.progress.write'],
        'partial_update': ['execution.progress.write'],
        'destroy': ['execution.progress.write'],
    }
    filterset_fields = ['project', 'task_code']
    search_fields = ['task_code', 'task_name']
    ordering_fields = ['task_code', 'created_at']
    ordering = ['task_code']

    def get_queryset(self):
        queryset = super().get_queryset()
        from hpm.permissions import get_visible_project_ids
        visible = get_visible_project_ids(self.request.user)
        if visible is not None:
            queryset = queryset.filter(project_id__in=visible)
        return queryset


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """项目成员视图集"""
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    required_permissions = {
        'list': ['project.read'],
        'retrieve': ['project.read'],
        'create': ['project.update'],
        'update': ['project.update'],
        'partial_update': ['project.update'],
        'destroy': ['project.update'],
    }
    filterset_fields = ['project', 'employee', 'project_role', 'is_core_member']
    search_fields = ['employee_code', 'department']
    ordering_fields = ['employee_code', 'created_at']
    ordering = ['employee_code']

    def get_queryset(self):
        queryset = super().get_queryset()
        from hpm.permissions import get_visible_project_ids
        visible = get_visible_project_ids(self.request.user)
        if visible is not None:
            queryset = queryset.filter(project_id__in=visible)
        return queryset


class ActualHourViewSet(mixins.ListModelMixin, 
                        mixins.RetrieveModelMixin, 
                        viewsets.GenericViewSet):
    """实际工时视图集（只读）"""
    queryset = ActualHour.objects.all()
    serializer_class = ActualHourSerializer
    required_permissions = {
        'list': ['execution.actual_hours.read'],
        'retrieve': ['execution.actual_hours.read'],
    }
    filterset_fields = [
        'project', 'resource_code', 'task', 
        'sync_month', 'hour_date'
    ]
    search_fields = ['name', 'resource_code']
    ordering_fields = ['hour_date', 'sync_month', 'created_at']
    ordering = ['-hour_date']
