# PantryChef Frontend

**React 18.2 | Vite 5.0 | Tailwind CSS 3.4 | JavaScript ES6+**

---

## What This Is

The frontend is a React single-page application that gives users a way to interact with the PantryChef backend. The interface handles ingredient input, filter selection, and recipe browsing — and it stays out of the way while doing it. The design goal was functional and clean, not flashy. A sidebar for inputs, a grid for results, a modal for detail, and an AI pitch box at the top that translates the backend's scoring math into a sentence a person actually wants to read.

---

## Component Structure

```
src/
    App.jsx                 Root component, state management, API calls
    main.jsx                React entry point
    index.css               Global styles and Tailwind imports
    components/
        Sidebar.jsx         Ingredient input, mood, dietary filters, profile selector
        RecipeGrid.jsx      Responsive card grid with loading skeleton
        RecipeCard.jsx      Individual recipe card with expandable modal
        AIPitchBox.jsx      AI-generated recommendation display
        HeroSection.jsx     Landing section shown before first search
```

### How Data Flows

State lives in App.jsx. The user builds their ingredient list and filter selections in the Sidebar. When they hit search, App.jsx sends a POST request to the backend, receives the ranked recipe list and AI pitch, and passes them down to RecipeGrid and AIPitchBox as props. RecipeCard handles its own modal state locally — opening and closing detail views does not touch App-level state.

```
App.jsx
    Sidebar.jsx         reads filters from props, calls setIngredients and setFilters
    AIPitchBox.jsx      receives pitch string and top recipe object
    RecipeGrid.jsx      receives recipes array and loading boolean
        RecipeCard.jsx  manages isModalOpen locally
```

---

## Setup

### Prerequisites

- Node.js 16 or higher

### Installation

```bash
cd frontend
npm install
npm run dev
```

The development server runs at http://localhost:3000 with hot module replacement enabled through Vite.

### Build for Production

```bash
npm run build
npm run preview
```

---

## Components

### App.jsx

Manages all application state and the two API integrations.

State:

```javascript
const [ingredients, setIngredients] = useState([]);
const [recipes, setRecipes] = useState([]);
const [filters, setFilters] = useState({
    mood: 'casual',
    dietaryRequirements: [],
    intolerances: [],
    userProfile: 'balanced'
});
const [aiPitch, setAiPitch] = useState('');
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

Recipe fetch:

```javascript
const fetchRecipes = async () => {
    try {
        setLoading(true);
        setError(null);

        const response = await fetch('http://localhost:8000/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ingredients,
                mood: filters.mood,
                dietary_requirements: filters.dietaryRequirements,
                intolerances: filters.intolerances,
                user_profile: filters.userProfile,
                number: 20
            })
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        setRecipes(data.recipes);
        setAiPitch(data.pitch);

    } catch (err) {
        setError('Could not load recipes. Check that the backend is running.');
    } finally {
        setLoading(false);
    }
};
```

Substitution fetch:

```javascript
const askChef = async (recipeTitle, query) => {
    try {
        const response = await fetch('http://localhost:8000/ask-chef', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipe_title: recipeTitle,
                query,
                ingredients
            })
        });

        const data = await response.json();
        return data.response;

    } catch (err) {
        return 'Could not get a substitution right now. Try again.';
    }
};
```

### Sidebar.jsx

Handles all user input before a search is triggered. Ingredients are entered as text and added as tags on Enter or comma. Each tag has a remove button. The mood selector, dietary requirement checkboxes, intolerance checkboxes, and profile selector all update the filters object in App.jsx.

```javascript
<div className="bg-white rounded-lg shadow-lg p-6 sticky top-4">
    <h2 className="text-2xl font-bold text-emerald-700 mb-4">
        Your Pantry
    </h2>

    <input
        type="text"
        placeholder="Add an ingredient and press Enter"
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
        onKeyPress={handleAddIngredient}
    />

    <div className="flex flex-wrap gap-2 mt-3">
        {ingredients.map((ing, idx) => (
            <span key={idx} className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                {ing}
                <button onClick={() => removeIngredient(idx)}>x</button>
            </span>
        ))}
    </div>

    <select className="w-full px-4 py-2 border border-gray-300 rounded-lg mt-4">
        <option value="tired">Tired — Quick and easy</option>
        <option value="casual">Casual — Moderate effort</option>
        <option value="energetic">Energetic — Complexity is fine</option>
    </select>

    <button
        onClick={fetchRecipes}
        className="w-full bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 transition-colors font-semibold mt-6"
    >
        {loading ? 'Searching...' : 'Find Recipes'}
    </button>
</div>
```

### RecipeGrid.jsx

Renders the recipe cards in a responsive three-column grid. While loading, it renders a skeleton grid of nine placeholder cards using animated pulse styling so the layout does not shift when results arrive.

```javascript
{loading && (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(9)].map((_, i) => (
            <div key={i} className="animate-pulse">
                <div className="bg-gray-300 h-48 rounded-t-lg"></div>
                <div className="bg-white p-4">
                    <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                </div>
            </div>
        ))}
    </div>
)}
```

### RecipeCard.jsx

Displays the recipe image, title, confidence badge, time, difficulty, and a safety flag if the backend marked the recipe as requiring AI validation. Clicking the card opens a modal with the full ingredient list, step-by-step instructions, nutritional data, and the Ask Chef button.

The confidence badge color reflects the score tier:

```javascript
<div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-3 ${
    recipe.match_confidence >= 0.9 ? 'bg-green-100 text-green-800' :
    recipe.match_confidence >= 0.7 ? 'bg-yellow-100 text-yellow-800' :
    'bg-orange-100 text-orange-800'
}`}>
    {recipe.match_confidence === 1.0 ? 'Strong Match' :
     recipe.match_confidence === 0.9 ? 'AI Confirmed' : 'Possible Match'}
</div>
```

The safety flag appears when `requires_ai_validation` is true on the recipe object:

```javascript
{recipe.requires_ai_validation && (
    <div className="mt-3 text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded">
        Contains borderline ingredients — reviewed by AI
    </div>
)}
```

### AIPitchBox.jsx

Displays the AI-generated recommendation text alongside a preview of the top-ranked recipe. The pitch comes directly from the backend as a string — the component just renders it.

```javascript
<div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg shadow-lg p-6 mb-8">
    <h3 className="font-bold text-lg text-emerald-800 mb-2">
        AI Chef Recommendation
    </h3>
    <p className="text-gray-700 leading-relaxed">
        {pitch}
    </p>

    {topRecipe && (
        <div className="mt-4 flex items-center gap-3">
            <img
                src={topRecipe.image}
                alt={topRecipe.title}
                className="w-20 h-20 rounded-lg object-cover"
            />
            <div>
                <p className="font-semibold text-gray-800">{topRecipe.title}</p>
                <p className="text-sm text-gray-600">
                    {topRecipe.time} min
                </p>
            </div>
        </div>
    )}
</div>
```

---

## Styling

Tailwind CSS handles all styling. The custom theme extends the default emerald color palette with Inter as the primary font.

```javascript
// tailwind.config.js
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx}",
    ],
    theme: {
        extend: {
            colors: {
                emerald: {
                    50:  '#ecfdf5',
                    100: '#d1fae5',
                    500: '#10b981',
                    600: '#059669',
                    700: '#047857',
                    800: '#065f46',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
```

Two reusable component classes are defined in index.css:

```css
@layer components {
    .btn-primary {
        @apply bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 transition-colors font-semibold;
    }

    .card {
        @apply bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow;
    }
}
```

---

## Connecting to the Backend

The frontend expects the backend running at http://localhost:8000. If you change the backend port, update the fetch URLs in App.jsx. There is no environment variable abstraction for the API URL currently — it is hardcoded in two places, the fetchRecipes function and the askChef function.

CORS is handled on the backend side. The frontend does not require any proxy configuration in Vite for local development.

---

## Dependencies

```json
{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "vite": "^5.0.8",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.16"
}
```

---

## What Is Not Built Yet

Ingredient autocomplete is planned but not implemented. Right now, you type the ingredient name in full and press Enter.

Filter persistence across page reloads is not implemented. State resets on refresh.

The dark mode toggle referenced in the component documentation is a future feature. Only the light theme exists currently.

Component-level testing with React Testing Library is not set up. The test infrastructure would need to be installed separately.

---

## Deployment

For a production build:

```bash
npm run build
```

This outputs a static dist/ directory that can be served from any static hosting service — Vercel, Netlify, GitHub Pages, AWS S3, Firebase Hosting. The backend needs to be deployed separately and the fetch URLs in App.jsx updated to point to the production backend URL.