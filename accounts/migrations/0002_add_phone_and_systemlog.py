# Generated migration for adding phone_number field and SystemLog model

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add phone_number field to User
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(
                blank=True,
                help_text='Format: +1234567890 or 1234567890',
                max_length=20,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        code='invalid_phone',
                        message='Phone number must contain 7-20 digits and may start with +',
                        regex='^[+]?[0-9]{7,20}$'
                    )
                ]
            ),
        ),
        # Create SystemLog model
        migrations.CreateModel(
            name='SystemLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('level', models.CharField(
                    choices=[
                        ('DEBUG', 'Debug'),
                        ('INFO', 'Info'),
                        ('WARNING', 'Warning'),
                        ('ERROR', 'Error'),
                        ('CRITICAL', 'Critical')
                    ],
                    db_index=True,
                    default='INFO',
                    max_length=10
                )),
                ('category', models.CharField(
                    choices=[
                        ('AUTH', 'Authentication'),
                        ('USER', 'User Management'),
                        ('PROPERTY', 'Property Management'),
                        ('INQUIRY', 'Inquiry'),
                        ('REVIEW', 'Review'),
                        ('SECURITY', 'Security'),
                        ('SYSTEM', 'System'),
                        ('LANDLORD', 'Landlord Management')
                    ],
                    db_index=True,
                    max_length=20
                )),
                ('action', models.CharField(db_index=True, max_length=255)),
                ('message', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='accounts.user',
                    db_index=True
                )),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='systemlog',
            index=models.Index(fields=['-timestamp', 'level'], name='systemlog_timestamp_level_idx'),
        ),
        migrations.AddIndex(
            model_name='systemlog',
            index=models.Index(fields=['-timestamp', 'category'], name='systemlog_timestamp_category_idx'),
        ),
        migrations.AddIndex(
            model_name='systemlog',
            index=models.Index(fields=['user', '-timestamp'], name='systemlog_user_timestamp_idx'),
        ),
    ]
