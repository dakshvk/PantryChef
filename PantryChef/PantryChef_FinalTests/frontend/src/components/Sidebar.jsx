import { useState } from 'react'

const Sidebar = ({ onSearch, loading }) => {
  const [ingredients, setIngredients] = useState([])
  const [currentIngredient, setCurrentIngredient] = useState('')
  const [mood, setMood] = useState('casual')
  const [intolerances, setIntolerances] = useState([])
  const [otherIntolerance, setOtherIntolerance] = useState('')
  const [showOtherIntolerance, setShowOtherIntolerance] = useState(false)
  const [userProfile, setUserProfile] = useState('balanced')
  const [diet, setDiet] = useState('')
  const [otherDiet, setOtherDiet] = useState('')
  const [showOtherDiet, setShowOtherDiet] = useState(false)
  const [mealType, setMealType] = useState('')
  const [cuisine, setCuisine] = useState('')

  const moodOptions = [
    { value: 'tired', icon: '😴', label: 'Tired' },
    { value: 'casual', icon: '😊', label: 'Casual' },
    { value: 'energetic', icon: '⚡', label: 'Energetic' },
  ]

  // Common intolerances only - specific nut allergies go in "Other"
  const intoleranceOptions = ['dairy', 'gluten', 'eggs']

  const dietOptions = [
    { value: '', label: 'None' },
    { value: 'vegan', label: 'Vegan' },
    { value: 'vegetarian', label: 'Vegetarian' },
    { value: 'pescatarian', label: 'Pescatarian' },
    { value: 'other', label: 'Other' },
  ]

  const handleDietChange = (value) => {
    if (value === 'other') {
      setShowOtherDiet(true)
      setDiet('')
    } else {
      setShowOtherDiet(false)
      setOtherDiet('')
      setDiet(value)
    }
  }

  const mealTypeOptions = [
    { value: '', label: 'Any' },
    { value: 'main course', label: 'Main Course' },
    { value: 'side dish', label: 'Side Dish/Snack' },
    { value: 'dessert', label: 'Dessert' },
    { value: 'appetizer', label: 'Appetizer' },
    { value: 'breakfast', label: 'Breakfast' },
  ]

  const cuisineOptions = [
    { value: '', label: 'Any' },
    { value: 'italian', label: 'Italian' },
    { value: 'mexican', label: 'Mexican' },
    { value: 'chinese', label: 'Chinese' },
    { value: 'indian', label: 'Indian' },
    { value: 'japanese', label: 'Japanese' },
    { value: 'thai', label: 'Thai' },
    { value: 'french', label: 'French' },
    { value: 'mediterranean', label: 'Mediterranean' },
    { value: 'american', label: 'American' },
    { value: 'greek', label: 'Greek' },
    { value: 'spanish', label: 'Spanish' },
  ]

  const handleAddIngredient = (e) => {
    if (e.key === 'Enter' && currentIngredient.trim()) {
      e.preventDefault()
      setIngredients([...ingredients, currentIngredient.trim().toLowerCase()])
      setCurrentIngredient('')
    }
  }

  const handleRemoveIngredient = (index) => {
    setIngredients(ingredients.filter((_, i) => i !== index))
  }

  const handleToggleIntolerance = (intolerance) => {
    setIntolerances(
      intolerances.includes(intolerance)
        ? intolerances.filter(i => i !== intolerance)
        : [...intolerances, intolerance]
    )
  }

  const handleToggleOtherIntolerance = () => {
    setShowOtherIntolerance(!showOtherIntolerance)
    if (showOtherIntolerance && otherIntolerance) {
      // Remove custom intolerance if unchecking
      setIntolerances(intolerances.filter(i => i !== otherIntolerance))
      setOtherIntolerance('')
    }
  }

  const handleOtherIntoleranceChange = (value) => {
    // Remove previous custom intolerance if it exists
    const commonIntolerances = intoleranceOptions
    const previousCustom = intolerances.find(i => !commonIntolerances.includes(i))
    if (previousCustom) {
      setIntolerances(intolerances.filter(i => i !== previousCustom))
    }
    
    setOtherIntolerance(value)
    if (value.trim()) {
      setIntolerances([...intolerances.filter(i => commonIntolerances.includes(i)), value.trim().toLowerCase()])
    }
  }

  const handleSearch = () => {
    // Build complete intolerance list (common + custom "other")
    const finalIntolerances = [...intolerances]
    if (otherIntolerance.trim() && !finalIntolerances.includes(otherIntolerance.trim().toLowerCase())) {
      finalIntolerances.push(otherIntolerance.trim().toLowerCase())
    }

    // Use custom diet if "Other" is selected, otherwise use selected diet
    const finalDiet = showOtherDiet && otherDiet.trim() ? otherDiet.trim().toLowerCase() : (diet || undefined)

    const searchData = {
      ingredients,
      mood,
      intolerances: finalIntolerances,
      user_profile: userProfile,
      diet: finalDiet,
      meal_type: mealType || undefined,
      cuisine: cuisine || undefined,
      number: 20,
    }

    // Debug logging: Show exactly what's being sent
    console.log('🔍 [Sidebar] Sending to backend:', searchData)
    console.log('   - Mood value:', mood, '(type:', typeof mood, ')')
    console.log('   - Ingredients count:', ingredients.length)
    console.log('   - Intolerances:', finalIntolerances)

    onSearch(searchData)
  }

  return (
    <aside className="w-80 h-full bg-emerald-50 border-r border-emerald-100 flex flex-col p-6 overflow-y-auto rounded-r-[40px] shadow-sm">
      <h2 className="text-2xl font-bold text-emerald-900 mb-6">PantryChef</h2>
      
      <div className="space-y-6 flex-1">

        {/* Ingredients Input */}
        <div>
          <label className="block text-sm font-medium text-emerald-900 mb-2">
            Ingredients
          </label>
        <input
          type="text"
          value={currentIngredient}
          onChange={(e) => setCurrentIngredient(e.target.value)}
          onKeyPress={handleAddIngredient}
          placeholder="Type ingredient and press Enter"
          className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white"
        />
        <div className="flex flex-wrap gap-2 mt-2">
          {ingredients.map((ing, index) => (
            <span
              key={index}
              className="inline-flex items-center px-3 py-1 bg-emerald-600 text-white rounded-full text-sm"
            >
              {ing}
              <button
                onClick={() => handleRemoveIngredient(index)}
                className="ml-2 text-white hover:text-emerald-100"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

        {/* Mood Selection */}
        <div>
          <label className="block text-sm font-medium text-emerald-900 mb-2">
            Mood {mood && <span className="text-xs text-emerald-600">({mood})</span>}
          </label>
          <div className="flex gap-2">
            {moodOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  console.log('🎯 [Sidebar] Mood clicked:', option.value)
                  setMood(option.value)
                }}
                className={`flex-1 px-3 py-2 rounded-2xl border-2 transition-colors ${
                  mood === option.value
                    ? 'border-emerald-600 bg-emerald-600 text-white'
                    : 'border-emerald-200 hover:border-emerald-400 bg-white'
                }`}
                title={option.label}
              >
                <span className="text-xl">{option.icon}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Intolerances */}
        <div>
        <label className="block text-sm font-medium text-emerald-900 mb-2">
          Intolerances
        </label>
        <div className="space-y-2">
          {intoleranceOptions.map((intolerance) => (
            <label key={intolerance} className="flex items-center">
              <input
                type="checkbox"
                checked={intolerances.includes(intolerance)}
                onChange={() => handleToggleIntolerance(intolerance)}
                className="mr-2 rounded"
              />
              <span className="text-sm text-emerald-900 capitalize">{intolerance}</span>
            </label>
          ))}
          {/* Other Intolerance Option - For specific nut allergies, soy, shellfish, etc. */}
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showOtherIntolerance}
              onChange={handleToggleOtherIntolerance}
              className="mr-2 rounded"
            />
            <span className="text-sm text-emerald-900">Other (e.g., peanuts, tree nuts, soy, shellfish)</span>
          </label>
          {showOtherIntolerance && (
            <input
              type="text"
              value={otherIntolerance}
              onChange={(e) => handleOtherIntoleranceChange(e.target.value)}
              placeholder="Type specific allergies (e.g., peanuts, almonds, soy)..."
              className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white text-sm mt-1"
            />
          )}
        </div>
      </div>

        {/* Diet Selector */}
        <div>
        <label className="block text-sm font-medium text-emerald-900 mb-2">
          Diet
        </label>
        <select
          value={showOtherDiet ? 'other' : diet}
          onChange={(e) => handleDietChange(e.target.value)}
          className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white"
        >
          {dietOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {showOtherDiet && (
          <input
            type="text"
            value={otherDiet}
            onChange={(e) => setOtherDiet(e.target.value)}
            placeholder="Type your diet preference (e.g., paleo, keto, raw)..."
            className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white text-sm mt-2"
          />
        )}
      </div>

        {/* Meal Type Selector */}
        <div>
        <label className="block text-sm font-medium text-emerald-900 mb-2">
          Meal Type
        </label>
        <select
          value={mealType}
          onChange={(e) => setMealType(e.target.value)}
          className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white"
        >
          {mealTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

        {/* Cuisine Preference */}
        <div>
        <label className="block text-sm font-medium text-emerald-900 mb-2">
          Cuisine Preference
        </label>
        <select
          value={cuisine}
          onChange={(e) => setCuisine(e.target.value)}
          className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white"
        >
          {cuisineOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

        {/* User Profile */}
        <div>
        <label className="block text-sm font-medium text-emerald-900 mb-2">
          Profile
        </label>
        <select
          value={userProfile}
          onChange={(e) => setUserProfile(e.target.value)}
          className="w-full px-3 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white"
        >
          <option value="balanced">Balanced</option>
          <option value="minimal_shopper">Minimal Shopper</option>
          <option value="pantry_cleaner">Pantry Cleaner</option>
        </select>
      </div>

        {/* Search Button - Never disabled except when loading */}
        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full px-4 py-3 bg-emerald-600 text-white rounded-2xl font-semibold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm mt-auto"
        >
          {loading ? 'Searching...' : 'Find Recipes'}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar

