import { useState } from 'react'

const RecipeCard = ({ recipe }) => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showSubstitution, setShowSubstitution] = useState(false)
  const [askChefQuery, setAskChefQuery] = useState('')
  const [chefResponse, setChefResponse] = useState('')
  const [isAskingChef, setIsAskingChef] = useState(false)

  const safetyCheck = recipe._metadata?.safety_check || {}
  const requiresValidation = recipe.requires_ai_validation || safetyCheck.requires_ai_validation
  const safetyScore = safetyCheck.safety_score || 1.0
  const violationNote = recipe.violation_note || safetyCheck.violation_note || safetyCheck.safety_reason

  // Flag, Don't Fail: Style with amber border if safety_score is 0.2 (soft violation)
  const isSoftViolation = safetyScore === 0.2 || requiresValidation

  // Calculate match score as "X / Y" (ingredients I have / total ingredients)
  const usedIngredients = recipe.usedIngredientCount || recipe.used_ingredients || 0
  const missedIngredients = recipe.missedIngredientCount || recipe.missing_ingredients || 0
  const totalIngredients = usedIngredients + missedIngredients
  const matchScore = totalIngredients > 0 ? `${usedIngredients} / ${totalIngredients}` : '0 / 0'

  // Extract nutritional tags from nutrition data
  const getNutritionalTags = () => {
    const tags = []
    const nutrients = recipe.nutrition?.nutrients || []
    
    // Find vitamins and minerals in nutrients array
    const nutrientMap = {}
    nutrients.forEach(nutrient => {
      const name = nutrient.name?.toLowerCase() || ''
      nutrientMap[name] = nutrient.amount || 0
    })

    // High protein (20g+ per serving)
    const protein = recipe.protein || nutrientMap['protein'] || 0
    if (protein >= 20) {
      tags.push({ label: 'High Protein', color: 'bg-blue-100 text-blue-800' })
    }

    // High calcium
    const calcium = nutrientMap['calcium'] || 0
    if (calcium >= 300) {
      tags.push({ label: 'Rich in Calcium', color: 'bg-purple-100 text-purple-800' })
    }

    // High iron
    const iron = nutrientMap['iron'] || 0
    if (iron >= 3) {
      tags.push({ label: 'High Iron', color: 'bg-red-100 text-red-800' })
    }

    // High Vitamin C
    const vitC = nutrientMap['vitamin c'] || nutrientMap['vitamin c (total ascorbic acid)'] || 0
    if (vitC >= 60) {
      tags.push({ label: 'Rich in Vitamin C', color: 'bg-orange-100 text-orange-800' })
    }

    // High Fiber
    const fiber = nutrientMap['fiber'] || nutrientMap['dietary fiber'] || 0
    if (fiber >= 5) {
      tags.push({ label: 'High Fiber', color: 'bg-green-100 text-green-800' })
    }

    return tags
  }

  const nutritionalTags = getNutritionalTags()

  // Parse instructions into steps
  const getInstructionsSteps = () => {
    // Try analyzedInstructions first (structured)
    if (recipe.analyzedInstructions && recipe.analyzedInstructions.length > 0) {
      const steps = []
      recipe.analyzedInstructions.forEach(section => {
        if (section.steps && Array.isArray(section.steps)) {
          section.steps.forEach(step => {
            if (step.step) {
              steps.push(step.step)
            }
          })
        }
      })
      return steps.length > 0 ? steps : null
    }

    // Fallback to plain instructions string (split by periods/newlines)
    if (recipe.instructions) {
      const steps = recipe.instructions
        .split(/[.!?]\s+|[\n]/)
        .map(s => s.trim())
        .filter(s => s.length > 10) // Filter out very short fragments
      return steps.length > 0 ? steps : null
    }

    return null
  }

  const instructionSteps = getInstructionsSteps()

  // Get ingredients list
  const getIngredientsList = () => {
    if (recipe.extendedIngredients && recipe.extendedIngredients.length > 0) {
      return recipe.extendedIngredients.map(ing => {
        const amount = ing.amount || ''
        const unit = ing.unitShort || ing.unit || ''
        const name = ing.name || ''
        return { amount, unit, name, full: `${amount} ${unit} ${name}`.trim() }
      })
    }
    return []
  }

  const ingredients = getIngredientsList()

  // Get ready time
  const readyTime = recipe.readyInMinutes || recipe.time || 0

  // Use recipe.image directly from Spoonacular data
  const imageUrl = recipe.image || null
  const [imageError, setImageError] = useState(false)
  
  // Handle image load errors - fallback to generic food icon
  const handleImageError = () => {
    setImageError(true)
  }

  // Handle "Ask Chef" - Send ingredient substitution query to backend
  const handleAskChef = async (e) => {
    e.preventDefault()
    if (!askChefQuery.trim()) return

    setIsAskingChef(true)
    setChefResponse('')

    try {
      const response = await fetch('http://localhost:8000/ask-chef', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipe_title: recipe.title,
          query: askChefQuery,
          ingredients: ingredients.map(ing => ing.name || ing.full),
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setChefResponse(data.response || data.substitution || 'Sorry, I couldn\'t help with that.')
      setAskChefQuery('') // Clear input after getting response
    } catch (err) {
      console.error('Error asking chef:', err)
      setChefResponse('Sorry, I couldn\'t reach the chef right now. Please try again.')
    } finally {
      setIsAskingChef(false)
    }
  }

  return (
    <>
      {/* Compact Card - Initial View - Only Name, Match %, Nutrition Tags */}
      <div
        className={`bg-emerald-50/50 rounded-[40px] shadow-sm overflow-hidden cursor-pointer transition-transform hover:scale-[1.02] ${
          isSoftViolation ? 'border-2 border-amber-400' : 'border border-emerald-100'
        }`}
        onClick={() => setIsModalOpen(true)}
      >
        {/* Image from Spoonacular API */}
        <div className="relative w-full h-48 lg:h-64 bg-gradient-to-br from-emerald-100 to-emerald-200">
          {imageUrl && !imageError ? (
            <img
              src={imageUrl}
              alt={recipe.title}
              className="w-full h-full object-cover rounded-t-[40px]"
              onError={handleImageError}
            />
          ) : (
            /* Generic food icon fallback if image is missing or fails to load */
            <div className="w-full h-full flex items-center justify-center rounded-t-[40px] bg-gradient-to-br from-emerald-100 via-emerald-50 to-white">
              <div className="text-center p-6">
                <div className="text-6xl mb-2">🍽️</div>
                <div className="text-emerald-900 font-semibold text-sm">Recipe</div>
              </div>
            </div>
          )}
          
          {/* Match Score Badge - Overlay on Image */}
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg">
            <span className="text-sm font-bold text-emerald-900">{matchScore}</span>
          </div>
        </div>

        {/* Card Content - Clean and Minimal */}
        <div className="p-6">
          {/* Title */}
          <h3 className="text-xl font-bold text-emerald-900 mb-3 line-clamp-2">
            {recipe.title}
          </h3>

          {/* Nutritional Tags */}
          {nutritionalTags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {nutritionalTags.map((tag, idx) => (
                <span
                  key={idx}
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${tag.color}`}
                >
                  {tag.label}
                </span>
              ))}
            </div>
          )}

          {/* Click to Expand Hint */}
          <div className="mt-4 pt-4 border-t border-emerald-200">
            <button className="text-sm text-emerald-600 font-semibold hover:text-emerald-700 transition-colors">
              View Full Recipe →
            </button>
          </div>
        </div>
      </div>

      {/* Modal - Expanded View */}
      {isModalOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setIsModalOpen(false)}
        >
          <div
            className="bg-white rounded-[40px] shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="relative h-64 lg:h-80 bg-gradient-to-br from-emerald-100 to-emerald-200">
              {imageUrl && !imageError ? (
                <img
                  src={imageUrl}
                  alt={recipe.title}
                  className="w-full h-full object-cover"
                  onError={handleImageError}
                />
              ) : (
                /* Generic food icon fallback if image is missing or fails to load */
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-emerald-100 via-emerald-50 to-white">
                  <div className="text-center p-6">
                    <div className="text-6xl mb-2">🍽️</div>
                    <div className="text-emerald-900 font-semibold text-sm">Recipe</div>
                  </div>
                </div>
              )}
              {/* Match Score Badge */}
              <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg">
                <span className="text-sm font-bold text-emerald-900">{matchScore}</span>
              </div>
              {/* Close Button */}
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-full w-10 h-10 flex items-center justify-center shadow-lg hover:bg-white transition-colors"
              >
                ✕
              </button>
              {/* Title Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-6">
                <h2 className="text-2xl lg:text-3xl font-bold text-white mb-2">
                  {recipe.title}
                </h2>
                <div className="flex items-center gap-4 text-white/90 text-sm">
                  {readyTime > 0 && (
                    <div className="flex items-center">
                      <span className="mr-2">⏱️</span>
                      <span>{readyTime} mins</span>
                    </div>
                  )}
                  <div className="flex items-center">
                    <span className="mr-2">📊</span>
                    <span>Match: {matchScore}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Content - Scrollable */}
            <div className="flex-1 overflow-y-auto p-6 lg:p-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Left: Ingredients */}
                <div className="bg-emerald-50/50 rounded-[40px] p-6 shadow-sm">
                  <h3 className="text-lg font-semibold text-emerald-900 mb-4 pb-2 border-b border-emerald-200">
                    Ingredients
                  </h3>
                  <ul className="space-y-2 text-sm text-gray-700">
                    {ingredients.length > 0 ? (
                      ingredients.map((ing, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-emerald-600 mr-2">•</span>
                          <span>{ing.full || ing.name || 'Ingredient'}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-gray-400 italic">No ingredients listed</li>
                    )}
                  </ul>

                  {/* Chef's Note / Substitution */}
                  {requiresValidation && (
                    <div className="mt-6 pt-4 border-t border-emerald-200">
                      <button
                        onClick={() => setShowSubstitution(!showSubstitution)}
                        className="inline-flex items-center px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-semibold hover:bg-amber-200 transition-colors"
                      >
                        👨‍🍳 Chef's Note
                      </button>
                      {showSubstitution && violationNote && (
                        <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-900">
                          <p className="font-semibold mb-1">Substitution needed:</p>
                          <p>{violationNote}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Nutritional Tags */}
                  {nutritionalTags.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-emerald-200">
                      <div className="flex flex-wrap gap-2">
                        {nutritionalTags.map((tag, idx) => (
                          <span
                            key={idx}
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${tag.color}`}
                          >
                            {tag.label}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Right: Instructions */}
                <div className="bg-emerald-50/50 rounded-[40px] p-6 shadow-sm">
                  <h3 className="text-lg font-semibold text-emerald-900 mb-4 pb-2 border-b border-emerald-200">
                    Instructions
                  </h3>
                  <div className="text-sm text-gray-700">
                    {instructionSteps && instructionSteps.length > 0 ? (
                      <ol className="space-y-3">
                        {instructionSteps.map((step, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-600 text-white text-xs font-bold flex items-center justify-center mr-3 mt-0.5">
                              {idx + 1}
                            </span>
                            <span className="flex-1">{step}</span>
                          </li>
                        ))}
                      </ol>
                    ) : recipe.instructions ? (
                      <div className="whitespace-pre-line">{recipe.instructions}</div>
                    ) : (
                      <p className="text-gray-400 italic">No instructions available</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Ask Chef Box - At bottom of modal */}
              <div className="px-6 lg:px-8 pb-6 lg:pb-8 pt-4 border-t border-emerald-200">
                <div className="bg-emerald-50/50 rounded-[40px] p-6 shadow-sm">
                  <h3 className="text-lg font-semibold text-emerald-900 mb-3">
                    👨‍🍳 Ask Chef
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Missing an ingredient? Ask for a substitution!
                  </p>
                  
                  <form onSubmit={handleAskChef} className="space-y-3">
                    <input
                      type="text"
                      value={askChefQuery}
                      onChange={(e) => setAskChefQuery(e.target.value)}
                      placeholder="e.g., I don't have yogurt"
                      className="w-full px-4 py-2 border border-emerald-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white text-sm"
                      disabled={isAskingChef}
                    />
                    <button
                      type="submit"
                      disabled={isAskingChef || !askChefQuery.trim()}
                      className="w-full px-4 py-2 bg-emerald-600 text-white rounded-2xl font-semibold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                    >
                      {isAskingChef ? 'Asking Chef...' : 'Ask Chef'}
                    </button>
                  </form>

                  {chefResponse && (
                    <div className="mt-4 p-4 bg-white border border-emerald-200 rounded-2xl text-sm text-gray-700">
                      <p className="font-semibold text-emerald-900 mb-2">Chef's Response:</p>
                      <p className="whitespace-pre-line">{chefResponse}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default RecipeCard
