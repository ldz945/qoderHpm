"""
项目验收模块 - Acceptance App Admin
"""

from django.contrib import admin
from .models import Acceptance


@admin.register(Acceptance)
class AcceptanceAdmin(admin.ModelAdmin):
    list_display = [
        'acceptance_id', 'acceptance_no', 'project', 'acceptance_type',
        'acceptance_phase', 'acceptance_status', 'vpp_verified',
        'acceptance_date', 'accepted_by', 'created_by'
    ]
    list_filter = ['acceptance_status', 'acceptance_type', 'acceptance_phase', 'vpp_verified']
    search_fields = ['acceptance_no', 'accepted_by', 'created_by']
    raw_id_fields = ['project']
    date_hierarchy = 'acceptance_date'
