from django.conf import settings
from rest_framework.permissions import BasePermission

# Map role -> permission codes (mirrors frontend permissions.js)
ROLE_PERMISSIONS = {
    'SUPER_ADMIN': ['*'],
    'MD_ADMIN': [
        'master_data.employee.read', 'master_data.employee.write',
        'master_data.department.read', 'master_data.department.write',
        'master_data.resource.read', 'master_data.resource.write',
        'master_data.price.read', 'master_data.price.write',
    ],
    'PMO': [
        'project.read', 'project.create', 'project.update', 'project.status.update', 'project.pm.update',
        'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
        'plan.version.read', 'plan.version.write',
        'execution.read', 'execution.detail.read', 'execution.actual_hours.read',
        'master_data.department.read', 'master_data.employee.read',
        'master_data.resource.read', 'master_data.price.read',
    ],
    'PROJECT_MANAGER': [
        'project.read', 'project.create', 'project.update', 'project.status.update',
        'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
        'plan.version.read', 'plan.version.write',
        'execution.read', 'execution.detail.read',
        'master_data.department.read', 'master_data.employee.read',
        'master_data.resource.read', 'master_data.price.read',
    ],
    'PLAN_ENGINEER': [
        'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
        'plan.version.read',
        'master_data.department.read', 'master_data.employee.read',
    ],
    'EXECUTOR': [
        'execution.read', 'execution.detail.read', 'execution.progress.write', 'execution.actual_hours.read',
        'master_data.department.read', 'master_data.employee.read',
    ],
    'AUDITOR': [
        'project.read', 'plan.task.read', 'plan.version.read', 'execution.read', 'execution.detail.read',
        'master_data.employee.read', 'master_data.department.read', 'master_data.resource.read', 'master_data.price.read',
    ],
}


def get_user_roles(user):
    """Get role list from user.last_name field (comma-separated)."""
    last_name = getattr(user, 'last_name', '') or ''
    if not last_name:
        return ['SUPER_ADMIN']
    return [r.strip() for r in last_name.split(',') if r.strip()]


# 拥有"全局可见"数据范围的角色（看全部项目）
ELEVATED_ROLES = {'SUPER_ADMIN', 'PMO', 'AUDITOR', 'MD_ADMIN'}


def user_can_see_all_projects(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return bool(set(get_user_roles(user)) & ELEVATED_ROLES)


def get_visible_project_ids(user):
    """返回该用户可见的项目 ID 列表；返回 None 表示不限制（看全部）。"""
    if user_can_see_all_projects(user):
        return None
    from project.models import Project
    pm_name = user.first_name or user.username
    return list(Project.objects.filter(pm__in=[pm_name, user.username]).values_list('project_id', flat=True))


def user_has_perm(user, perm_code):
    if user.is_superuser:
        return True
    roles = get_user_roles(user)
    for role in roles:
        perms = ROLE_PERMISSIONS.get(role, [])
        if '*' in perms or perm_code in perms:
            return True
    return False


class HpmActionPermission(BasePermission):
    """Action-level permission checker controlled by view.required_permissions."""

    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if hasattr(view, 'get_required_permissions'):
            required = view.get_required_permissions(request)
        else:
            required_map = getattr(view, 'required_permissions', None)
            if not required_map:
                return True
            action = getattr(view, 'action', None)
            required = required_map.get(action) or required_map.get('*') or []

        if not required:
            return True

        if not getattr(settings, 'HPM_PERMISSION_ENFORCEMENT', False):
            return True

        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # OR semantics: 任一权限即可
        return any(user_has_perm(user, p) for p in required)
