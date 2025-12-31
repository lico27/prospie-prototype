import { useState, useEffect } from "react"
import CreatableSelect from "react-select/creatable"
import { supabase } from "../../supabaseClient"

function Step3Areas({ selectedAreas, onChange }) {
  const [areaOptions, setAreaOptions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAreas = async () => {
      try {
        const { data, error } = await supabase
          .from("areas")
          .select("area_id, area_name, area_level")
          .order("area_level")
          .order("area_name")

        if (error) throw error

        //group areas by level
        const groupedAreas = data.reduce((acc, area) => {
          const level = area.area_level || "Other"
          if (!acc[level]) {
            acc[level] = []
          }
          acc[level].push({
            value: area.area_name,
            label: area.area_name
          })
          return acc
        }, {})

        const formattedOptions = Object.keys(groupedAreas)
          .sort()
          .map(level => ({
            label: level.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
            options: groupedAreas[level]
          }))

        setAreaOptions(formattedOptions)
      } catch (err) {
        console.error("Error fetching areas:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchAreas()
  }, [])

  const selectedOptions = selectedAreas.map(area => ({
    value: area,
    label: area
  }))

  const handleChange = (selected) => {
    const areaNames = selected ? selected.map(option => option.value) : []
    onChange(areaNames)
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
    groupHeading: (provided) => ({
      ...provided,
      backgroundColor: getColor('--positive-glow'),
      color: getColor('--accent-teal'),
      fontSize: "0.85rem",
      fontWeight: "700",
      textTransform: "uppercase",
      letterSpacing: "0.05em",
      padding: "0.5rem 0.75rem",
      marginBottom: "0.25rem",
      borderRadius: "4px"
    }),
    group: (provided) => ({
      ...provided,
      paddingTop: "0.25rem",
      paddingBottom: "0.5rem"
    }),
    indicatorSeparator: (provided) => ({
      ...provided,
      backgroundColor: getColor('--border-primary')
    }),
    dropdownIndicator: (provided) => ({
      ...provided,
      color: getColor('--text-secondary'),
      "&:hover": {
        color: getColor('--text-tertiary')
      }
    }),
    clearIndicator: (provided) => ({
      ...provided,
      color: getColor('--text-secondary'),
      "&:hover": {
        color: getColor('--negative-color')
      }
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
        <span className="question-heading-text">Where does your project operate?</span>
      </div>
      <p className="form-helper-text">Select all that apply. Type to search or add a custom area.</p>
      {loading ? (
        <div>Loading areas...</div>
      ) : (
        <CreatableSelect
          isMulti
          options={areaOptions}
          value={selectedOptions}
          onChange={handleChange}
          placeholder="Select areas..."
          styles={customStyles}
          className="react-select-container"
          classNamePrefix="react-select"
          formatCreateLabel={(inputValue) => `Add "${inputValue}"`}
        />
      )}
    </div>
  )
}

export default Step3Areas
