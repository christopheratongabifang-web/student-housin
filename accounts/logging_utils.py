"""
Logging utilities for application-wide event tracking and audit trails
"""
import logging
from django.contrib.auth import get_user_model
from .log_models import SystemLog

User = get_user_model()
logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_event(
    level=SystemLog.LogLevel.INFO,
    category=SystemLog.LogCategory.SYSTEM,
    action='',
    message='',
    user=None,
    request=None,
    status_code=None
):
    """
    Log an event to both file and database
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        category: Log category (AUTH, USER, PROPERTY, etc.)
        action: Short action description
        message: Detailed message
        user: User instance (optional)
        request: Request object to extract IP and user agent (optional)
        status_code: HTTP status code (optional)
    """
    try:
        # Extract IP and user agent from request if available
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            # Use request user if no explicit user provided
            if not user and request.user.is_authenticated:
                user = request.user
        
        # Create log entry
        log_entry = SystemLog.objects.create(
            level=level,
            category=category,
            action=action,
            message=message,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            status_code=status_code
        )
        
        # Also log to Python logger
        log_message = f"{action} - {message}"
        if user:
            log_message = f"[{user.username}] {log_message}"
        
        if level == SystemLog.LogLevel.DEBUG:
            logger.debug(log_message)
        elif level == SystemLog.LogLevel.INFO:
            logger.info(log_message)
        elif level == SystemLog.LogLevel.WARNING:
            logger.warning(log_message)
        elif level == SystemLog.LogLevel.ERROR:
            logger.error(log_message)
        elif level == SystemLog.LogLevel.CRITICAL:
            logger.critical(log_message)
        
        return log_entry
    except Exception as e:
        # Fallback to file logging if database fails
        logger.error(f"Failed to create log entry: {str(e)}")
        logger.error(f"Original event: [{level}] {category} - {action} - {message}")


class RequestLoggingMiddleware:
    """Middleware to log all requests and responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log successful requests
        response = self.get_response(request)
        
        # Skip logging for static files and media
        if not request.path.startswith(('/static/', '/media/')):
            # Only log non-2xx responses and important paths
            if response.status_code >= 400 or any(important_path in request.path for important_path in ['/admin/', '/dashboard/', '/login', '/signup']):
                user = request.user if request.user.is_authenticated else None
                log_event(
                    level=SystemLog.LogLevel.WARNING if response.status_code >= 400 else SystemLog.LogLevel.INFO,
                    category=SystemLog.LogCategory.SECURITY,
                    action=f"{request.method} {request.path}",
                    message=f"Status: {response.status_code}",
                    user=user,
                    request=request,
                    status_code=response.status_code
                )
        
        return response
