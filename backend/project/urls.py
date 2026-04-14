"""
项目管理 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('projects', views.ProjectViewSet)
router.register('project-tasks', views.ProjectTaskViewSet)
router.register('project-members', views.ProjectMemberViewSet)
router.register('actual-hours', views.ActualHourViewSet)

urlpatterns = router.urls
