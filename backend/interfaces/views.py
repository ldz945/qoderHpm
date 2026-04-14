"""
接口模块 - Views
包含：InterfaceLogViewSet, TomsWebhookView
"""

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import InterfaceLog
from .serializers import InterfaceLogSerializer, InterfaceLogListSerializer


class InterfaceLogViewSet(viewsets.ModelViewSet):
    """接口日志视图集"""
    queryset = InterfaceLog.objects.all()
    filterset_fields = ['service_code', 'direction', 'request_status']
    search_fields = ['service_name', 'service_code', 'error_message']
    ordering_fields = ['request_time', 'created_at']
    ordering = ['-request_time']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InterfaceLogListSerializer
        return InterfaceLogSerializer


class TomsWebhookView(APIView):
    """TOMS系统数据推送接口入口"""
    
    def post(self, request):
        service_code = request.data.get('service_code', '')
        
        # 记录接口日志
        InterfaceLog.objects.create(
            service_code=service_code,
            service_name=request.data.get('service_name', ''),
            direction='TOMS_TO_HPM',
            request_data=str(request.data),
            request_status='PENDING'
        )
        
        # TODO: 根据service_code分发到不同的处理逻辑
        # 例如：
        # - PROJECT_SYNC: 项目同步
        # - TASK_SYNC: 任务同步
        # - MEMBER_SYNC: 成员同步
        # - ACTUAL_HOUR_SYNC: 实际工时同步
        
        return Response({
            'status': 'received',
            'service_code': service_code,
            'message': '数据已接收，正在处理中'
        }, status=status.HTTP_202_ACCEPTED)
