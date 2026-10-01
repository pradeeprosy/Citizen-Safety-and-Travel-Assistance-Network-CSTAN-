from datetime import datetime, timedelta, timezone
from app import create_app
from models import db, User, TravelProfile, Geofence, EmergencyRequest, SafetyAlert, NearbyService, LocationLog, Incident

def populate_data():
    """Populate default demo data into currently active database session."""
    # 1. Create Admin Account
    admin = User(
        username='HQ_Commander',
        email='admin@cstan.org',
        phone='+91 94440 12345',
        role='admin',
        language='en',
        digital_id='CSTAN-HQ-001',
        blood_group='O+',
        medical_notes='HQ Admin - Authorized Personnel',
        emergency_contact_name='Police HQ Dispatch',
        emergency_contact_phone='112',
        last_latitude=13.0827,
        last_longitude=80.2707
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # 2. Create Demo Tourist / Citizen Account
    tourist = User(
        username='Sarah_Jenkins',
        email='tourist@cstan.org',
        phone='+91 98840 99881',
        role='user',
        language='en',
        digital_id='CSTAN-TN-2026-8842',
        blood_group='A+',
        medical_notes='Mild Asthmatic, carries inhaler',
        emergency_contact_name='David Jenkins (Brother)',
        emergency_contact_phone='+91 98765 43210',
        last_latitude=13.0827,
        last_longitude=80.2707
    )
    tourist.set_password('password123')
    db.session.add(tourist)

    # 3. Second demo tourist
    tourist2 = User(
        username='Arun_Karthik',
        email='arun@cstan.org',
        phone='+91 97711 22334',
        role='user',
        language='ta',
        digital_id='CSTAN-TN-2026-1049',
        blood_group='B+',
        medical_notes='None',
        emergency_contact_name='Lakshmi Karthik (Mother)',
        emergency_contact_phone='+91 94441 55667',
        last_latitude=13.0878,
        last_longitude=80.2785
    )
    tourist2.set_password('password123')
    db.session.add(tourist2)
    db.session.commit()

    # 4. Travel Profiles
    tp1 = TravelProfile(
        user_id=tourist.id,
        destination='Chennai Heritage & Coastal Route',
        purpose='Cultural Tourism',
        start_date='2026-10-01',
        end_date='2026-10-07',
        status='Active'
    )
    tp2 = TravelProfile(
        user_id=tourist2.id,
        destination='Mahabalipuram Temple Corridor',
        purpose='Photography & Heritage',
        start_date='2026-10-01',
        end_date='2026-10-03',
        status='Active'
    )
    db.session.add_all([tp1, tp2])

    # 5. Geofences
    geofences = [
        Geofence(
            name='Port Trust Security Enclosure',
            latitude=13.0905,
            longitude=80.2920,
            radius=500.0,
            risk_level='restricted',
            description='High-security naval port basin. Civilians prohibited without harbor pass.',
            advisory='⚠️ RESTRICTED ZONE: Unauthorized entry is prohibited. Turn around immediately.',
            active=True
        ),
        Geofence(
            name='Old Fort Trench Excavation Zone',
            latitude=13.0780,
            longitude=80.2630,
            radius=350.0,
            risk_level='caution',
            description='Ongoing archaeological excavation with unlit trenches and slippery terrain.',
            advisory='🔔 CAUTION ZONE: Increased caution recommended after sunset. Stay on lighted paved paths.',
            active=True
        ),
        Geofence(
            name='Marina Promenade Safe Tourist Haven',
            latitude=13.0550,
            longitude=80.2825,
            radius=900.0,
            risk_level='safe',
            description='Patrolled pedestrian promenade with 24/7 tourist police booths and lighting.',
            advisory='✅ SAFE ZONE: Well patrolled tourist corridor with emergency help kiosks.',
            active=True
        ),
        Geofence(
            name='Railway Freight Corridor Underpass',
            latitude=13.0850,
            longitude=80.2600,
            radius=300.0,
            risk_level='restricted',
            description='Active industrial rail maneuvering yard with high-voltage electrification.',
            advisory='⚠️ RESTRICTED RAIL CORRIDOR: Danger of active trains and high voltage.',
            active=True
        )
    ]
    db.session.add_all(geofences)

    # 6. Nearby Services (Police, Hospital, Fire, Tourist Desk)
    services = [
        NearbyService(
            name='Fort St. George Police Station & Tourist Assistance',
            category='police',
            latitude=13.0795,
            longitude=80.2870,
            contact_number='044-25670112',
            address='Rajaji Salai, Fort St George, Chennai',
            is_24_7=True
        ),
        NearbyService(
            name='Marina Beach Tourist Patrol Outpost',
            category='police',
            latitude=13.0520,
            longitude=80.2830,
            contact_number='044-28447711',
            address='Kamarajar Promenade, Marina Beach',
            is_24_7=True
        ),
        NearbyService(
            name='Rajiv Gandhi Government General Hospital (Trauma Center)',
            category='hospital',
            latitude=13.0815,
            longitude=80.2770,
            contact_number='044-25305000',
            address='EVR Periyar Salai, Park Town, Chennai',
            is_24_7=True
        ),
        NearbyService(
            name='Apollo Specialty Hospital & Emergency Care',
            category='hospital',
            latitude=13.0600,
            longitude=80.2500,
            contact_number='044-28290200',
            address='Greams Lane, Thousand Lights, Chennai',
            is_24_7=True
        ),
        NearbyService(
            name='Central Fire & Rescue Headquarters',
            category='fire',
            latitude=13.0750,
            longitude=80.2680,
            contact_number='101 / 044-28552222',
            address='Poonamallee High Road, Kilpauk, Chennai',
            is_24_7=True
        ),
        NearbyService(
            name='Tamil Nadu Tourist Information & Facilitation Center',
            category='tourist_desk',
            latitude=13.0835,
            longitude=80.2720,
            contact_number='1800-4253-1111',
            address='Opposite Chennai Central Station, Park Town',
            is_24_7=True
        )
    ]
    db.session.add_all(services)

    # 7. Safety Alerts
    alerts = [
        SafetyAlert(
            title='High Tide Advisory along Marina Coast',
            description='Rough sea conditions expected along eastern shoreline between 18:00 and 22:00. Swimming is strictly prohibited.',
            latitude=13.0550,
            longitude=80.2830,
            risk_level='medium',
            active=True
        ),
        SafetyAlert(
            title='Temporary Metro Construction Diversion',
            description='Anna Salai section near Central station is restricted to single-lane pedestrian traffic due to elevated metro corridor girder work.',
            latitude=13.0805,
            longitude=80.2730,
            risk_level='low',
            active=True
        ),
        SafetyAlert(
            title='Heavy Logistics Vehicle Movement',
            description='Increased freight movement near North Port road. Pedestrians advised to use designated pedestrian overhead pass.',
            latitude=13.0920,
            longitude=80.2890,
            risk_level='high',
            active=True
        )
    ]
    db.session.add_all(alerts)

    # 8. Emergency Requests (Sample for Admin live monitoring)
    em1 = EmergencyRequest(
        user_id=tourist.id,
        type='Lost Person',
        latitude=13.0845,
        longitude=80.2740,
        description='Separated from tour group near heritage market alley; phone battery low.',
        status='ACKNOWLEDGED',
        severity='Medium',
        created_at=datetime.now(timezone.utc) - timedelta(minutes=24),
        admin_notes='Dispatched Tourist Patrol Officer Kumar (Unit 14) to Central Heritage Market.'
    )
    em2 = EmergencyRequest(
        user_id=tourist2.id,
        type='Medical Emergency',
        latitude=13.0760,
        longitude=80.2650,
        description='Sudden dehydration and severe heat exhaustion near temple steps.',
        status='RESOLVED',
        severity='High',
        created_at=datetime.now(timezone.utc) - timedelta(hours=3),
        resolved_at=datetime.now(timezone.utc) - timedelta(hours=2),
        admin_notes='Ambulance 108 provided first aid and oral rehydration. Patient safely stabilized.'
    )
    db.session.add_all([em1, em2])

    # 9. Initial Location Logs for Sarah (for trajectory rendering)
    base_time = datetime.now(timezone.utc) - timedelta(minutes=15)
    trail_coords = [
        (13.0800, 80.2680, 12.0),
        (13.0812, 80.2695, 14.5),
        (13.0820, 80.2702, 10.2),
        (13.0827, 80.2707, 4.0),
    ]
    for i, (lat, lon, spd) in enumerate(trail_coords):
        log = LocationLog(
            user_id=tourist.id,
            latitude=lat,
            longitude=lon,
            speed=spd,
            timestamp=base_time + timedelta(minutes=i*3)
        )
        db.session.add(log)

    db.session.commit()
    print("Database successfully seeded with realistic CSTAN safety data!")

def seed_database(app=None):
    if app is None:
        app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_data()

if __name__ == '__main__':
    seed_database()
