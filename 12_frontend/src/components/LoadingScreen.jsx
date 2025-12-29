import React from "react";
import "./LoadingScreen.css";

const LoadingScreen = () => {
  return (
    <div className="loading-screen-overlay">
      <div className="loading-screen-content">
        <div className="loading-animation">
          <div className="loading-spinner"></div>
          <div className="loading-ring"></div>
        </div>
        <h2 className="loading-title">Calculating your prospie score!</h2>
        <p className="loading-subtitle">Analysing how well your charity aligns with this funder...</p>
      </div>
    </div>
  );
};

export default LoadingScreen;
