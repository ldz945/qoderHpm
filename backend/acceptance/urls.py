"""
项目验收模块 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('acceptances', views.AcceptanceViewSet)

urlpatterns = router.urls
