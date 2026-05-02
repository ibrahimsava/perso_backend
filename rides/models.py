# rides/models.py
from django.db import models
from django.contrib.gis.db import models as gis_models
from accounts.models import User, ClientProfile, ConvoyeurProfile


class Ride(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente de offres'),
        ('bidding', 'Enchères en cours'),
        ('accepted', 'Offre acceptée'),
        ('assigned', 'Convoyeur assigné'),
        ('in_progress', 'Course en cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('disputed', 'Litige')
    ]
    
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='rides')
    pickup_location = gis_models.PointField()
    pickup_address = models.CharField(max_length=255)
    dropoff_location = gis_models.PointField()
    dropoff_address = models.CharField(max_length=255)
    distance_km = models.FloatField()
    estimated_duration_minutes = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    selected_bid = models.ForeignKey('Bid', null=True, on_delete=models.SET_NULL, related_name='selected_ride')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'En attente'), ('paid', 'Payé'), ('failed', 'Échoué')], default='pending')


class Bid(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bids')
    convoyeur = models.ForeignKey(ConvoyeurProfile, on_delete=models.CASCADE, related_name='bids')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_arrival_minutes = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('pending', 'En attente'), ('accepted', 'Acceptée'), ('rejected', 'Rejetée'), ('expired', 'Expirée')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['proposed_price']