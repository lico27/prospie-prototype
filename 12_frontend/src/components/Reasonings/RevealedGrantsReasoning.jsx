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

const GrantItem = ({ grant, funderName }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const descriptionPreviewLength = 150;

  const recipientName = toTitleCase(grant.recipient_name || "an unknown recipient");
  const grantTitle = toTitleCase(grant.grant_title || "Untitled grant");
  const grantDesc = grant.grant_desc ? toSentenceCase(grant.grant_desc) : "";
  const year = grant.year || "an unknown year";
  const amount = formatCurrency(grant.amount);
  const funder = toTitleCase(funderName || "This funder");

  const needsPreview = grantDesc.length > descriptionPreviewLength;
  const displayDesc = needsPreview && !isExpanded
    ? grantDesc.substring(0, descriptionPreviewLength) + "..."
    : grantDesc;

  const getMatchRating = (score) => {
    if (score >= 0.7) return "strong";
    if (score >= 0.55) return "good";
    if (score >= 0.4) return "moderate";
    return "weak";
  };

  return (
    <div className="grant-item">
      <div className="grant-item-header">
        <strong>{funder}</strong> gave <strong>{amount}</strong> to <strong>{recipientName}</strong> in <strong>{year}</strong>
      </div>
      <div className="grant-item-title">
        {grantTitle}
      </div>
      {grantDesc && (
        <div className="grant-item-description">
          {displayDesc}
          {needsPreview && (
            <span
              onClick={() => setIsExpanded(!isExpanded)}
              className="grant-item-read-more"
            >
              {isExpanded ? "Show less" : "Read more"}
            </span>
          )}
        </div>
      )}
      <div className="grant-item-score">
        Match score: <em>{getMatchRating(grant.similarity)}</em>
      </div>
    </div>
  );
};

const RevealedGrantsReasoning = ({ reasonings, funderName }) => {
  const score = reasonings?.grants_rp_score;
  const grantsReasoning = reasonings?.grants_rp_reasoning;

  //handle missing data
  if (score === undefined || score === null || score === 0) {
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
            This funder has given grants that, on average, have a <em>{rating}</em> alignment score with your organisation
          </span>
        </li>
      </ul>

      {grantsReasoning && grantsReasoning.length > 0 && (
        <div className="reasoning-dropdown-wrapper">
          <ReasoningDropdown
            title="Top matches"
            description="funder's grant-making history"
            defaultOpen={false}
          >
            <div>
              {grantsReasoning.map((grant, index) => (
                <GrantItem
                  key={grant.grant_id || index}
                  grant={grant}
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

export default RevealedGrantsReasoning;
