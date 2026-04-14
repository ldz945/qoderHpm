"""
主数据管理 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('employees', views.EmployeeViewSet)
router.register('resources', views.ResourceViewSet)
router.register('price-headers', views.PriceHeaderViewSet)
router.register('price-lines', views.PriceLineViewSet)

urlpatterns = router.urls
