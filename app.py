import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, TravelProfile, Geofence, EmergencyRequest, SafetyAlert, NearbyService, LocationLog, Incident
from safety_engine import haversine_distance, check_geofences, calculate_safety_score, anomaly_engine

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cstan-secret-key-super-secure-2026')
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///cstan.db')
    # Support postgresql:// URL format on cloud hosts like Render/Heroku
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Helper function to generate digital safety IDs
    def generate_digital_id():
        code = random.randint(1000, 9999)
        return f"CSTAN-TN-2026-{code}"

    # ------------------ Web Pages ------------------

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = True if request.form.get('remember') else False
            
            user = User.query.filter_by(email=email).first()
            if not user or not user.check_password(password):
                flash('Invalid credentials. Please check your email and password.', 'danger')
                return render_template('login.html')
                
            login_user(user, remember=remember)
            session['lang'] = user.language or 'en'
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
            
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            phone = request.form.get('phone', '').strip()
            language = request.form.get('language', 'en')
            blood_group = request.form.get('blood_group', 'Unknown')
            medical_notes = request.form.get('medical_notes', '')
            emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
            emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
            destination = request.form.get('destination', 'Chennai Central').strip()
            
            if User.query.filter_by(email=email).first():
                flash('An account with this email already exists.', 'warning')
                return render_template('register.html')
                
            if User.query.filter_by(username=username).first():
                flash('Username is already taken. Please choose another.', 'warning')
                return render_template('register.html')
                
            digital_id = generate_digital_id()
            while User.query.filter_by(digital_id=digital_id).first():
                digital_id = generate_digital_id()
                
            new_user = User(
                username=username,
                email=email,
                phone=phone,
                role='user',
                language=language,
                digital_id=digital_id,
                blood_group=blood_group,
                medical_notes=medical_notes or 'None',
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone,
                last_latitude=13.0827,
                last_longitude=80.2707
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Create active travel profile
            tp = TravelProfile(
                user_id=new_user.id,
                destination=destination,
                purpose='Tourism & Citizen Travel',
                start_date=datetime.utcnow().strftime('%Y-%m-%d'),
                status='Active'
            )
            db.session.add(tp)
            db.session.commit()
            
            login_user(new_user)
            session['lang'] = language
            flash(f'Account created successfully! Your Digital Safety ID is {digital_id}', 'success')
            return redirect(url_for('user_dashboard'))
            
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        flash('You have been logged out safely.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def user_dashboard():
        # Fetch user travel profile, geofences, alerts
        profile = TravelProfile.query.filter_by(user_id=current_user.id, status='Active').first()
        geofences = Geofence.query.filter_by(active=True).all()
        alerts = SafetyAlert.query.filter_by(active=True).order_by(SafetyAlert.created_at.desc()).all()
        
        # Check active SOS
        active_sos = EmergencyRequest.query.filter(
            EmergencyRequest.user_id == current_user.id,
            EmergencyRequest.status.in_(['NEW', 'ACKNOWLEDGED', 'IN PROGRESS'])
        ).first()
        
        # Calculate initial score based on last known coordinate
        lat = current_user.last_latitude or 13.0827
        lon = current_user.last_longitude or 80.2707
        score_data = calculate_safety_score(lat, lon, geofences, alerts, active_sos=bool(active_sos))
        
        return render_template('user_dashboard.html',
                               profile=profile,
                               geofences=geofences,
                               alerts=alerts,
                               active_sos=active_sos,
                               safety=score_data,
                               current_lang=current_user.language or 'en')

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            current_user.phone = request.form.get('phone', current_user.phone)
            current_user.emergency_contact_name = request.form.get('emergency_contact_name', current_user.emergency_contact_name)
            current_user.emergency_contact_phone = request.form.get('emergency_contact_phone', current_user.emergency_contact_phone)
            current_user.blood_group = request.form.get('blood_group', current_user.blood_group)
            current_user.medical_notes = request.form.get('medical_notes', current_user.medical_notes)
            current_user.language = request.form.get('language', current_user.language)
            session['lang'] = current_user.language
            db.session.commit()
            flash('Profile information updated successfully.', 'success')
            return redirect(url_for('profile'))
            
        travel_profiles = TravelProfile.query.filter_by(user_id=current_user.id).order_by(TravelProfile.created_at.desc()).all()
        my_emergencies = EmergencyRequest.query.filter_by(user_id=current_user.id).order_by(EmergencyRequest.created_at.desc()).all()
        return render_template('profile.html', travel_profiles=travel_profiles, emergencies=my_emergencies)

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Access denied: Authorities only.', 'danger')
            return redirect(url_for('user_dashboard'))
            
        total_users = User.query.filter_by(role='user').count()
        active_travelers = TravelProfile.query.filter_by(status='Active').count()
        active_alerts_count = SafetyAlert.query.filter_by(active=True).count()
        active_sos_count = EmergencyRequest.query.filter(EmergencyRequest.status.in_(['NEW', 'ACKNOWLEDGED', 'IN PROGRESS'])).count()
        
        all_emergencies = EmergencyRequest.query.order_by(EmergencyRequest.created_at.desc()).all()
        geofences = Geofence.query.all()
        alerts = SafetyAlert.query.order_by(SafetyAlert.created_at.desc()).all()
        active_users = User.query.filter_by(role='user').all()
        
        return render_template('admin_dashboard.html',
                               total_users=total_users,
                               active_travelers=active_travelers,
                               active_alerts_count=active_alerts_count,
                               active_sos_count=active_sos_count,
                               emergencies=all_emergencies,
                               geofences=geofences,
                               alerts=alerts,
                               active_users=active_users)

    # ------------------ REST APIs ------------------

    @app.route('/api/update-location', methods=['POST'])
    @login_required
    def api_update_location():
        data = request.get_json() or {}
        lat = data.get('latitude')
        lon = data.get('longitude')
        speed = data.get('speed', 0.0)
        
        if lat is None or lon is None:
            return jsonify({'error': 'Coordinates required'}), 400
            
        current_user.last_latitude = float(lat)
        current_user.last_longitude = float(lon)
        current_user.last_active = datetime.utcnow()
        
        # Save telemetry log
        log = LocationLog(
            user_id=current_user.id,
            latitude=float(lat),
            longitude=float(lon),
            speed=float(speed),
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Evaluate Geofences
        geofences = Geofence.query.filter_by(active=True).all()
        gf_result = check_geofences(float(lat), float(lon), geofences)
        
        # Check active SOS
        active_sos = EmergencyRequest.query.filter(
            EmergencyRequest.user_id == current_user.id,
            EmergencyRequest.status.in_(['NEW', 'ACKNOWLEDGED', 'IN PROGRESS'])
        ).first()
        
        # Run AI Anomaly Detector on recent telemetry logs
        recent_logs = LocationLog.query.filter_by(user_id=current_user.id)\
            .order_by(LocationLog.timestamp.desc()).limit(5).all()
        recent_logs.reverse() # chronological
        
        is_in_caution = (gf_result['highest_risk'] in ['caution', 'restricted'])
        anomaly_result = anomaly_engine.analyze_movement(
            recent_logs, float(lat), float(lon), is_in_caution_zone=is_in_caution
        )
        
        # Compute Dynamic Safety Score
        alerts = SafetyAlert.query.filter_by(active=True).all()
        score_data = calculate_safety_score(
            float(lat), float(lon), geofences, alerts,
            active_sos=bool(active_sos),
            anomaly_flag=anomaly_result['is_anomaly']
        )
        
        return jsonify({
            'success': True,
            'location': {'latitude': float(lat), 'longitude': float(lon)},
            'geofence_status': gf_result,
            'safety': score_data,
            'anomaly': anomaly_result,
            'active_sos': active_sos.to_dict() if active_sos else None
        })

    @app.route('/api/sos', methods=['POST'])
    @login_required
    def api_send_sos():
        data = request.get_json() or {}
        emergency_type = data.get('type', 'Other')
        lat = data.get('latitude', current_user.last_latitude or 13.0827)
        lon = data.get('longitude', current_user.last_longitude or 80.2707)
        desc = data.get('description', 'User triggered Emergency SOS button.')
        severity = data.get('severity', 'High')
        
        emergency = EmergencyRequest(
            user_id=current_user.id,
            type=emergency_type,
            latitude=float(lat),
            longitude=float(lon),
            description=desc,
            status='NEW',
            severity=severity,
            created_at=datetime.utcnow()
        )
        db.session.add(emergency)
        
        # Create corresponding incident entry
        inc = Incident(
            user_id=current_user.id,
            emergency_id=emergency.id,
            title=f"SOS: {emergency_type} from {current_user.username}",
            type=emergency_type,
            location_name=f"Lat {round(float(lat), 4)}, Lon {round(float(lon), 4)}",
            latitude=float(lat),
            longitude=float(lon),
            description=desc,
            status='Reported'
        )
        db.session.add(inc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Emergency SOS dispatched to Central Authorities and Emergency Contacts.',
            'emergency': emergency.to_dict()
        })

    @app.route('/api/nearby-services')
    def api_nearby_services():
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        category = request.args.get('category')
        
        query = NearbyService.query
        if category and category != 'all':
            query = query.filter_by(category=category)
            
        services = query.all()
        result = []
        for s in services:
            s_dict = s.to_dict()
            if lat is not None and lon is not None:
                dist_m = haversine_distance(lat, lon, s.latitude, s.longitude)
                s_dict['distance_m'] = round(dist_m, 1)
                s_dict['distance_km'] = round(dist_m / 1000.0, 2)
            else:
                s_dict['distance_m'] = None
                s_dict['distance_km'] = None
            result.append(s_dict)
            
        if lat is not None and lon is not None:
            result.sort(key=lambda x: x['distance_m'])
            
        return jsonify(result)

    @app.route('/api/geofences')
    def api_geofences():
        geofences = Geofence.query.filter_by(active=True).all()
        return jsonify([g.to_dict() for g in geofences])

    @app.route('/api/alerts')
    def api_alerts():
        alerts = SafetyAlert.query.filter_by(active=True).order_by(SafetyAlert.created_at.desc()).all()
        return jsonify([a.to_dict() for a in alerts])

    @app.route('/api/set-language', methods=['POST'])
    def api_set_language():
        data = request.get_json() or {}
        lang = data.get('language', 'en')
        session['lang'] = lang
        if current_user.is_authenticated:
            current_user.language = lang
            db.session.commit()
        return jsonify({'success': True, 'language': lang})

    # ------------------ Admin APIs ------------------

    @app.route('/admin/sos/update', methods=['POST'])
    @login_required
    def admin_sos_update():
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json() or {}
        emergency_id = data.get('emergency_id')
        new_status = data.get('status')
        notes = data.get('admin_notes', '')
        
        emergency = db.session.get(EmergencyRequest, emergency_id)
        if not emergency:
            return jsonify({'error': 'Emergency request not found'}), 404
            
        if new_status:
            emergency.status = new_status
            if new_status == 'RESOLVED':
                emergency.resolved_at = datetime.utcnow()
        if notes:
            emergency.admin_notes = notes
            
        emergency.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'emergency': emergency.to_dict()
        })

    @app.route('/admin/geofence/create', methods=['POST'])
    @login_required
    def admin_geofence_create():
        if current_user.role != 'admin':
            flash('Unauthorized', 'danger')
            return redirect(url_for('user_dashboard'))
            
        name = request.form.get('name')
        lat = float(request.form.get('latitude'))
        lon = float(request.form.get('longitude'))
        radius = float(request.form.get('radius'))
        risk_level = request.form.get('risk_level', 'caution')
        description = request.form.get('description', '')
        advisory = request.form.get('advisory', '')
        
        gf = Geofence(
            name=name,
            latitude=lat,
            longitude=lon,
            radius=radius,
            risk_level=risk_level,
            description=description,
            advisory=advisory,
            active=True
        )
        db.session.add(gf)
        db.session.commit()
        flash(f'Geofence "{name}" defined successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/geofence/toggle/<int:id>', methods=['POST'])
    @login_required
    def admin_geofence_toggle(id):
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        gf = db.session.get(Geofence, id)
        if not gf:
            return jsonify({'error': 'Geofence not found'}), 404
        gf.active = not gf.active
        db.session.commit()
        return jsonify({'success': True, 'active': gf.active})

    @app.route('/admin/alerts/create', methods=['POST'])
    @login_required
    def admin_alert_create():
        if current_user.role != 'admin':
            flash('Unauthorized', 'danger')
            return redirect(url_for('user_dashboard'))
            
        title = request.form.get('title')
        description = request.form.get('description')
        risk_level = request.form.get('risk_level', 'medium')
        lat = request.form.get('latitude')
        lon = request.form.get('longitude')
        
        alert = SafetyAlert(
            title=title,
            description=description,
            risk_level=risk_level,
            latitude=float(lat) if lat else None,
            longitude=float(lon) if lon else None,
            active=True
        )
        db.session.add(alert)
        db.session.commit()
        flash(f'Safety alert "{title}" broadcasted to all travelers.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/api/live-data')
    @login_required
    def admin_api_live_data():
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        emergencies = EmergencyRequest.query.order_by(EmergencyRequest.created_at.desc()).all()
        users = User.query.filter_by(role='user').all()
        
        return jsonify({
            'emergencies': [e.to_dict() for e in emergencies],
            'users': [{
                'id': u.id,
                'username': u.username,
                'digital_id': u.digital_id,
                'latitude': u.last_latitude,
                'longitude': u.last_longitude,
                'phone': u.phone,
                'last_active': u.last_active.strftime('%H:%M:%S') if u.last_active else 'N/A'
            } for u in users if u.last_latitude and u.last_longitude]
        })

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1']
    app.run(debug=debug, host='0.0.0.0', port=port)
