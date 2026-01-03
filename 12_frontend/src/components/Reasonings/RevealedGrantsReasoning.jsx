import React from "react";

const RevealedGrantsReasoning = ({ reasonings }) => {
  const score = reasonings?.grants_rp_score;

  //handle missing data
  if (score === undefined || score === null) {
    return (
      <div className="reasoning-section">
        <ul className="reasoning-list">
          <li className="reasoning-item">
            <span className="reasoning-icon">ℹ️</span>
            <span className="reasoning-text">
              No grants data available for this funder
            </span>
          </li>
        </ul>
      </div>
    );
  }

  //assign rating based on score ranges
  let rating = "";
  let icon = "";

  if (score >= 0.7) {
    rating = "strong";
    icon = "✅";
  } else if (score >= 0.55) {
    rating = "good";
    icon = "✅";
  } else if (score >= 0.4) {
    rating = "moderate";
    icon = "✴️";
  } else {
    rating = "weak";
    icon = "‼️";
  }

  return (
    <div className="reasoning-section">
      <ul className="reasoning-list">
        <li className="reasoning-item">
          <span className="reasoning-icon">{icon}</span>
          <span className="reasoning-text">
            This funder has supported projects that are overall a <em>{rating}</em> match to yours
          </span>
        </li>
      </ul>
    </div>
  );
};

export default RevealedGrantsReasoning;
