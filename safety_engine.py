import math
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in meters between two points
    on the earth (specified in decimal degrees).
    """
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
        
    # Earth radius in meters
    R = 6371000.0
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def check_geofences(user_lat, user_lon, geofences):
    """
    Evaluate user's coordinate against active geofences.
    Returns:
      - inside_zones: list of geofences the user is currently inside
      - proximity_warnings: list of geofences within warning buffer (300m)
      - highest_risk: 'restricted' | 'caution' | 'safe'
    """
    inside_zones = []
    proximity_warnings = []
    highest_risk = 'safe'
    
    for gf in geofences:
        if not gf.active:
            continue
        dist = haversine_distance(user_lat, user_lon, gf.latitude, gf.longitude)
        
        # Check if inside
        if dist <= gf.radius:
            inside_zones.append({
                'geofence': gf.to_dict(),
                'distance': round(dist, 1),
                'status': 'INSIDE'
            })
            if gf.risk_level == 'restricted':
                highest_risk = 'restricted'
            elif gf.risk_level == 'caution' and highest_risk != 'restricted':
                highest_risk = 'caution'
        # Check proximity warning buffer (within radius + 300 meters)
        elif dist <= (gf.radius + 300.0):
            proximity_warnings.append({
                'geofence': gf.to_dict(),
                'distance': round(dist, 1),
                'status': 'APPROACHING'
            })
            if gf.risk_level == 'restricted' and highest_risk == 'safe':
                highest_risk = 'caution'
                
    return {
        'inside_zones': inside_zones,
        'proximity_warnings': proximity_warnings,
        'highest_risk': highest_risk
    }

def calculate_safety_score(user_lat, user_lon, geofences, active_alerts, active_sos=False, anomaly_flag=False):
    """
    Computes an informative safety score (10 - 100) based on real-time factors:
    - Geofence risk level
    - Distance to active safety alerts
    - Active SOS status
    - Time of day (night risk factor)
    - Anomaly detection status
    """
    score = 100
    deductions = []
    
    # 1. Geofence evaluation
    gf_result = check_geofences(user_lat, user_lon, geofences)
    if gf_result['highest_risk'] == 'restricted':
        score -= 45
        deductions.append("Inside restricted or high-risk zone (-45)")
    elif gf_result['highest_risk'] == 'caution':
        score -= 20
        deductions.append("In caution zone or approaching restricted boundary (-20)")
        
    # 2. Proximity to active safety alerts (within 1.5 km)
    nearby_alert_count = 0
    for alert in active_alerts:
        if alert.latitude and alert.longitude:
            dist = haversine_distance(user_lat, user_lon, alert.latitude, alert.longitude)
            if dist <= 1500:
                nearby_alert_count += 1
    if nearby_alert_count > 0:
        penalty = min(25, nearby_alert_count * 10)
        score -= penalty
        deductions.append(f"{nearby_alert_count} active safety alerts nearby (-{penalty})")
        
    # 3. Active Emergency SOS
    if active_sos:
        score -= 40
        deductions.append("Active emergency SOS in progress (-40)")
        
    # 4. Anomaly detection flag
    if anomaly_flag:
        score -= 15
        deductions.append("Movement anomaly / route deviation detected (-15)")
        
    # 5. Night time travel factor (11 PM - 5 AM)
    current_hour = datetime.now().hour
    if current_hour >= 23 or current_hour < 5:
        score -= 10
        deductions.append("Late night travel hours (-10)")
        
    score = max(10, min(100, score))
    
    if score >= 80:
        rating = "Low Risk - Safe"
        badge = "success"
    elif score >= 55:
        rating = "Moderate Risk - Caution"
        badge = "warning"
    else:
        rating = "High Risk - Alert"
        badge = "danger"
        
    return {
        'score': score,
        'rating': rating,
        'badge': badge,
        'deductions': deductions,
        'geofence_status': gf_result
    }

class AnomalyDetector:
    """
    AI/ML Anomaly Detector combining Scikit-Learn IsolationForest
    with heuristic kinematic trajectory analysis.
    """
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        # Train with a baseline distribution of normal travel movements:
        # Features: [speed (km/h), delta_distance (m), delta_time (s), heading_change (deg)]
        np.random.seed(42)
        normal_speeds = np.random.normal(loc=15.0, scale=10.0, size=(200, 1)) # normal walking/driving
        normal_speeds = np.clip(normal_speeds, 0, 70)
        normal_deltas = np.random.normal(loc=40.0, scale=20.0, size=(200, 1))
        normal_times = np.random.uniform(5.0, 30.0, size=(200, 1))
        normal_headings = np.random.uniform(0.0, 45.0, size=(200, 1)) # gentle turns
        
        X_train = np.hstack([normal_speeds, normal_deltas, normal_times, normal_headings])
        self.model.fit(X_train)

    def analyze_movement(self, recent_logs, current_lat, current_lon, is_in_caution_zone=False):
        """
        Analyze recent coordinates and logs to detect anomalies:
        - Sudden route deviation
        - Prolonged inactivity in caution/restricted zone
        - Erratic movement pattern
        """
        if not recent_logs or len(recent_logs) < 2:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'reason': 'Telemetry gathering in progress'
            }
            
        last_log = recent_logs[-1]
        prev_log = recent_logs[-2]
        
        # Calculate kinematics
        dist_m = haversine_distance(last_log.latitude, last_log.longitude, current_lat, current_lon)
        if hasattr(last_log, 'timestamp') and last_log.timestamp:
            delta_seconds = max(1.0, abs((datetime.utcnow() - last_log.timestamp).total_seconds()))
        else:
            delta_seconds = 10.0
        speed_kmh = (dist_m / delta_seconds) * 3.6
        
        # Heuristic 1: Prolonged stationary in caution/restricted area
        if is_in_caution_zone and dist_m < 5.0 and delta_seconds > 180:
            return {
                'is_anomaly': True,
                'confidence': 0.88,
                'reason': 'Prolonged stationary inactivity detected in high-risk zone'
            }
            
        # Heuristic 2: Extreme sudden jump / route divergence
        if speed_kmh > 140:
            return {
                'is_anomaly': True,
                'confidence': 0.92,
                'reason': 'Abnormal velocity / unexpected telemetry jump'
            }
            
        # ML Model check:
        feature_vector = np.array([[speed_kmh, dist_m, delta_seconds, 15.0]])
        ml_prediction = self.model.predict(feature_vector)[0] # -1 = anomaly, 1 = normal
        
        if ml_prediction == -1 and (dist_m > 300 or speed_kmh > 90):
            return {
                'is_anomaly': True,
                'confidence': 0.81,
                'reason': 'Machine learning model flagged unusual movement vector'
            }
            
        return {
            'is_anomaly': False,
            'confidence': 0.05,
            'reason': 'Movement pattern is within normal parameters'
        }

# Global singleton detector
anomaly_engine = AnomalyDetector()
