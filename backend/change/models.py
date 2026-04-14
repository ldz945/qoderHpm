"""
变更管理 - 数据模型定义
包含：ChangeOrder
"""

from django.db import models


class ChangeOrder(models.Model):
    """变更单"""

    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('PENDING', '待审批'),
        ('APPROVED', '已审批'),
        ('REJECTED', '已驳回'),
        ('EXECUTED', '已执行'),
    ]

    change_id = models.AutoField(primary_key=True, verbose_name='变更ID')
    change_no = models.CharField(max_length=50, unique=True, verbose_name='变更编号')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='所属项目',
        related_name='change_orders'
    )
    change_type = models.CharField(max_length=50, verbose_name='变更类型')
    change_field = models.CharField(max_length=100, blank=True, verbose_name='变更字段')
    old_value = models.TextField(blank=True, verbose_name='变更前值')
    new_value = models.TextField(blank=True, verbose_name='变更后值')
    change_impact = models.TextField(blank=True, verbose_name='变更影响')
    change_reason = models.TextField(blank=True, verbose_name='变更原因')
    change_content = models.TextField(blank=True, verbose_name='变更内容')
    task_code = models.CharField(max_length=50, blank=True, verbose_name='关联任务编码')
    status = models.CharField(
        max_length=20, default='DRAFT', choices=STATUS_CHOICES, verbose_name='状态'
    )
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    approved_by = models.CharField(max_length=100, blank=True, verbose_name='审批人')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')

    class Meta:
        db_table = 'hpm_change_order'
        verbose_name = '变更单'
        verbose_name_plural = '变更单'

    def __str__(self):
        return f'{self.change_no} ({self.get_status_display()})'
