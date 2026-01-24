import { useState } from 'react'
import Sidebar from './components/Sidebar'
import HeroSection from './components/HeroSection'
import AIPitchBox from './components/AIPitchBox'
import RecipeGrid from './components/RecipeGrid'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (searchParams) => {
    setLoading(true)
    setError(null)
    setResults(null)

    // Debug logging: Show what's being sent to backend
    console.log('📤 [App] Sending to backend:', searchParams)
    console.log('   - Mood:', searchParams.mood)
    console.log('   - Ingredients:', searchParams.ingredients)

    try {
      const response = await fetch('http://localhost:8000/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('📥 [App] Response from backend:', data)
      console.log('   - Recipes found:', data.recipes?.length || 0)
      setResults(data)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching recipes:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen w-full bg-white overflow-hidden">
      {/* SIDEBAR: Stays on the left, does not move */}
      <Sidebar onSearch={handleSearch} loading={loading} />

      {/* MAIN CONTENT: This scrolls while the sidebar stays put */}
      <main className="flex-1 h-full overflow-y-auto bg-white">
        <HeroSection />
        
        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="mx-8 mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-2xl">
            Error: {error}
          </div>
        )}

        {/* AI Pitch Box */}
        {results?.pitch && (
          <AIPitchBox pitch={results.pitch} />
        )}

        {/* Recipe Grid */}
        {results?.recipes && results.recipes.length > 0 && (
          <RecipeGrid recipes={results.recipes} />
        )}

        {/* No Results */}
        {results && results.recipes && results.recipes.length === 0 && (
          <div className="text-center py-20 text-emerald-900">
            <p className="text-xl">No recipes found. Try adjusting your ingredients or filters.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

