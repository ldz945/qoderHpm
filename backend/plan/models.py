"""
计划管理 - 数据模型定义
包含：PlanTask, ResourcePlan, ResourceReserve, PlanVersion
"""

from django.db import models


class PlanVersion(models.Model):
    """计划版本"""

    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('PUBLISHED', '已发布'),
        ('ARCHIVED', '已归档'),
    ]

    version_id = models.AutoField(primary_key=True, verbose_name='版本ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='所属项目',
        related_name='plan_versions'
    )
    version_no = models.CharField(max_length=20, verbose_name='版本号')
    version_name = models.CharField(max_length=100, blank=True, verbose_name='版本名称')
    status = models.CharField(
        max_length=20, default='DRAFT', choices=STATUS_CHOICES, verbose_name='状态'
    )
    is_current = models.BooleanField(default=False, verbose_name='是否当前版本')
    publish_date = models.DateField(null=True, blank=True, verbose_name='发布日期')
    published_by = models.CharField(max_length=100, blank=True, verbose_name='发布人')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hpm_plan_version'
        verbose_name = '计划版本'
        verbose_name_plural = '计划版本'
        unique_together = [['project', 'version_no']]

    def __str__(self):
        return f'{self.project_id} - {self.version_no} ({self.get_status_display()})'


class PlanTask(models.Model):
    """计划任务（WBS）"""

    LOGIC_RELATION_CHOICES = [
        ('FS', '完成-开始'),
        ('SF', '开始-完成'),
        ('FF', '完成-完成'),
        ('SS', '开始-开始'),
    ]

    TASK_STATUS_CHOICES = [
        ('NOT_STARTED', '未开始'),
        ('IN_PROGRESS', '进行中'),
        ('COMPLETED', '已完成'),
        ('SUSPENDED', '已暂停'),
        ('CANCELLED', '已取消'),
        ('DELAYED', '已延期'),
        ('PENDING_REVIEW', '待审核'),
        ('APPROVED', '已审批'),
        ('REJECTED', '已驳回'),
    ]

    plan_task_id = models.AutoField(primary_key=True, verbose_name='任务ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='所属项目',
        related_name='plan_tasks'
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父任务'
    )
    task_name = models.CharField(max_length=200, verbose_name='任务名称')
    task_level = models.IntegerField(default=1, verbose_name='任务层级')
    pre_task_code = models.CharField(max_length=50, blank=True, verbose_name='前置任务编码')
    logic_relation = models.CharField(
        max_length=10, default='FS', choices=LOGIC_RELATION_CHOICES, verbose_name='逻辑关系'
    )
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    task_owner = models.CharField(max_length=100, blank=True, verbose_name='任务负责人')
    authorized_owner = models.CharField(max_length=100, blank=True, verbose_name='授权负责人')
    planned_start_date = models.DateField(null=True, blank=True, verbose_name='计划开始日期')
    planned_end_date = models.DateField(null=True, blank=True, verbose_name='计划结束日期')
    workload_days = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='工作量（天）'
    )
    task_status = models.CharField(
        max_length=20, default='NOT_STARTED', choices=TASK_STATUS_CHOICES, verbose_name='任务状态'
    )
    has_deliverable = models.CharField(max_length=1, default='N', verbose_name='是否有交付物')
    is_hour_task = models.CharField(max_length=1, default='N', verbose_name='是否工时任务')
    acceptance_item = models.CharField(max_length=500, blank=True, verbose_name='验收项')
    remark = models.TextField(blank=True, verbose_name='备注')
    phase = models.CharField(max_length=50, blank=True, verbose_name='阶段')
    progress_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name='完成百分比'
    )
    baseline_start_date = models.DateField(null=True, blank=True, verbose_name='基线开始日期')
    baseline_end_date = models.DateField(null=True, blank=True, verbose_name='基线结束日期')
    include_weekend = models.CharField(max_length=1, default='N', verbose_name='包含周末')
    version = models.ForeignKey(
        PlanVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='计划版本',
        related_name='tasks'
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序序号')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hpm_plan_task'
        verbose_name = '计划任务'
        verbose_name_plural = '计划任务'
        ordering = ['sort_order', 'plan_task_id']

    def __str__(self):
        return f'{self.task_name} ({self.get_task_status_display()})'


class PlanTaskDependency(models.Model):
    """任务依赖关系（支持一个任务多个前置）"""

    LOGIC_RELATION_CHOICES = PlanTask.LOGIC_RELATION_CHOICES

    dependency_id = models.AutoField(primary_key=True, verbose_name='依赖ID')
    successor_task = models.ForeignKey(
        PlanTask,
        on_delete=models.CASCADE,
        related_name='successor_dependencies',
        verbose_name='后续任务'
    )
    predecessor_task = models.ForeignKey(
        PlanTask,
        on_delete=models.CASCADE,
        related_name='predecessor_dependencies',
        verbose_name='前置任务'
    )
    logic_relation = models.CharField(
        max_length=10,
        default='FS',
        choices=LOGIC_RELATION_CHOICES,
        verbose_name='逻辑关系'
    )
    lag_days = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='时差(天)')
    sort_order = models.IntegerField(default=0, verbose_name='排序序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hpm_plan_task_dependency'
        verbose_name = '任务依赖关系'
        verbose_name_plural = '任务依赖关系'
        ordering = ['successor_task_id', 'sort_order', 'dependency_id']
        constraints = [
            models.UniqueConstraint(
                fields=['successor_task', 'predecessor_task'],
                name='uniq_task_dependency_pair'
            )
        ]

    def __str__(self):
        return f'{self.predecessor_task_id}->{self.successor_task_id} ({self.logic_relation})'


class PlanTaskCategory(models.Model):
    """计划任务类别字典（部门/负责人）"""

    CATEGORY_TYPE_CHOICES = [
        ('DEPARTMENT', '部门'),
        ('OWNER', '负责人'),
    ]

    category_id = models.AutoField(primary_key=True, verbose_name='类别ID')
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, verbose_name='类别类型')
    category_value = models.CharField(max_length=100, verbose_name='类别值')
    enabled = models.CharField(max_length=1, default='Y', verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hpm_plan_task_category'
        verbose_name = '计划任务类别'
        verbose_name_plural = '计划任务类别'
        ordering = ['category_type', 'sort_order', 'category_id']
        unique_together = [['category_type', 'category_value']]

    def __str__(self):
        return f'{self.category_type}:{self.category_value}'


class PlanChangeLog(models.Model):
    """计划/基线变更记录"""

    CHANGE_TYPE_CHOICES = [
        ('PLAN', '计划变更'),
        ('BASELINE', '基线变更'),
    ]

    log_id = models.AutoField(primary_key=True, verbose_name='记录ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='所属项目',
        related_name='plan_change_logs',
    )
    change_type = models.CharField(
        max_length=20, choices=CHANGE_TYPE_CHOICES, default='PLAN', verbose_name='变更类型'
    )
    change_reason = models.TextField(verbose_name='变更原因')
    affected_count = models.IntegerField(default=0, verbose_name='影响任务数')
    affected_task_ids = models.TextField(blank=True, verbose_name='受影响任务ID(逗号分隔)')
    detail = models.TextField(blank=True, verbose_name='变更明细(JSON)')
    operator = models.CharField(max_length=100, verbose_name='操作人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='变更时间')

    class Meta:
        db_table = 'hpm_plan_change_log'
        verbose_name = '计划变更记录'
        verbose_name_plural = '计划变更记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.project_id} [{self.get_change_type_display()}] {self.created_at:%Y-%m-%d %H:%M}'


class ResourcePlan(models.Model):
    """资源计划"""

    RESOURCE_TYPE_CHOICES = [
        ('PERSON', '人员'),
        ('EQUIPMENT', '设备'),
        ('BENCH', '台位'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', '有效'),
        ('INACTIVE', '无效'),
    ]

    resource_plan_id = models.AutoField(primary_key=True, verbose_name='资源计划ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='所属项目',
        related_name='resource_plans'
    )
    task = models.ForeignKey(
        PlanTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联任务',
        related_name='resource_plans'
    )
    resource_type = models.CharField(
        max_length=50, choices=RESOURCE_TYPE_CHOICES, verbose_name='资源类型'
    )
    resource_code = models.CharField(max_length=50, verbose_name='资源编码')
    resource_name = models.CharField(max_length=200, blank=True, verbose_name='资源名称')
    resource_quantity = models.IntegerField(default=1, verbose_name='资源数量')
    daily_effective_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=8, verbose_name='日有效工时（小时）'
    )
    resource_price = models.DecimalField(
        max_digits=18, decimal_places=2, default=0, verbose_name='资源单价'
    )
    price_unit = models.CharField(max_length=20, default='HOUR', verbose_name='计价单位')
    planned_start_date = models.DateField(null=True, blank=True, verbose_name='计划开始日期')
    planned_end_date = models.DateField(null=True, blank=True, verbose_name='计划结束日期')
    include_weekend = models.CharField(max_length=1, default='N', verbose_name='包含周末')
    price_version = models.ForeignKey(
        'master_data.PriceHeader',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='价格版本',
        related_name='resource_plans'
    )
    resource_manager = models.CharField(max_length=100, blank=True, verbose_name='资源管理人')
    remark = models.TextField(blank=True, verbose_name='备注')
    status = models.CharField(
        max_length=20, default='ACTIVE', choices=STATUS_CHOICES, verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hpm_resource_plan'
        verbose_name = '资源计划'
        verbose_name_plural = '资源计划'

    def __str__(self):
        return f'{self.resource_name or self.resource_code} ({self.get_resource_type_display()})'


class ResourceReserve(models.Model):
    """资源预占"""

    RESOURCE_TYPE_CHOICES = [
        ('BENCH', '台位'),
        ('PERSON', '人员'),
        ('EQUIPMENT', '设备'),
    ]

    RESERVE_STATUS_CHOICES = [
        ('RESERVED', '已预占'),
        ('RELEASED', '已释放'),
        ('USED', '已使用'),
    ]

    reserve_id = models.AutoField(primary_key=True, verbose_name='预占ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='所属项目',
        related_name='resource_reserves'
    )
    project_short_code = models.CharField(max_length=50, verbose_name='项目简码')
    resource_type = models.CharField(
        max_length=50, choices=RESOURCE_TYPE_CHOICES, verbose_name='资源类型'
    )
    resource_code = models.CharField(max_length=50, verbose_name='资源编码')
    resource_name = models.CharField(max_length=200, blank=True, verbose_name='资源名称')
    reserve_start_time = models.DateTimeField(verbose_name='预占开始时间')
    reserve_end_time = models.DateTimeField(verbose_name='预占结束时间')
    reserve_status = models.CharField(
        max_length=20, default='RESERVED', choices=RESERVE_STATUS_CHOICES, verbose_name='预占状态'
    )
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hpm_resource_reserve'
        verbose_name = '资源预占'
        verbose_name_plural = '资源预占'

    def __str__(self):
        return f'{self.resource_name or self.resource_code} [{self.get_reserve_status_display()}]'
