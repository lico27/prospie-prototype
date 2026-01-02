function Step2ConfirmDetails({ charityData }) {
  if (!charityData) {
    return <div className="loading">Loading charity data...</div>
  }

  return (
    <div className="charity-details">
      <div className="entity-column">

        <div className="instruction-box">
          <div className="instruction-icon">ℹ️</div>
          <div className="instruction-content">
            <h4 className="instruction-heading">Choose Your Details</h4>
            <p className="instruction-text">
              Below is your charity's information taken from the Charity Commission website. Use the Next/Back buttons or click the numbered steps at the top to navigate through each section and make any changes you'd like.
            </p>
          </div>
        </div>

        <div className="entity-section">
          <h3>{charityData.recipient_name}</h3>
        </div>

        {charityData.recipient_objectives && (
          <div className="entity-section">
            <h4>Objectives</h4>
            <div className="scrollable-text-box">
              <p>{charityData.recipient_objectives}</p>
            </div>
          </div>
        )}

        {charityData.recipient_activities && (
          <div className="entity-section">
            <h4>Activities</h4>
            <div className="scrollable-text-box">
              <p>{charityData.recipient_activities}</p>
            </div>
          </div>
        )}

        <div className="entity-section">
          <h4>Areas</h4>
          {charityData.areas && charityData.areas.length > 0 ? (
            <div className="tag-list">
              {charityData.areas.map((area, idx) => (
                <span key={idx} className="tag">
                  {area.area_name}
                </span>
              ))}
            </div>
          ) : (
            <div className="empty-state-message">
              <p style={{ fontStyle: 'italic', color: '#888', margin: '0.5rem 0', textAlign: 'center' }}>
                Sorry! prospie was unable to retrieve geographic data for your charity. Please add your areas manually.
              </p>
            </div>
          )}
        </div>

        <div className="entity-section">
          <h4>Beneficiaries</h4>
          {charityData.beneficiaries && charityData.beneficiaries.length > 0 ? (
            <div className="tag-list">
              {charityData.beneficiaries.map((ben, idx) => (
                <span key={idx} className="tag">{ben.ben_name}</span>
              ))}
            </div>
          ) : (
            <div className="empty-state-message">
              <p style={{ fontStyle: 'italic', color: '#888', margin: '0.5rem 0', textAlign: 'center' }}>
                Sorry! prospie was unable to retrieve beneficiary data for your charity. Please add your beneficiaries manually.
              </p>
            </div>
          )}
        </div>

        <div className="entity-section">
          <h4>Causes</h4>
          {charityData.causes && charityData.causes.length > 0 ? (
            <div className="tag-list">
              {charityData.causes.map((cause, idx) => (
                <span key={idx} className="tag">{cause.cause_name}</span>
              ))}
            </div>
          ) : (
            <div className="empty-state-message">
              <p style={{ fontStyle: 'italic', color: '#888', margin: '0.5rem 0', textAlign: 'center' }}>
                Sorry! prospie was unable to retrieve cause data for your charity. Please add your causes manually.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Step2ConfirmDetails
