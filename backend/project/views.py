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

        return queryset


class ProjectTaskViewSet(viewsets.ModelViewSet):
    """项目任务视图集"""
    queryset = ProjectTask.objects.all()
    serializer_class = ProjectTaskSerializer
    filterset_fields = ['project', 'task_code']
    search_fields = ['task_code', 'task_name']
    ordering_fields = ['task_code', 'created_at']
    ordering = ['task_code']


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """项目成员视图集"""
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    filterset_fields = ['project', 'employee', 'project_role', 'is_core_member']
    search_fields = ['employee_code', 'department']
    ordering_fields = ['employee_code', 'created_at']
    ordering = ['employee_code']


class ActualHourViewSet(mixins.ListModelMixin, 
                        mixins.RetrieveModelMixin, 
                        viewsets.GenericViewSet):
    """实际工时视图集（只读）"""
    queryset = ActualHour.objects.all()
    serializer_class = ActualHourSerializer
    filterset_fields = [
        'project', 'resource_code', 'task', 
        'sync_month', 'hour_date'
    ]
    search_fields = ['name', 'resource_code']
    ordering_fields = ['hour_date', 'sync_month', 'created_at']
    ordering = ['-hour_date']
