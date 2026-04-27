from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from master_data.models import Employee
from project.models import Project
from plan.models import PlanTask
from auxiliary.models import IssueRisk, ActionItem
from change.models import ChangeOrder
from acceptance.models import Acceptance

ROLE_CHOICES = [
    ('SUPER_ADMIN', '超级管理员'),
    ('MD_ADMIN', '主数据管理员'),
    ('PMO', 'PMO'),
    ('PROJECT_MANAGER', '项目经理'),
    ('PLAN_ENGINEER', '计划工程师'),
    ('EXECUTOR', '执行人'),
    ('AUDITOR', '审计/只读'),
]


def parse_roles(last_name):
    """Parse comma-separated roles from last_name field, return list."""
    if not last_name:
        return ['SUPER_ADMIN']
    return [r.strip() for r in last_name.split(',') if r.strip()]


ROLE_LABEL_MAP = dict(ROLE_CHOICES)


def sync_user_to_employee(user):
    """Create or update Employee record to match the Django User."""
    code = f'U{user.id:05d}'
    defaults = {
        'employee_name': user.first_name or user.username,
        'department': '',
        'email': user.email or '',
        'source': 'HPM',
        'is_external': 'N',
    }
    Employee.objects.update_or_create(
        employee_code=code,
        defaults={**defaults, 'employee_id': user.id},
    )


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'is_active', 'is_superuser', 'roles', 'password']

    def get_roles(self, obj):
        return parse_roles(obj.last_name)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password or 'hpm123456')
        user.save()
        sync_user_to_employee(user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        sync_user_to_employee(instance)
        return instance


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @action(detail=True, methods=['post'])
    def set_role(self, request, pk=None):
        user = self.get_object()
        roles = request.data.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
        # Store as comma-separated in last_name
        user.last_name = ','.join(roles)
        user.is_superuser = 'SUPER_ADMIN' in roles
        user.save()
        sync_user_to_employee(user)
        return Response({'status': 'ok', 'roles': roles})

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        user_id = request.data.get('user_id')
        new_password = request.data.get('password', 'hpm123456')
        try:
            user = User.objects.get(pk=user_id)
            user.set_password(new_password)
            user.save()
            return Response({'status': 'ok'})
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    roles = parse_roles(user.last_name)
    return Response({
        'id': user.id,
        'username': user.username,
        'name': user.first_name or user.username,
        'roles': roles,
        'is_superuser': user.is_superuser,
    })


ROLE_LIST = [{'value': k, 'label': v} for k, v in ROLE_CHOICES]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_list(request):
    return Response(ROLE_LIST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Dashboard summary with unified counting rules and project scope filtering."""
    from hpm.permissions import get_visible_project_ids

    visible = get_visible_project_ids(request.user)

    project_qs = Project.objects.all()
    if visible is not None:
        project_qs = project_qs.filter(project_id__in=visible)

    active_projects = project_qs.exclude(status__in=['CLOSURE', 'CANCEL'])
    project_count = active_projects.count()

    plan_pending_qs = PlanTask.objects.filter(task_status='PENDING_REVIEW')
    change_pending_qs = ChangeOrder.objects.filter(status='PENDING')
    acceptance_pending_qs = Acceptance.objects.filter(acceptance_status='IN_PROGRESS')
    if visible is not None:
        plan_pending_qs = plan_pending_qs.filter(project_id__in=visible)
        change_pending_qs = change_pending_qs.filter(project_id__in=visible)
        acceptance_pending_qs = acceptance_pending_qs.filter(project_id__in=visible)
    workflow_count = plan_pending_qs.count() + change_pending_qs.count() + acceptance_pending_qs.count()

    issue_qs = IssueRisk.objects.exclude(status__in=['COMPLETED', 'CANCEL'])
    action_qs = ActionItem.objects.exclude(status__in=['COMPLETED', 'CANCEL'])
    if visible is not None:
        issue_qs = issue_qs.filter(project_id__in=visible)
        action_qs = action_qs.filter(project_id__in=visible)

    return Response({
        'projects': project_count,
        'workflows': workflow_count,
        'issues': issue_qs.count(),
        'actions': action_qs.count(),
        'meta': {
            'scope': 'ALL' if visible is None else 'OWNED_PROJECTS',
            'as_of': timezone.now().isoformat(),
        }
    })

