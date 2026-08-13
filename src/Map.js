import React from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Create custom colored markers for Leaflet map using HTML div icons
const createCustomIcon = (isUnauthorized) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div class="marker-pin ${isUnauthorized ? 'unauthorized' : 'cleared'}"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12]
  });
};

const MapComponent = ({ boundaries, hotspots }) => {
  // Default map center (Trichy agricultural region)
  const defaultCenter = [10.75, 78.25];
  const defaultZoom = 12;

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const { field_id, owner, crop_type } = feature.properties;
      layer.bindTooltip(
        `<strong>${field_id}</strong><br/>Owner: ${owner || 'N/A'}<br/>Crop: ${crop_type || 'N/A'}`,
        { sticky: true }
      );
    }
  };

  const geoJsonStyle = {
    fillColor: '#10b981',
    weight: 2,
    opacity: 0.8,
    color: '#34d399',
    fillOpacity: 0.15
  };

  return (
    <div className="map-wrapper">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* Render Field Boundaries GeoJSON */}
        {boundaries && (
          <GeoJSON
            key={JSON.stringify(boundaries)}
            data={boundaries}
            style={geoJsonStyle}
            onEachFeature={onEachFeature}
          />
        )}

        {/* Render Hotspot Markers */}
        {hotspots.map((hotspot, idx) => {
          const position = [hotspot.latitude, hotspot.longitude];
          const isUnauthorized = hotspot.unauthorized;
          const icon = createCustomIcon(isUnauthorized);

          return (
            <Marker key={idx} position={position} icon={icon}>
              <Popup>
                <div className="popup-details">
                  <div className="popup-title">Field: {hotspot.field_id}</div>
                  <div className={`popup-badge ${isUnauthorized ? 'unauthorized' : 'cleared'}`}>
                    {isUnauthorized ? '🔴 Unauthorized Burn' : '🟢 Cleared / Permitted'}
                  </div>
                  <div className="popup-info-row"><strong>Owner:</strong> {hotspot.owner || 'N/A'}</div>
                  <div className="popup-info-row"><strong>Crop:</strong> {hotspot.crop_type || 'N/A'}</div>
                  <div className="popup-info-row"><strong>Date:</strong> {hotspot.acq_date}</div>
                  <div className="popup-info-row"><strong>Confidence:</strong> {hotspot.confidence}</div>
                  <div className="popup-info-row">
                    <strong>Coordinates:</strong> {hotspot.latitude.toFixed(4)}, {hotspot.longitude.toFixed(4)}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default MapComponent;
