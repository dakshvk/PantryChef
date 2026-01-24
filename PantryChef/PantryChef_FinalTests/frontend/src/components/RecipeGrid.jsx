import RecipeCard from './RecipeCard'

const RecipeGrid = ({ recipes }) => {
  return (
    <div className="px-8 py-6 lg:py-8">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id || recipe.title} recipe={recipe} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default RecipeGrid

