# PantryChef Frontend

> **React-powered user interface with Tailwind CSS styling, real-time recipe discovery, and interactive AI-powered recommendations**

A modern, responsive web application built with React 18.2 and Tailwind CSS that provides an intuitive interface for discovering recipes, managing dietary preferences, and receiving intelligent substitution recommendations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Component Architecture](#component-architecture)
- [Installation](#installation)
- [Development](#development)
- [Components Documentation](#components-documentation)
- [Styling & Theming](#styling--theming)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Performance Optimization](#performance-optimization)
- [Testing](#testing)
- [Build & Deployment](#build--deployment)

---

## Overview

The PantryChef frontend is a **React 18.2 single-page application** built with:

- **Vite**: Lightning-fast build tool with hot module replacement (HMR)
- **Tailwind CSS**: Utility-first CSS framework with custom emerald chef theme
- **Component-Based Architecture**: Reusable, maintainable React components
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Real-Time Updates**: Live recipe refresh with configurable filters

### Tech Stack

- React 18.2.0
- JavaScript (ES6+)
- Tailwind CSS 3.4.1
- Vite 5.0.8
- PostCSS 8.4.33

---

## Features

### User Interface

- **Responsive Grid Layout**: Adaptive recipe cards that reflow based on screen size
- **Interactive Modals**: Expandable recipe details with full ingredients and instructions
- **Real-Time Search**: Instant recipe updates as filters change
- **AI Pitch Box**: Natural language recommendations from AI Chef
- **Dietary Safety Indicators**: Visual flags for recipes requiring validation

### Accessibility

- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Scalable Fonts**: Font sizes from 80%-150% based on user preference
- **High Contrast**: WCAG AA compliant color ratios
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **Dark/Light Theme**: Toggle between themes (future feature)

### User Experience

- **Ingredient Autocomplete**: Smart suggestions as you type (future feature)
- **Filter Persistence**: Remembers user preferences across sessions
- **Loading States**: Skeleton screens and spinners for better UX
- **Error Handling**: User-friendly error messages with retry options
- **Smooth Animations**: CSS transitions for polished interactions

---

## Component Architecture

```
src/
├── App.jsx                    # Root component & main layout
├── main.jsx                   # React entry point
├── index.css                  # Global styles + Tailwind imports
└── components/
    ├── Sidebar.jsx            # Ingredient input & filters
    ├── RecipeGrid.jsx         # Recipe card grid layout
    ├── RecipeCard.jsx         # Individual recipe card with modal
    ├── AIPitchBox.jsx         # AI recommendation display
    └── HeroSection.jsx        # Landing page hero (optional)
```

### Component Flow

```
App.jsx (Root)
│
├─── Sidebar.jsx (Filters)
│    └─── Ingredient Input
│    └─── Mood Selector
│    └─── Dietary Filters
│    └─── User Profile Selector
│
├─── AIPitchBox.jsx (AI Recommendations)
│    └─── Displays AI-generated pitch
│
└─── RecipeGrid.jsx (Results)
     └─── RecipeCard.jsx (×20)
          └─── Image
          └─── Title
          └─── Match Score
          └─── Tags
          └─── Modal (on click)
               └─── Full Ingredients
               └─── Instructions
               └─── Nutrition
               └─── Ask Chef Button
```

---

## Installation

### Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

### Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open browser
# Visit http://localhost:3000
```

### Dependencies

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

## Development

### Development Server

```bash
npm run dev
# Starts Vite dev server with hot module replacement
# Available at http://localhost:3000
```

### Build for Production

```bash
npm run build
# Creates optimized production build in dist/
```

### Preview Production Build

```bash
npm run preview
# Preview production build locally
```

---

## Components Documentation

### App.jsx - Root Component

**Purpose**: Main application layout and state management

**State Management**:
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
```

**Key Methods**:
```javascript
const fetchRecipes = async () => {
    setLoading(true);
    
    const response = await fetch('http://localhost:8000/recommend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            ingredients,
            mood: filters.mood,
            dietary_requirements: filters.dietaryRequirements,
            intolerances: filters.intolerances,
            user_profile: filters.userProfile,
            number: 20
        })
    });
    
    const data = await response.json();
    setRecipes(data.recipes);
    setAiPitch(data.pitch);
    setLoading(false);
};
```

### Sidebar.jsx - Filter Panel

**Purpose**: Ingredient input and filter controls

**Props**: None (uses state from parent via props drilling or context)

**Features**:
- Multi-input ingredient field with tag display
- Mood selector (Tired, Casual, Energetic)
- Dietary requirement checkboxes (Vegetarian, Vegan)
- Intolerance checkboxes (Dairy, Gluten, Nuts, Soy)
- User profile selector (Balanced, Minimal Shopper, Pantry Cleaner)
- Clear all button
- Search button with loading state

**Example Code**:
```javascript
<div className="bg-white rounded-lg shadow-lg p-6 sticky top-4">
    <h2 className="text-2xl font-bold text-emerald-700 mb-4">
        Your Pantry
    </h2>
    
    {/* Ingredient Input */}
    <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
            Add Ingredients
        </label>
        <input
            type="text"
            placeholder="e.g., chicken, rice, garlic"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            onKeyPress={handleAddIngredient}
        />
        
        {/* Ingredient Tags */}
        <div className="flex flex-wrap gap-2 mt-3">
            {ingredients.map((ing, idx) => (
                <span key={idx} className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                    {ing}
                    <button onClick={() => removeIngredient(idx)}>×</button>
                </span>
            ))}
        </div>
    </div>
    
    {/* Mood Selector */}
    <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
            Cooking Mood
        </label>
        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg">
            <option value="tired">Tired (Quick & Easy)</option>
            <option value="casual">Casual (Moderate)</option>
            <option value="energetic">Energetic (Complex OK)</option>
        </select>
    </div>
    
    {/* Search Button */}
    <button
        onClick={fetchRecipes}
        className="w-full bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 transition-colors font-semibold"
    >
        {loading ? 'Searching...' : 'Find Recipes'}
    </button>
</div>
```

### RecipeGrid.jsx - Grid Layout

**Purpose**: Displays recipe cards in responsive grid

**Props**:
```javascript
{
    recipes: Array,     // Recipe data from API
    loading: Boolean    // Loading state
}
```

**Layout**:
```javascript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {recipes.map(recipe => (
        <RecipeCard key={recipe.id} recipe={recipe} />
    ))}
</div>
```

**Loading State**:
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

### RecipeCard.jsx - Individual Recipe

**Purpose**: Displays recipe preview with expandable modal

**Props**:
```javascript
{
    recipe: {
        id: Number,
        title: String,
        image: String,
        match_confidence: Number,
        time: Number,
        used_ingredients: Number,
        missing_ingredients: Number,
        difficulty: String,
        nutrition_summary: Object,
        extendedIngredients: Array,
        instructions: String,
        requires_ai_validation: Boolean
    }
}
```

**Features**:
- Recipe image with fallback
- Match confidence badge (color-coded by score)
- Time & difficulty indicators
- Dietary safety flag (if requires_ai_validation)
- Modal with full details on click

**Example Code**:
```javascript
const [isModalOpen, setIsModalOpen] = useState(false);

return (
    <>
        {/* Card Preview */}
        <div
            onClick={() => setIsModalOpen(true)}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
        >
            {/* Image */}
            <img
                src={recipe.image}
                alt={recipe.title}
                className="w-full h-48 object-cover"
            />
            
            {/* Content */}
            <div className="p-4">
                {/* Title */}
                <h3 className="font-bold text-lg text-gray-800 mb-2">
                    {recipe.title}
                </h3>
                
                {/* Confidence Badge */}
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-3 ${
                    recipe.match_confidence >= 80 ? 'bg-green-100 text-green-800' :
                    recipe.match_confidence >= 65 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-orange-100 text-orange-800'
                }`}>
                    {recipe.match_confidence}% Match
                </div>
                
                {/* Meta Info */}
                <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>🕐 {recipe.time} min</span>
                    <span>✨ {recipe.difficulty}</span>
                </div>
                
                {/* Safety Flag */}
                {recipe.requires_ai_validation && (
                    <div className="mt-3 text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded">
                        ⚠️ Contains borderline ingredients - AI validated
                    </div>
                )}
            </div>
        </div>
        
        {/* Modal */}
        {isModalOpen && (
            <RecipeModal
                recipe={recipe}
                onClose={() => setIsModalOpen(false)}
            />
        )}
    </>
);
```

### AIPitchBox.jsx - AI Recommendations

**Purpose**: Displays AI-generated recipe pitch

**Props**:
```javascript
{
    pitch: String,      // AI-generated recommendation
    topRecipe: Object   // Top-ranked recipe data
}
```

**Example Code**:
```javascript
<div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg shadow-lg p-6 mb-8">
    <div className="flex items-start gap-4">
        {/* AI Chef Icon */}
        <div className="bg-emerald-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-2xl flex-shrink-0">
            👨‍🍳
        </div>
        
        {/* Pitch Content */}
        <div>
            <h3 className="font-bold text-lg text-emerald-800 mb-2">
                AI Chef Recommends
            </h3>
            <p className="text-gray-700 leading-relaxed">
                {pitch}
            </p>
            
            {/* Top Recipe Preview */}
            {topRecipe && (
                <div className="mt-4 flex items-center gap-3">
                    <img
                        src={topRecipe.image}
                        alt={topRecipe.title}
                        className="w-20 h-20 rounded-lg object-cover"
                    />
                    <div>
                        <p className="font-semibold text-gray-800">
                            {topRecipe.title}
                        </p>
                        <p className="text-sm text-gray-600">
                            {topRecipe.time} min • {topRecipe.match_confidence}% match
                        </p>
                    </div>
                </div>
            )}
        </div>
    </div>
</div>
```

---

## Styling & Theming

### Tailwind Configuration

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
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
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

### Global Styles

```css
/* index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

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

## State Management

### Local State (useState)

```javascript
// App.jsx
const [ingredients, setIngredients] = useState([]);
const [recipes, setRecipes] = useState([]);
const [filters, setFilters] = useState({
    mood: 'casual',
    dietaryRequirements: [],
    intolerances: [],
    userProfile: 'balanced'
});
```

### Future: Context API

```javascript
// contexts/RecipeContext.jsx (future enhancement)
const RecipeContext = createContext();

export const RecipeProvider = ({ children }) => {
    const [state, setState] = useState(initialState);
    
    return (
        <RecipeContext.Provider value={{state, setState}}>
            {children}
        </RecipeContext.Provider>
    );
};
```

---

## API Integration

### Fetch Recipes

```javascript
const fetchRecipes = async () => {
    try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('http://localhost:8000/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
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
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setRecipes(data.recipes);
        setAiPitch(data.pitch);
        
    } catch (error) {
        console.error('Error fetching recipes:', error);
        setError('Failed to load recipes. Please try again.');
    } finally {
        setLoading(false);
    }
};
```

### Ask Chef (Substitution)

```javascript
const askChef = async (recipeTitle, query) => {
    try {
        const response = await fetch('http://localhost:8000/ask-chef', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                recipe_title: recipeTitle,
                query,
                ingredients
            })
        });
        
        const data = await response.json();
        return data.response;
        
    } catch (error) {
        console.error('Error getting substitution:', error);
        return 'Sorry, I couldn\'t find a good substitution right now.';
    }
};
```

---

## Performance Optimization

### Code Splitting

```javascript
// Lazy load components (future enhancement)
const RecipeModal = lazy(() => import('./components/RecipeModal'));
```

### Memoization

```javascript
// Prevent unnecessary re-renders
const MemoizedRecipeCard = memo(RecipeCard);
```

### Debouncing

```javascript
// Debounce search input (future enhancement)
const debouncedSearch = useDebounce(searchTerm, 500);
```

---

## Testing

### Component Testing

```bash
# Install testing libraries (future enhancement)
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

### Example Test

```javascript
// RecipeCard.test.jsx
import { render, screen } from '@testing-library/react';
import RecipeCard from './RecipeCard';

test('renders recipe title', () => {
    const recipe = {
        title: 'Pasta Carbonara',
        match_confidence: 85,
        time: 30
    };
    
    render(<RecipeCard recipe={recipe} />);
    expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
});
```

---

## Build & Deployment

### Production Build

```bash
npm run build
# Creates optimized build in dist/
```

### Deployment Options

#### Vercel (Recommended)
```bash
npm install -g vercel
vercel deploy
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### Static Hosting
```bash
# Copy dist/ folder to any static hosting service
# (GitHub Pages, AWS S3, Firebase Hosting, etc.)
```

---

**Frontend built with React, Tailwind CSS, and modern web technologies**