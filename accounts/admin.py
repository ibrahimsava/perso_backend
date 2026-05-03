from django.contrib import admin
from .models import User, ClientProfile, ConvoyeurProfile

# Register your models here.

# Personnalisation des titres de l'interface ##########################################
admin.site.site_header = "Ibrahim Transport Administration"
admin.site.index_title = "Bienvenue sur la gestion de Ibrahim Transport"
#############################################################3########333


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_active_profile', 'created_at')
    list_filter = ('role', 'is_active_profile', 'created_at')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-created_at',)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name', 'address')
    ordering = ('-created_at',)


@admin.register(ConvoyeurProfile)
class ConvoyeurProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_display = ('user',  'profile_photo', 'national_id_photo', 'driver_license_photo', 'joined_date')
    search_fields = ('first_name', 'address')
    ordering = ('-joined_date',)
    


