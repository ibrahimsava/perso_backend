from django.db import models
from django.contrib.auth.models import AbstractUser
# Note : Pour PointField, assure-toi d'avoir installé 'django.contrib.gis' 
# et configuré une base de données spatiale (PostGIS).
from django.contrib.gis.db import models as gis_models

class User(AbstractUser):
    # Constantes pour les types d'utilisateurs
    CLIENT = 'client'
    CONVOYEUR = 'convoyeur'
    ADMIN = 'admin'

    USER_TYPE_CHOICES = [
        (CLIENT, 'Client'),
        (CONVOYEUR, 'Convoyeur'),
        (ADMIN, 'Administrateur'),
    ]

    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default=CLIENT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Définit le champ de connexion sur le numéro de téléphone au lieu de l'username
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return f"{self.phone_number} ({self.user_type})"

class ConvoyeurProfile(models.Model):
    VEHICLE_CHOICES = [
        ('moto', 'Moto'),
        ('voiture', 'Voiture'),
        ('velo', 'Vélo')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='convoyeur_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    vehicle_plate = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    total_rides = models.IntegerField(default=0)
    # Utilisation de gis_models pour le champ de géolocalisation
    current_location = gis_models.PointField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    bank_info = models.JSONField(default=dict) 

    def __str__(self):
        return f"Profil Convoyeur: {self.user.phone_number}"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    total_rides = models.IntegerField(default=0)
    saved_addresses = models.JSONField(default=list)

    def __str__(self):
        return f"Profil Client: {self.user.phone_number}"
