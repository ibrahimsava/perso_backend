# payments/models.py
from django.db import models
from accounts.models import User, ClientProfile, ConvoyeurProfile
from rides.models import Ride


class Transaction(models.Model):
    PAYMENT_METHOD = [
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Money'),
        ('card', 'Credit Card'),
        ('wallet', 'Wallet')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé')
    ]
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='transactions')
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Commission(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='commission')
    convoyeur = models.ForeignKey(ConvoyeurProfile, on_delete=models.CASCADE, related_name='commissions')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)  # 15%
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    convoyeur_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'En attente'), ('paid', 'Payé'), ('failed', 'Échoué')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)