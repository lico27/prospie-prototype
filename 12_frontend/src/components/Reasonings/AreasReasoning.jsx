import React from "react";

const AreasReasoning = ({ reasonings, userAreas, funderAreas }) => {
  
  //handle missing areas
  if (!reasonings?.areas_reasoning || reasonings.areas_reasoning.length === 0) {
    const hasUserAreas = userAreas && userAreas.length > 0;
    const hasFunderAreas = funderAreas && funderAreas.length > 0;
    return (
      <div className="reasoning-section">
        <ul className="reasoning-list">
          <li className="reasoning-item">
            <span className="reasoning-icon">‼️</span>
            <span className="reasoning-text">
              {!hasUserAreas && !hasFunderAreas && "No matches on areas: neither you nor the funder stated where you work"}
              {!hasUserAreas && hasFunderAreas && "No matches on areas: you did not state where you work"}
              {hasUserAreas && !hasFunderAreas && "No matches on areas: the funder did not state where they work"}
            </span>
          </li>
        </ul>
      </div>
    );
  }

  return (
    <div className="reasoning-section">
      <ul className="reasoning-list">
        {(() => {
          const hasMatches = reasonings.areas_reasoning.some(
            r => r.startsWith("Exact match:") || r.startsWith("Hierarchical match:")
          );

          const allNoMatches = reasonings.areas_reasoning.every(r => r.startsWith("No match:"));

          if (allNoMatches) {
            //display no matches
            return (
              <li key="no-match" className="reasoning-item">
                <span className="reasoning-icon">‼️</span>
                <span className="reasoning-text">No matches on areas.</span>
              </li>
            );
          }

          //display individual matches
          return reasonings.areas_reasoning.map((reason, index) => {
            let icon = "";
            let textContent = null;

            if (reason.startsWith("Exact match:")) {
              icon = "✅";
              const area = reason.replace("Exact match: ", "");
              textContent = (
                <>Direct match on areas: you work in <em>{area}</em> and so does the funder</>
              );
            } else if (reason.startsWith("Hierarchical match:")) {
              icon = "✴️";
              const match = reason.match(/Hierarchical match: (.*?) \(user\) within (.*?) \(funder\)|Hierarchical match: (.*?) \(funder\) within (.*?) \(user\)/);
              if (match) {
                if (match[1] && match[2]) {
                  textContent = (
                    <>Partial match on areas: you work in <em>{match[1]}</em> which is within the funder's area of <em>{match[2]}</em></>
                  );
                } else if (match[3] && match[4]) {
                  textContent = (
                    <>Partial match on areas: the funder works in <em>{match[3]}</em> which is within your area of <em>{match[4]}</em></>
                  );
                }
              }
            } else if (reason.startsWith("No match:")) {
              icon = "‼️";
              const area = reason.replace("No match: ", "");
              textContent = (
                <>No match on your area: <em>{area}</em></>
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

export default AreasReasoning;
