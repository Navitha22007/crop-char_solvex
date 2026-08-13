
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import MapComponent from './Map';
import Sidebar from './Sidebar';
import StatsPanel from './StatsPanel';

// Client-side emergency fallback data if backend is offline
const CLIENT_FALLBACK_HOTSPOTS = [
  {
    field_id: "field_01",
    owner: "Ramesh Kumar",
    crop_type: "Paddy",
    latitude: 10.750,
    longitude: 78.240,
    acq_date: "2026-11-02",
    confidence: "high",
    unauthorized: true
  },
  {
    field_id: "field_02",
    owner: "Suresh Patel",
    crop_type: "Wheat",
    latitude: 10.770,
    longitude: 78.240,
    acq_date: "2026-11-03",
    confidence: "95",
    unauthorized: false
  },
  {
    field_id: "field_03",
    owner: "Anitha Reddy",
    crop_type: "Sugarcane",
    latitude: 10.745,
    longitude: 78.255,
    acq_date: "2026-11-04",
    confidence: "nominal",
    unauthorized: true
  },
  {
    field_id: "field_04",
    owner: "Vikram Singh",
    crop_type: "Maize",
    latitude: 10.765,
    longitude: 78.265,
    acq_date: "2026-11-05",
    confidence: "high",
    unauthorized: false
  },
  {
    field_id: "field_05",
    owner: "Kavitha Sharma",
    crop_type: "Cotton",
    latitude: 10.730,
    longitude: 78.250,
    acq_date: "2026-11-06",
    confidence: "88",
    unauthorized: true
  }
];

const CLIENT_FALLBACK_OFFENDERS = {
  field_01: 2,
  field_03: 1,
  field_05: 1
};

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [hotspots, setHotspots] = useState([]);
  const [boundaries, setBoundaries] = useState(null);
  const [source, setSource] = useState('loading');
  const [offenderCounts, setOffenderCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [alertSendingMap, setAlertSendingMap] = useState({});
  const [alertStatus, setAlertStatus] = useState(null);

  // Fetch field boundaries GeoJSON
  useEffect(() => {
    fetch('/sample_boundaries.geojson')
      .then((res) => res.json())
      .then((data) => setBoundaries(data))
      .catch((err) => console.error('Failed to load local boundary GeoJSON:', err));
  }, []);

  // Fetch hotspots & statistics from backend API
  const fetchData = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/hotspots`, { timeout: 12000 });
      if (response.data) {
        setHotspots(response.data.hotspots || []);
        setSource(response.data.source || 'live');
        setOffenderCounts(response.data.offender_counts || {});
      }
    } catch (err) {
      console.warn('Backend API request failed. Using client fallback data:', err);
      setErrorMsg('Backend unavailable — showing fallback demo dataset.');
      setHotspots(CLIENT_FALLBACK_HOTSPOTS);
      setOffenderCounts(CLIENT_FALLBACK_OFFENDERS);
      setSource('client-fallback');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle email alert dispatch
  const handleTriggerAlert = async (fieldId, acqDate) => {
    setAlertSendingMap((prev) => ({ ...prev, [fieldId]: true }));
    setAlertStatus(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/alerts/trigger`, {
        field_id: fieldId,
        acq_date: acqDate
      });

      if (response.data.status === 'sent') {
        setAlertStatus(`✅ Alert sent successfully to ${response.data.recipient}`);
      } else if (response.data.status === 'simulated') {
        setAlertStatus(`ℹ️ ${response.data.message}`);
      } else {
        setAlertStatus(`⚠️ ${response.data.message || 'Alert failed'}`);
      }
    } catch (err) {
      console.error('Alert trigger error:', err);
      setAlertStatus('⚠️ Failed to connect to alert service.');
    } finally {
      setAlertSendingMap((prev) => ({ ...prev, [fieldId]: false }));
      // Clear status after 5 seconds
      setTimeout(() => setAlertStatus(null), 5000);
    }
  };

  // Calculate statistics
  const totalHotspots = hotspots.length;
  const flaggedHotspots = hotspots.filter((h) => h.unauthorized);
  const clearedHotspots = hotspots.filter((h) => !h.unauthorized);
  const repeatOffendersCount = Object.keys(offenderCounts).length;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="logo-badge">🔥</div>
          <div>
            <h1 className="brand-title">CropChar</h1>
            <p className="brand-subtitle">Crop-Residue Burn & Permit Compliance Platform</p>
          </div>
        </div>

        <div className="header-status">
          <div className={`source-badge ${source === 'live' ? 'live' : 'fallback'}`}>
            <span className="pulse-dot"></span>
            Data Source: {source.toUpperCase()}
          </div>
          <button className="btn-refresh" onClick={fetchData} disabled={loading}>
            🔄 {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </header>

      {/* Main Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Top Summary Statistics */}
        <StatsPanel
          totalCount={totalHotspots}
          unauthorizedCount={flaggedHotspots.length}
          clearedCount={clearedHotspots.length}
          offendersCount={repeatOffendersCount}
        />

        {/* Map View */}
        <main className="map-wrapper">
          {errorMsg && (
            <div style={{ position: 'absolute', top: 16, left: 60, zIndex: 1000, display: 'flex', alignItems: 'center', gap: 10 }} className="error-banner">
              <span>⚠️ {errorMsg}</span>
              <button 
                onClick={() => setErrorMsg(null)}
                style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', fontWeight: 'bold' }}
              >
                ✕
              </button>
            </div>
          )}
          {loading && (
            <div style={{ position: 'absolute', top: 16, left: 60, zIndex: 1000 }} className="loading-overlay">
              ⌛ Loading hotspot data from pipeline...
            </div>
          )}
          <MapComponent boundaries={boundaries} hotspots={hotspots} />
        </main>

        {/* Right Sidebar */}
        <aside style={{ gridRow: '2', gridColumn: '2' }}>
          <Sidebar
            flaggedHotspots={flaggedHotspots}
            offenderCounts={offenderCounts}
            onTriggerAlert={handleTriggerAlert}
            alertSendingMap={alertSendingMap}
            alertStatus={alertStatus}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
