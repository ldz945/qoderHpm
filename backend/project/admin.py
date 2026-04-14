from django.contrib import admin
from .models import Project, ProjectTask, ProjectMember, ActualHour


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 1
    fields = ['task_id', 'task_code', 'task_name']


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    fields = ['employee', 'employee_code', 'resource_code', 'project_role', 'is_core_member', 'effective_from', 'effective_to']


class ActualHourInline(admin.TabularInline):
    model = ActualHour
    extra = 0
    fields = ['name', 'hour_date', 'resource_code', 'task', 'work_hours', 'run_time', 'stop_time', 'sync_month']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'project_code', 'project_name', 'version', 'project_type', 'status', 'pm', 'am', 'customer_name', 'contract_amount', 'currency']
    list_filter = ['status', 'project_type', 'project_level', 'health_status', 'currency']
    search_fields = ['project_code', 'project_name', 'pm', 'am', 'customer_name']
    inlines = [ProjectTaskInline, ProjectMemberInline, ActualHourInline]


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'project', 'task_code', 'task_name']
    list_filter = ['project__project_name']
    search_fields = ['task_code', 'task_name', 'project__project_code', 'project__project_name']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['member_id', 'project', 'employee', 'employee_code', 'resource_code', 'project_role', 'is_core_member', 'effective_from', 'effective_to']
    list_filter = ['is_core_member', 'project_role', 'person_source']
    search_fields = ['employee_code', 'resource_code', 'project__project_code', 'project__project_name']


@admin.register(ActualHour)
class ActualHourAdmin(admin.ModelAdmin):
    list_display = ['actual_hour_id', 'project', 'name', 'hour_date', 'resource_code', 'task', 'work_hours', 'run_time', 'stop_time', 'sync_month']
    list_filter = ['sync_month', 'hour_date']
    search_fields = ['name', 'resource_code', 'project__project_code', 'project__project_name']
    date_hierarchy = 'hour_date'
