from rest_framework import serializers
from .models import Task, TaskCategory, TaskAttachment

class TaskCategorySerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'color', 'icon', 'task_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def validate_color(self, value):
        # Validate hex color format
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color must be in hex format (#RRGGBB)")
        return value

class TaskAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'file_url', 'file_name', 'file_size', 'file_type', 'uploaded_at']
        read_only_fields = ['id', 'file_size', 'file_type', 'uploaded_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class TaskSerializer(serializers.ModelSerializer):
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField()
    custom_category_name = serializers.CharField(
        source='custom_category.name', 
        read_only=True
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'custom_category', 'custom_category_name',
            'default_category', 'category_name', 'status', 'priority',
            'date', 'time', 'reminder_datetime', 'reminder_sent',
            'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reminder_sent']
    
    def validate_title(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty")
        return value
    
    def validate(self, attrs):
        # If custom_category is provided, ensure it belongs to the user
        custom_category = attrs.get('custom_category')
        if custom_category:
            request = self.context.get('request')
            if request and custom_category.user != request.user:
                raise serializers.ValidationError({
                    'custom_category': 'You can only use your own categories'
                })
        return attrs

class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks with file uploads"""
    attachment_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'custom_category', 'default_category',
            'status', 'priority', 'date', 'time', 'reminder_datetime',
            'attachment_files'
        ]
    
    def create(self, validated_data):
        attachment_files = validated_data.pop('attachment_files', [])
        task = Task.objects.create(**validated_data)
        
        # Create attachments
        for file in attachment_files:
            TaskAttachment.objects.create(
                task=task,
                file=file,
                file_name=file.name,
                file_size=file.size,
                file_type=file.content_type
            )
        
        return task