from django.contrib import admin

# Register your models here.

from django.contrib.gis import admin
from .models import ConvoyeurProfile

@admin.register(ConvoyeurProfile)
class ConvoyeurProfileAdmin(admin.GISModelAdmin):
    list_display = ('user', 'vehicle_type', 'is_available')

