import React from "react";
import ReasoningDropdown from "../ReasoningDropdown";
import "../../css/components/Reasonings/RevealedKeywordsReasoning.css";

const RevealedKeywordsReasoning = ({ reasonings }) => {
  const bonus = reasonings?.keywords_rp_bonus;
  const keywordsReasoning = reasonings?.keywords_rp_reasoning;

  //handle missing data
  if (bonus === undefined || bonus === null) {
    return (
      <div className="reasoning-section">
        <ul className="reasoning-list">
          <li className="reasoning-item">
            <span className="reasoning-icon">ℹ️</span>
            <span className="reasoning-text">
              No revealed keyword data available for this funder
            </span>
          </li>
        </ul>
      </div>
    );
  }

  //assign rating based on bonus ranges
  let rating = "";
  let icon = "";

  if (bonus >= 1.1) {
    rating = "excellent";
    icon = "✅";
  } else if (bonus >= 1.05) {
    rating = "good";
    icon = "✴️";
  } else if (bonus >= 1.02) {
    rating = "fair";
    icon = "✴️";
  } else {
    rating = "poor";
    icon = "‼️";
  }

  return (
    <div className="reasoning-section">
      <ul className="reasoning-list">
        <li className="reasoning-item">
          <span className="reasoning-icon">{icon}</span>
          <span className="reasoning-text">
            This funder has a <em>{rating}</em> track record of funding recipients with similar keywords
          </span>
        </li>
      </ul>

      {keywordsReasoning && keywordsReasoning.length > 0 && (
        <div className="reasoning-dropdown-wrapper">
          <ReasoningDropdown
            title="Keyword matches"
            description="keywords found in recipients this funder has supported"
            defaultOpen={false}
          >
            <ul className="reasoning-list">
              {keywordsReasoning.map((item, index) => (
                <li key={index} className="reasoning-item">
                  <span className="reasoning-text">{item}</span>
                </li>
              ))}
            </ul>
          </ReasoningDropdown>
        </div>
      )}
    </div>
  );
};

export default RevealedKeywordsReasoning;
