from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    language = db.Column(db.String(10), default='en') # 'en', 'ta', 'hi', 'te', 'ml', 'kn'
    digital_id = db.Column(db.String(30), unique=True, nullable=False)
    blood_group = db.Column(db.String(10), default='Unknown')
    medical_notes = db.Column(db.String(255), default='None')
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    last_latitude = db.Column(db.Float, nullable=True)
    last_longitude = db.Column(db.Float, nullable=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    travel_profiles = db.relationship('TravelProfile', backref='user', lazy=True, cascade='all, delete-orphan')
    emergency_requests = db.relationship('EmergencyRequest', backref='user', lazy=True, cascade='all, delete-orphan')
    location_logs = db.relationship('LocationLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'language': self.language,
            'digital_id': self.digital_id,
            'blood_group': self.blood_group,
            'medical_notes': self.medical_notes,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'last_latitude': self.last_latitude,
            'last_longitude': self.last_longitude,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


class TravelProfile(db.Model):
    __tablename__ = 'travel_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    purpose = db.Column(db.String(100), default='Tourism')
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Active')  # 'Active', 'Completed', 'Planned'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'destination': self.destination,
            'purpose': self.purpose,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Geofence(db.Model):
    __tablename__ = 'geofences'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, nullable=False)  # in meters
    risk_level = db.Column(db.String(20), default='caution')  # 'safe', 'caution', 'restricted'
    description = db.Column(db.Text, nullable=True)
    advisory = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'risk_level': self.risk_level,
            'description': self.description,
            'advisory': self.advisory,
            'active': self.active
        }


class EmergencyRequest(db.Model):
    __tablename__ = 'emergency_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'Medical Emergency', 'Accident', 'Lost Person', 'Harassment', 'Security Threat', 'Other'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='NEW')  # 'NEW', 'ACKNOWLEDGED', 'IN PROGRESS', 'RESOLVED'
    severity = db.Column(db.String(20), default='High')  # 'Medium', 'High', 'Critical'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'digital_id': self.user.digital_id if self.user else '',
            'user_phone': self.user.phone if self.user else '',
            'emergency_contact': f"{self.user.emergency_contact_name} ({self.user.emergency_contact_phone})" if self.user and self.user.emergency_contact_name else 'N/A',
            'type': self.type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'status': self.status,
            'severity': self.severity,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else '',
            'admin_notes': self.admin_notes or ''
        }


class SafetyAlert(db.Model):
    __tablename__ = 'safety_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    risk_level = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'risk_level': self.risk_level,
            'active': self.active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class NearbyService(db.Model):
    __tablename__ = 'nearby_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'police', 'hospital', 'fire', 'tourist_desk'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact_number = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    is_24_7 = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'contact_number': self.contact_number,
            'address': self.address,
            'is_24_7': self.is_24_7
        }


class LocationLog(db.Model):
    __tablename__ = 'location_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, default=0.0)  # km/h
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    emergency_id = db.Column(db.Integer, db.ForeignKey('emergency_requests.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    location_name = db.Column(db.String(150), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Reported') # 'Reported', 'Under Investigation', 'Resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emergency_id': self.emergency_id,
            'title': self.title,
            'type': self.type,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
