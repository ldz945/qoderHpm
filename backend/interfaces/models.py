"""
接口模块 - Interfaces App Models
包含：接口日志
"""

from django.db import models


class InterfaceLog(models.Model):
    """接口日志表 HPM_INTERFACE_LOG"""
    
    DIRECTION_CHOICES = [
        ('TOMS_TO_HPM', 'TOMS到HPM'),
        ('HPM_TO_TOMS', 'HPM到TOMS'),
    ]
    
    REQUEST_STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('SUCCESS', '成功'),
        ('FAILED', '失败'),
    ]
    
    log_id = models.AutoField(primary_key=True, verbose_name='日志ID')
    service_code = models.CharField(max_length=50, verbose_name='服务代码')
    service_name = models.CharField(max_length=200, verbose_name='服务名称')
    client_id = models.CharField(max_length=100, blank=True, verbose_name='客户端ID')
    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        verbose_name='方向'
    )
    request_data = models.TextField(blank=True, verbose_name='请求数据')
    response_data = models.TextField(blank=True, verbose_name='响应数据')
    request_status = models.CharField(
        max_length=20,
        default='PENDING',
        choices=REQUEST_STATUS_CHOICES,
        verbose_name='请求状态'
    )
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    request_time = models.DateTimeField(auto_now_add=True, verbose_name='请求时间')
    process_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'hpm_interface_log'
        verbose_name = '接口日志'
        verbose_name_plural = '接口日志'
    
    def __str__(self):
        return f"{self.service_code} ({self.direction})"
