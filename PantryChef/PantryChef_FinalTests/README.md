Pantry # PantryChef Frontend

Modern React + Vite + Tailwind CSS frontend for PantryChef.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:3000`

## Features

- **Modern Chef Aesthetic**: Clean, welcoming design with amber/chef color scheme
- **Sidebar**: Input ingredients as tags, select mood with icons, set dietary toggles
- **Hero Section**: Big welcoming header
- **AI Pitch Box**: Displays Gemini's chef recommendation with high contrast
- **Recipe Grid**: Responsive (1 column mobile, 3 columns desktop)
- **Recipe Cards**: Show image, circular progress bar for match confidence, and "Chef's Note" badge for recipes needing validation
- **Flag, Don't Fail**: Recipes with safety_score 0.2 get amber border and "Substitution Required" label

## API Connection

The frontend connects to the FastAPI backend at `http://localhost:8000`.

Make sure your FastAPI server is running before starting the frontend.

