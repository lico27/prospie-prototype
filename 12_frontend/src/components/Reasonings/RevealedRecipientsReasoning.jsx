import React, { useState } from "react";

const RevealedRecipientsReasoning = ({ reasonings, funderName }) => {
  const recipientsScore = reasonings?.recipients_rp_score;
  const nameScore = reasonings?.name_rp_score;
  const recipientsReasoning = reasonings?.recipients_rp_reasoning;

  //calculate average of available scores
  let score = null;
  const validScores = [];

  if (recipientsScore !== undefined && recipientsScore !== null) {
    validScores.push(recipientsScore);
  }
  if (nameScore !== undefined && nameScore !== null) {
    validScores.push(nameScore);
  }

  if (validScores.length > 0) {
    score = validScores.reduce((a, b) => a + b, 0) / validScores.length;
  }

  //handle missing data
  if (score === null || score === 0) {
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
