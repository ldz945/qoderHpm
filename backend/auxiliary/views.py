"""
辅助功能模块 - Views
包含：IssueRiskViewSet, SevenStepViewSet, VppViewSet, ScorecardViewSet,
      MeetingViewSet, ActionItemViewSet, MiscExpenseViewSet, 
      ProjectScopeViewSet, DocumentViewSet, DocumentFileViewSet
"""

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    IssueRisk, SevenStep, Vpp, Scorecard, Meeting, 
    ActionItem, MiscExpense, ProjectScope, Document, DocumentFile
)
from .serializers import (
    IssueRiskSerializer, SevenStepSerializer, VppSerializer, 
    ScorecardSerializer, MeetingSerializer, ActionItemSerializer,
    MiscExpenseSerializer, ProjectScopeSerializer, 
    DocumentSerializer, DocumentFileSerializer
)


class IssueRiskViewSet(viewsets.ModelViewSet):
    """问题/风险视图集"""
    queryset = IssueRisk.objects.all()
    serializer_class = IssueRiskSerializer
    filterset_fields = ['project', 'type', 'status', 'severity', 'capability', 'owner']
    search_fields = ['issue_no', 'title', 'description']
    ordering_fields = ['created_at', 'status', 'severity']
    ordering = ['-created_at']


class SevenStepViewSet(viewsets.ModelViewSet):
    """七步法视图集"""
    queryset = SevenStep.objects.all()
    serializer_class = SevenStepSerializer
    filterset_fields = ['project', 'status', 'current_step', 'figr_owner']
    search_fields = ['step_no', 'problem_description']
    ordering_fields = ['current_step', 'created_at']
    ordering = ['-created_at']


class VppViewSet(viewsets.ModelViewSet):
    """VPP视图集"""
    queryset = Vpp.objects.all()
    serializer_class = VppSerializer
    filterset_fields = ['project', 'status']
    search_fields = ['version_no', 'description']
    ordering_fields = ['version_no', 'created_at']
    ordering = ['-version_no']


class ScorecardViewSet(viewsets.ModelViewSet):
    """积分卡视图集"""
    queryset = Scorecard.objects.all()
    serializer_class = ScorecardSerializer
    filterset_fields = ['project', 'template_type', 'phase', 'status']
    search_fields = ['phase']
    ordering_fields = ['phase', 'total_score', 'created_at']
    ordering = ['-created_at']


class MeetingViewSet(viewsets.ModelViewSet):
    """会议视图集"""
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    filterset_fields = ['project', 'status', 'meeting_date', 'organizer']
    search_fields = ['meeting_subject', 'meeting_location']
    ordering_fields = ['meeting_date', 'created_at']
    ordering = ['-meeting_date']


class ActionItemViewSet(viewsets.ModelViewSet):
    """行动项视图集"""
    queryset = ActionItem.objects.all()
    serializer_class = ActionItemSerializer
    filterset_fields = ['project', 'meeting', 'status', 'current_owner', 'priority']
    search_fields = ['action_no', 'description']
    ordering_fields = ['planned_finish_date', 'priority', 'created_at']
    ordering = ['planned_finish_date']


class MiscExpenseViewSet(viewsets.ModelViewSet):
    """杂项费用视图集"""
    queryset = MiscExpense.objects.all()
    serializer_class = MiscExpenseSerializer
    filterset_fields = ['project', 'settlement_period', 'expense_type', 'status']
    search_fields = ['resource_name', 'department']
    ordering_fields = ['settlement_period', 'created_at']
    ordering = ['-settlement_period']


class ProjectScopeViewSet(viewsets.ModelViewSet):
    """项目范围视图集"""
    queryset = ProjectScope.objects.all()
    serializer_class = ProjectScopeSerializer
    filterset_fields = ['project', 'status']
    search_fields = ['version_no', 'scope_content']
    ordering_fields = ['version_no', 'effective_from', 'created_at']
    ordering = ['-version_no']


class DocumentViewSet(viewsets.ModelViewSet):
    """文档目录视图集"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filterset_fields = ['project', 'parent', 'enabled', 'level']
    search_fields = ['catalog_name', 'catalog_desc']
    ordering_fields = ['level', 'sort_order', 'created_at']
    ordering = ['level', 'sort_order']


class DocumentFileViewSet(viewsets.ModelViewSet):
    """文档文件视图集"""
    queryset = DocumentFile.objects.all()
    serializer_class = DocumentFileSerializer
    filterset_fields = ['catalog', 'is_latest', 'status']
    search_fields = ['file_name', 'description']
    ordering_fields = ['uploaded_at', 'version_no']
    ordering = ['-uploaded_at']
