/**
 * CSTAN Central Command Admin Map & Dispatch Engine
 */

let adminMap = null;
let adminEmergencyMarkers = {};
let adminUserMarkers = {};
let adminGeofenceLayers = [];

document.addEventListener('DOMContentLoaded', () => {
  initAdminMap();
  loadAdminGeofences();
  loadLiveTelemetry();
  setInterval(loadLiveTelemetry, 4000);
});

function initAdminMap() {
  const mapEl = document.getElementById('adminMap');
  if (!mapEl) return;

  adminMap = L.map('adminMap').setView([13.0827, 80.2707], 13);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 19
  }).addTo(adminMap);
}

function loadAdminGeofences() {
  fetch('/api/geofences')
    .then(res => res.json())
    .then(geofences => {
      adminGeofenceLayers.forEach(l => adminMap.removeLayer(l));
      adminGeofenceLayers = [];

      geofences.forEach(gf => {
        let color = gf.risk_level === 'restricted' ? '#ef4444' : (gf.risk_level === 'caution' ? '#f59e0b' : '#10b981');
        const circle = L.circle([gf.latitude, gf.longitude], {
          color: color,
          fillColor: color,
          fillOpacity: 0.18,
          radius: gf.radius,
          weight: 2
        }).addTo(adminMap);

        circle.bindPopup(`
          <div>
            <strong style="color:${color}; text-transform:uppercase;">${gf.risk_level} ZONE</strong><br>
            <b>${gf.name}</b><br>
            <span>${gf.description || ''}</span><br>
            <small>Radius: ${gf.radius}m</small>
          </div>
        `);
        adminGeofenceLayers.push(circle);
      });
    })
    .catch(err => console.error('Error fetching admin geofences:', err));
}

function loadLiveTelemetry() {
  fetch('/admin/api/live-data')
    .then(res => res.json())
    .then(data => {
      // 1. Update Active Travelers Markers
      const currentUsers = data.users || [];
      const userIdsOnMap = new Set();

      currentUsers.forEach(u => {
        userIdsOnMap.add(u.id);
        const iconHtml = `<div style="background-color: #0284c7; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 8px #0284c7;"></div>`;
        const icon = L.divIcon({ className: 'user-pin', html: iconHtml, iconSize: [16, 16], iconAnchor: [8, 8] });

        if (adminUserMarkers[u.id]) {
          adminUserMarkers[u.id].setLatLng([u.latitude, u.longitude]);
        } else {
          const marker = L.marker([u.latitude, u.longitude], { icon: icon }).addTo(adminMap);
          marker.bindPopup(`
            <div>
              <strong>${u.username}</strong><br>
              <small class="text-primary font-monospace">${u.digital_id}</small><br>
              <span>Phone: ${u.phone || 'N/A'}</span><br>
              <small>Last Active: ${u.last_active}</small>
            </div>
          `);
          adminUserMarkers[u.id] = marker;
        }
      });

      // Remove off-grid users
      Object.keys(adminUserMarkers).forEach(uid => {
        if (!userIdsOnMap.has(parseInt(uid))) {
          adminMap.removeLayer(adminUserMarkers[uid]);
          delete adminUserMarkers[uid];
        }
      });

      // 2. Update Emergency SOS Markers
      const emergencies = data.emergencies || [];
      emergencies.forEach(em => {
        if (em.status === 'RESOLVED') {
          if (adminEmergencyMarkers[em.id]) {
            adminMap.removeLayer(adminEmergencyMarkers[em.id]);
            delete adminEmergencyMarkers[em.id];
          }
          return;
        }

        const sosIcon = L.divIcon({
          className: 'admin-sos-pin',
          html: `<div style="background-color: #ef4444; color: white; border-radius: 50%; width: 28px; height: 28px; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:bold; box-shadow: 0 0 15px #ef4444; border: 2px solid white;">🚨</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });

        if (adminEmergencyMarkers[em.id]) {
          adminEmergencyMarkers[em.id].setLatLng([em.latitude, em.longitude]);
        } else {
          const marker = L.marker([em.latitude, em.longitude], { icon: sosIcon }).addTo(adminMap);
          marker.bindPopup(`
            <div style="font-family:inherit;">
              <strong style="color: #dc2626; font-size:1.1rem;">🚨 SOS ALERT #${em.id}</strong><br>
              <b>User:</b> ${em.username} (${em.digital_id})<br>
              <b>Type:</b> ${em.type}<br>
              <b>Phone:</b> <a href="tel:${em.user_phone}">${em.user_phone}</a><br>
              <b>Contact:</b> ${em.emergency_contact}<br>
              <div style="margin-top: 6px; padding: 4px; background: #fee2e2; border-radius: 4px; font-size: 0.85rem; color:#991b1b;">
                ${em.description}
              </div>
              <div style="margin-top: 6px;">
                <span class="badge bg-danger">${em.status}</span>
              </div>
            </div>
          `);
          adminEmergencyMarkers[em.id] = marker;
        }
      });
    })
    .catch(err => console.error('Error fetching admin live data:', err));
}

function updateSosStatus(emergencyId, newStatus) {
  const notes = prompt(`Enter disposition / response log for status [${newStatus}]:`, `Handled by Central Support Unit at ${new Date().toLocaleTimeString()}`);
  if (notes === null) return;

  fetch('/admin/sos/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      emergency_id: emergencyId,
      status: newStatus,
      admin_notes: notes
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.reload();
      } else {
        alert(data.error || 'Failed to update emergency status.');
      }
    })
    .catch(err => console.error('Error updating SOS:', err));
}

function toggleGeofence(id) {
  fetch(`/admin/geofence/toggle/${id}`, { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.reload();
      }
    });
}
