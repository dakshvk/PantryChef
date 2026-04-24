# PantryChef Backend

**FastAPI | Python 3.9+ | Gemini 2.0 Flash | Spoonacular API**

---

## What This Is

The backend is the part of PantryChef that does the actual thinking. It is a FastAPI server that sits between the React frontend and two external services — Spoonacular for recipe data and Google Gemini for AI reasoning — and coordinates them through a pipeline I designed to handle the cases where either service falls short on its own.

The short version: Spoonacular has 360,000+ recipes but imperfect tagging. Gemini is good at reasoning but should not be trusted without validation. The backend combines them so that each one covers the other's weaknesses.

---

## Files and What They Do

```
backend/
    main.py                       FastAPI server, route definitions, startup
    app_orchestrator.py           Coordinates the full pipeline end to end
    pantry_chef_api.py            Spoonacular client with two-pass fallback search
    Logic.py                      Deterministic scoring and filtering (1000+ lines)
    Gemini_recipe_validator.py    Semantic classifier and dietary safety validator
    gemini_integration.py         Substitution logic and recommendation pitches
    substitution_helper.py        Combines API substitution data with Gemini output

    test_semantic_fallback.py     Unit test for the two-pass filtering system
    test_full_semantic_fallback.py Integration test for the full pipeline
    debug_logic.py                Debug script for Logic.py processing
    debug_recipe_flags.py         Debug script for confidence flag verification

    requirements.txt
    .env.example
    README.md
```

---

## Setup

### Prerequisites

- Python 3.9 or higher
- A Spoonacular API key — free tier available at spoonacular.com/food-api (150 points per day)
- A Gemini API key — free tier available at ai.google.dev

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your keys to the .env file:

```
SPOONACULAR_API_KEY=your_spoonacular_key
GEMINI_API_KEY=your_gemini_key
```

```bash
python main.py
```

The server runs at http://localhost:8000. Interactive API documentation is at http://localhost:8000/docs.

---

## The Pipeline

Every request to /recommend runs through three stages in sequence.

### Stage 1: Recipe Discovery (pantry_chef_api.py)

The Spoonacular client does not just fire a single query. It runs a two-pass search designed to avoid returning zero results.

Pass 1 applies all filters the user specified — cuisine, diet, and intolerances — and asks for recipes with strict tag matching. If that comes back with fewer than five results, which happens frequently because Spoonacular's tagging is inconsistent, Pass 2 drops the cuisine constraint and retrieves a broader candidate set. Those candidates get marked with a lower initial confidence score and flagged for Gemini validation downstream.

When a user has ten or more ingredients, the client also runs ingredient prioritization before searching. Gemini categorizes the ingredients into core (things that define the dish) and secondary (spices, garnishes, finishing ingredients). The search runs first with all ingredients, and if results are low, reruns with only core ingredients. This typically produces significantly more results without changing what the user actually wants to cook.

The batch enrichment endpoint (`informationBulk`) pulls full ingredient lists, nutritional data, and instructions for the top results in a single API call rather than one call per recipe. This reduces Spoonacular quota usage by around 70% compared to individual requests.

### Stage 2: Scoring and Filtering (Logic.py)

Every recipe that comes out of the discovery stage passes through the Logic Engine. This is deterministic — no AI involved, just code. It runs in this order:

**Hard Executioner**: Scans the recipe's extended ingredient list against a keyword set covering 70+ meat terms, seafood, dairy, and eggs. This check only reads ingredient data, not recipe titles or descriptions. A recipe titled "Mushroom Shawarma" passes. A recipe titled "Chicken Shawarma" fails at the ingredient scan, not the title scan.

**Intolerance Auditor**: Checks ingredients against allergen categories (dairy, gluten, nuts, soy) with a safe-word layer. Finding "milk" does not immediately reject a recipe if the actual ingredient is "almond milk" or "oat milk." Those ambiguous cases are flagged for Gemini rather than hard-rejected, because a hard reject on "coconut cream" for a dairy-free user would be wrong.

**Smart Scoring**: Recipes that pass safety filtering get scored across four dimensions — ingredient match percentage, time, difficulty, and skill level. The weights depend on the user's selected profile.

| Profile | What It Prioritizes |
|---|---|
| Balanced | Equal weight between ingredient match and missing ingredients |
| Minimal Shopper | Minimizes the number of ingredients you need to buy |
| Pantry Cleaner | Maximizes the number of your existing ingredients used |

**Mood Modifiers**: After scoring, mood shifts the ranking. Tired users get time and effort weighted more heavily, with a bonus for anything under 20 minutes. Energetic users get complexity and technique weighted up, with a bonus for recipes over 60 minutes. Casual is neutral across all factors.

### Stage 3: Gemini Validation (Gemini_recipe_validator.py + gemini_integration.py)

Rescue candidates and allergen-flagged recipes go to Gemini. The model does three things:

First, semantic validation. It evaluates whether a recipe is genuinely appropriate for the requested cuisine based on its actual ingredients, not just its tags. A pasta dish with tomatoes, basil, and mozzarella that is missing the Italian tag in Spoonacular gets evaluated on its ingredients and, if confirmed, has its confidence score upgraded from 0.6 to 0.9.

Second, safety validation on flagged edge cases. The model reads the full ingredient context and makes a binary judgment — safe or not safe. "Heavy cream" in a dairy-free recipe is rejected. "Coconut cream" in the same recipe is approved.

Third, the recommendation pitch. The top-ranked recipe's match data gets translated into a human-readable explanation that appears in the AI Chef box on the frontend.

A constitutional AI layer runs cross-validation on Gemini outputs to catch hallucinations before they reach the response.

---

## Confidence Score System

Every recipe in the API response includes a `match_confidence` field.

| Value | Source | Meaning |
|---|---|---|
| 1.0 | Pass 1 strict filtering | All requested tags matched in Spoonacular |
| 0.9 | Gemini upgrade | Failed strict tag matching but confirmed semantically appropriate |
| 0.6 | Pass 2 rescue | Did not pass strict filtering, Gemini validation pending or incomplete |

---

## Dietary Safety in Detail

Safety is the one thing in this system that does not get relaxed under any fallback condition. A recipe that fails the Hard Executioner never reaches the user regardless of how good its ingredient match is. A recipe that fails Gemini safety validation gets dropped even if it passed keyword detection.

The three-layer design handles the cases each layer cannot:

Keywords catch clear violations fast without burning Gemini quota. The safe-word check handles compound ingredients that would be false positives under pure keyword matching. Gemini handles the cases that require reading context — ingredients with the same word meaning different things depending on what surrounds them.

---

## API Quota Management

Spoonacular's free tier allows 150 points per day. A single `findByIngredients` call costs 1 point. An individual `information` call costs 1 point per recipe. The bulk endpoint costs roughly 3 points for up to 20 recipes — the same data that would otherwise cost 20 points.

The pipeline tracks cumulative usage per session and logs a warning when remaining quota drops below 20 points. For development work, the Spoonacular client has a mock data mode that returns static fixtures without making live API calls.

---

## API Endpoints

### POST /recommend

Accepts ingredient list, mood, dietary requirements, intolerances, user profile, and number of results. Returns ranked recipes with confidence scores, nutritional summaries, and the AI pitch.

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["tomato", "basil", "mozzarella"],
    "cuisine": "italian",
    "diet": "vegetarian",
    "mood": "casual",
    "number": 10
  }'
```

Example response structure:

```json
{
  "recipes": [
    {
      "id": 636958,
      "title": "Caprese Sticks",
      "match_confidence": 1.0,
      "needs_semantic_validation": false,
      "time": 45,
      "difficulty": "easy",
      "nutrition_summary": {
        "protein": 1.59,
        "calories": 146.51
      }
    }
  ],
  "pitch": "Based on what you have, Caprese Sticks are the cleanest match...",
  "metadata": {
    "total_processed": 5,
    "ai_enriched": true
  }
}
```

### POST /ask-chef

Accepts recipe title, a question about a missing ingredient, and the user's current ingredient list. Returns a pantry-aware substitution with a usage tip.

```bash
curl -X POST http://localhost:8000/ask-chef \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_title": "Stir Fry",
    "query": "I do not have soy sauce",
    "ingredients": ["balsamic vinegar", "salt", "garlic"]
  }'
```

### GET /health

Returns server status and basic diagnostics. Useful for confirming both API keys are loaded and the server is running before sending requests from the frontend.

---

## Testing

```bash
# Two-pass filtering unit test
python test_semantic_fallback.py

# Full pipeline integration test
python test_full_semantic_fallback.py

# Logic.py processing debug
python debug_logic.py

# Confidence flag verification
python debug_recipe_flags.py
```

The semantic fallback test confirms the system finds rescue candidates when strict filtering returns zero results. Expected output for an Italian plus Vegetarian query with imperfect Spoonacular tags:

```
TEST: Semantic Fallback System
Total recipes: 6
Golden matches (1.0): 0
Rescue candidates (0.6): 6
Rescue Candidates sent to Gemini:
  - Farfalle with Tomatoes, Basil and Mozzarella
    Reason: Missing tags: cuisine=italian
TEST PASSED
```

---

## Configuration Options

```bash
SPOONACULAR_API_KEY=required
GEMINI_API_KEY=required

MAX_RECIPES_FETCH=20
API_TIMEOUT=15
LOG_LEVEL=INFO
```

User-level settings passed per request:

```python
{
    'user_profile': 'balanced',        # balanced, minimal_shopper, pantry_cleaner
    'mood': 'casual',                  # tired, casual, energetic
    'max_time_minutes': 120,
    'max_missing_ingredients': 10,
    'dietary_requirements': [],
    'intolerances': [],
    'skill_level': 50                  # 0 to 100
}
```

---

## Dependencies

```
fastapi>=0.104.1
uvicorn>=0.24.0
requests>=2.31.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
pydantic>=2.4.2
```

---

## Known Constraints

Spoonacular's tag data is inconsistent. A recipe that is clearly Italian by ingredients may not carry the Italian cuisine tag in their database. This is the core reason the semantic fallback system exists — the API alone cannot be trusted for strict cuisine filtering.

Gemini calls add latency. The full pipeline with semantic validation and pitch generation takes around five to six seconds. Requests that hit only Pass 1 with good tag coverage complete in two to three seconds. This is a known tradeoff between accuracy and speed.

The free Spoonacular tier limits real usage to a few full pipeline runs per day before quota is exhausted. The mock data mode covers development and testing without burning quota.