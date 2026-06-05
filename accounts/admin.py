from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User
from .log_models import SystemLog

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
        ('Contact', {'fields': ('phone_number',)}),
    )

admin.site.register(User, CustomUserAdmin)


class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp_display', 'level_badge', 'category', 'action', 'user_display', 'ip_address')
    list_filter = ('level', 'category', 'timestamp')
    search_fields = ('action', 'message', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'level', 'category', 'user', 'action', 'message', 'ip_address', 'user_agent', 'status_code')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def timestamp_display(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Timestamp'
    
    def level_badge(self, obj):
        colors = {
            'DEBUG': '#6b7280',
            'INFO': '#3b82f6',
            'WARNING': '#f59e0b',
            'ERROR': '#ef4444',
            'CRITICAL': '#991b1b',
        }
        color = colors.get(obj.level, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_level_display()
        )
    level_badge.short_description = 'Level'
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.get_role_display()})"
        return '-'
    user_display.short_description = 'User'

admin.site.register(SystemLog, SystemLogAdmin)
