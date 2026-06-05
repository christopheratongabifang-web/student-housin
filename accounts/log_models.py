from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SystemLog(models.Model):
    """System audit log for tracking all important application events"""
    
    class LogLevel(models.TextChoices):
        DEBUG = 'DEBUG', 'Debug'
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'
        CRITICAL = 'CRITICAL', 'Critical'
    
    class LogCategory(models.TextChoices):
        AUTH = 'AUTH', 'Authentication'
        USER = 'USER', 'User Management'
        PROPERTY = 'PROPERTY', 'Property Management'
        INQUIRY = 'INQUIRY', 'Inquiry'
        REVIEW = 'REVIEW', 'Review'
        SECURITY = 'SECURITY', 'Security'
        SYSTEM = 'SYSTEM', 'System'
        LANDLORD = 'LANDLORD', 'Landlord Management'
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(
        max_length=10, 
        choices=LogLevel.choices, 
        default=LogLevel.INFO,
        db_index=True
    )
    category = models.CharField(
        max_length=20, 
        choices=LogCategory.choices,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True
    )
    action = models.CharField(max_length=255, db_index=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'level']),
            models.Index(fields=['-timestamp', 'category']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"[{self.get_level_display()}] {self.get_category_display()} - {self.action} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
