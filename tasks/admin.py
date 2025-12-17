from django.contrib import admin
from .models import Task, TaskCategory, TaskAttachment

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'icon', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'user__username']
    ordering = ['name']

class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ['file_size', 'file_type', 'uploaded_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'date', 'category_name', 'created_at']
    list_filter = ['status', 'priority', 'date', 'created_at', 'custom_category']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TaskAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Categorization', {
            'fields': ('custom_category', 'default_category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Schedule', {
            'fields': ('date', 'time', 'reminder_datetime', 'reminder_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'task', 'file_size', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['file_name', 'task__title']
    readonly_fields = ['file_size', 'file_type', 'uploaded_at']