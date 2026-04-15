from django.db import migrations, models
import django.db.models.deletion


def backfill_dependencies(apps, schema_editor):
    PlanTask = apps.get_model('plan', 'PlanTask')
    PlanTaskDependency = apps.get_model('plan', 'PlanTaskDependency')

    task_by_id = {task.plan_task_id: task for task in PlanTask.objects.all()}

    rows = []
    for task in PlanTask.objects.exclude(pre_task_code='').all():
        raw = (task.pre_task_code or '').strip()
        try:
            predecessor_id = int(raw)
        except (TypeError, ValueError):
            continue

        predecessor = task_by_id.get(predecessor_id)
        if not predecessor:
            continue
        if predecessor.plan_task_id == task.plan_task_id:
            continue
        if predecessor.project_id != task.project_id:
            continue

        rows.append(
            PlanTaskDependency(
                successor_task_id=task.plan_task_id,
                predecessor_task_id=predecessor.plan_task_id,
                logic_relation=task.logic_relation or 'FS',
                lag_days=0,
                sort_order=0,
            )
        )

    if rows:
        PlanTaskDependency.objects.bulk_create(rows, ignore_conflicts=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanTaskDependency',
            fields=[
                ('dependency_id', models.AutoField(primary_key=True, serialize=False, verbose_name='依赖ID')),
                ('logic_relation', models.CharField(choices=[('FS', '完成-开始'), ('SF', '开始-完成'), ('FF', '完成-完成'), ('SS', '开始-开始')], default='FS', max_length=10, verbose_name='逻辑关系')),
                ('lag_days', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='时差(天)')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序序号')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('predecessor_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predecessor_dependencies', to='plan.plantask', verbose_name='前置任务')),
                ('successor_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='successor_dependencies', to='plan.plantask', verbose_name='后续任务')),
            ],
            options={
                'verbose_name': '任务依赖关系',
                'verbose_name_plural': '任务依赖关系',
                'db_table': 'hpm_plan_task_dependency',
                'ordering': ['successor_task_id', 'sort_order', 'dependency_id'],
                'constraints': [
                    models.UniqueConstraint(fields=('successor_task', 'predecessor_task'), name='uniq_task_dependency_pair')
                ],
            },
        ),
        migrations.RunPython(backfill_dependencies, noop_reverse),
    ]

