"""
项目管理 - 数据模型定义
包含：Project, ProjectTask, ProjectMember, ActualHour
"""

from django.db import models


class Project(models.Model):
    """项目立项表 HPM_PROJECT"""
    
    PROJECT_TYPE_CHOICES = [
        ('VPI', 'VPI'),
        ('VPC', 'VPC'),
        ('CPS', 'CPS'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('ONGOING', '进行中'),
        ('HOLD', '暂停'),
        ('CLOSURE', '已关闭'),
        ('CANCEL', '已取消'),
    ]
    
    LEVEL_CHOICES = [
        ('L1', 'L1'),
        ('L2', 'L2'),
        ('L3', 'L3'),
        ('L4', 'L4'),
    ]
    
    HEALTH_CHOICES = [
        ('GREEN', '绿色'),
        ('BLUE', '蓝色'),
        ('YELLOW', '黄色'),
        ('RED', '红色'),
    ]
    
    project_id = models.CharField(max_length=50, primary_key=True, verbose_name='项目ID')
    project_code = models.CharField(max_length=50, verbose_name='项目编码')
    project_name = models.CharField(max_length=200, verbose_name='项目名称')
    version = models.CharField(max_length=20, default='1.0', verbose_name='版本')
    price_version = models.ForeignKey(
        'master_data.PriceHeader', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='价格版本', related_name='projects'
    )
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, verbose_name='项目类型')
    quote_type = models.CharField(max_length=50, blank=True, verbose_name='报价类型')
    contract_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='合同金额')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    status = models.CharField(max_length=20, default='DRAFT', choices=STATUS_CHOICES, verbose_name='项目状态')
    pm = models.CharField(max_length=100, blank=True, verbose_name='项目经理')
    am = models.CharField(max_length=100, blank=True, verbose_name='客户经理')
    customer_name = models.CharField(max_length=200, blank=True, verbose_name='客户名称')
    quote_date = models.DateField(null=True, blank=True, verbose_name='报价日期')
    effective_date = models.DateField(null=True, blank=True, verbose_name='生效日期')
    project_level = models.CharField(max_length=10, blank=True, choices=LEVEL_CHOICES, verbose_name='项目等级')
    health_status = models.CharField(max_length=10, default='GREEN', choices=HEALTH_CHOICES, verbose_name='健康状态')
    health_remark = models.CharField(max_length=500, blank=True, verbose_name='健康备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_project'
        verbose_name = '项目'
        verbose_name_plural = '项目'
        unique_together = [['project_code', 'version']]
    
    def __str__(self):
        return f'{self.project_code} - {self.project_name}'


class ProjectTask(models.Model):
    """项目任务表 HPM_PROJECT_TASK"""
    
    task_id = models.BigIntegerField(primary_key=True, verbose_name='任务ID')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目', related_name='tasks')
    task_code = models.CharField(max_length=50, verbose_name='任务编码')
    task_name = models.CharField(max_length=200, verbose_name='任务名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_project_task'
        verbose_name = '项目任务'
        verbose_name_plural = '项目任务'
    
    def __str__(self):
        return f'{self.task_code} - {self.task_name}'


class ProjectMember(models.Model):
    """项目成员表 HPM_PROJECT_MEMBER"""
    
    member_id = models.AutoField(primary_key=True, verbose_name='成员ID')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目', related_name='members')
    employee = models.ForeignKey(
        'master_data.Employee', on_delete=models.CASCADE, verbose_name='员工', related_name='project_memberships'
    )
    employee_code = models.CharField(max_length=50, verbose_name='员工工号')
    resource_code = models.CharField(max_length=50, blank=True, verbose_name='资源编码')
    effective_from = models.DateField(null=True, blank=True, verbose_name='有效期起')
    effective_to = models.DateField(null=True, blank=True, verbose_name='有效期止')
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    person_source = models.CharField(max_length=50, blank=True, verbose_name='人员来源')
    is_core_member = models.CharField(max_length=1, default='N', verbose_name='是否核心成员')
    project_role = models.CharField(max_length=50, blank=True, verbose_name='项目角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_project_member'
        verbose_name = '项目成员'
        verbose_name_plural = '项目成员'
    
    def __str__(self):
        return f'{self.employee_code} - {self.project_role}'


class ActualHour(models.Model):
    """实际工时表 HPM_ACTUAL_HOUR"""
    
    actual_hour_id = models.AutoField(primary_key=True, verbose_name='工时ID')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目', related_name='actual_hours')
    name = models.CharField(max_length=100, verbose_name='资源标识')
    hour_date = models.DateField(verbose_name='工时日期')
    resource_code = models.CharField(max_length=50, blank=True, verbose_name='资源代码')
    task = models.ForeignKey(
        ProjectTask, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联任务', related_name='actual_hours'
    )
    work_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='工时')
    run_time = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='运行时间')
    stop_time = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='停机时间')
    sync_month = models.CharField(max_length=10, verbose_name='同步月份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_actual_hour'
        verbose_name = '实际工时'
        verbose_name_plural = '实际工时'
    
    def __str__(self):
        return f'{self.name} - {self.hour_date} ({self.sync_month})'
