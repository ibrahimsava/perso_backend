# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User Model with role-based authentication"""
    
    ROLE_CHOICES = [
        ('client', _('Client')),
        ('convoyeur', _('Convoyeur')),
        ('admin', _('Administrator')),
    ]
###################################################################################
    # Override ManyToMany fields with custom related_names
    # cette modification est nécessaire pour éviter les conflits avec les champs de groupe et de permission de Django
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    ###########################################################################
    
    phone_number = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    is_phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    is_active_profile = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



####################################################################################

# le profil du client debute ici 


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    profile_photo = models.ImageField(upload_to='client_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    home_location = gis_models.PointField(blank=True, null=True)
    home_address = models.CharField(max_length=255, blank=True)
    work_location = gis_models.PointField(blank=True, null=True)
    work_address = models.CharField(max_length=255, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Client: {self.user.username}"

##############################################################################
### le profil convoyeur et ses attributs 


class ConvoyeurProfile(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'), 
        ('verified', 'Verified'), 
        ('rejected', 'Rejected'), 
        ('suspended', 'Suspended')]
    
    VEHICLE_TYPE = [
                    ('voiture', 'Voiture'), 
                   ('motorcycle', 'Motorcycle'),  
                   ('velo', 'Velo')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='convoyeur_profile')
    profile_photo = models.ImageField(upload_to='convoyeur_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE, default='motorcycle')
    vehicle_plate = models.CharField(max_length=20, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    numero_id = models.CharField(max_length=50, blank=True)
    national_id_photo = models.ImageField(upload_to='convoyeur_docs/', blank=True, null=True)
    driver_license = models.CharField(max_length=50, blank=True)
    driver_license_photo = models.ImageField(upload_to='convoyeur_docs/', blank=True, null=True)
    vehicle_registration = models.CharField(max_length=50, blank=True)
    vehicle_registration_photo = models.ImageField(upload_to='convoyeur_docs/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_at = models.DateTimeField(blank=True, null=True)
    current_location = gis_models.PointField(blank=True, null=True)
    location_updated_at = models.DateTimeField(blank=True, null=True)
    is_available = models.BooleanField(default=False)
    total_rides = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    joined_date = models.DateField(auto_now_add=True)
   
    def __str__(self):
        return f"Convoyeurs: {self.user.username}"