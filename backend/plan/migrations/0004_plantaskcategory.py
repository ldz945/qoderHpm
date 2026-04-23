from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0003_add_baseline_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanTaskCategory',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False, verbose_name='类别ID')),
                ('category_type', models.CharField(choices=[('DEPARTMENT', '部门'), ('OWNER', '负责人')], max_length=20, verbose_name='类别类型')),
                ('category_value', models.CharField(max_length=100, verbose_name='类别值')),
                ('enabled', models.CharField(default='Y', max_length=1, verbose_name='是否启用')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序序号')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '计划任务类别',
                'verbose_name_plural': '计划任务类别',
                'db_table': 'hpm_plan_task_category',
                'ordering': ['category_type', 'sort_order', 'category_id'],
                'unique_together': {('category_type', 'category_value')},
            },
        ),
    ]

