import React from "react";

const StatedSemanticReasoning = ({ reasonings }) => {
  const score = reasonings?.text_similarity_score;
  if (score === undefined || score === null) {
    return null;
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
            Your Activities and Objectives narratives are a <em>{rating}</em> match to the funder's stated priorities
          </span>
        </li>
      </ul>
    </div>
  );
};

export default StatedSemanticReasoning;
