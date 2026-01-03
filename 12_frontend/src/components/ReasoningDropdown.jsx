import { useState } from "react";
import "../css/components/ReasoningDropdown.css";

const ReasoningDropdown = ({ title, description, heading, children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="reasoning-dropdown">
      {heading && (
        <div className="question-heading">
          <span className="question-heading-text">{heading}</span>
        </div>
      )}

      <div className="reasoning-toggle" onClick={() => setIsOpen(!isOpen)}>
        <span className="reasoning-toggle-icon">{isOpen ? "▼" : "▶"}</span>
        <div className="reasoning-toggle-content">
          <span className="reasoning-toggle-title">{title}:</span>
          {description && <span className="reasoning-toggle-description">{description}</span>}
        </div>
      </div>

      {isOpen && (
        <div className="reasoning-content">
          {children}
        </div>
      )}
    </div>
  );
};

export default ReasoningDropdown;
