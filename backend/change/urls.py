"""
变更管理 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('change-orders', views.ChangeOrderViewSet)

urlpatterns = router.urls
