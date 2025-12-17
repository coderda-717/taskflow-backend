from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date, datetime, timedelta
from .models import Task, TaskCategory, TaskAttachment
from .serializers import (
    TaskSerializer, TaskCreateSerializer, 
    TaskCategorySerializer, TaskAttachmentSerializer
)

class TaskCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing custom task categories"""
    serializer_class = TaskCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        return TaskCategory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks with all features"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'default_category', 'custom_category', 'date']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'date', 'time', 'priority']
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).prefetch_related(
            'attachments', 'custom_category'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks for today"""
        today_tasks = self.get_queryset().filter(date=date.today())
        serializer = self.get_serializer(today_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)"""
        end_date = date.today() + timedelta(days=7)
        upcoming_tasks = self.get_queryset().filter(
            date__gte=date.today(),
            date__lte=end_date,
            status='pending'
        )
        serializer = self.get_serializer(upcoming_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        overdue_tasks = self.get_queryset().filter(
            date__lt=date.today(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        """Get tasks grouped by priority"""
        priority = request.query_params.get('priority', 'high')
        tasks = self.get_queryset().filter(priority=priority)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        """Toggle task completion status"""
        task = self.get_object()
        if task.status == 'completed':
            task.status = 'pending'
        else:
            task.status = 'completed'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request, pk=None):
        """Upload file attachment to a task"""
        task = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'File size must be less than 10MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachment = TaskAttachment.objects.create(
            task=task,
            file=file,
            file_name=file.name,
            file_size=file.size,
            file_type=file.content_type
        )
        
        serializer = TaskAttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def delete_attachment(self, request, pk=None):
        """Delete a specific attachment"""
        attachment_id = request.query_params.get('attachment_id')
        
        if not attachment_id:
            return Response(
                {'error': 'attachment_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attachment = TaskAttachment.objects.get(
                id=attachment_id, 
                task__user=request.user
            )
            attachment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TaskAttachment.DoesNotExist:
            return Response(
                {'error': 'Attachment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'completed': queryset.filter(status='completed').count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'overdue': queryset.filter(
                date__lt=date.today(), 
                status__in=['pending', 'in_progress']
            ).count(),
            'today': queryset.filter(date=date.today()).count(),
            'by_priority': {
                'urgent': queryset.filter(priority='urgent').count(),
                'high': queryset.filter(priority='high').count(),
                'medium': queryset.filter(priority='medium').count(),
                'low': queryset.filter(priority='low').count(),
            }
        }
        
        return Response(stats)