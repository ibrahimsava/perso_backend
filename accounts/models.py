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


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    profile_photo = models.ImageField(upload_to='client_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    home_location = gis_models.PointField(blank=True, null=True)
    home_address = models.CharField(max_length=255, blank=True)
    work_location = gis_models.PointField(blank=True, null=True)
    work_address = models.CharField(max_length=255, blank=True)
    preferred_payment_method = models.CharField(
        max_length=20,
        choices=[('orange_money', 'Orange Money'), ('mtn_money', 'MTN Money'), ('card', 'Card')],
        default='orange_money'
    )
    total_rides = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ConvoyeurProfile(models.Model):
    VERIFICATION_STATUS = [('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected'), ('suspended', 'Suspended')]
    VEHICLE_TYPE = [('motorcycle', 'Motorcycle'), ('car', 'Car'), ('truck', 'Truck'), ('van', 'Van')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='convoyeur_profile')
    profile_photo = models.ImageField(upload_to='convoyeur_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE, default='motorcycle')
    vehicle_plate = models.CharField(max_length=20, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_color = models.CharField(max_length=50, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    national_id_photo = models.ImageField(upload_to='convoyeur_docs/', blank=True, null=True)
    driver_license = models.CharField(max_length=50, blank=True)
    driver_license_photo = models.ImageField(upload_to='convoyeur_docs/', blank=True, null=True)
    vehicle_registration = models.CharField(max_length=50, blank=True)
    vehicle_registration_photo = models.ImageField(upload_to='convoyeur_docs/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    current_location = gis_models.PointField(blank=True, null=True)
    location_updated_at = models.DateTimeField(blank=True, null=True)
    is_available = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    account_holder_name = models.CharField(max_length=100, blank=True)
    mobile_money_number = models.CharField(max_length=20, blank=True)
    total_rides = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cancellation_count = models.PositiveIntegerField(default=0)
    years_of_experience = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    joined_date = models.DateField(auto_now_add=True)