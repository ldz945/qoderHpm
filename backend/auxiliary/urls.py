"""
辅助功能模块 - URLs
"""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('issue-risks', views.IssueRiskViewSet)
router.register('seven-steps', views.SevenStepViewSet)
router.register('vpps', views.VppViewSet)
router.register('scorecards', views.ScorecardViewSet)
router.register('meetings', views.MeetingViewSet)
router.register('action-items', views.ActionItemViewSet)
router.register('misc-expenses', views.MiscExpenseViewSet)
router.register('project-scopes', views.ProjectScopeViewSet)
router.register('documents', views.DocumentViewSet)
router.register('document-files', views.DocumentFileViewSet)

urlpatterns = router.urls
