import { useEffect } from "react"
import "../css/components/InstructionsModal.css"

function InstructionsModal({ isOpen, onClose, onProceed }) {
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
        <h2 className="modal-title">How to use <span className="prospie-highlight">prospie</span></h2>
        <div className="modal-body">
          <p>Instructions TBC</p>
        </div>
        {onProceed && (
          <div className="modal-footer">
            <button className="modal-button" onClick={onProceed}>
              Get started
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default InstructionsModal
