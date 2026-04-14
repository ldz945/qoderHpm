"""
接口模块 - Interfaces App Admin
"""

from django.contrib import admin
from .models import InterfaceLog


@admin.register(InterfaceLog)
class InterfaceLogAdmin(admin.ModelAdmin):
    list_display = [
        'log_id', 'service_code', 'service_name', 'client_id',
        'direction', 'request_status', 'request_time', 'process_time'
    ]
    list_filter = ['direction', 'request_status', 'service_code']
    search_fields = ['service_code', 'service_name', 'client_id', 'error_message']
    date_hierarchy = 'request_time'
    readonly_fields = ['log_id', 'request_time', 'created_at']
