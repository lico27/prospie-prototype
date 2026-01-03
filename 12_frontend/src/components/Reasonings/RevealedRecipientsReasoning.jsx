import React, { useState } from "react";

const RevealedRecipientsReasoning = ({ reasonings, funderName }) => {
  const score = reasonings?.recipients_rp_score;
  const recipientsReasoning = reasonings?.recipients_rp_reasoning;

  //handle missing data
  if (score === undefined || score === null) {
    return (
      <div className="reasoning-section">
        <ul className="reasoning-list">
          <li className="reasoning-item">
            <span className="reasoning-icon">ℹ️</span>
            <span className="reasoning-text">
              No recipients data available for this funder
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
            This funder has supported organisations that, on average, have a <em>{rating}</em> alignment score with your organisation
          </span>
        </li>
      </ul>
    </div>
  );
};

export default RevealedRecipientsReasoning;
