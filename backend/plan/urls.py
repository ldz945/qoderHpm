"""
计划管理 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('plan-tasks', views.PlanTaskViewSet)
router.register('task-categories', views.PlanTaskCategoryViewSet)
router.register('resource-plans', views.ResourcePlanViewSet)
router.register('resource-reserves', views.ResourceReserveViewSet)
router.register('plan-versions', views.PlanVersionViewSet)
router.register('change-logs', views.PlanChangeLogViewSet)

urlpatterns = router.urls
