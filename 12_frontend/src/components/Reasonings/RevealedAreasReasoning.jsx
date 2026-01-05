import React from "react";
import ReasoningDropdown from "../ReasoningDropdown";

const RevealedAreasReasoning = ({ reasonings }) => {
  const bonus = reasonings?.areas_rp_bonus;
  const areasReasoning = reasonings?.areas_rp_reasoning;

  //handle missing data
  if (bonus === undefined || bonus === null) {
    return (
      <div className="reasoning-section">
        <ul className="reasoning-list">
          <li className="reasoning-item">
            <span className="reasoning-icon">ℹ️</span>
            <span className="reasoning-text">
              No revealed geographic area data available for this funder
            </span>
          </li>
        </ul>
      </div>
    );
  }

  //assign rating based on bonus ranges
  let rating = "";
  let icon = "";

  if (bonus >= 1.15) {
    rating = "excellent";
    icon = "✅";
  } else if (bonus >= 1.1) {
    rating = "good";
    icon = "✴️";
  } else if (bonus >= 1.05) {
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
            This funder has a <em>{rating}</em> track record of funding in your geographic areas
          </span>
        </li>
      </ul>

      {areasReasoning && areasReasoning.length > 0 && (
        <div className="reasoning-dropdown-wrapper">
          <ReasoningDropdown
            title="Geographic breakdown"
            description="where the funder has given grants (number and % of total)"
            defaultOpen={false}
          >
            <div>
              <ul className="reasoning-list">
                {areasReasoning.map((item, index) => (
                  <li key={index} className="reasoning-item">
                    <span className="reasoning-text">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </ReasoningDropdown>
        </div>
      )}
    </div>
  );
};

export default RevealedAreasReasoning;
