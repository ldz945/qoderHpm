"""
接口模块 - URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('interface-logs', views.InterfaceLogViewSet)

urlpatterns = [
    path('toms-webhook/', views.TomsWebhookView.as_view(), name='toms-webhook'),
] + router.urls
