import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Geofence, EmergencyRequest, SafetyAlert, NearbyService, LocationLog
from safety_engine import haversine_distance, check_geofences, calculate_safety_score, anomaly_engine

class CSTANTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create test user
            self.user = User(
                username='TestUser',
                email='test@example.com',
                phone='+91 99999 88888',
                role='user',
                digital_id='CSTAN-TEST-001',
                emergency_contact_name='Emergency Contact',
                emergency_contact_phone='+91 99999 77777',
                last_latitude=13.0827,
                last_longitude=80.2707
            )
            self.user.set_password('testpass123')
            db.session.add(self.user)

            # Create test admin
            self.admin = User(
                username='TestAdmin',
                email='admin@example.com',
                role='admin',
                digital_id='CSTAN-ADMIN-001'
            )
            self.admin.set_password('adminpass123')
            db.session.add(self.admin)

            # Create test geofence
            self.gf_restricted = Geofence(
                name='Restricted Test Zone',
                latitude=13.0900,
                longitude=80.2900,
                radius=400.0,
                risk_level='restricted',
                active=True
            )
            self.gf_caution = Geofence(
                name='Caution Test Zone',
                latitude=13.0780,
                longitude=80.2630,
                radius=300.0,
                risk_level='caution',
                active=True
            )
            db.session.add_all([self.gf_restricted, self.gf_caution])

            # Create test nearby service
            self.service = NearbyService(
                name='City Central Police Station',
                category='police',
                latitude=13.0820,
                longitude=80.2710,
                contact_number='100'
            )
            db.session.add(self.service)

            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_haversine_distance(self):
        # Coordinates very close (~100m)
        dist = haversine_distance(13.0827, 80.2707, 13.0827, 80.2717)
        self.assertTrue(90 < dist < 130)

    def test_geofence_logic(self):
        with self.app.app_context():
            geofences = Geofence.query.all()
            
            # Point right at center of restricted zone
            res_inside = check_geofences(13.0900, 80.2900, geofences)
            self.assertEqual(res_inside['highest_risk'], 'restricted')
            self.assertEqual(len(res_inside['inside_zones']), 1)

            # Point far away
            res_safe = check_geofences(13.0500, 80.2500, geofences)
            self.assertEqual(res_safe['highest_risk'], 'safe')
            self.assertEqual(len(res_safe['inside_zones']), 0)

    def test_safety_score_calculation(self):
        with self.app.app_context():
            geofences = Geofence.query.all()
            alerts = []

            # Safe area
            safe_calc = calculate_safety_score(13.0500, 80.2500, geofences, alerts)
            self.assertGreaterEqual(safe_calc['score'], 80)
            self.assertEqual(safe_calc['badge'], 'success')

            # Inside restricted zone
            restricted_calc = calculate_safety_score(13.0900, 80.2900, geofences, alerts)
            self.assertLess(restricted_calc['score'], 60)

            # Active SOS
            sos_calc = calculate_safety_score(13.0500, 80.2500, geofences, alerts, active_sos=True)
            self.assertLess(sos_calc['score'], 70)

    def test_anomaly_detector(self):
        from datetime import datetime, timedelta
        class FakeLog:
            def __init__(self, lat, lon, offset_sec):
                self.latitude = lat
                self.longitude = lon
                self.timestamp = datetime.utcnow() - timedelta(seconds=offset_sec)

        # Normal walking: ~20 meters over 15 seconds (~4.8 km/h)
        logs = [FakeLog(13.08000, 80.27000, 30), FakeLog(13.08010, 80.27010, 15)]
        res_normal = anomaly_engine.analyze_movement(logs, 13.08020, 80.27020)
        self.assertFalse(res_normal['is_anomaly'])

    def test_user_authentication_flow(self):
        # 1. Login with bad password
        res = self.client.post('/login', data={'email': 'test@example.com', 'password': 'wrong'})
        self.assertEqual(res.status_code, 200)

        # 2. Login successfully
        res = self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpass123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'TestUser', res.data)

    def test_location_update_and_sos_api(self):
        # Login first
        self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpass123'})

        # Update location
        res = self.client.post('/api/update-location', 
                               data=json.dumps({'latitude': 13.0830, 'longitude': 80.2710, 'speed': 5.0}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('safety', data)
        self.assertIn('score', data['safety'])

        # Dispatch Emergency SOS
        sos_res = self.client.post('/api/sos',
                                  data=json.dumps({
                                      'type': 'Medical Emergency',
                                      'latitude': 13.0830,
                                      'longitude': 80.2710,
                                      'description': 'Test chest pain'
                                  }),
                                  content_type='application/json')
        self.assertEqual(sos_res.status_code, 200)
        sos_data = json.loads(sos_res.data)
        self.assertTrue(sos_data['success'])
        self.assertEqual(sos_data['emergency']['status'], 'NEW')

    def test_admin_incident_triage(self):
        # 1. User creates SOS
        self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpass123'})
        sos_res = self.client.post('/api/sos',
                                  data=json.dumps({
                                      'type': 'Lost Person',
                                      'latitude': 13.0830,
                                      'longitude': 80.2710,
                                      'description': 'Lost in crowd'
                                  }),
                                  content_type='application/json')
        em_id = json.loads(sos_res.data)['emergency']['id']
        self.client.get('/logout')

        # 2. Admin logs in
        self.client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass123'})

        # 3. Admin acknowledges SOS
        triage_res = self.client.post('/admin/sos/update',
                                     data=json.dumps({
                                         'emergency_id': em_id,
                                         'status': 'ACKNOWLEDGED',
                                         'admin_notes': 'Tourist Police Unit dispatched'
                                     }),
                                     content_type='application/json')
        self.assertEqual(triage_res.status_code, 200)
        self.assertEqual(json.loads(triage_res.data)['emergency']['status'], 'ACKNOWLEDGED')

        # 4. Admin marks RESOLVED
        resolve_res = self.client.post('/admin/sos/update',
                                      data=json.dumps({
                                          'emergency_id': em_id,
                                          'status': 'RESOLVED',
                                          'admin_notes': 'Tourist located and escorted'
                                      }),
                                      content_type='application/json')
        self.assertEqual(resolve_res.status_code, 200)
        self.assertEqual(json.loads(resolve_res.data)['emergency']['status'], 'RESOLVED')

if __name__ == '__main__':
    unittest.main()
