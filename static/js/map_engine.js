/**
 * CSTAN User Map & Real-Time Safety Engine
 */

let userMap = null;
let userMarker = null;
let pathPolyline = null;
let geofenceLayers = [];
let serviceMarkers = [];
let movementHistory = [];
let simulationInterval = null;
let isSimulating = false;
let currentCoords = { lat: 13.0827, lon: 80.2707 };

// Waypoints for demo route walk (traveling across safe zone into Old Fort & Port Trust perimeter)
const demoWaypoints = [
  { lat: 13.0827, lon: 80.2707, speed: 4.5 },
  { lat: 13.0815, lon: 80.2725, speed: 4.2 },
  { lat: 13.0805, lon: 80.2745, speed: 5.0 },
  { lat: 13.0792, lon: 80.2770, speed: 4.8 },
  // Approaching Old Fort Trench (Caution zone near 13.0780, 80.2630)
  { lat: 13.0782, lon: 80.2635, speed: 2.1 }, // Slowdown inside caution zone
  { lat: 13.0780, lon: 80.2630, speed: 0.5 }, // Prolonged stay
  // Moving towards Port Trust Security Enclosure (Restricted zone: 13.0905, 80.2920)
  { lat: 13.0850, lon: 80.2800, speed: 28.0 },
  { lat: 13.0890, lon: 80.2880, speed: 18.0 },
  { lat: 13.0905, lon: 80.2920, speed: 6.0 } // Breaching restricted zone
];
let waypointIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadGeofences();
  loadNearbyServices('all');
  setupEventListeners();
  
  // Apply saved language
  const savedLang = localStorage.getItem('cstan_lang') || 'en';
  const langSelect = document.getElementById('langSelect');
  if (langSelect) {
    langSelect.value = savedLang;
  }
  applyLanguage(savedLang);
});

function initMap() {
  const mapElement = document.getElementById('userMap');
  if (!mapElement) return;

  const initialLat = parseFloat(mapElement.getAttribute('data-lat')) || 13.0827;
  const initialLon = parseFloat(mapElement.getAttribute('data-lon')) || 80.2707;
  currentCoords = { lat: initialLat, lon: initialLon };

  userMap = L.map('userMap').setView([initialLat, initialLon], 14);

  // Modern CartoDB Dark Matter tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(userMap);

  // Custom User Marker
  const userIcon = L.divIcon({
    className: 'custom-user-marker',
    html: `<div style="background-color: #3b82f6; width: 22px; height: 22px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 14px #2563eb;"></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11]
  });

  userMarker = L.marker([initialLat, initialLon], { icon: userIcon }).addTo(userMap);
  userMarker.bindPopup("<b>You are here</b><br>Live Safety Telemetry Active").openPopup();

  // Trail line
  movementHistory.push([initialLat, initialLon]);
  pathPolyline = L.polyline(movementHistory, { color: '#38bdf8', weight: 4, opacity: 0.75, dashArray: '6, 8' }).addTo(userMap);
}

function loadGeofences() {
  fetch('/api/geofences')
    .then(res => res.json())
    .then(geofences => {
      // Clear old
      geofenceLayers.forEach(l => userMap.removeLayer(l));
      geofenceLayers = [];

      geofences.forEach(gf => {
        let color = '#10b981';
        let fillColor = '#10b981';
        let label = 'Safe Monitored Area';

        if (gf.risk_level === 'restricted') {
          color = '#ef4444';
          fillColor = '#ef4444';
          label = 'RESTRICTED / HIGH RISK ZONE';
        } else if (gf.risk_level === 'caution') {
          color = '#f59e0b';
          fillColor = '#f59e0b';
          label = 'CAUTION ZONE';
        }

        const circle = L.circle([gf.latitude, gf.longitude], {
          color: color,
          fillColor: fillColor,
          fillOpacity: 0.22,
          radius: gf.radius,
          weight: 2
        }).addTo(userMap);

        circle.bindPopup(`
          <div style="font-family: inherit;">
            <strong style="color: ${color}; font-size: 1.05rem;">${label}</strong><br>
            <b>${gf.name}</b><br>
            <span style="font-size: 0.85rem; color: #555;">${gf.description || ''}</span><br>
            <div style="margin-top: 6px; padding: 4px 8px; background: #fee2e2; border-left: 3px solid ${color}; font-size: 0.8rem; color: #991b1b;">
              ${gf.advisory || 'Comply with local safety directions.'}
            </div>
            <div style="margin-top: 4px; font-size: 0.75rem; color: #888;">Radius: ${gf.radius} meters</div>
          </div>
        `);

        geofenceLayers.push(circle);
      });
    })
    .catch(err => console.error('Error loading geofences:', err));
}

function loadNearbyServices(category = 'all') {
  const url = `/api/nearby-services?lat=${currentCoords.lat}&lon=${currentCoords.lon}&category=${category}`;
  fetch(url)
    .then(res => res.json())
    .then(services => {
      // Clear previous
      serviceMarkers.forEach(m => userMap.removeLayer(m));
      serviceMarkers = [];

      const listContainer = document.getElementById('nearbyServicesList');
      if (listContainer) listContainer.innerHTML = '';

      services.forEach(s => {
        let iconHtml = '🏢';
        let colorClass = '#3b82f6';

        if (s.category === 'police') {
          iconHtml = '👮';
          colorClass = '#1d4ed8';
        } else if (s.category === 'hospital') {
          iconHtml = '🏥';
          colorClass = '#dc2626';
        } else if (s.category === 'fire') {
          iconHtml = '🚒';
          colorClass = '#ea580c';
        } else if (s.category === 'tourist_desk') {
          iconHtml = 'ℹ️';
          colorClass = '#7c3aed';
        }

        const customMarkerIcon = L.divIcon({
          className: 'service-pin',
          html: `<div style="background: white; border: 2px solid ${colorClass}; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">${iconHtml}</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });

        const marker = L.marker([s.latitude, s.longitude], { icon: customMarkerIcon }).addTo(userMap);
        marker.bindPopup(`
          <div>
            <strong style="color:${colorClass};">${s.name}</strong><br>
            <span style="font-size: 0.85rem; color:#666;">${s.address || ''}</span><br>
            <div style="margin-top: 6px;">
              <b>Distance:</b> ${s.distance_km ? s.distance_km + ' km' : 'N/A'}<br>
              <b>Phone:</b> <a href="tel:${s.contact_number}">${s.contact_number}</a>
            </div>
          </div>
        `);
        serviceMarkers.push(marker);

        // Populate side panel list card
        if (listContainer) {
          const item = document.createElement('div');
          item.className = 'p-2 mb-2 rounded bg-dark border border-secondary d-flex justify-content-between align-items-center';
          item.innerHTML = `
            <div>
              <div class="fw-bold text-light">${iconHtml} ${s.name}</div>
              <small class="text-muted">${s.address || 'Nearby service'} • <span class="text-info">${s.distance_km || 0} km</span></small>
            </div>
            <div>
              <a href="tel:${s.contact_number}" class="btn btn-sm btn-outline-info">
                📞 <span data-i18n="call_service">Call</span>
              </a>
            </div>
          `;
          listContainer.appendChild(item);
        }
      });
    })
    .catch(err => console.error('Error loading nearby services:', err));
}

function updateLocation(lat, lon, speed = 0.0) {
  currentCoords = { lat, lon };

  // Move marker and pan map smoothly
  if (userMarker) {
    userMarker.setLatLng([lat, lon]);
  }
  movementHistory.push([lat, lon]);
  if (pathPolyline) {
    pathPolyline.setLatLngs(movementHistory);
  }

  // Send update to CSTAN backend engine
  fetch('/api/update-location', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude: lat, longitude: lon, speed: speed })
  })
    .then(res => res.json())
    .then(data => {
      if (!data.success) return;

      // 1. Update Safety Score Gauge
      const score = data.safety.score;
      const scoreEl = document.getElementById('safetyScoreVal');
      const gaugeEl = document.getElementById('safetyGauge');
      const ratingEl = document.getElementById('safetyRatingText');
      const deductionsEl = document.getElementById('safetyDeductions');

      if (scoreEl) scoreEl.innerText = score;

      if (gaugeEl) {
        gaugeEl.className = 'safety-gauge-circle';
        if (score >= 80) gaugeEl.classList.add('gauge-success');
        else if (score >= 55) gaugeEl.classList.add('gauge-warning');
        else gaugeEl.classList.add('gauge-danger');
      }

      if (ratingEl) {
        ratingEl.innerText = data.safety.rating;
        ratingEl.className = `fw-bold text-${data.safety.badge}`;
      }

      if (deductionsEl) {
        if (data.safety.deductions.length > 0) {
          deductionsEl.innerHTML = data.safety.deductions.map(d => `<li>${d}</li>`).join('');
        } else {
          deductionsEl.innerHTML = '<li class="text-success">All parameters safe and normal</li>';
        }
      }

      // 2. Geofence Alerts Banner
      const banner = document.getElementById('geofenceAlertBanner');
      if (banner) {
        const highestRisk = data.geofence_status.highest_risk;
        const savedLang = localStorage.getItem('cstan_lang') || 'en';

        if (highestRisk === 'restricted') {
          banner.className = 'cstan-alert-box cstan-alert-danger';
          banner.innerHTML = `<strong>⚠️ ${getTranslation('restricted_warning', savedLang)}</strong>`;
          banner.style.display = 'flex';
          playAlertTone();
        } else if (highestRisk === 'caution') {
          banner.className = 'cstan-alert-box cstan-alert-warning';
          banner.innerHTML = `<strong>🔔 ${getTranslation('caution_warning', savedLang)}</strong>`;
          banner.style.display = 'flex';
        } else {
          banner.className = 'cstan-alert-box cstan-alert-success';
          banner.innerHTML = `<strong>✅ ${getTranslation('safe_info', savedLang)}</strong>`;
          banner.style.display = 'flex';
        }
      }

      // 3. Anomaly Banner
      const anomalyBanner = document.getElementById('anomalyAlertBanner');
      if (anomalyBanner) {
        if (data.anomaly && data.anomaly.is_anomaly) {
          anomalyBanner.className = 'cstan-alert-box cstan-alert-warning';
          anomalyBanner.innerHTML = `
            <div>
              <strong>⚠️ Safety Check: Unusual Movement Pattern Detected</strong><br>
              <small>${data.anomaly.reason} (Confidence: ${Math.round(data.anomaly.confidence * 100)}%)</small>
            </div>
          `;
          anomalyBanner.style.display = 'flex';
        } else {
          anomalyBanner.style.display = 'none';
        }
      }

      // Refresh nearby services for new location
      loadNearbyServices(currentCategory);
    })
    .catch(err => console.error('Error updating location:', err));
}

let currentCategory = 'all';

function setupEventListeners() {
  // Service category filters
  document.querySelectorAll('.service-filter-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      document.querySelectorAll('.service-filter-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      currentCategory = e.target.getAttribute('data-cat');
      loadNearbyServices(currentCategory);
    });
  });

  // Language Dropdown
  const langSelect = document.getElementById('langSelect');
  if (langSelect) {
    langSelect.addEventListener('change', e => {
      const selectedLang = e.target.value;
      applyLanguage(selectedLang);
      fetch('/api/set-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: selectedLang })
      });
    });
  }

  // Simulation Toggle
  const simBtn = document.getElementById('btnSimulateRoute');
  if (simBtn) {
    simBtn.addEventListener('click', () => {
      if (!isSimulating) {
        startSimulation();
      } else {
        stopSimulation();
      }
    });
  }

  // Real GPS Toggle
  const gpsBtn = document.getElementById('btnRealGps');
  if (gpsBtn) {
    gpsBtn.addEventListener('click', () => {
      stopSimulation();
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            userMap.setView([lat, lon], 15);
            updateLocation(lat, lon, pos.coords.speed || 0.0);
            alert(`GPS coordinates acquired: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
          },
          err => {
            alert(`Geolocation error: ${err.message}. Using default demonstration location.`);
          }
        );
      } else {
        alert('Geolocation is not supported by your browser.');
      }
    });
  }

  // SOS Form Submission
  const sosConfirmBtn = document.getElementById('btnConfirmSos');
  if (sosConfirmBtn) {
    sosConfirmBtn.addEventListener('click', () => {
      const type = document.getElementById('sosTypeSelect').value;
      const notes = document.getElementById('sosNotesInput').value;

      fetch('/api/sos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: type,
          latitude: currentCoords.lat,
          longitude: currentCoords.lon,
          description: notes || `Emergency SOS triggered near ${currentCoords.lat.toFixed(4)}, ${currentCoords.lon.toFixed(4)}`,
          severity: 'High'
        })
      })
        .then(res => res.json())
        .then(data => {
          // Close modal
          const modalEl = document.getElementById('sosModal');
          const modal = bootstrap.Modal.getInstance(modalEl);
          if (modal) modal.hide();

          // Play alarm & display banner
          playAlertTone();
          showNotification(data.message || 'SOS Dispatched!', 'danger');

          // Trigger immediate location refresh to recalculate score with active SOS
          updateLocation(currentCoords.lat, currentCoords.lon);
        })
        .catch(err => {
          console.error('SOS dispatch error:', err);
          alert('Could not dispatch SOS. Please call emergency services directly.');
        });
    });
  }
}

function startSimulation() {
  isSimulating = true;
  waypointIndex = 0;
  const simBtn = document.getElementById('btnSimulateRoute');
  if (simBtn) {
    simBtn.innerText = '⏹️ Stop Simulation';
    simBtn.classList.replace('btn-outline-warning', 'btn-warning');
  }

  // Center map on path start
  userMap.setView([demoWaypoints[0].lat, demoWaypoints[0].lon], 15);

  simulationInterval = setInterval(() => {
    if (waypointIndex >= demoWaypoints.length) {
      waypointIndex = 0; // loop or finish
    }
    const wp = demoWaypoints[waypointIndex];
    updateLocation(wp.lat, wp.lon, wp.speed);
    userMap.panTo([wp.lat, wp.lon]);
    waypointIndex++;
  }, 3500);
}

function stopSimulation() {
  isSimulating = false;
  clearInterval(simulationInterval);
  const simBtn = document.getElementById('btnSimulateRoute');
  if (simBtn) {
    simBtn.innerText = '🚶 Simulate Walk Route';
    simBtn.classList.replace('btn-warning', 'btn-outline-warning');
  }
}

function playAlertTone() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
    osc.frequency.setValueAtTime(440, ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.4);
  } catch (e) {
    // Audio context may require user interaction
  }
}

function showNotification(msg, type = 'info') {
  const notif = document.createElement('div');
  notif.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-4 shadow-lg`;
  notif.style.zIndex = '9999';
  notif.innerHTML = `<strong>🚨 ${msg}</strong>`;
  document.body.appendChild(notif);
  setTimeout(() => notif.remove(), 4000);
}
