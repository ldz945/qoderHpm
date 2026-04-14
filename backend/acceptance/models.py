"""
项目验收模块 - Acceptance App Models
包含：验收单
"""

from django.db import models


class Acceptance(models.Model):
    """项目验收表 HPM_ACCEPTANCE"""
    
    ACCEPTANCE_STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('IN_PROGRESS', '进行中'),
        ('REJECTED', '已拒绝'),
        ('COMPLETED', '已完成'),
    ]
    
    acceptance_id = models.AutoField(primary_key=True, verbose_name='验收ID')
    acceptance_no = models.CharField(max_length=50, unique=True, verbose_name='验收单号')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    acceptance_type = models.CharField(max_length=50, verbose_name='验收类型')
    acceptance_phase = models.CharField(max_length=50, blank=True, verbose_name='验收阶段')
    acceptance_status = models.CharField(
        max_length=20,
        default='DRAFT',
        choices=ACCEPTANCE_STATUS_CHOICES,
        verbose_name='验收状态'
    )
    attachment_path = models.CharField(max_length=500, blank=True, verbose_name='附件路径')
    vpp_verified = models.CharField(max_length=1, default='N', verbose_name='VPP已核对')
    acceptance_date = models.DateField(null=True, blank=True, verbose_name='验收日期')
    accepted_by = models.CharField(max_length=100, blank=True, verbose_name='验收人')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_acceptance'
        verbose_name = '验收单'
        verbose_name_plural = '验收单'
    
    def __str__(self):
        return f"{self.acceptance_no} ({self.acceptance_type})"
