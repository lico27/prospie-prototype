import React from "react";
import "./ResultScreen.css";

const ResultScreen = ({ score, reasonings, onReset }) => {
  return (
    <div className="result-screen-overlay">
      <div className="result-screen-content">
        <div className="result-card">
          <h2 className="result-label">Your <span className="prospie-highlight">prospie</span> score is...</h2>
          <div className="result-score">
            {(score * 100).toFixed(1)}%
          </div>

          <div className="result-reasonings-placeholder">
            <p className="reasonings-label">Detailed Reasoning</p>
            <pre style={{ textAlign: 'left', fontSize: '0.75rem', color: '#c9c0de', overflow: 'auto', maxHeight: '400px' }}>
              {JSON.stringify(reasonings, null, 2)}
            </pre>
          </div>

          <div className="reasoning-cards">
            <div className="reasoning-card positive">
              <div className="card-header">
                <span className="card-icon">✓</span>
                <h3 className="card-title">Positive Factors</h3>
              </div>
              <div className="card-content">
                <p>Placeholder content for positive factors...</p>
              </div>
            </div>

            <div className="reasoning-card neutral">
              <div className="card-header">
                <span className="card-icon">−</span>
                <h3 className="card-title">Neutral Factors</h3>
              </div>
              <div className="card-content">
                <p>Placeholder content for neutral factors...</p>
              </div>
            </div>

            <div className="reasoning-card negative">
              <div className="card-header">
                <span className="card-icon">✕</span>
                <h3 className="card-title">Negative Factors</h3>
              </div>
              <div className="card-content">
                <p>Placeholder content for negative factors...</p>
              </div>
            </div>
          </div>

          <button className="reset-button" onClick={onReset}>
            Start Again
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultScreen;
