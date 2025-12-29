function Step8FunderNumber({ funderNumber, onChange }) {
  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">What is the funder's registered charity number?</span>
      </div>
      <input
        type="text"
        id="funderNumber"
        value={funderNumber}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter the funder's charity number"
        pattern="[0-9]*"
        inputMode="numeric"
        required
      />
    </div>
  )
}

export default Step8FunderNumber
