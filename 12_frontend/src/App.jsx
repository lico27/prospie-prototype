import "./css/App.css"
import { useState } from "react"
import Navbar1 from "./components/Navbar"
import HomePage from "./components/HomePage"
import UserInput from "./components/UserInput"
import About from "./components/About"
import InstructionsModal from "./components/InstructionsModal"

//set navigation and modal state
function App() {
  const [currentView, setCurrentView] = useState("home")
  const [formResetTrigger, setFormResetTrigger] = useState(0)
  const [isInstructionsOpen, setIsInstructionsOpen] = useState(false)
  const [hasSeenInstructions, setHasSeenInstructions] = useState(false)
  const [instructionsSource, setInstructionsSource] = useState("home")

  //show instructions on first visit only
  const handleGetStarted = () => {
    if (!hasSeenInstructions) {
      setInstructionsSource("home")
      setIsInstructionsOpen(true)
    } else {
      setFormResetTrigger(prev => prev + 1)
      setCurrentView("app")
    }
  }

  const handleInstructionsClose = () => {
    setIsInstructionsOpen(false)
  }

  const handleProceedToApp = () => {
    setIsInstructionsOpen(false)
    setHasSeenInstructions(true)
    setFormResetTrigger(prev => prev + 1)
    setCurrentView("app")
  }

  //set modal handlers for form and about page
  const handleOpenInstructions = () => {
    setInstructionsSource("form")
    setIsInstructionsOpen(true)
  }

  const handleOpenInstructionsAbout = () => {
    setInstructionsSource("about")
    setIsInstructionsOpen(true)
  }

  const handleContinue = () => {
    setIsInstructionsOpen(false)
  }

  //render home, about or form based on navigation
  const renderView = () => {
    switch (currentView) {
      case "home":
        return <HomePage onGetStarted={handleGetStarted} />
      case "about":
        return <About onOpenInstructions={handleOpenInstructionsAbout} />
      case "app":
        return <UserInput resetTrigger={formResetTrigger} onOpenInstructions={handleOpenInstructions} />
      default:
        return <HomePage onGetStarted={handleGetStarted} />
    }
  }

  return (
    <>
      <InstructionsModal
        isOpen={isInstructionsOpen}
        onClose={handleInstructionsClose}
        onProceed={instructionsSource === "about" ? null : (instructionsSource === "home" ? handleProceedToApp : handleContinue)}
        buttonText={instructionsSource === "home" ? "Get started" : "Continue"}
      />
      <Navbar1
        onHomeClick={() => setCurrentView("home")}
        onAboutClick={() => setCurrentView("about")}
      />
      {renderView()}
    </>
  )
}

export default App

//garbage collection code adapted from Shaibu (2024)