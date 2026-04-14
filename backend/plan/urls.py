"""
计划管理 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('plan-tasks', views.PlanTaskViewSet)
router.register('resource-plans', views.ResourcePlanViewSet)
router.register('resource-reserves', views.ResourceReserveViewSet)
router.register('plan-versions', views.PlanVersionViewSet)

urlpatterns = router.urls
