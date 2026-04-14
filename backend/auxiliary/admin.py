"""
辅助功能模块 - Auxiliary App Admin
"""

from django.contrib import admin
from .models import (
    IssueRisk, SevenStep, Vpp, Scorecard, Meeting,
    ActionItem, MiscExpense, ProjectScope, Document, DocumentFile
)


@admin.register(IssueRisk)
class IssueRiskAdmin(admin.ModelAdmin):
    list_display = [
        'issue_id', 'issue_no', 'project', 'type', 'title',
        'status', 'severity', 'owner', 'created_by', 'created_at'
    ]
    list_filter = ['type', 'status', 'severity', 'capability']
    search_fields = ['issue_no', 'title', 'owner', 'created_by', 'closed_by']
    raw_id_fields = ['project']
    date_hierarchy = 'created_at'


@admin.register(SevenStep)
class SevenStepAdmin(admin.ModelAdmin):
    list_display = [
        'step_id', 'step_no', 'project', 'current_step',
        'status', 'figr_owner', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'current_step', 'platform_impact']
    search_fields = ['step_no', 'figr_owner', 'figr_team', 'local_specialist']
    raw_id_fields = ['project']


@admin.register(Vpp)
class VppAdmin(admin.ModelAdmin):
    list_display = [
        'vpp_id', 'project', 'version_no', 'status',
        'created_by', 'published_by', 'published_at'
    ]
    list_filter = ['status']
    search_fields = ['version_no', 'description']
    raw_id_fields = ['project']


@admin.register(Scorecard)
class ScorecardAdmin(admin.ModelAdmin):
    list_display = [
        'scorecard_id', 'project', 'template_type', 'phase',
        'total_score', 'status', 'evaluated_by', 'evaluated_at'
    ]
    list_filter = ['template_type', 'status']
    search_fields = ['phase', 'evaluated_by']
    raw_id_fields = ['project']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = [
        'meeting_id', 'project', 'meeting_subject', 'meeting_date',
        'meeting_time', 'meeting_duration', 'organizer', 'status'
    ]
    list_filter = ['status', 'meeting_type']
    search_fields = ['meeting_subject', 'organizer', 'meeting_location']
    raw_id_fields = ['project']
    date_hierarchy = 'meeting_date'


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = [
        'action_id', 'action_no', 'project', 'description',
        'current_owner', 'status', 'priority', 'planned_finish_date', 'actual_finish_date'
    ]
    list_filter = ['status', 'priority']
    search_fields = ['action_no', 'description', 'recorder', 'current_owner']
    raw_id_fields = ['project', 'meeting']


@admin.register(MiscExpense)
class MiscExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'expense_id', 'project', 'expense_type', 'settlement_period',
        'estimated_amount', 'actual_amount', 'status', 'created_by'
    ]
    list_filter = ['expense_type', 'status']
    search_fields = ['settlement_period', 'department', 'resource_name']
    raw_id_fields = ['project']


@admin.register(ProjectScope)
class ProjectScopeAdmin(admin.ModelAdmin):
    list_display = [
        'scope_id', 'project', 'version_no', 'status',
        'effective_from', 'effective_to', 'created_by'
    ]
    list_filter = ['status']
    search_fields = ['version_no', 'approved_by']
    raw_id_fields = ['project']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'catalog_id', 'project', 'catalog_name', 'level_code',
        'level', 'enabled', 'sort_order', 'created_by'
    ]
    list_filter = ['level', 'enabled']
    search_fields = ['catalog_name', 'level_code', 'catalog_desc']
    raw_id_fields = ['project', 'parent']


@admin.register(DocumentFile)
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = [
        'file_id', 'catalog', 'file_name', 'file_size',
        'file_type', 'version_no', 'is_latest', 'status', 'uploaded_by', 'uploaded_at'
    ]
    list_filter = ['file_type', 'is_latest', 'status']
    search_fields = ['file_name', 'description', 'uploaded_by']
    raw_id_fields = ['catalog']
