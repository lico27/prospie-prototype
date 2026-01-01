import React from "react";
import "./ResultScreen.css";
import AreasReasoning from "./Reasonings/AreasReasoning";
import BeneficiariesReasoning from "./Reasonings/BeneficiariesReasoning";
import CausesReasoning from "./Reasonings/CausesReasoning";
import ReasoningDropdown from "./ReasoningDropdown";

const toTitleCase = (str) => {
  if (!str) return "";
  return str
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const ResultScreen = ({ score, reasonings, userName, funderName, onReset }) => {
  return (
    <div className="result-screen-overlay">
      <div className="result-screen-content">
        <div className="result-card">
          <div className="result-score-container">
            <h2 className="result-label">Your <span className="prospie-highlight">prospie</span> score is...</h2>
            <div className="result-score">
              {(score * 100).toFixed(1)}%
            </div>

            {userName && funderName && (
              <p className="result-match-caption">
                This score represents <span className="match-name">{toTitleCase(userName)}'s</span> alignment with <span className="match-name">{toTitleCase(funderName)}.</span>
              </p>
            )}
          </div>

          {(reasonings?.existing_relationship || reasonings?.is_on_list || reasonings?.is_nua || reasonings?.is_sbf) && (
            <>
              <hr className="result-section-break" />

              <div className="points-to-note-container">
                <div className="question-heading">
                  <span className="question-heading-text">Points to note</span>
                </div>

                {reasonings?.existing_relationship && (
                  <div className="message-box benefit">
                    <span className="message-icon">✅</span>
                    <p className="message-text">
                      This funder has given your organisation a grant before! According to the available data, your last gift was in {reasonings?.last_grant_year || 'an unknown year'}.
                    </p>
                  </div>
                )}

                {reasonings?.is_on_list && (
                  <div className="message-box flag">
                    <span className="message-icon">✴️</span>
                    <p className="message-text">
                      This funder appears on <a href="https://the-list.uk" target="_blank" rel="noopener noreferrer">The List</a>
                      {reasonings?.list_reasoning && reasonings.list_reasoning.length > 0 && (
                        <>, in the {reasonings.list_reasoning.length > 1 ? 'categories' : 'category'} "{reasonings.list_reasoning.join('", "')}"</>
                      )}. This suggests that they might currently be reviewing their giving strategy, not accepting applications, or winding down. It is important to research their current status before applying.
                    </p>
                  </div>
                )}

                {reasonings?.is_nua && (
                  <div className="message-box warning">
                    <span className="message-icon">‼️</span>
                    <p className="message-text">
                      This funder has potentially indicated that they do not accept unsolicited applications. Your score has been reduced to reflect this, and it is important to be cautious about applying to this funder.
                    </p>
                  </div>
                )}

                {reasonings?.is_sbf && (
                  <div className="message-box warning">
                    <span className="message-icon">‼️</span>
                    <p className="message-text">
                      This could be a single-beneficiary funder. Data suggests that they may only support one cause (e.g a school, a hospital, or a church). Your score has been reduced to reflect this, and it is important to be cautious about applying to this funder.
                    </p>
                  </div>
                )}
              </div>
            </>
          )}

          <hr className="result-section-break" />

          <div className="result-reasonings">
            <ReasoningDropdown
              heading="Explanation for your score"
              title="Classifications"
              description="how your stated areas, beneficiaries and causes match with the funder's"
              defaultOpen={false}
            >
              <AreasReasoning reasonings={reasonings} />
              <BeneficiariesReasoning reasonings={reasonings} />
              <CausesReasoning reasonings={reasonings} />
            </ReasoningDropdown>
          </div>

        {/* <div className="result-reasonings-placeholder">
            <pre style={{ textAlign: "left", fontSize: "0.75rem", color: "#c9c0de", overflow: "auto", maxHeight: "400px" }}>
              {JSON.stringify(reasonings, null, 2)}
            </pre>
          </div> */}

          <button className="reset-button" onClick={onReset}>
            Start Again
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultScreen;
