import { useEffect } from "react"
import "../css/components/InstructionsModal.css"

function InstructionsModal({ isOpen, onClose, onProceed, buttonText = "Get started" }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "unset"
    }
    return () => {
      document.body.style.overflow = "unset"
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ×
        </button>
        <h2 className="modal-title">Tips for using <span className="prospie-highlight">prospie</span></h2>
        <div className="modal-body">
          <div className="modal-section">
          <div className="question-heading">
            <span className="question-heading-text">Steps</span>
          </div>
          <ol>
            <li><strong>Enter your details</strong><br></br>Enter your charity number. prospie will pull your organisation's information from the Charity Commission.</li>
            <li><strong>Edit your data (recommended)</strong><br></br>
                  Whilst you can use the data as-is for a quick assessment, editing it will likely significantly improve the quality of your score:
                  <ul>
                  <li>Be specific – consider focusing on a single project rather than your entire organisation, especially if you work in multiple areas/sectors</li>
                  <li>Replace generic charity sector language (e.g. "improving wellbeing", "making a difference") with concrete and distinctive keywords – vague language will result in a good alignment with pretty much any funder!</li>
                  <li>Add or delete keywords and text in any field</li>
                  </ul>
              </li>
              <li><strong>Enter the funder's charity number</strong><br></br>Input the registered charity number of the funder you want to assess alignment with.</li>
              <li><strong>Click "Submit" and wait...</strong><br></br>prospie calculates your score from lots of different factors, so it can take up to two or three minutes, especially if your funder has a large giving history (fun fact: Esmee Fairbairn Foundation is the biggest, with a whopping 6,987 grants!).</li>
              <li><strong>Review your results</strong><br></br>Your alignment score will be displayed with clear reasoning behind it. Click the dropdown sections to see detailed breakdowns of how different factors contributed to your score.</li>
          </ol>
          </div>
          <div className="modal-section">
          <div className="question-heading">
            <span className="question-heading-text">Please note</span>
          </div>
          <ul>
            <li><strong>Alignment scores range from 5% to 95%</strong><br></br>They will never  be 0% or 100%. This reflects the uncertainty of prospecting. prospie can never be 100% certain of an alignment but it can equally never completely rule out the possibility of a match.</li>
            <li><strong>This tool supports your judgment, it doesn't replace it.</strong><br></br> prospie is designed to help you make more informed prospecting decisions, not to make those decisions for you.</li>
            <li><strong>The data in this prototype has limitations</strong><br></br>The current app only has 996 funders, and many funders have missing or incomplete information.</li>
          </ul>
        </div>
        </div>

        {onProceed && (
          <div className="modal-footer">
            <button className="modal-button" onClick={onProceed}>
              {buttonText}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default InstructionsModal
