import { useState, useEffect } from "react"
import Footer from "./Footer"
import scoreDark from "../assets/prospie-score-dark.png"
import scoreLight from "../assets/prospie-score-light.png"
import reasoningDark from "../assets/prospie-reasoning-dark.png"
import reasoningLight from "../assets/prospie-reasoning-light.png"
import "../css/components/HomePage.css"

function HomePage({ onGetStarted }) {
  const [theme, setTheme] = useState(() => {
    return document.documentElement.getAttribute("data-theme") || "dark"
  })

  useEffect(() => {
    const observer = new MutationObserver(() => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "dark"
      setTheme(currentTheme)
    })

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"]
    })

    return () => observer.disconnect()
  }, [])

  const scoreImage = theme === "dark" ? scoreDark : scoreLight
  const reasoningImage = theme === "dark" ? reasoningDark : reasoningLight

  return (
    <>
      <div className="hero-section">
        <div className="hero-content">
          <h1>Trusts prospecting without the guesswork</h1>
          <p>Stop trawling accounts. Check how your project aligns with funders' giving patterns in seconds.</p>
          <button className="cta-button" onClick={onGetStarted}>Get your score now</button>
        </div>
      </div>

      <div className="showcase-section">
        <div className="divider-line"></div>

        <div className="showcase-container">
          <div className="showcase-item">
            <div className="showcase-content">
              <h2 className="showcase-title">Your alignment score</h2>
              <p className="showcase-description">
                Get your data-driven score, showing how well your organisation aligns with a funder's priorities.
              </p>
            </div>
            <div className="showcase-image-wrapper">
              <div className="showcase-card">
                <img src={scoreImage} alt="prospie alignment score" className="showcase-image" />
              </div>
            </div>
          </div>

          <div className="showcase-item showcase-item-reverse">
            <div className="showcase-image-wrapper">
              <div className="showcase-card">
                <img src={reasoningImage} alt="prospie transparent reasoning" className="showcase-image" />
              </div>
            </div>
            <div className="showcase-content">
              <h2 className="showcase-title">Transparent reasoning</h2>
              <p className="showcase-description">
                See exactly why you got your score. Explore detailed breakdowns of how your work matches with funders'
                stated priorities and past giving patterns.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </>
  )
}

export default HomePage
