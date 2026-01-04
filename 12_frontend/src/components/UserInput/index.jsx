import { useState, useEffect } from "react"
import { supabase } from "../../supabaseClient"
import ProgressIndicator from "../ProgressIndicator"
import FormNavigation from "../FormNavigation"
import Step1CharityNumber from "./Step1CharityNumber"
import Step2CheckDetails from "./Step2CheckDetails"
import Step3Areas from "./Step3Areas"
import Step4Beneficiaries from "./Step4Beneficiaries"
import Step5Causes from "./Step5Causes"
import Step6Activities from "./Step6ActivitiesObjectives"
import Step7Keywords from "./Step7Keywords"
import Step8FunderNumber from "./Step8FunderNumber"
import LoadingScreen from "../LoadingScreen"
import ResultScreen from "../ResultScreen"
import { fetchUkcatData, extractClassifications } from "../../utils/keywordExtractor"

function UserInput({ resetTrigger, onOpenInstructions }) {
  const [currentStep, setCurrentStep] = useState(1)
  const [charityNumber, setCharityNumber] = useState("")
  const [charityData, setCharityData] = useState(null)
  const [selectedAreas, setSelectedAreas] = useState([])
  const [selectedBeneficiaries, setSelectedBeneficiaries] = useState([])
  const [selectedCauses, setSelectedCauses] = useState([])
  const [activities, setActivities] = useState("")
  const [objectives, setObjectives] = useState("")
  const [keywords, setKeywords] = useState([])
  const [isExtractingKeywords, setIsExtractingKeywords] = useState(false)
  const [funderNumber, setFunderNumber] = useState("")
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isCalculating, setIsCalculating] = useState(false)
  const [confirmedSteps, setConfirmedSteps] = useState([])
  const [alignmentScore, setAlignmentScore] = useState(null)
  const [reasonings, setReasonings] = useState(null)
  const [pairData, setPairData] = useState(null)

  const preparePairData = () => {
    //prepare user data
    const pair_df = {
      user_id: charityNumber,
      user_name: charityData?.recipient_name || "",
      user_name_em: null,
      user_areas: selectedAreas,
      user_beneficiaries: selectedBeneficiaries,
      user_causes: selectedCauses,
      user_concat_em: null,
      user_extracted_class: JSON.stringify(keywords),
      user_activities: activities,
      user_objectives: objectives
    }

    return pair_df
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsCalculating(true)
    setError(null)
    setAlignmentScore(null)

    try {
      const pair_df = preparePairData()
      console.log("User data prepared for scoring:", pair_df)

      //send to backend for alignment scoring
      const apiUrl = import.meta.env.DEV
        ? "http://localhost:5000/api/calculate"
        : import.meta.env.VITE_API_URL || "https://prospie.onrender.com/api/calculate"

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userData: pair_df,
          funderNumber: funderNumber
        })
      })

      const scoringResult = await response.json()
      console.log("Scoring result:", scoringResult)

      if (scoringResult.error) {
        setError(scoringResult.error)
      } else {
        setAlignmentScore(scoringResult.score)
        setReasonings(scoringResult.reasonings)
        setPairData(scoringResult.pair_data)
      }
    } catch (err) {
      setError(err.message || "An error occurred while calculating the score")
    } finally {
      setIsCalculating(false)
    }
  }

  const handleNext = async () => {
    if (currentStep < 8) {
      //mark current step as confirmed
      if (!confirmedSteps.includes(currentStep)) {
        setConfirmedSteps([...confirmedSteps, currentStep])
      }

      if (currentStep === 1) {
        await validateCharityNumber()
      } else if (currentStep === 6) {
        //extract keywords before moving to step 7
        await extractKeywordsFromData()
        setCurrentStep(currentStep + 1)
        setError(null)
      } else {
        setCurrentStep(currentStep + 1)
        setError(null)
      }
    }
  }

  const extractKeywordsFromData = async () => {
    setIsExtractingKeywords(true)
    try {
      const ukcatData = await fetchUkcatData()

      //prepare data and extract classifications
      const extractionData = {
        activities,
        objectives,
        areas: selectedAreas,
        beneficiaries: selectedBeneficiaries,
        causes: selectedCauses
      }
      const extractedKeywords = extractClassifications(extractionData, ukcatData, [])
      setKeywords(extractedKeywords)
    } catch (err) {
      console.error("Error extracting keywords:", err)
      setError("Failed to extract keywords. You can still add them manually.")
    } finally {
      setIsExtractingKeywords(false)
    }
  }

  const validateCharityNumber = async () => {
    if (!charityNumber) {
      setError("Please enter a charity number")
      return
    }

    if (!/^\d+$/.test(charityNumber)) {
      setError("Charity number must contain only numbers")
      return
    }

    //reset everything when validating a new charity number
    setLoading(true)
    setError(null)
    setCharityData(null)
    setSelectedAreas([])
    setSelectedBeneficiaries([])
    setSelectedCauses([])
    setActivities("")
    setObjectives("")
    setKeywords([])
    setConfirmedSteps([])
    setFunderNumber("")

    try {
      const { data: recipient, error } = await supabase
        .from("recipients")
        .select("*")
        .eq("recipient_id", charityNumber)
        .single()

      if (error) throw error

      if (recipient) {
        const [areaLinks, benLinks, causeLinks] = await Promise.all([
          supabase.from("recipient_areas").select("area_id").eq("recipient_id", charityNumber),
          supabase.from("recipient_beneficiaries").select("ben_id").eq("recipient_id", charityNumber),
          supabase.from("recipient_causes").select("cause_id").eq("recipient_id", charityNumber)
        ])

        const areaIds = areaLinks.data?.map(a => a.area_id) || []
        const benIds = benLinks.data?.map(b => b.ben_id) || []
        const causeIds = causeLinks.data?.map(c => c.cause_id) || []
        
        const [areas, beneficiaries, causes] = await Promise.all([
          areaIds.length > 0
            ? supabase.from("areas").select("area_name, area_level").in("area_id", areaIds)
            : Promise.resolve({ data: [] }),
          benIds.length > 0
            ? supabase.from("beneficiaries").select("ben_name").in("ben_id", benIds)
            : Promise.resolve({ data: [] }),
          causeIds.length > 0 
            ? supabase.from("causes").select("cause_name").in("cause_id", causeIds)
            : Promise.resolve({ data: [] }),
        ])

        const enrichedData = {
          ...recipient,
          areas: areas.data || [],
          beneficiaries: beneficiaries.data || [],
          causes: causes.data || []
        }

        //pre-populate areas
        const dbAreas = areas.data?.map(a => a.area_name) || []
        setSelectedAreas(dbAreas)

        //pre-populate beneficiaries
        const dbBeneficiaries = beneficiaries.data?.map(b => b.ben_name) || []
        setSelectedBeneficiaries(dbBeneficiaries)

        //pre-populate causes
        const dbCauses = causes.data?.map(c => c.cause_name) || []
        setSelectedCauses(dbCauses)

        //pre-populate activities
        setActivities(recipient.recipient_activities || "")

        //pre-populate objectives
        setObjectives(recipient.recipient_objectives || "")

        setCharityData(enrichedData)
        setCurrentStep(currentStep + 1)
        setError(null)
      }
    } catch (err) {
      if (err.message.includes("Cannot coerce the result to a single JSON object")) {
        setError("Charity number not found. Please enter a valid registered charity number.")
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      setError(null)
    }
  }

  const handleReset = () => {
    setCurrentStep(1)
    setCharityNumber("")
    setCharityData(null)
    setSelectedAreas([])
    setSelectedBeneficiaries([])
    setSelectedCauses([])
    setActivities("")
    setObjectives("")
    setKeywords([])
    setIsExtractingKeywords(false)
    setFunderNumber("")
    setError(null)
    setConfirmedSteps([])
    setAlignmentScore(null)
  }

  useEffect(() => {
    handleReset()
  }, [resetTrigger])

  const handleFormSubmit = (e) => {
    e.preventDefault()
    if (currentStep === 8) {
      handleSubmit(e)
    } else {
      handleNext()
    }
  }

  const handleStepClick = (step) => {
    setCurrentStep(step)
    setError(null)
  }

  return (
    <>
      {isCalculating && <LoadingScreen />}

      {alignmentScore !== null && (
        <ResultScreen
          score={alignmentScore}
          reasonings={reasonings}
          userName={pairData?.user_name}
          funderName={pairData?.funder_name}
          pairData={pairData}
          onReset={handleReset}
        />
      )}

      {!isCalculating && alignmentScore === null && (
        <div className="app-view">
          <div className="app-container">
            <h2 className="app-title">Get your prospie score</h2>

            <ProgressIndicator
              currentStep={currentStep}
              totalSteps={8}
              onStepClick={handleStepClick}
              confirmedSteps={confirmedSteps}
            />

            <div className="app-form-container">
              <form onSubmit={handleFormSubmit}>
                {currentStep === 1 && (
                  <Step1CharityNumber charityNumber={charityNumber} onChange={setCharityNumber} />
                )}

                {currentStep === 2 && (
                  <Step2CheckDetails
                    charityData={charityData}
                    onUseDetails={async () => {
                      await extractKeywordsFromData();
                      setConfirmedSteps([...confirmedSteps, 2, 3, 4, 5, 6, 7]);
                      setCurrentStep(8);
                      setError(null);
                    }}
                    onEdit={() => {
                      if (!confirmedSteps.includes(2)) {
                        setConfirmedSteps([...confirmedSteps, 2]);
                      }
                      setCurrentStep(3);
                      setError(null);
                    }}
                    onBack={handleBack}
                  />
                )}

                {currentStep === 3 && (
                  <Step3Areas
                    selectedAreas={selectedAreas}
                    onChange={setSelectedAreas}
                  />
                )}

                {currentStep === 4 && (
                  <Step4Beneficiaries
                    selectedBeneficiaries={selectedBeneficiaries}
                    onChange={setSelectedBeneficiaries}
                  />
                )}

                {currentStep === 5 && (
                  <Step5Causes
                    selectedCauses={selectedCauses}
                    onChange={setSelectedCauses}
                  />
                )}

                {currentStep === 6 && (
                  <Step6Activities
                    activities={activities}
                    objectives={objectives}
                    onActivitiesChange={setActivities}
                    onObjectivesChange={setObjectives}
                  />
                )}

                {currentStep === 7 && (
                  <Step7Keywords
                    keywords={keywords}
                    onChange={setKeywords}
                    isExtracting={isExtractingKeywords}
                  />
                )}

                {currentStep === 8 && (
                  <Step8FunderNumber funderNumber={funderNumber} onChange={setFunderNumber} />
                )}

                {currentStep !== 2 && (
                  <FormNavigation
                    currentStep={currentStep}
                    totalSteps={8}
                    onBack={handleBack}
                    onNext={handleNext}
                    onSubmit={handleSubmit}
                    loading={loading || isCalculating}
                  />
                )}
              </form>

              {error && (
                <div className="error">
                  <p>{error}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default UserInput