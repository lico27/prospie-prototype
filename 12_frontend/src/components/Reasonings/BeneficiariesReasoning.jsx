import React from "react";

const BeneficiariesReasoning = ({ reasonings, userBeneficiaries, funderBeneficiaries }) => {
  //handle missing beneficiaries
  if (!reasonings?.beneficiaries_reasoning || reasonings.beneficiaries_reasoning.length === 0) {
    const hasUserBeneficiaries = userBeneficiaries && userBeneficiaries.length > 0;
    const hasFunderBeneficiaries = funderBeneficiaries && funderBeneficiaries.length > 0;
    return (
      <div className="reasoning-section">
        <ul className="reasoning-list">
          <li className="reasoning-item">
            <span className="reasoning-icon">‼️</span>
            <span className="reasoning-text">
              {!hasUserBeneficiaries && !hasFunderBeneficiaries && "No matches on beneficiaries: neither you nor the funder stated who you support"}
              {!hasUserBeneficiaries && hasFunderBeneficiaries && "No matches on beneficiaries: you did not state who you support"}
              {hasUserBeneficiaries && !hasFunderBeneficiaries && "No matches on beneficiaries: the funder did not state who they support"}
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
          const allNoMatches = reasonings.beneficiaries_reasoning.every(r => r.startsWith("No match:"));

          if (allNoMatches) {
            //display no matches
            return (
              <li key="no-match" className="reasoning-item">
                <span className="reasoning-icon">‼️</span>
                <span className="reasoning-text">No matches on beneficiaries.</span>
              </li>
            );
          }

          //display individual matches
          return reasonings.beneficiaries_reasoning.map((reason, index) => {
            let icon = "";
            let textContent = null;

            if (reason.startsWith("Exact match:")) {
              icon = "✅";
              const beneficiary = reason.replace("Exact match: ", "");
              textContent = (
                <>Direct match on beneficiaries: you support <em>{beneficiary}</em> and so does the funder</>
              );
            } else if (reason.startsWith("Weak match:")) {
              icon = "✴️";
              const match = reason.match(/Weak match: user states '(.*?)' and funder supports broad categories/);
              if (match) {
                const beneficiary = match[1];
                textContent = (
                  <>Weak match on beneficiaries: you support <em>{beneficiary}</em> and the funder supports broad beneficiary categories</>
                );
              }
            } else if (reason.startsWith("No match:")) {
              icon = "‼️";
              const beneficiary = reason.replace("No match: ", "");
              textContent = (
                <>No match on your beneficiary: <em>{beneficiary}</em></>
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

export default BeneficiariesReasoning;
