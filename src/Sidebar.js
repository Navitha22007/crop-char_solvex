import React from 'react';

const Sidebar = ({ flaggedHotspots, offenderCounts, onTriggerAlert, alertSendingMap, alertStatus }) => {
  const offenderEntries = Object.entries(offenderCounts || {}).sort((a, b) => b[1] - a[1]);

  return (
    <div className="sidebar-container">
      {/* Alert Status Feedback Banner */}
      {alertStatus && (
        <div className={`loading-overlay ${alertStatus.includes('error') ? 'error-banner' : ''}`}>
          {alertStatus}
        </div>
      )}

      {/* Flagged Unauthorized Burns Section */}
      <div className="sidebar-section">
        <div className="section-header">
          <h3 className="section-title">
            <span>🚨</span> Flagged Unauthorized Burns
          </h3>
          <span className="badge-count">{flaggedHotspots.length}</span>
        </div>

        {flaggedHotspots.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '12px 0' }}>
            No unauthorized burns detected.
          </p>
        ) : (
          <div className="flagged-list">
            {flaggedHotspots.map((item, index) => {
              const isSending = alertSendingMap[item.field_id];
              return (
                <div className="flagged-card" key={index}>
                  <div className="card-top">
                    <span className="field-id-tag">Field: {item.field_id}</span>
                    <span className="date-tag">📅 {item.acq_date}</span>
                  </div>
                  <div className="card-meta">
                    <span>🌾 {item.crop_type || 'Crop'}</span>
                    <span>👤 {item.owner || 'Unknown Owner'}</span>
                  </div>
                  <div className="card-meta">
                    <span>Sat Conf: <strong>{item.confidence}</strong></span>
                    <span>Location: [{item.latitude.toFixed(3)}, {item.longitude.toFixed(3)}]</span>
                  </div>
                  <button
                    className="btn-alert"
                    onClick={() => onTriggerAlert(item.field_id, item.acq_date)}
                    disabled={isSending}
                  >
                    {isSending ? 'Sending Alert...' : '📧 Send Email Alert'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Repeat Offenders Section */}
      <div className="sidebar-section">
        <div className="section-header">
          <h3 className="section-title">
            <span>⚠️</span> Repeat Offender Log
          </h3>
          <span className="badge-count">{offenderEntries.length}</span>
        </div>

        {offenderEntries.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '12px 0' }}>
            No repeat offenders logged yet.
          </p>
        ) : (
          <div className="offender-list">
            {offenderEntries.map(([fieldId, count]) => (
              <div className="offender-card" key={fieldId}>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '14px' }}>{fieldId}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Violations Recorded</div>
                </div>
                <div className="offender-count-badge">
                  {count} {count === 1 ? 'time' : 'times'}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
