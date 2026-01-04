import "./css/App.css"
import { useState } from "react"
import Navbar1 from "./components/Navbar"
import HomePage from "./components/HomePage"
import UserInput from "./components/UserInput"
import About from "./components/About"
import InstructionsModal from "./components/InstructionsModal"

function App() {
  const [currentView, setCurrentView] = useState("home")
  const [formResetTrigger, setFormResetTrigger] = useState(0)
  const [isInstructionsOpen, setIsInstructionsOpen] = useState(false)
  const [hasSeenInstructions, setHasSeenInstructions] = useState(false)

  const handleGetStarted = () => {
    if (!hasSeenInstructions) {
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

  const handleOpenInstructions = () => {
    setIsInstructionsOpen(true)
  }

  const renderView = () => {
    switch (currentView) {
      case "home":
        return <HomePage onGetStarted={handleGetStarted} />
      case "about":
        return <About onOpenInstructions={handleOpenInstructions} />
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
        onProceed={handleProceedToApp}
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
