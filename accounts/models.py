from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        LANDLORD = 'LANDLORD', 'Landlord'
        ADMIN = 'ADMIN', 'Admin'
        
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    
    # Phone number field with validation to prevent injection attacks
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[+]?[0-9]{7,20}$',
                message='Phone number must contain 7-20 digits and may start with +',
                code='invalid_phone'
            )
        ],
        help_text='Format: +1234567890 or 1234567890'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
