import React from "react";

const CausesReasoning = ({ reasonings }) => {
  if (!reasonings?.causes_reasoning || reasonings.causes_reasoning.length === 0) {
    return null;
  }

  return (
    <div className="reasoning-section">
      <ul className="reasoning-list">
        {(() => {
          const allNoMatches = reasonings.causes_reasoning.every(r => r.startsWith("No match:"));

          if (allNoMatches) {
            //display no matches
            return (
              <li key="no-match" className="reasoning-item">
                <span className="reasoning-icon">‼️</span>
                <span className="reasoning-text">No matches on causes.</span>
              </li>
            );
          }

          //display individual matches
          return reasonings.causes_reasoning.map((reason, index) => {
            let icon = "";
            let textContent = null;

            if (reason.startsWith("Exact match:")) {
              icon = "✅";
              const cause = reason.replace("Exact match: ", "");
              textContent = (
                <>Direct match on causes: you support the cause of <em>{cause}</em> and so does the funder</>
              );
            } else if (reason.startsWith("No match:")) {
              icon = "‼️";
              const cause = reason.replace("No match: ", "");
              textContent = (
                <>No match on your cause: <em>{cause}</em></>
              );
            }

            return (
              <li key={index} className="reasoning-item">
                <span className="reasoning-icon">{icon}</span>
                <span className="reasoning-text">{textContent}</span>
              </li>
            );
          });
        })()}
      </ul>
    </div>
  );
};

export default CausesReasoning;
