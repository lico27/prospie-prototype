import React from "react";
import ReasoningDropdown from "../ReasoningDropdown";
import "../../css/components/Reasonings/RevealedAreasReasoning.css";

const RevealedAreasReasoning = ({ reasonings, userAreas }) => {
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

  //confirm data missing not poor match
  const noDataMessages = ["No grants history available", "No area data available", "Only broad geographic areas found"];
  const hasNoData = areasReasoning && areasReasoning.length > 0 &&
                    areasReasoning.some(msg => noDataMessages.includes(msg));

  if (hasNoData) {
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

      {areasReasoning && areasReasoning.length > 0 && (() => {
        //parse area names and filter matches
        const allAreas = areasReasoning;
        const matchedAreas = userAreas
          ? allAreas.filter(item => {
              const areaName = item.split(':')[0].trim();
              return userAreas.some(userArea =>
                userArea.toLowerCase() === areaName.toLowerCase()
              );
            })
          : [];

        return (
          <div className="reasoning-dropdown-wrapper">
            <ReasoningDropdown
              title="Geographic breakdown"
              description="where the funder has given grants"
              defaultOpen={false}
            >
              <div className="areas-columns">
                <div className="areas-column">
                  <h4 className="areas-column-title">Top 10 funded areas</h4>
                  <ul className="reasoning-list">
                    {allAreas.slice(0, 10).map((item, index) => (
                      <li key={index} className="reasoning-item">
                        <span className="reasoning-text">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="areas-column">
                  <h4 className="areas-column-title">Matches with your areas</h4>
                  {matchedAreas.length > 0 ? (
                    <ul className="reasoning-list">
                      {matchedAreas.map((item, index) => (
                        <li key={index} className="reasoning-item">
                          <span className="reasoning-text">{item}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="no-matches">No exact area matches found</p>
                  )}
                </div>
              </div>
            </ReasoningDropdown>
          </div>
        );
      })()}
    </div>
  );
};

export default RevealedAreasReasoning;
