"""
变更管理 - Views
包含：ChangeOrderViewSet
"""

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import ChangeOrder
from .serializers import ChangeOrderSerializer, ChangeOrderListSerializer


class ChangeOrderViewSet(viewsets.ModelViewSet):
    """变更单视图集"""
    queryset = ChangeOrder.objects.all()
    filterset_fields = ['project', 'change_type', 'status', 'created_by']
    search_fields = ['change_no', 'change_content', 'change_reason']
    ordering_fields = ['created_at', 'change_no', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChangeOrderListSerializer
        return ChangeOrderSerializer
