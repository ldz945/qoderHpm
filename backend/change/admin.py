"""
项目变更模块 - Change App Admin
"""

from django.contrib import admin
from .models import ChangeOrder


@admin.register(ChangeOrder)
class ChangeOrderAdmin(admin.ModelAdmin):
    list_display = [
        'change_id', 'change_no', 'project', 'change_type',
        'status', 'task_code', 'created_by', 'created_at', 'approved_by', 'approved_at'
    ]
    list_filter = ['change_type', 'status']
    search_fields = ['change_no', 'change_field', 'task_code', 'created_by', 'approved_by']
    raw_id_fields = ['project']
    date_hierarchy = 'created_at'
