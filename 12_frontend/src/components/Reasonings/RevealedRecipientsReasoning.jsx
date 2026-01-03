import React, { useState } from "react";
import ReasoningDropdown from "../ReasoningDropdown";
import "../../css/components/Reasonings/RevealedGrantsReasoning.css";

const toTitleCase = (str) => {
  if (!str) return "";
  return str
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const toSentenceCase = (str) => {
  if (!str) return "";
  const lower = str.toLowerCase();
  return lower.replace(/(^\w|[.!?]\s+\w)/g, match => match.toUpperCase());
};

const formatCurrency = (amount) => {
  if (!amount) return "an undisclosed amount";
  return `£${amount.toLocaleString()}`;
};

const RecipientItem = ({ recipient, funderName }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const activitiesPreviewLength = 150;

  const recipientName = toTitleCase(recipient.recipient_name || "an unknown recipient");
  const year = recipient.year || "an unknown year";
  const amount = formatCurrency(recipient.amount);
  const funder = toTitleCase(funderName || "This funder");
  const activities = recipient.recipient_activities ? toSentenceCase(recipient.recipient_activities) : "";

  const needsPreview = activities.length > activitiesPreviewLength;
  const displayActivities = needsPreview && !isExpanded
    ? activities.substring(0, activitiesPreviewLength) + "..."
    : activities;

  const getMatchRating = (similarity) => {
    if (similarity >= 0.7) return "strong";
    if (similarity >= 0.55) return "good";
    if (similarity >= 0.4) return "moderate";
    return "weak";
  };

  return (
    <div className="grant-item">
      <div className="grant-item-header">
        <strong>{funder}</strong> gave <strong>{amount}</strong> to <strong>{recipientName}</strong> in <strong>{year}</strong>
      </div>
      {activities && (
        <div className="grant-item-description">
          {displayActivities}
          {needsPreview && (
            <span
              className="grant-item-read-more"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? "Show less" : "Read more"}
            </span>
          )}
        </div>
      )}
      <div className="grant-item-score">
        Match score: <em>{getMatchRating(recipient.similarity)}</em>
      </div>
    </div>
  );
};

const RevealedRecipientsReasoning = ({ reasonings, funderName }) => {
  const recipientsScore = reasonings?.recipients_rp_score;
  const nameScore = reasonings?.name_rp_score;
  const recipientsReasoning = reasonings?.recipients_rp_reasoning || [];
  const nameReasoning = reasonings?.name_rp_reasoning || [];

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

  //combine both reasoning arrays and sort by similarity
  const allRecipients = [...recipientsReasoning, ...nameReasoning];
  const top10Recipients = allRecipients
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, 10);

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

      {top10Recipients.length > 0 && (
        <div className="reasoning-dropdown-wrapper">
          <ReasoningDropdown
            title="Top matches"
            description="funder's recipient history"
            defaultOpen={false}
          >
            <div>
              {top10Recipients.map((recipient, index) => (
                <RecipientItem
                  key={index}
                  recipient={recipient}
                  funderName={funderName}
                />
              ))}
            </div>
          </ReasoningDropdown>
        </div>
      )}
    </div>
  );
};

export default RevealedRecipientsReasoning;
