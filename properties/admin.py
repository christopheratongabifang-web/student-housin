from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'price_per_month', 'distance_to_campus')
    list_filter = ('price_per_month', 'distance_to_campus')
    search_fields = ('title', 'description')
