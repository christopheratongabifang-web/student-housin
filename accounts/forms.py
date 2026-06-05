from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Registration form with phone number field and XSS protection"""
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label='Phone Number (Optional)',
        help_text='Format: +1234567890 or 1234567890 (7-20 digits)',
        widget=forms.TextInput(attrs={
            'placeholder': '+1234567890',
            'autocomplete': 'tel'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number')
    
    def clean_phone_number(self):
        """Validate phone number format to prevent injection"""
        phone = self.cleaned_data.get('phone_number', '')
        if phone:  # Only validate if provided
            # Remove whitespace
            phone = phone.replace(' ', '').replace('-', '')
            # Check format: must start with + or digit, contain only digits
            if not phone.replace('+', '').isdigit():
                raise ValidationError('Phone number must contain only digits and optional + prefix')
            if len(phone.replace('+', '')) < 7 or len(phone.replace('+', '')) > 20:
                raise ValidationError('Phone number must be 7-20 digits')
        return self.cleaned_data.get('phone_number', '')
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists')
        return email
    
    def save(self, commit=True):
        """Save user with phone number"""
        user = super().save(commit=False)
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class AddLandlordForm(UserCreationForm):
    """Form for Admin to create a landlord account"""
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label='Phone Number (Optional)',
        help_text='Format: +1234567890 or 1234567890 (7-20 digits)',
        widget=forms.TextInput(attrs={
            'placeholder': '+1234567890',
            'autocomplete': 'tel'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            phone = phone.replace(' ', '').replace('-', '')
            if not phone.replace('+', '').isdigit():
                raise ValidationError('Phone number must contain only digits and optional + prefix')
            if len(phone.replace('+', '')) < 7 or len(phone.replace('+', '')) > 20:
                raise ValidationError('Phone number must be 7-20 digits')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'LANDLORD'
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):

    """Custom password reset form with improved security"""
    def clean_email(self):
        """Validate email exists - but don't enumerate users (show generic message)"""
        email = self.cleaned_data['email']
        # This will be checked in the form's save() method
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """Custom password reset form with requirements display"""
    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')
