import React from "react";
import "./ResultScreen.css";

const ResultScreen = ({ score, onReset }) => {
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
            <p className="reasonings-coming-soon">Coming soon...</p>
          </div>

          <button className="reset-button" onClick={onReset}>
            Start Again!
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultScreen;
