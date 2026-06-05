from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from .forms import CustomUserCreationForm, CustomPasswordResetForm, CustomSetPasswordForm

User = get_user_model()

@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log successful registration
            from .logging_utils import log_event
            log_event(
                level='INFO',
                category='USER',
                action='User Registration',
                message=f"User '{user.username}' registered successfully with email {user.email}",
                user=user,
                request=request
            )
            
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')
        else:
            # Log failed registration attempt
            from .logging_utils import log_event
            log_event(
                level='WARNING',
                category='AUTH',
                action='Failed Registration',
                message=f"Registration failed - Errors: {form.errors}",
                request=request
            )
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Log successful login
                from .logging_utils import log_event
                log_event(
                    level='INFO',
                    category='AUTH',
                    action='Login Successful',
                    message=f"User '{username}' logged in successfully",
                    user=user,
                    request=request
                )
                
                messages.info(request, f"You are now logged in as {username}.")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            # Log failed login attempt
            from .logging_utils import log_event
            username = request.POST.get('username', 'unknown')
            log_event(
                level='WARNING',
                category='AUTH',
                action='Login Failed',
                message=f"Failed login attempt for username '{username}'",
                request=request
            )
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


@csrf_protect
@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    """Forgot password request view - sends reset email with secure token"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '')
        
        # Prevent user enumeration: always show same message
        generic_message = "If an account with this email exists, a password reset link will be sent."
        
        # Validate email is not empty
        if not email:
            messages.warning(request, generic_message)
            return render(request, 'registration/forgot_password.html')
        
        try:
            user = User.objects.get(email=email)
            # Generate secure token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset link
            current_site = get_current_site(request)
            reset_url = f"http://{current_site.domain}/reset/{uid}/{token}/"
            
            # Send email
            subject = "Password Reset Request - Student Housing Platform"
            message = render_to_string('registration/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'domain': current_site.domain,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        
        messages.success(request, generic_message)
        return redirect('forgot_password')
    
    return render(request, 'registration/forgot_password.html')


@csrf_protect
@require_http_methods(["GET", "POST"])
def reset_password_view(request, uidb64, token):
    """Reset password with secure token validation"""
    if request.user.is_authenticated:
        return redirect('home')
    
    try:
        # Decode UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        messages.error(request, "Invalid password reset link.")
        return redirect('forgot_password')
    
    # Validate token
    if not default_token_generator.check_token(user, token):
        messages.error(request, "Password reset link has expired.")
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been reset successfully. You can now log in.")
            return redirect('two_factor:login')
    else:
        form = CustomSetPasswordForm(user)
    
    return render(request, 'registration/reset_password.html', {'form': form, 'uidb64': uidb64})
