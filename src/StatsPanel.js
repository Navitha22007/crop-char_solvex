import React from 'react';

const StatsPanel = ({ totalCount, unauthorizedCount, clearedCount, offendersCount }) => {
  return (
    <div className="stats-container">
      <div className="stat-card">
        <div className="stat-icon-wrapper total">🔥</div>
        <div className="stat-details">
          <span className="stat-value">{totalCount}</span>
          <span className="stat-label">Total Hotspots Detected</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon-wrapper flagged">🔴</div>
        <div className="stat-details">
          <span className="stat-value">{unauthorizedCount}</span>
          <span className="stat-label">Flagged Unauthorized</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon-wrapper cleared">🟢</div>
        <div className="stat-details">
          <span className="stat-value">{clearedCount}</span>
          <span className="stat-label">Cleared / Permitted</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon-wrapper offenders">⚠️</div>
        <div className="stat-details">
          <span className="stat-value">{offendersCount}</span>
          <span className="stat-label">Repeat Offending Fields</span>
        </div>
      </div>
    </div>
  );
};

export default StatsPanel;
