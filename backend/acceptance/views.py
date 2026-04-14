"""
项目验收模块 - Views
包含：AcceptanceViewSet
"""

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Acceptance
from .serializers import AcceptanceSerializer, AcceptanceListSerializer


class AcceptanceViewSet(viewsets.ModelViewSet):
    """验收单视图集"""
    queryset = Acceptance.objects.all()
    filterset_fields = [
        'project', 'acceptance_type', 'acceptance_status', 'acceptance_phase'
    ]
    search_fields = ['acceptance_no']
    ordering_fields = ['acceptance_date', 'created_at', 'acceptance_status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AcceptanceListSerializer
        return AcceptanceSerializer
