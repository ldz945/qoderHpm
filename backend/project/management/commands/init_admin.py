from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create initial admin user (admin/hpm123456) with SUPER_ADMIN role'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
            return
        user = User.objects.create_superuser(
            username='admin',
            password='hpm123456',
            first_name='系统管理员',
            last_name='SUPER_ADMIN',
            email='admin@hpm.local',
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin user (id={user.id}), password: hpm123456'))

