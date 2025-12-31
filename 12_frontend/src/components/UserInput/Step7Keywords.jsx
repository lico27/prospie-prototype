import { useState, useEffect } from "react"
import CreatableSelect from "react-select/creatable"

function Step7Keywords({ keywords, onChange, isExtracting }) {
  const [showHint, setShowHint] = useState(false)

  const keywordOptions = keywords.map(keyword => ({
    value: keyword,
    label: keyword
  }))

  const handleChange = (selected) => {
    const keywordList = selected ? selected.map(option => option.value) : []
    onChange(keywordList)
  }

  //apply styles
  const getColor = (varName) => {
    return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
  }

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      backgroundColor: getColor('--bg-tertiary'),
      borderColor: state.isFocused ? getColor('--positive-hover') : getColor('--border-primary'),
      borderRadius: "8px",
      padding: "0.25rem",
      boxShadow: state.isFocused ? `0 0 0 3px ${getColor('--positive-glow')}` : "none",
      transition: "all 0.3s ease",
      "&:hover": {
        borderColor: getColor('--border-hover')
      }
    }),
    menu: (provided) => ({
      ...provided,
      backgroundColor: getColor('--bg-secondary'),
      border: `1px solid ${getColor('--border-primary')}`,
      borderRadius: "8px",
      backdropFilter: "blur(10px)",
      boxShadow: `0 8px 32px ${getColor('--shadow-secondary')}`
    }),
    menuList: (provided) => ({
      ...provided,
      padding: "0.5rem",
      maxHeight: "300px",
      "::-webkit-scrollbar": {
        width: "8px"
      },
      "::-webkit-scrollbar-track": {
        background: getColor('--bg-tertiary')
      },
      "::-webkit-scrollbar-thumb": {
        background: getColor('--border-primary'),
        borderRadius: "4px"
      },
      "::-webkit-scrollbar-thumb:hover": {
        background: getColor('--border-hover')
      }
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected
        ? getColor('--border-primary')
        : state.isFocused
        ? getColor('--border-secondary')
        : "transparent",
      color: state.isSelected ? getColor('--text-tertiary') : getColor('--text-secondary'),
      padding: "0.6rem 0.75rem",
      cursor: "pointer",
      borderRadius: "4px",
      fontSize: "0.9rem",
      transition: "all 0.2s ease",
      "&:active": {
        backgroundColor: getColor('--border-primary')
      }
    }),
    multiValue: (provided) => ({
      ...provided,
      backgroundColor: getColor('--border-secondary'),
      border: `1px solid ${getColor('--border-primary')}`,
      borderRadius: "6px"
    }),
    multiValueLabel: (provided) => ({
      ...provided,
      color: getColor('--text-tertiary'),
      fontSize: "0.85rem",
      padding: "0.3rem 0.5rem"
    }),
    multiValueRemove: (provided) => ({
      ...provided,
      color: getColor('--text-secondary'),
      ":hover": {
        backgroundColor: getColor('--negative-color'),
        color: getColor('--negative-color'),
        borderRadius: "0 4px 4px 0"
      }
    }),
    placeholder: (provided) => ({
      ...provided,
      color: getColor('--text-secondary'),
      opacity: 0.6,
      fontSize: "0.9rem"
    }),
    input: (provided) => ({
      ...provided,
      color: getColor('--text-primary')
    }),
    noOptionsMessage: (provided) => ({
      ...provided,
      color: getColor('--text-secondary'),
      fontSize: "0.9rem",
      padding: "0.75rem"
    })
  }

  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">Review Your Keywords</span>
      </div>
      <p className="form-helper-text">
        These keywords have been automatically extracted from your areas, beneficiaries, causes, activities, and objectives.
        You can add (or delete) keywords below.
      </p>

      <div className="hint-toggle" onClick={() => setShowHint(!showHint)}>
        <span className="hint-icon">{showHint ? "▼" : "▶"}</span>
        <span className="hint-toggle-text">What are keywords and how do they help?</span>
      </div>

      {showHint && (
        <div className="hint-box">
          <p className="hint-intro">
            Keywords are specific terms and phrases that describe your charity's work. prospie uses them as part of the calculation of your alignment score with your selected funder.
          </p>
          <div className="hint-example">
            <p><strong>How it works:</strong></p>
            <ul className="hint-list">
              <li>prospie has automatically extracted keywords using <a href="https://charityclassification.org.uk/" target="_blank" rel="noopener noreferrer" className="app-link">UKCAT charity classifications</a> and your input</li>
              <li>More specific keywords (like "care-experienced young people") offer more value than broad terms (like "education")</li>
              <li>You can remove irrelevant keywords or add additional ones that better describe your work</li>
            </ul>
          </div>
        </div>
      )}

      {isExtracting ? (
        <div className="loading" style={{ textAlign: "left", padding: "1rem 0" }}>
          Extracting keywords from your data...
        </div>
      ) : (
        <CreatableSelect
          isMulti
          value={keywordOptions}
          onChange={handleChange}
          options={[]}
          placeholder="Your extracted keywords will appear here. Type to add custom keywords..."
          styles={customStyles}
          className="react-select-container"
          classNamePrefix="react-select"
          formatCreateLabel={(inputValue) => `Add "${inputValue}"`}
        />
      )}
    </div>
  )
}

export default Step7Keywords
