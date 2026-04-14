from django.contrib import admin
from .models import Employee, Resource, PriceHeader, PriceLine


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'employee_code', 'employee_name', 'department', 'email', 'source', 'is_external', 'expiry_date']
    list_filter = ['source', 'is_external', 'department', 'expiry_date']
    search_fields = ['employee_code', 'employee_name', 'department', 'email']
    ordering = ['employee_code']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_pk_id', 'resource_code', 'resource_name', 'resource_type', 'resource_manager', 'daily_charge', 'enabled']
    list_filter = ['resource_type', 'daily_charge', 'enabled']
    search_fields = ['resource_code', 'resource_name', 'short_name', 'resource_manager']


class PriceLineInline(admin.TabularInline):
    model = PriceLine
    extra = 1
    fields = ['resource_type', 'resource_code', 'price', 'unit']


@admin.register(PriceHeader)
class PriceHeaderAdmin(admin.ModelAdmin):
    list_display = ['header_id', 'version_name', 'version_no', 'currency', 'effective_from', 'effective_to', 'status']
    list_filter = ['status', 'currency', 'effective_from']
    search_fields = ['version_name', 'version_no']
    inlines = [PriceLineInline]


@admin.register(PriceLine)
class PriceLineAdmin(admin.ModelAdmin):
    list_display = ['line_id', 'header', 'resource_type', 'resource_code', 'price', 'unit']
    list_filter = ['resource_type', 'unit', 'header__version_name']
    search_fields = ['resource_code', 'header__version_name']
