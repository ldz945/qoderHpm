"""
辅助功能模块 - Auxiliary App Models
包含：问题风险、七步法、VPP、积分卡、会议、行动项、杂项费用、项目范围、文档目录、文档文件
"""

from django.db import models


class IssueRisk(models.Model):
    """问题/风险表 HPM_ISSUE_RISK"""
    
    TYPE_CHOICES = [
        ('ISSUE', '问题'),
        ('RISK', '风险'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('IN_PROGRESS', '进行中'),
        ('CANCEL', '已取消'),
        ('COMPLETED', '已完成'),
    ]
    
    SEVERITY_CHOICES = [
        ('MAJOR_IMPACT', '重大影响'),
        ('SOME_IMPACT', '一定影响'),
        ('NO_IMPACT', '无影响'),
    ]
    
    CAPABILITY_CHOICES = [
        ('INCAPABLE', '无能力'),
        ('MARGINAL', '边缘能力'),
        ('CAPABLE', '有能力'),
    ]
    
    issue_id = models.AutoField(primary_key=True, verbose_name='问题/风险ID')
    issue_no = models.CharField(max_length=50, unique=True, verbose_name='编号')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    owner = models.CharField(max_length=100, blank=True, verbose_name='负责人')
    issue_type = models.CharField(max_length=50, blank=True, verbose_name='问题类型')
    status = models.CharField(
        max_length=20,
        default='DRAFT',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    severity = models.CharField(
        max_length=20,
        blank=True,
        choices=SEVERITY_CHOICES,
        verbose_name='严重程度'
    )
    capability = models.CharField(
        max_length=20,
        blank=True,
        choices=CAPABILITY_CHOICES,
        verbose_name='能力'
    )
    program = models.CharField(max_length=100, blank=True, verbose_name='项目集')
    next_m_review = models.CharField(max_length=500, blank=True, verbose_name='下次评审')
    next_m_review_date = models.DateField(null=True, blank=True, verbose_name='下次评审日期')
    revision_date = models.DateField(null=True, blank=True, verbose_name='修订日期')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    closed_by = models.CharField(max_length=100, blank=True, verbose_name='关闭人')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='关闭时间')
    
    class Meta:
        db_table = 'hpm_issue_risk'
        verbose_name = '问题/风险'
        verbose_name_plural = '问题/风险'
    
    def __str__(self):
        return f"{self.issue_no} ({self.title})"


class SevenStep(models.Model):
    """七步法表 HPM_SEVEN_STEP"""
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', '进行中'),
        ('COMPLETED', '已完成'),
        ('CLOSED', '已关闭'),
    ]
    
    step_id = models.AutoField(primary_key=True, verbose_name='七步法ID')
    step_no = models.CharField(max_length=50, unique=True, verbose_name='编号')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    problem_description = models.TextField(verbose_name='问题描述')
    figr_owner = models.CharField(max_length=100, blank=True, verbose_name='FIGR负责人')
    figr_team = models.CharField(max_length=200, blank=True, verbose_name='FIGR团队')
    platform_impact = models.CharField(max_length=1, default='N', verbose_name='平台影响')
    local_specialist = models.CharField(max_length=100, blank=True, verbose_name='本地专家')
    current_step = models.IntegerField(default=1, verbose_name='当前步骤')
    step1_define = models.TextField(blank=True, verbose_name='步骤1-定义')
    step2_contain = models.TextField(blank=True, verbose_name='步骤2-遏制')
    step3_root_cause = models.TextField(blank=True, verbose_name='步骤3-根本原因')
    step4_correct = models.TextField(blank=True, verbose_name='步骤4-纠正措施')
    step5_verify = models.TextField(blank=True, verbose_name='步骤5-验证')
    step6_prevent = models.TextField(blank=True, verbose_name='步骤6-预防')
    step7_congratulate = models.TextField(blank=True, verbose_name='步骤7-祝贺')
    next_action = models.TextField(blank=True, verbose_name='下一步行动')
    risk_assessment = models.TextField(blank=True, verbose_name='风险评估')
    status = models.CharField(
        max_length=20,
        default='IN_PROGRESS',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_seven_step'
        verbose_name = '七步法'
        verbose_name_plural = '七步法'
    
    def __str__(self):
        return f"{self.step_no} (步骤{self.current_step})"


class Vpp(models.Model):
    """VPP表 HPM_VPP"""
    
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('PUBLISHED', '已发布'),
        ('ARCHIVED', '已归档'),
    ]
    
    vpp_id = models.AutoField(primary_key=True, verbose_name='VPP ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    version_no = models.CharField(max_length=20, default='1.0', verbose_name='版本号')
    description = models.TextField(blank=True, verbose_name='描述')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='文件路径')
    status = models.CharField(
        max_length=20,
        default='DRAFT',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    published_by = models.CharField(max_length=100, blank=True, verbose_name='发布人')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    
    class Meta:
        db_table = 'hpm_vpp'
        verbose_name = 'VPP'
        verbose_name_plural = 'VPP'
        unique_together = [['project', 'version_no']]
    
    def __str__(self):
        return f"VPP {self.version_no} ({self.project})"


class Scorecard(models.Model):
    """积分卡表 HPM_SCORECARD"""
    
    TEMPLATE_TYPE_CHOICES = [
        ('L1', 'L1'),
        ('L2', 'L2'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('COMPLETED', '已完成'),
    ]
    
    scorecard_id = models.AutoField(primary_key=True, verbose_name='积分卡ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    template_type = models.CharField(
        max_length=10,
        choices=TEMPLATE_TYPE_CHOICES,
        verbose_name='模板类型'
    )
    phase = models.CharField(max_length=50, verbose_name='阶段')
    score_data = models.TextField(blank=True, verbose_name='评分数据')
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='总分')
    status = models.CharField(
        max_length=20,
        default='DRAFT',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    evaluated_by = models.CharField(max_length=100, blank=True, verbose_name='评估人')
    evaluated_at = models.DateTimeField(null=True, blank=True, verbose_name='评估时间')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_scorecard'
        verbose_name = '积分卡'
        verbose_name_plural = '积分卡'
        unique_together = [['project', 'phase']]
    
    def __str__(self):
        return f"{self.project} - {self.phase} ({self.total_score})"


class Meeting(models.Model):
    """会议表 HPM_MEETING"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', '已安排'),
        ('IN_PROGRESS', '进行中'),
        ('COMPLETED', '已结束'),
        ('CANCELLED', '已取消'),
    ]
    
    meeting_id = models.AutoField(primary_key=True, verbose_name='会议ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    meeting_subject = models.CharField(max_length=200, verbose_name='会议主题')
    meeting_date = models.DateField(verbose_name='会议日期')
    meeting_time = models.CharField(max_length=50, blank=True, verbose_name='会议时间')
    meeting_duration = models.IntegerField(default=60, verbose_name='会议时长(分钟)')
    organizer = models.CharField(max_length=100, verbose_name='组织人')
    attendees = models.TextField(blank=True, verbose_name='参会人员')
    meeting_location = models.CharField(max_length=200, blank=True, verbose_name='会议地点')
    meeting_content = models.TextField(blank=True, verbose_name='会议纪要')
    meeting_type = models.CharField(max_length=50, blank=True, verbose_name='会议类型')
    status = models.CharField(
        max_length=20,
        default='SCHEDULED',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_meeting'
        verbose_name = '会议'
        verbose_name_plural = '会议'
    
    def __str__(self):
        return f"{self.meeting_subject} ({self.meeting_date})"


class ActionItem(models.Model):
    """行动项表 HPM_ACTION_ITEM"""
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', '进行中'),
        ('CANCEL', '已取消'),
        ('COMPLETED', '已完成'),
    ]
    
    PRIORITY_CHOICES = [
        ('HIGH', '高'),
        ('MEDIUM', '中'),
        ('LOW', '低'),
    ]
    
    action_id = models.AutoField(primary_key=True, verbose_name='行动项ID')
    action_no = models.CharField(max_length=50, unique=True, verbose_name='编号')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联会议'
    )
    description = models.TextField(verbose_name='描述')
    recorder = models.CharField(max_length=100, verbose_name='记录人')
    current_owner = models.CharField(max_length=100, verbose_name='当前负责人')
    status = models.CharField(
        max_length=20,
        default='IN_PROGRESS',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    priority = models.CharField(
        max_length=20,
        default='MEDIUM',
        choices=PRIORITY_CHOICES,
        verbose_name='优先级'
    )
    planned_finish_date = models.DateField(null=True, blank=True, verbose_name='计划完成日期')
    actual_finish_date = models.DateField(null=True, blank=True, verbose_name='实际完成日期')
    completion_remark = models.TextField(blank=True, verbose_name='完成备注')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_action_item'
        verbose_name = '行动项'
        verbose_name_plural = '行动项'
    
    def __str__(self):
        return f"{self.action_no} ({self.description[:30]})"


class MiscExpense(models.Model):
    """杂项费用表 HPM_MISC_EXPENSE"""
    
    STATUS_CHOICES = [
        ('ACTIVE', '有效'),
        ('INACTIVE', '无效'),
    ]
    
    EXPENSE_TYPE_CHOICES = [
        ('RESERVE_FUND', '备用金'),
        ('FUEL', '油耗'),
        ('TRAVEL', '项目差旅'),
        ('PURCHASE', '采购'),
    ]
    
    expense_id = models.AutoField(primary_key=True, verbose_name='费用ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    settlement_period = models.CharField(max_length=10, verbose_name='结算周期')
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    resource_type = models.CharField(max_length=50, blank=True, verbose_name='资源类型')
    resource_name = models.CharField(max_length=200, blank=True, verbose_name='资源名称')
    estimated_price = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='预计单价')
    estimated_quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='预计数量')
    estimated_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='预计金额')
    actual_price = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='实际单价')
    actual_quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='实际数量')
    actual_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='实际金额')
    remark = models.TextField(blank=True, verbose_name='备注')
    status = models.CharField(
        max_length=20,
        default='ACTIVE',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    expense_type = models.CharField(
        max_length=50,
        choices=EXPENSE_TYPE_CHOICES,
        verbose_name='费用类型'
    )
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_misc_expense'
        verbose_name = '杂项费用'
        verbose_name_plural = '杂项费用'
    
    def __str__(self):
        return f"{self.expense_type} ({self.settlement_period})"


class ProjectScope(models.Model):
    """项目范围表 HPM_PROJECT_SCOPE"""
    
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('EFFECTIVE', '生效'),
        ('MODIFIABLE', '可变更'),
    ]
    
    scope_id = models.AutoField(primary_key=True, verbose_name='范围ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    version_no = models.CharField(max_length=20, verbose_name='版本号')
    scope_content = models.TextField(verbose_name='范围内容')
    status = models.CharField(
        max_length=20,
        default='DRAFT',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    effective_from = models.DateField(null=True, blank=True, verbose_name='生效日期')
    effective_to = models.DateField(null=True, blank=True, verbose_name='失效日期')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    approved_by = models.CharField(max_length=100, blank=True, verbose_name='审批人')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    
    class Meta:
        db_table = 'hpm_project_scope'
        verbose_name = '项目范围'
        verbose_name_plural = '项目范围'
        unique_together = [['project', 'version_no']]
    
    def __str__(self):
        return f"{self.project} - {self.version_no}"


class Document(models.Model):
    """文档目录表 HPM_DOCUMENT"""
    
    catalog_id = models.AutoField(primary_key=True, verbose_name='目录ID')
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='项目'
    )
    catalog_name = models.CharField(max_length=200, verbose_name='目录名称')
    catalog_desc = models.CharField(max_length=500, blank=True, verbose_name='目录描述')
    level_code = models.CharField(max_length=100, verbose_name='层级编码')
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='父目录'
    )
    level = models.IntegerField(default=1, verbose_name='层级')
    enabled = models.CharField(max_length=1, default='Y', verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    created_by = models.CharField(max_length=100, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_document'
        verbose_name = '文档目录'
        verbose_name_plural = '文档目录'
        unique_together = [['project', 'level_code']]
    
    def __str__(self):
        return f"{self.catalog_name} ({self.level_code})"


class DocumentFile(models.Model):
    """文档文件表 HPM_DOCUMENT_FILE"""
    
    STATUS_CHOICES = [
        ('ACTIVE', '有效'),
        ('DELETED', '已删除'),
    ]
    
    file_id = models.AutoField(primary_key=True, verbose_name='文件ID')
    catalog = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name='所属目录'
    )
    file_name = models.CharField(max_length=200, verbose_name='文件名')
    file_path = models.CharField(max_length=500, verbose_name='文件路径')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小')
    file_type = models.CharField(max_length=50, blank=True, verbose_name='文件类型')
    version_no = models.CharField(max_length=20, default='1.0', verbose_name='版本号')
    description = models.TextField(blank=True, verbose_name='描述')
    uploaded_by = models.CharField(max_length=100, verbose_name='上传人')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    is_latest = models.CharField(max_length=1, default='Y', verbose_name='是否最新')
    status = models.CharField(
        max_length=20,
        default='ACTIVE',
        choices=STATUS_CHOICES,
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hpm_document_file'
        verbose_name = '文档文件'
        verbose_name_plural = '文档文件'
    
    def __str__(self):
        return f"{self.file_name} ({self.version_no})"
