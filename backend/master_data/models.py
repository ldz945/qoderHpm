"""
主数据管理 - 数据模型定义
包含：Employee, Resource, PriceHeader, PriceLine
"""

from django.db import models


class Employee(models.Model):
    """员工表 HPM_EMPLOYEE"""
    
    SOURCE_CHOICES = [
        ('TOMS', 'TOMS同步'),
        ('HPM', 'HPM创建'),
    ]
    
    employee_id = models.BigIntegerField(primary_key=True, verbose_name='员工ID')
    employee_name = models.CharField(max_length=100, verbose_name='员工姓名')
    employee_code = models.CharField(max_length=50, unique=True, verbose_name='员工工号')
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    email = models.CharField(max_length=100, blank=True, verbose_name='邮箱')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='失效日期')
    source = models.CharField(max_length=20, default='TOMS', choices=SOURCE_CHOICES, verbose_name='数据来源')
    is_external = models.CharField(max_length=1, default='N', verbose_name='是否外部员工')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_employee'
        verbose_name = '员工'
        verbose_name_plural = '员工'
    
    def __str__(self):
        return f'{self.employee_name} ({self.employee_code})'


class Resource(models.Model):
    """资源表 HPM_RESOURCE"""
    
    resource_pk_id = models.AutoField(primary_key=True, verbose_name='资源主键ID')
    source_id = models.BigIntegerField(null=True, blank=True, verbose_name='TOMS系统ID')
    source_code = models.BigIntegerField(null=True, blank=True, verbose_name='TOMS系统CODE')
    resource_code = models.CharField(max_length=50, unique=True, verbose_name='资源代码')
    resource_type = models.CharField(max_length=50, verbose_name='资源类型')
    resource_name = models.CharField(max_length=200, verbose_name='资源名称')
    daily_charge = models.CharField(max_length=1, default='N', verbose_name='按天收费')
    resource_manager = models.CharField(max_length=100, blank=True, verbose_name='资源负责人')
    short_name = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name='资源短名')
    enabled = models.CharField(max_length=1, default='Y', verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_resource'
        verbose_name = '资源'
        verbose_name_plural = '资源'
    
    def __str__(self):
        return f'{self.resource_name} ({self.resource_code})'


class PriceHeader(models.Model):
    """价格表头 HPM_PRICE_HEADER"""
    
    STATUS_CHOICES = [
        ('ACTIVE', '生效'),
        ('INACTIVE', '失效'),
    ]
    
    header_id = models.AutoField(primary_key=True, verbose_name='表头ID')
    version_name = models.CharField(max_length=100, unique=True, verbose_name='版本名称')
    version_no = models.IntegerField(verbose_name='版本号')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='货币')
    effective_from = models.DateField(null=True, blank=True, verbose_name='生效日期')
    effective_to = models.DateField(null=True, blank=True, verbose_name='失效日期')
    status = models.CharField(max_length=20, default='ACTIVE', choices=STATUS_CHOICES, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_price_header'
        verbose_name = '价格表头'
        verbose_name_plural = '价格表头'
    
    def __str__(self):
        return f'{self.version_name} (v{self.version_no})'


class PriceLine(models.Model):
    """价格表行 HPM_PRICE_LINE"""
    
    line_id = models.AutoField(primary_key=True, verbose_name='行ID')
    header = models.ForeignKey(PriceHeader, on_delete=models.CASCADE, related_name='lines', verbose_name='价格表头')
    resource_type = models.CharField(max_length=50, verbose_name='资源类型')
    resource_code = models.CharField(max_length=50, verbose_name='资源代码')
    price = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='价格')
    unit = models.CharField(max_length=20, verbose_name='单位')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_price_line'
        verbose_name = '价格表行'
        verbose_name_plural = '价格表行'
    
    def __str__(self):
        return f'{self.resource_code} - {self.price} {self.unit}'
