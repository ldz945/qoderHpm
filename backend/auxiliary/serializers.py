"""
辅助功能模块 - Serializers
包含：IssueRisk, SevenStep, Vpp, Scorecard, Meeting, ActionItem, 
      MiscExpense, ProjectScope, Document, DocumentFile
"""

from rest_framework import serializers
from .models import (
    IssueRisk, SevenStep, Vpp, Scorecard, Meeting, 
    ActionItem, MiscExpense, ProjectScope, Document, DocumentFile
)


class IssueRiskSerializer(serializers.ModelSerializer):
    """问题/风险序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = IssueRisk
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SevenStepSerializer(serializers.ModelSerializer):
    """七步法序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = SevenStep
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class VppSerializer(serializers.ModelSerializer):
    """VPP序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = Vpp
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ScorecardSerializer(serializers.ModelSerializer):
    """积分卡序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = Scorecard
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MeetingSerializer(serializers.ModelSerializer):
    """会议序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ActionItemSerializer(serializers.ModelSerializer):
    """行动项序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    meeting_subject = serializers.CharField(source='meeting.meeting_subject', read_only=True)
    
    class Meta:
        model = ActionItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MiscExpenseSerializer(serializers.ModelSerializer):
    """杂项费用序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = MiscExpense
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectScopeSerializer(serializers.ModelSerializer):
    """项目范围序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    class Meta:
        model = ProjectScope
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    """文档目录序列化器"""
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_children(self, obj):
        children = obj.children.filter(enabled='Y')
        return DocumentSerializer(children, many=True).data


class DocumentFileSerializer(serializers.ModelSerializer):
    """文档文件序列化器"""
    catalog_name = serializers.CharField(source='catalog.catalog_name', read_only=True)
    
    class Meta:
        model = DocumentFile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
