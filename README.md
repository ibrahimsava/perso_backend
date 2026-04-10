# perso_backend, user=toto, pwd=toto

# Structure des apps Django
transport_project/
├── accounts/
│   ├── User (Custom User Model)
│   ├── ClientProfile
│   └── ConvoyeurProfile
├── rides/
│   ├── Ride (course)
│   ├── Bid (offre de prix)
│   └── RideStatus
├── geolocation/
│   ├── Tracking
│   └── Route
├── payments/
│   ├── Transaction
│   ├── MobileMoneyGateway
│   └── Commission
└── notifications/
    ├── PushNotification
    └── RealTimeEvents




# futter structure

lib/
├── core/
│   ├── models/          # Shared models
│   ├── services/        # API service, WebSocket
│   └── utils/
├── modules/
│   ├── auth/            # Login/Register
│   ├── client/          # Client flows
│   │   ├── create_ride/
│   │   ├── view_bids/
│   │   └── track_ride/
│   └── driver/          # Convoyeur flows
│       ├── available_rides/
│       ├── make_bid/
│       └── navigate/




📋 CAHIER DE CHARGES TECHNIQUE
Application de Transport/Livraison Locale (Style Uber/Yango)
Version 1.0 | Date: [Date actuelle]
1. PRÉSENTATION GÉNÉRALE
1.1 Objectif du projet

Développer une plateforme de mise en relation entre convoyeurs (livreurs/chauffeurs) et clients pour des courses et livraisons locales, avec système d'enchères de prix et paiement mobile.
1.2 Périmètre fonctionnel

    Géolocalisation en temps réel

    Création et gestion de courses

    Système d'enchères/offres de prix

    Paiement via Mobile Money (Orange Money, MTN Money)

    Commission automatique sur chaque course

    Suivi en temps réel


# 1.3 Technologies imposées


Couche	Technologie	Version
Backend	Django	4.2+
API	Django REST Framework	3.14+
Temps réel	Django Channels + Redis	4.0+
Base de données	PostgreSQL + PostGIS	14+
Frontend Mobile	Flutter	3.16+
Cache	Redis	7.0+



2. ACTEURS ET FONCTIONNALITÉS
2.1 Acteurs principaux
Client (Demandeur de course)
yaml

Rôles:
  - Créer une demande de course/livraison
  - Visualiser les offres des convoyeurs
  - Accepter une offre
  - Payer via Mobile Money
  - Suivre la course en temps réel
  - Noter le convoyeur

Convoyeur (Livreur/Chauffeur)
yaml

Rôles:
  - S'enregistrer avec vérification
  - Voir les courses disponibles (rayon 5km)
  - Proposer un prix pour une course
  - Accepter une course acceptée
  - Mettre à jour sa position GPS
  - Marquer début/fin de course
  - Recevoir les paiements (après commission)

Administrateur
yaml

Rôles:
  - Valider les convoyeurs
  - Configurer la commission
  - Gérer les litiges
  - Voir les statistiques
  - Modérer les utilisateurs

2.2 Matrice fonctionnelle détaillée
Fonctionnalité	Client	Convoyeur	Admin
Inscription/Connexion	✓	✓	✓
Vérification SMS OTP	✓	✓	✗
Création course	✓	✗	✗
Géocodage adresse	✓	✓	✗
Voir courses proches	✗	✓	✗
Proposer prix (bid)	✗	✓	✗
Voir les offres	✓	✗	✗
Accepter offre	✓	✗	✗
Paiement Mobile Money	✓	✗	✗
Tracking GPS	✓	✓	✗
Notifications push	✓	✓	✗
Historique courses	✓	✓	✓
Évaluation	✓	✓	✗
Dashboard stats	✗	✓	✓
Gestion commission	✗	✗	✓
3. SPÉCIFICATIONS TECHNIQUES DÉTAILLÉES
3.1 Architecture backend (Django)
Structure des applications
text

transport_project/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── asgi.py (pour Channels)
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services/
│   ├── rides/
│   │   ├── models.py
│   │   ├── services/
│   │   │   ├── matching.py
│   │   │   ├── pricing.py
│   │   │   └── tracking.py
│   │   └── consumers.py
│   ├── payments/
│   │   ├── models.py
│   │   ├── mtn_money.py
│   │   ├── orange_money.py
│   │   └── commission.py
│   └── notifications/
│       ├── push.py
│       └── sms.py

Modèles de données (Django ORM)
python

# accounts/models.py
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=[
        ('client', 'Client'),
        ('convoyeur', 'Convoyeur'),
        ('admin', 'Administrateur')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

class ConvoyeurProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('moto', 'Moto'),
        ('voiture', 'Voiture'),
        ('velo', 'Vélo')
    ])
    vehicle_plate = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    total_rides = models.IntegerField(default=0)
    current_location = models.PointField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    bank_info = models.JSONField()  # Pour virements

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_rides = models.IntegerField(default=0)
    saved_addresses = models.JSONField(default=list)

python

# rides/models.py
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
    
    # Client info
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    
    # Locations
    pickup_location = models.PointField()
    pickup_address = models.CharField(max_length=255)
    dropoff_location = models.PointField()
    dropoff_address = models.CharField(max_length=255)
    
    # Ride details
    distance_km = models.FloatField()
    estimated_duration_minutes = models.IntegerField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Selected bid
    selected_bid = models.ForeignKey('Bid', null=True, on_delete=models.SET_NULL)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # 10 minutes pour enchères
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    
    # Payment
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('failed', 'Échoué')
    ], default='pending')

class Bid(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bids')
    convoyeur = models.ForeignKey(ConvoyeurProfile, on_delete=models.CASCADE)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_arrival_minutes = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
        ('expired', 'Expirée')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['proposed_price']  # Plus petit prix d'abord

3.2 API Endpoints (Django REST Framework)
yaml

# AUTHENTIFICATION
POST   /api/auth/register/          # Inscription
POST   /api/auth/verify-otp/        # Vérification SMS
POST   /api/auth/login/             # Connexion (JWT)
POST   /api/auth/logout/            # Déconnexion
POST   /api/auth/refresh-token/     # Rafraîchir token

# CLIENTS
POST   /api/client/rides/           # Créer une course
GET    /api/client/rides/{id}/      # Détail course
GET    /api/client/rides/{id}/bids/ # Voir les offres
POST   /api/client/rides/{id}/accept-bid/ # Accepter offre
GET    /api/client/history/         # Historique courses

# CONVOYEURS
GET    /api/convoyeur/rides/available/ # Courses disponibles (rayon 5km)
POST   /api/convoyeur/rides/{id}/bid/  # Proposer prix
GET    /api/convoyeur/rides/active/    # Course en cours
POST   /api/convoyeur/location/update/ # Mettre à jour GPS
POST   /api/convoyeur/rides/{id}/start/ # Démarrer course
POST   /api/convoyeur/rides/{id}/complete/ # Terminer course

# PAIEMENTS
POST   /api/payments/mobile-money/initiate/ # Initier paiement
POST   /api/payments/mobile-money/confirm/  # Confirmer paiement
GET    /api/payments/history/               # Historique transactions

# NOTIFICATIONS
POST   /api/notifications/register-device/  # Enregistrer token FCM
GET    /api/notifications/unread/           # Notifications non lues

# WEBSOCKETS (Django Channels)
WS     /ws/rides/{ride_id}/tracking/        # Tracking temps réel
WS     /ws/convoyeur/{convoyeur_id}/location/ # Position convoyeur
WS     /ws/notifications/                   # Notifications push

3.3 Architecture frontend (Flutter)
Structure du projet
text

lib/
├── main.dart
├── app/
│   ├── app.dart
│   ├── routes.dart
│   └── theme.dart
├── core/
│   ├── constants/
│   │   ├── api_constants.dart
│   │   └── app_constants.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── websocket_service.dart
│   │   ├── location_service.dart
│   │   ├── notification_service.dart
│   │   └── storage_service.dart
│   ├── models/
│   │   ├── user_model.dart
│   │   ├── ride_model.dart
│   │   └── bid_model.dart
│   └── utils/
│       ├── validators.dart
│       ├── formatters.dart
│       └── permissions.dart
├── modules/
│   ├── auth/
│   │   ├── login_screen.dart
│   │   ├── register_screen.dart
│   │   └── otp_verification_screen.dart
│   ├── client/
│   │   ├── home_screen.dart
│   │   ├── create_ride_screen.dart
│   │   ├── view_bids_screen.dart
│   │   ├── track_ride_screen.dart
│   │   └── history_screen.dart
│   ├── convoyeur/
│   │   ├── home_screen.dart
│   │   ├── available_rides_screen.dart
│   │   ├── make_bid_screen.dart
│   │   ├── active_ride_screen.dart
│   │   └── earnings_screen.dart
│   └── shared/
│       ├── widgets/
│       │   ├── ride_card.dart
│       │   ├── bid_card.dart
│       │   └── map_view.dart
│       └── dialogs/
│           ├── bid_dialog.dart
│           └── payment_dialog.dart
├── providers/  # State management
│   ├── auth_provider.dart
│   ├── ride_provider.dart
│   └── location_provider.dart
└── generated/  # Code généré (json_serializable, etc.)

Packages Flutter requis
yaml

dependencies:
  flutter:
    sdk: flutter
  
  # UI
  google_maps_flutter: ^2.5.0
  geolocator: ^10.0.0
  geocoding: ^2.1.1
  
  # State & Data
  provider: ^6.1.1
  shared_preferences: ^2.2.0
  hive: ^2.2.0
  hive_flutter: ^1.1.0
  
  # Networking
  dio: ^5.3.0
  web_socket_channel: ^2.4.0
  socket_io_client: ^2.0.3
  
5. EXIGENCES NON FONCTIONNELLES
5.1 Performance
Métrique	Seuil acceptable
Temps de réponse API	< 200ms (p95)
Temps de chargement course	< 1.5s
Mise à jour GPS	Toutes les 3 secondes
Latence WebSocket	< 100ms
Paiement Mobile Money	< 5 secondes
5.2 Sécurité
yaml

Authentification:
  - JWT avec refresh token
  - Expiration token: 1 heure
  - Refresh token: 7 jours
  
Validation:
  - Tous endpoints requirent JWT (sauf login/register)
  - Rate limiting: 100 requêtes/minute par IP
  - OTP SMS obligatoire pour inscription
  
Protection données:
  - HTTPS obligatoire
  - Hash des mots de passe (bcrypt)
  - Chiffrement des données sensibles (AES-256)
  
Paiement:
  - Double validation (autorisation + capture)
  - Logs de toutes transactions
  - Anti-fraud scoring

5.3 Scalabilité
yaml

Horizontal scaling:
  - Django: Multiple instances avec Gunicorn
  - Database: Read replicas pour requêtes GET
  - Redis: Cluster pour WebSocket/Cache
  - Static files: CDN (CloudFront)

Capacité initiale:
  - 1000 courses/jour
  - 500 convoyeurs simultanés
  - 2000 requêtes/sec API

Strategie scaling:
  - Auto-scaling sur CPU > 70%
  - Cache Redis pour géolocalisation
  - Pagination sur tous les endpoints

5.4 Disponibilité
yaml

Objectifs:
  - Disponibilité: 99.5% (hors maintenance)
  - RTO (Recovery Time Objective): 2 heures
  - RPO (Recovery Point Objective): 15 minutes

Redondance:
  - Base de données: Primary + Standby
  - Redis: Sentinel pour haute disponibilité
  - Load balancer: HAProxy avec failover

6. INTÉGRATIONS EXTERNES
6.1 Paiement Mobile Money
python

# MTN Money API Integration
class MTNMoneyGateway:
    BASE_URL = "https://sandbox.mtn.com/v1"
    
    def initiate_payment(self, phone: str, amount: float, reference: str):
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'X-Reference-Id': reference,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "amount": str(amount),
            "currency": "XAF",
            "externalId": reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": f"Course {reference}",
            "payeeNote": "Paiement course transport"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/collection/v1_0/requesttopay",
            headers=headers,
            json=payload
        )
        
        return response.status_code == 202
    
    def check_payment_status(self, reference: str):
        # Vérifier statut paiement
        pass

6.2 Notifications Push (Firebase)
dart

// Flutter - FCM Configuration
class NotificationService {
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  
  Future<void> init() async {
    // Request permissions
    await _fcm.requestPermission();
    
    // Get token
    String? token = await _fcm.getToken();
    await saveTokenToServer(token!);
    
    // Foreground notifications
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      showLocalNotification(message);
    });
    
    // Background notification tap
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      handleNavigation(message.data);
    });
  }
  
  void showLocalNotification(RemoteMessage message) {
    // Afficher notification locale
    flutterLocalNotificationsPlugin.show(
      message.hashCode,
      message.notification?.title,
      message.notification?.body,
      NotificationDetails(...)
    );
  }
}

6.3 Cartographie (Google Maps/OpenStreetMap)
dart

// Flutter - Map Service
class MapService {
  GoogleMapController? _controller;
  
  Future<void> showRoute(LatLng pickup, LatLng dropoff) async {
    // Get directions from API
    final directions = await getDirections(pickup, dropoff);
    
    // Draw polyline
    _controller?.addPolyline(
      Polyline(
        polylineId: PolylineId('route'),
        points: directions.points,
        color: Colors.blue,
        width: 5,
      )
    );
    
    // Fit camera to bounds
    final bounds = LatLngBounds(
      southwest: directions.southwest,
      northeast: directions.northeast,
    );
    await _controller?.animateCamera(
      CameraUpdate.newLatLngBounds(bounds, 50)
    );
  }
  
  Future<double> calculateDistance(LatLng point1, LatLng point2) async {
    // Haversine formula or API call
    return Geolocator.distanceBetween(
      point1.latitude, point1.longitude,
      point2.latitude, point2.longitude
    ) / 1000; // Convert to km
  }
}

7. BASE DE DONNÉES
7.1 Schéma PostgreSQL + PostGIS
sql

-- Enable PostGIS
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Tables principales
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rides (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(id),
    pickup_location GEOGRAPHY(POINT, 4326) NOT NULL,
    dropoff_location GEOGRAPHY(POINT, 4326) NOT NULL,
    pickup_address TEXT NOT NULL,
    dropoff_address TEXT NOT NULL,
    distance_km FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    final_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_rides_status_status (status),
    INDEX idx_rides_location USING GIST (pickup_location)
);

CREATE TABLE bids (
    id SERIAL PRIMARY KEY,
    ride_id INTEGER REFERENCES rides(id),
    convoyeur_id INTEGER REFERENCES users(id),
    proposed_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index spatial pour courses proches
CREATE INDEX idx_rides_nearby ON rides 
USING GIST (pickup_location) 
WHERE status = 'pending';

-- Vues matérialisées pour statistiques
CREATE MATERIALIZED VIEW daily_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_rides,
    AVG(final_price) as avg_price,
    SUM(final_price) as revenue
FROM rides
WHERE status = 'completed'
GROUP BY DATE(created_at);

7.2 Index et optimisation
sql

-- Index composites pour requêtes fréquentes
CREATE INDEX idx_rides_client_status ON rides(client_id, status);
CREATE INDEX idx_bids_ride_status ON bids(ride_id, status);
CREATE INDEX idx_convoyeur_location ON convoyeur_profiles USING GIST(current_location);

-- Pour recherche courses proches (rayon 5km)
CREATE OR REPLACE FUNCTION get_nearby_rides(lat FLOAT, lng FLOAT, radius_km FLOAT)
RETURNS TABLE(
    ride_id INTEGER,
    distance FLOAT,
    pickup_address TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        ST_Distance(r.pickup_location, ST_SetSRID(ST_MakePoint(lng, lat), 4326)) as distance,
        r.pickup_address
    FROM rides r
    WHERE r.status = 'pending'
        AND ST_DWithin(
            r.pickup_location,
            ST_SetSRID(ST_MakePoint(lng, lat), 4326),
            radius_km * 1000
        )
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

8. GESTION DE PROJET
8.1 Planning indicatif (4 semaines)
yaml

Semaine 1 - Fondation:
  - Setup Django + PostgreSQL + PostGIS
  - Modèles de données + migrations
  - Authentification JWT + SMS OTP
  - API de base (CRUD courses)

Semaine 2 - Cœur fonctionnel:
  - Système d'enchères (bids)
  - WebSocket + Redis pour temps réel
  - Géolocalisation de base
  - Intégration Google Maps Flutter

Semaine 3 - Paiements et finalisation:
  - Intégration Orange Money/MTN
  - Commission automatique
  - Tracking GPS en temps réel
  - Notifications push

Semaine 4 - Tests et déploiement:
  - Tests unitaires + intégration
  - Déploiement staging
  - Documentation API (Swagger)
  - Déploiement production

8.2 Équipe recommandée
Rôle	Compétences	Quantité
Backend Django	Python, Django, PostGIS, Redis	1 senior
Frontend Flutter	Dart, Google Maps, WebSocket	1 senior


QA	Tests manuels/automatisés	0.5
8.3 Budget infrastructure (mois)
yaml

Production:
  - VPS 8GB RAM, 4 vCPU: $60 (DigitalOcean/Hetzner)
  - PostgreSQL Managed: $50 (ou self-hosted gratuit)
  - Redis Managed: $30
  - Firebase Cloud Messaging: Gratuit
  - SMS OTP (10k/mois): $20
  - Mobile Money fees: 2% par transaction

Total mensuel estimé: $160 + coûts variables

9. LIVRABLES ATTENDUS
9.1 Code source

    Repository GitHub/GitLab complet

    README avec instructions d'installation

    Docker Compose pour environnement dev

9.2 Documentation

    Swagger/OpenAPI pour API REST

    Documentation WebSocket

    Guide déploiement production

    Manuel utilisateur (Client + Convoyeur)

9.3 Tests

    Tests unitaires (coverage > 80%)

    Tests d'intégration API

    Tests de charge (Locust/k6)

10. ACCEPTATION ET CRITÈRES DE VALIDATION
10.1 Critères obligatoires (MVP)

    Client peut créer une course avec géolocalisation

    Convoyeur voit les courses dans rayon 5km

    Convoyeur peut proposer un prix

    Client peut accepter une offre

    Paiement Mobile Money fonctionnel

    Commission de 15% déduite automatiquement

    Tracking GPS temps réel

    Notifications push pour offres/acceptations

    5 courses parallèles sans crash

10.2 Critères souhaitables (V1.1)

    Évaluation client/convoyeur (étoiles)

    Chat intégré pendant course

    Plusieurs véhicules (moto, voiture)

    Courses planifiées

    Partage de position en direct

    Mode sombre

11. ANNEXES
11.1 Exemple de payload API
json

// POST /api/client/rides/create
{
  "pickup": {
    "lat": 12.3714,
    "lng": -1.5333,
    "address": "Avenue Kwame Nkrumah, Ouaga 2000"
  },
  "dropoff": {
    "lat": 12.3689,
    "lng": -1.5274,
    "address": "Zone du Bois, Ouagadougou"
  },
  "vehicle_type": "moto",
  "payment_method": "orange_money"
}

// Response
{
  "ride_id": 12345,
  "estimated_distance": 2.5,
  "estimated_price_range": [1000, 2000],
  "expires_at": "2024-01-15T14:30:00Z",
  "status": "pending"
}

11.2 Configuration Docker
yaml

# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgis/postgis:14-3.4
    environment:
      POSTGRES_DB: transport_db
      POSTGRES_USER: transport_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: daphne -b 0.0.0.0 -p 8000 config.asgi:application
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql://transport_user:secure_password@db:5432/transport_db
      REDIS_URL: redis://redis:6379

volumes:
  postgres_data:

Document préparé pour: Projet de transport/livraison locale
Version: 1.0
Statut: À valider

C
