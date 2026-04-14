"""
生成测试数据的管理命令
使用方法: python manage.py generate_test_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from master_data.models import Employee, Resource, PriceHeader, PriceLine
from project.models import Project, ProjectTask, ProjectMember, ActualHour
from plan.models import PlanTask, ResourcePlan, ResourceReserve, PlanVersion
from change.models import ChangeOrder
from acceptance.models import Acceptance
from auxiliary.models import (
    IssueRisk, SevenStep, Vpp, Scorecard, Meeting, 
    ActionItem, MiscExpense, ProjectScope, Document, DocumentFile
)


class Command(BaseCommand):
    help = '生成测试数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--projects', type=int, default=5,
            help='生成项目数量 (默认: 5)'
        )

    def handle(self, *args, **options):
        num_projects = options['projects']
        
        self.stdout.write(self.style.SUCCESS('开始生成测试数据...'))
        
        # 1. 生成主数据
        self.create_employees()
        self.create_resources()
        price_header = self.create_prices()
        
        # 2. 生成项目及相关数据
        for i in range(num_projects):
            project = self.create_project(i, price_header)
            self.create_project_tasks(project, i)
            self.create_project_members(project)
            self.create_actual_hours(project)
            self.create_plan_version(project)
            plan_tasks = self.create_plan_tasks(project)
            self.create_resource_plans(project, plan_tasks, price_header)
            self.create_resource_reserves(project)
            self.create_change_orders(project)
            self.create_acceptances(project)
            self.create_issues_risks(project)
            self.create_seven_steps(project)
            self.create_vpps(project)
            self.create_scorecards(project)
            meetings = self.create_meetings(project)
            self.create_action_items(project, meetings)
            self.create_misc_expenses(project)
            self.create_project_scopes(project)
            documents = self.create_documents(project)
            self.create_document_files(documents)
        
        self.stdout.write(self.style.SUCCESS(f'成功生成 {num_projects} 个项目的测试数据!'))

    def create_employees(self):
        """生成员工测试数据"""
        self.stdout.write('生成员工数据...')
        
        employees_data = [
            (1001, 'EMP001', '张三', '研发部', 'zhangsan@company.com'),
            (1002, 'EMP002', '李四', '研发部', 'lisi@company.com'),
            (1003, 'EMP003', '王五', '测试部', 'wangwu@company.com'),
            (1004, 'EMP004', '赵六', '产品部', 'zhaoliu@company.com'),
            (1005, 'EMP005', '钱七', '市场部', 'qianqi@company.com'),
            (1006, 'EMP006', '孙八', '研发部', 'sunba@company.com'),
            (1007, 'EMP007', '周九', '质量部', 'zhoujiu@company.com'),
            (1008, 'EMP008', '吴十', '项目部', 'wushi@company.com'),
            (1009, 'EMP009', '郑一一', '研发部', 'zhengyiyi@company.com'),
            (1010, 'EMP010', '刘二二', '测试部', 'liueree@company.com'),
        ]
        
        for emp_id, emp_code, emp_name, dept, email in employees_data:
            Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'employee_code': emp_code,
                    'employee_name': emp_name,
                    'department': dept,
                    'email': email,
                    'source': 'HPM',
                    'is_external': 'N',
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ 生成 {len(employees_data)} 名员工'))

    def create_resources(self):
        """生成资源测试数据"""
        self.stdout.write('生成资源数据...')
        
        resources_data = [
            ('RES001', 'PERSON', '高级工程师', '张三', 'Y'),
            ('RES002', 'PERSON', '测试工程师', '李四', 'Y'),
            ('RES003', 'EQUIPMENT', '测试设备A', '王五', 'Y'),
            ('RES004', 'EQUIPMENT', '测试设备B', '赵六', 'Y'),
            ('RES005', 'BENCH', '台位1号', '钱七', 'Y'),
            ('RES006', 'BENCH', '台位2号', '孙八', 'Y'),
            ('RES007', 'PERSON', '项目经理', '周九', 'Y'),
            ('RES008', 'PERSON', '产品经理', '吴十', 'Y'),
        ]
        
        for res_code, res_type, res_name, manager, enabled in resources_data:
            Resource.objects.get_or_create(
                resource_code=res_code,
                defaults={
                    'resource_type': res_type,
                    'resource_name': res_name,
                    'resource_manager': manager,
                    'daily_charge': 'Y' if res_type == 'EQUIPMENT' else 'N',
                    'enabled': enabled,
                    'short_name': res_name[:10],
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ 生成 {len(resources_data)} 个资源'))

    def create_prices(self):
        """生成价格测试数据"""
        self.stdout.write('生成价格数据...')
        
        price_header, created = PriceHeader.objects.get_or_create(
            version_name='2024标准价格',
            defaults={
                'version_no': 1,
                'currency': 'CNY',
                'effective_from': timezone.now().date(),
                'effective_to': None,
                'status': 'ACTIVE',
            }
        )
        
        if created:
            prices_data = [
                ('PERSON', 'RES001', Decimal('500.00'), 'HOUR'),
                ('PERSON', 'RES002', Decimal('300.00'), 'HOUR'),
                ('PERSON', 'RES007', Decimal('600.00'), 'HOUR'),
                ('PERSON', 'RES008', Decimal('550.00'), 'HOUR'),
                ('EQUIPMENT', 'RES003', Decimal('1000.00'), 'DAY'),
                ('EQUIPMENT', 'RES004', Decimal('800.00'), 'DAY'),
                ('BENCH', 'RES005', Decimal('2000.00'), 'DAY'),
                ('BENCH', 'RES006', Decimal('2000.00'), 'DAY'),
            ]
            
            for res_type, res_code, price, unit in prices_data:
                PriceLine.objects.get_or_create(
                    header=price_header,
                    resource_code=res_code,
                    defaults={
                        'resource_type': res_type,
                        'price': price,
                        'unit': unit,
                    }
                )
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ 生成价格版本: {price_header.version_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 价格版本已存在: {price_header.version_name}'))
        
        return price_header

    def create_project(self, index, price_header):
        """生成项目测试数据"""
        project_types = ['VPI', 'VPC', 'CPS', 'Other']
        statuses = ['DRAFT', 'ONGOING', 'HOLD', 'CLOSURE']
        levels = ['L1', 'L2', 'L3', 'L4']
        health_statuses = ['GREEN', 'BLUE', 'YELLOW', 'RED']
        
        project_id = f'PRJ{timezone.now().strftime("%Y")}{str(index + 1).zfill(3)}'
        project_code = f'HPM-{str(index + 1).zfill(3)}'
        
        project, created = Project.objects.get_or_create(
            project_id=project_id,
            defaults={
                'project_code': project_code,
                'project_name': f'测试项目{index + 1}号',
                'version': '1.0',
                'price_version': price_header,
                'project_type': random.choice(project_types),
                'quote_type': '固定报价',
                'contract_amount': Decimal(str(random.randint(100000, 1000000))),
                'currency': 'CNY',
                'status': random.choice(statuses),
                'pm': random.choice(['张三', '李四', '王五']),
                'am': random.choice(['赵六', '钱七']),
                'customer_name': random.choice(['客户A公司', '客户B公司', '客户C公司']),
                'quote_date': timezone.now().date() - timedelta(days=random.randint(30, 180)),
                'effective_date': timezone.now().date() - timedelta(days=random.randint(10, 90)),
                'project_level': random.choice(levels),
                'health_status': random.choice(health_statuses),
                'health_remark': '项目运行正常' if random.random() > 0.3 else '需要关注',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建项目: {project.project_name}'))
        else:
            self.stdout.write(f'  - 项目已存在: {project.project_name}')
        
        return project

    def create_project_tasks(self, project, project_index):
        """生成项目任务测试数据"""
        tasks_data = [
            (1001 + project_index * 100, 'TASK001', '需求分析'),
            (1002 + project_index * 100, 'TASK002', '系统设计'),
            (1003 + project_index * 100, 'TASK003', '编码实现'),
            (1004 + project_index * 100, 'TASK004', '测试验证'),
            (1005 + project_index * 100, 'TASK005', '部署上线'),
        ]
        
        for task_id, task_code, task_name in tasks_data:
            ProjectTask.objects.get_or_create(
                task_id=task_id,
                project=project,
                defaults={
                    'task_code': task_code,
                    'task_name': task_name,
                }
            )
        
        self.stdout.write(f'    ✓ 生成 {len(tasks_data)} 个项目任务')

    def create_project_members(self, project):
        """生成项目成员测试数据"""
        employees = list(Employee.objects.all()[:5])
        roles = ['项目经理', '开发工程师', '测试工程师', '产品经理', '技术负责人']
        
        for i, employee in enumerate(employees):
            ProjectMember.objects.get_or_create(
                project=project,
                employee=employee,
                effective_from=timezone.now().date(),
                defaults={
                    'employee_code': employee.employee_code,
                    'resource_code': f'RES{str(i + 1).zfill(3)}',
                    'effective_to': None,
                    'department': employee.department,
                    'person_source': 'HPM',
                    'is_core_member': 'Y' if i < 3 else 'N',
                    'project_role': roles[i] if i < len(roles) else '成员',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 {len(employees)} 个项目成员')

    def create_actual_hours(self, project):
        """生成实际工时测试数据"""
        tasks = list(project.tasks.all()[:3])
        names = ['张三', '李四', '王五']
        
        for i in range(10):
            ActualHour.objects.get_or_create(
                project=project,
                name=names[i % len(names)],
                hour_date=timezone.now().date() - timedelta(days=i),
                task=tasks[i % len(tasks)] if tasks else None,
                defaults={
                    'resource_code': f'RES{str((i % 3) + 1).zfill(3)}',
                    'work_hours': Decimal(str(round(random.uniform(4, 8), 2))),
                    'run_time': Decimal(str(round(random.uniform(6, 10), 2))),
                    'stop_time': Decimal(str(round(random.uniform(0, 2), 2))),
                    'sync_month': (timezone.now().date() - timedelta(days=i)).strftime('%Y-%m'),
                }
            )
        
        self.stdout.write(f'    ✓ 生成 10 条工时记录')

    def create_plan_version(self, project):
        """生成计划版本"""
        version, created = PlanVersion.objects.get_or_create(
            project=project,
            version_no='1.0',
            defaults={
                'version_name': '初始版本',
                'status': 'PUBLISHED',
                'is_current': True,
                'publish_date': timezone.now().date(),
                'published_by': '张三',
                'created_by': '张三',
            }
        )
        
        if created:
            self.stdout.write(f'    ✓ 创建计划版本: {version.version_no}')
        
        return version

    def create_plan_tasks(self, project):
        """生成计划任务(WBS)测试数据"""
        version = project.plan_versions.first()
        
        phases = ['需求阶段', '设计阶段', '开发阶段', '测试阶段']
        tasks_data = []
        
        for phase_idx, phase in enumerate(phases):
            # 父任务
            parent_task, _ = PlanTask.objects.get_or_create(
                project=project,
                task_name=f'{phase}',
                task_level=1,
                phase=phase,
                defaults={
                    'planned_start_date': timezone.now().date() + timedelta(days=phase_idx * 10),
                    'planned_end_date': timezone.now().date() + timedelta(days=(phase_idx + 1) * 10 - 1),
                    'task_status': 'NOT_STARTED' if phase_idx > 0 else 'IN_PROGRESS',
                    'created_by': '张三',
                    'version': version,
                }
            )
            tasks_data.append(parent_task)
            
            # 子任务
            for sub_idx in range(3):
                PlanTask.objects.get_or_create(
                    project=project,
                    parent_task=parent_task,
                    task_name=f'{phase}-任务{sub_idx + 1}',
                    task_level=2,
                    phase=phase,
                    defaults={
                        'planned_start_date': timezone.now().date() + timedelta(days=phase_idx * 10 + sub_idx * 3),
                        'planned_end_date': timezone.now().date() + timedelta(days=phase_idx * 10 + sub_idx * 3 + 2),
                        'task_status': random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED']),
                        'workload_days': Decimal(str(random.randint(5, 20))),
                        'is_hour_task': 'Y',
                        'created_by': '张三',
                        'version': version,
                    }
                )
        
        self.stdout.write(f'    ✓ 生成 WBS 任务 (4个父任务, 12个子任务)')
        
        return list(project.plan_tasks.all())

    def create_resource_plans(self, project, plan_tasks, price_header):
        """生成资源计划测试数据"""
        if not plan_tasks:
            return
        
        resource_types = ['PERSON', 'EQUIPMENT', 'BENCH']
        resource_codes = ['RES001', 'RES002', 'RES003', 'RES005']
        
        for i, task in enumerate(plan_tasks[:5]):
            if task.task_level == 1:  # 只为父任务创建资源计划
                ResourcePlan.objects.get_or_create(
                    project=project,
                    task=task,
                    resource_code=resource_codes[i % len(resource_codes)],
                    defaults={
                        'resource_type': resource_types[i % len(resource_types)],
                        'resource_name': f'资源{i + 1}',
                        'resource_quantity': random.randint(1, 3),
                        'daily_effective_hours': Decimal('8.00'),
                        'resource_price': Decimal(str(random.randint(300, 800))),
                        'price_unit': 'HOUR',
                        'planned_start_date': task.planned_start_date,
                        'planned_end_date': task.planned_end_date,
                        'include_weekend': 'N',
                        'price_version': price_header,
                        'resource_manager': '张三',
                        'status': 'ACTIVE',
                    }
                )
        
        self.stdout.write(f'    ✓ 生成资源计划')

    def create_resource_reserves(self, project):
        """生成资源预占测试数据"""
        for i in range(3):
            ResourceReserve.objects.get_or_create(
                project=project,
                resource_code=f'RES{str(i + 1).zfill(3)}',
                reserve_start_time=timezone.now() + timedelta(days=i),
                defaults={
                    'project_short_code': project.project_code,
                    'resource_type': ['BENCH', 'PERSON', 'EQUIPMENT'][i],
                    'resource_name': f'资源{i + 1}',
                    'reserve_end_time': timezone.now() + timedelta(days=i + 5),
                    'reserve_status': 'RESERVED',
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 3 条资源预占')

    def create_change_orders(self, project):
        """生成变更单测试数据"""
        for i in range(2):
            ChangeOrder.objects.get_or_create(
                change_no=f'CHG-{project.project_code}-{str(i + 1).zfill(3)}',
                defaults={
                    'project': project,
                    'change_type': '范围变更',
                    'change_field': '项目计划',
                    'old_value': '原计划',
                    'new_value': '新计划',
                    'change_impact': '影响项目进度',
                    'change_reason': '客户需求变更',
                    'change_content': '调整项目计划安排',
                    'status': random.choice(['DRAFT', 'PENDING', 'APPROVED']),
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 2 个变更单')

    def create_acceptances(self, project):
        """生成验收单测试数据"""
        for i in range(2):
            Acceptance.objects.get_or_create(
                acceptance_no=f'ACC-{project.project_code}-{str(i + 1).zfill(3)}',
                defaults={
                    'project': project,
                    'acceptance_type': '阶段验收',
                    'acceptance_phase': f'阶段{i + 1}',
                    'acceptance_status': random.choice(['DRAFT', 'IN_PROGRESS', 'COMPLETED']),
                    'vpp_verified': 'Y',
                    'acceptance_date': timezone.now().date() - timedelta(days=random.randint(1, 30)),
                    'accepted_by': '李四',
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 2 个验收单')

    def create_issues_risks(self, project):
        """生成问题/风险测试数据"""
        for i in range(3):
            IssueRisk.objects.get_or_create(
                issue_no=f'ISS-{project.project_code}-{str(i + 1).zfill(3)}',
                defaults={
                    'project': project,
                    'type': random.choice(['ISSUE', 'RISK']),
                    'title': f'问题/风险标题{i + 1}',
                    'description': f'这是问题/风险的详细描述{i + 1}',
                    'owner': random.choice(['张三', '李四', '王五']),
                    'issue_type': '技术问题',
                    'status': random.choice(['DRAFT', 'IN_PROGRESS', 'COMPLETED']),
                    'severity': random.choice(['MAJOR_IMPACT', 'SOME_IMPACT', 'NO_IMPACT']),
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 3 个问题/风险')

    def create_seven_steps(self, project):
        """生成七步法测试数据"""
        SevenStep.objects.get_or_create(
            step_no=f'7S-{project.project_code}-001',
            defaults={
                'project': project,
                'problem_description': '发现一个需要七步法解决的问题',
                'figr_owner': '张三',
                'figr_team': '张三,李四,王五',
                'platform_impact': 'Y',
                'local_specialist': '赵六',
                'current_step': 3,
                'step1_define': '问题定义：系统性能下降',
                'step2_contain': '遏制措施：增加监控',
                'step3_root_cause': '根本原因：数据库查询优化不足',
                'status': 'IN_PROGRESS',
                'created_by': '张三',
            }
        )
        
        self.stdout.write(f'    ✓ 生成 1 个七步法')

    def create_vpps(self, project):
        """生成VPP测试数据"""
        Vpp.objects.get_or_create(
            project=project,
            version_no='1.0',
            defaults={
                'description': '初始VPP版本',
                'status': 'PUBLISHED',
                'created_by': '张三',
                'published_by': '张三',
                'published_at': timezone.now(),
            }
        )
        
        self.stdout.write(f'    ✓ 生成 1 个VPP')

    def create_scorecards(self, project):
        """生成积分卡测试数据"""
        for phase in ['需求阶段', '设计阶段']:
            Scorecard.objects.get_or_create(
                project=project,
                phase=phase,
                defaults={
                    'template_type': 'L1',
                    'score_data': '{"score1": 85, "score2": 90}',
                    'total_score': Decimal('87.50'),
                    'status': 'COMPLETED',
                    'evaluated_by': '张三',
                    'evaluated_at': timezone.now(),
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 2 个积分卡')

    def create_meetings(self, project):
        """生成会议测试数据"""
        meetings = []
        for i in range(3):
            meeting, created = Meeting.objects.get_or_create(
                project=project,
                meeting_subject=f'项目会议{i + 1}',
                meeting_date=timezone.now().date() + timedelta(days=i * 7),
                defaults={
                    'meeting_time': '14:00-16:00',
                    'meeting_duration': 120,
                    'organizer': '张三',
                    'attendees': '张三,李四,王五',
                    'meeting_location': f'会议室{i + 1}',
                    'meeting_type': '周会',
                    'status': 'SCHEDULED',
                    'created_by': '张三',
                }
            )
            meetings.append(meeting)
        
        self.stdout.write(f'    ✓ 生成 {len(meetings)} 个会议')
        return meetings

    def create_action_items(self, project, meetings):
        """生成行动项测试数据"""
        for i in range(5):
            ActionItem.objects.get_or_create(
                action_no=f'AI-{project.project_code}-{str(i + 1).zfill(3)}',
                defaults={
                    'project': project,
                    'meeting': meetings[i % len(meetings)] if meetings else None,
                    'description': f'行动项描述{i + 1}',
                    'recorder': '张三',
                    'current_owner': random.choice(['张三', '李四', '王五']),
                    'status': random.choice(['IN_PROGRESS', 'COMPLETED']),
                    'priority': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                    'planned_finish_date': timezone.now().date() + timedelta(days=random.randint(7, 30)),
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 5 个行动项')

    def create_misc_expenses(self, project):
        """生成杂项费用测试数据"""
        expense_types = ['RESERVE_FUND', 'FUEL', 'TRAVEL', 'PURCHASE']
        
        for i, expense_type in enumerate(expense_types):
            MiscExpense.objects.get_or_create(
                project=project,
                settlement_period=(timezone.now().date() - timedelta(days=30 * i)).strftime('%Y-%m'),
                expense_type=expense_type,
                defaults={
                    'department': '研发部',
                    'resource_type': '人员',
                    'resource_name': '张三',
                    'estimated_price': Decimal(str(random.randint(100, 1000))),
                    'estimated_quantity': Decimal(str(random.randint(1, 10))),
                    'estimated_amount': Decimal(str(random.randint(1000, 10000))),
                    'actual_price': Decimal(str(random.randint(100, 1000))),
                    'actual_quantity': Decimal(str(random.randint(1, 10))),
                    'actual_amount': Decimal(str(random.randint(1000, 10000))),
                    'status': 'ACTIVE',
                    'created_by': '张三',
                }
            )
        
        self.stdout.write(f'    ✓ 生成 {len(expense_types)} 条杂项费用')

    def create_project_scopes(self, project):
        """生成项目范围测试数据"""
        ProjectScope.objects.get_or_create(
            project=project,
            version_no='1.0',
            defaults={
                'scope_content': '项目范围内容：包括需求分析、系统设计、开发实现、测试验证等阶段',
                'status': 'EFFECTIVE',
                'effective_from': timezone.now().date(),
                'created_by': '张三',
                'approved_by': '李四',
                'approved_at': timezone.now(),
            }
        )
        
        self.stdout.write(f'    ✓ 生成 1 个项目范围')

    def create_documents(self, project):
        """生成文档目录测试数据"""
        documents = []
        
        # 一级目录
        for i in range(3):
            doc, created = Document.objects.get_or_create(
                project=project,
                level_code=f'L1-{str(i + 1).zfill(3)}',
                defaults={
                    'catalog_name': f'文档目录{i + 1}',
                    'catalog_desc': f'这是一级文档目录{i + 1}',
                    'parent': None,
                    'level': 1,
                    'enabled': 'Y',
                    'sort_order': i,
                    'created_by': '张三',
                }
            )
            documents.append(doc)
            
            # 二级目录
            for j in range(2):
                sub_doc, _ = Document.objects.get_or_create(
                    project=project,
                    level_code=f'L1-{str(i + 1).zfill(3)}-L2-{str(j + 1).zfill(3)}',
                    defaults={
                        'catalog_name': f'子目录{i + 1}-{j + 1}',
                        'catalog_desc': f'这是二级文档目录',
                        'parent': doc,
                        'level': 2,
                        'enabled': 'Y',
                        'sort_order': j,
                        'created_by': '张三',
                    }
                )
                documents.append(sub_doc)
        
        self.stdout.write(f'    ✓ 生成文档目录结构')
        return documents

    def create_document_files(self, documents):
        """生成文档文件测试数据"""
        if not documents:
            return
        
        for i, doc in enumerate(documents[:5]):
            DocumentFile.objects.get_or_create(
                catalog=doc,
                file_name=f'测试文档{i + 1}.pdf',
                defaults={
                    'file_path': f'/documents/test_doc_{i + 1}.pdf',
                    'file_size': random.randint(100000, 1000000),
                    'file_type': 'PDF',
                    'version_no': '1.0',
                    'description': f'这是一个测试文档',
                    'uploaded_by': '张三',
                    'is_latest': 'Y',
                    'status': 'ACTIVE',
                }
            )
        
        self.stdout.write(f'    ✓ 生成文档文件')
