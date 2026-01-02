function ProgressIndicator({ currentStep, totalSteps = 4, onStepClick, confirmedSteps = [] }) {
  const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100

  const stepLabels = [
    "Charity Number",
    "Check Details",
    "Areas",
    "Beneficiaries",
    "Causes",
    "Activities & Objectives",
    "Keywords",
    "Funder Number"
  ]

  return (
    <div className="progress-container">
      <div className="progress-bar-wrapper">
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
        <div className="progress-labels">
          {[...Array(totalSteps)].map((_, index) => {
            const step = index + 1
            const isConfirmed = confirmedSteps.includes(step)
            const isClickable = (step <= currentStep || isConfirmed) && onStepClick
            return (
              <div
                key={step}
                className={`progress-label ${currentStep === step ? "active" : ""} ${isConfirmed ? "confirmed" : ""} ${isClickable ? "clickable" : ""}`}
                onClick={() => isClickable && onStepClick(step)}
                title={stepLabels[index]}
              >
                <span className="progress-label-number">
                  {isConfirmed ? "✓" : step}
                </span>
                <span className="progress-label-text">{stepLabels[index]}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ProgressIndicator
