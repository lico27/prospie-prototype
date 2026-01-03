import React, { useState } from "react";

const StatedKeywordsReasoning = ({ reasonings }) => {
  const score = reasonings?.keyword_similarity_score;
  const keywordReasoning = reasonings?.keyword_reasoning;
  const keywordStrongMatches = reasonings?.keyword_strong_matches;
  const [isOpen, setIsOpen] = useState(false);

  if (score === undefined || score === null) {
    return null;
  }

  //helper function to convert score to rating word
  const getMatchRating = (matchScore) => {
    if (matchScore >= 0.9999) {
      return "perfect";
    } else if (matchScore >= 0.7) {
      return "strong";
    } else if (matchScore >= 0.55) {
      return "good";
    } else if (matchScore >= 0.4) {
      return "moderate";
    } else {
      return "weak";
    }
  };

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
            The keywords you provided are a <em>{rating}</em> match to the keywords extracted from the funder's stated priorities
          </span>
        </li>
      </ul>

      {((keywordStrongMatches && Object.keys(keywordStrongMatches).length > 0) || (keywordReasoning && keywordReasoning.length > 0)) && (
        <div className="reasoning-dropdown-wrapper">
          <div className="reasoning-toggle" onClick={() => setIsOpen(!isOpen)}>
            <span className="reasoning-toggle-icon">{isOpen ? "▼" : "▶"}</span>
            <div className="reasoning-toggle-content">
              <span className="reasoning-toggle-title">
                Top matches: <span style={{ color: "#f97316" }}>funder's keywords</span> and <span style={{ color: "#9b87f5" }}>your keywords</span>
              </span>
            </div>
          </div>

          {isOpen && (
            <div className="reasoning-content">
              <ul className="reasoning-list">
                {(() => {
                  //combine reasonings and process for display
                  const allReasoning = [];
                  if (keywordStrongMatches) {
                    Object.entries(keywordStrongMatches).forEach(([matchPair, matchScore]) => {
                      const formattedPair = matchPair.replace(" & ", " ↔ ");
                      allReasoning.push({
                        text: formattedPair,
                        score: matchScore,
                        rating: getMatchRating(matchScore)
                      });
                    });
                  }
                  if (keywordReasoning) {
                    keywordReasoning.forEach((match) => {
                      const scoreMatch = match.match(/:\s*([\d.]+)$/);
                      if (scoreMatch) {
                        const numericScore = parseFloat(scoreMatch[1]);
                        let textWithoutScore = match.substring(0, match.lastIndexOf(":"));
                        textWithoutScore = textWithoutScore.replace(/'/g, "").replace(" & ", " ↔ ");
                        allReasoning.push({
                          text: textWithoutScore,
                          score: numericScore,
                          rating: getMatchRating(numericScore)
                        });
                      }
                    });
                  }

                  //get top 5
                  const topMatches = allReasoning
                    .sort((a, b) => b.score - a.score)
                    .slice(0, 5);

                  return topMatches.map((match, index) => {
                    const [funderKeyword, userKeyword] = match.text.split(" ↔ ");
                    return (
                      <li key={index} className="reasoning-item" style={{ fontSize: "0.85rem", padding: "0.1rem 0 0 0.1rem" }}>
                        <span className="reasoning-text">
                          "<span style={{ color: "#f97316" }}>{funderKeyword}</span>"
                          {" ↔ "}
                          "<span style={{ color: "#9b87f5" }}>{userKeyword}</span>"
                          : <em>{match.rating}</em>
                        </span>
                      </li>
                    );
                  });
                })()}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StatedKeywordsReasoning;
