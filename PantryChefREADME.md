# PantryChef

**Python 3.9+** | **React 18.2** | **FastAPI** | **Gemini 2.0 Flash** | **MIT License**

---

## The Problem I Was Trying to Solve

I go to UCSB. I live in Isla Vista. My fridge has random stuff in it at the end of the week — half an onion, some garlic, leftover rice — and I either throw it out or make something bad with it. The USDA puts food waste in the United States at around 40% of the total food supply. That is not an abstract statistic for a college student; it shows up in every grocery run where you buy something specific for one recipe and then forget about the rest.

I wanted to build something that actually solves this. Not a recipe app that tells you to go buy six new things. Something that looks at what you already have and finds a real answer. That turned into PantryChef — a full-stack application that combines a live recipe database, a custom-built scoring engine, and Google Gemini 2.0 to match pantry ingredients to recipes, validate dietary safety, and suggest substitutions when you are still missing something.

This is a personal project. I built it to learn, to ship something real, and because the problem was worth solving.

---

## What It Actually Does

At its core, PantryChef takes a list of ingredients you have, applies your dietary restrictions and how you are feeling about cooking that day, and returns ranked recipes with an explanation of why each one fits. The ranking is not a black box — it runs through a deterministic scoring pipeline I wrote from scratch, then passes edge cases to Gemini for judgment calls that pure keyword matching cannot handle.

When the Spoonacular database does not have enough matches under strict filtering, the pipeline relaxes **non-safety** constraints and sends the extra candidates to Gemini for semantic validation. A recipe that is genuinely Italian in its ingredients but missing the Italian tag in the database still gets found and surfaced. Safety constraints are never relaxed to fill a thin result set: if screening out unsafe recipes leaves you with two, you get two.

Substitutions work the same way. If you are missing an ingredient, the app does not just tell you what the standard swap is. It looks at what you actually have and generates a substitution grounded in your pantry.

---

## Demo

### Dashboard and Ingredient Input

![GIPHY#1](https://github.com/user-attachments/assets/f5636b93-54ba-4c7b-85ef-2ddfc60951e5)

The sidebar handles ingredient entry, mood selection, dietary filters, and your ingredient-use profile. The recipe grid updates on search with confidence scores visible on each card.

### Live Search Results and Recipe Detail

![GIPHY4-ezgif com-optimize](https://github.com/user-attachments/assets/ca1e4621-f1cd-4acb-b7d5-7cbc5a8629da)

The AI pitch at the top translates scoring math into plain language. Each recipe card opens into a full modal with ingredients, step-by-step instructions, nutritional data, and the Ask Chef button.

### Gemini Substitution Recommendations

![GIPHY#3](https://github.com/user-attachments/assets/7be253fc-dc3c-460d-a637-3f8315d69ab8)

Ask Chef takes your missing ingredient, looks at what you have listed, and returns a pantry-aware substitution with a practical tip on how to use it.

---

## How the System Works

### Three-Stage Backend Pipeline

**Stage 1 — Discovery**

The Spoonacular client runs a two-pass search. The first pass applies all filters including cuisine, diet, and intolerances. If that returns fewer than five results, the second pass drops the cuisine constraint and retrieves a broader set of candidates marked as rescue candidates with a lower initial confidence score.

**Stage 2 — Scoring and Filtering**

The Logic Engine runs every recipe through a multi-layer evaluation. Dietary screening happens first, against a versioned canonical ingredient table (`backend/allergen_table.py`) rather than a keyword list — see Dietary Screening below. Recipes that are not excluded are scored on ingredient match, time, effort, difficulty and skill level according to one of three user profiles. Mood modifiers shift the weights: Tired weights shopping and effort more heavily, Energetic weights skill more and the clock less. Those weights are the only place a mood changes the ranking.

**Stage 3 — Gemini Validation**

Rescue candidates go to Gemini. The model evaluates whether a recipe is semantically appropriate for the requested cuisine and meal type, and it generates the recommendation pitch and the substitution responses.

Gemini is **not** in the safety path. It cannot mark a recipe safe, cannot clear an allergen match, and cannot lift an unverified recipe to verified. If Gemini is unavailable, times out, or returns something unparseable, every screening verdict is byte-identical to a run with no model configured — because no path runs from the model to a verdict at all. The model affects what you are told about a recipe, never whether you are allowed to see it.

### Frontend

Built in React 18.2 with Tailwind CSS. The layout is a sidebar-plus-grid structure. State lives in App.jsx and passes down through props. Components are Sidebar, RecipeGrid, RecipeCard, and AIPitchBox. The modal in RecipeCard handles the full recipe detail view and the Ask Chef interaction.

---

## Scoring Logic in Detail

### User Profiles

Three profiles change how the scoring formula weights ingredient match against missing ingredients.

| Profile | What It Optimizes For |
|---|---|
| Balanced | Equal weight between what you have and what you do not |
| Minimal Shopper | Prioritizes avoiding grocery store trips |
| Pantry Cleaner | Maximizes use of what is already in your kitchen |

### Mood Modifiers

| Mood | Effect |
|---|---|
| Tired | Heavily favors quick recipes and low effort; bonus points for anything under 20 minutes |
| Casual | Neutral weights across all factors |
| Energetic | Rewards complexity and longer cook times; bonus for recipes over 60 minutes |

### Confidence Score Tiers

Every recipe in the response carries a match confidence value that reflects how it was found and validated.

| Score | What It Means |
|---|---|
| 1.0 | Passed strict filtering with all tags matching |
| 0.9 | Rescue candidate confirmed by Gemini as semantically appropriate |
| 0.6 | Rescue candidate pending or failed validation |

---

## Retrieval: Two Endpoints, One Screen

Spoonacular answers two different questions and the app needs both.
`findByIngredients` is the only endpoint that knows how much of a recipe you
already own, and it cannot filter by diet or intolerance at all.
`complexSearch` accepts `diet`, `intolerances`, `includeIngredients` and
`excludeIngredients`, so it returns a much denser set of plausible candidates,
but it has no idea what is in your fridge and ranks accordingly.

```
findByIngredients(pantry, ranking=1)     complexSearch(includeIngredients, diet,
  -> best pantry-coverage ranking           intolerances, excludeIngredients)
  -> no dietary filtering available        -> pre-filtered, denser, weaker ranking
                    \                     /
                     merge + dedupe by recipe id  (provenance recorded)
                                |
                     informationBulk(ids)   <- one call per 100 ids
                                |
                  DETERMINISTIC SCREEN over EVERY recipe
                                |
              UNSAFE dropped | UNKNOWN flagged | SAFE shown
```

Both arms run, results merge and deduplicate on recipe id, and every recipe
records which endpoint or endpoints produced it. Details are then fetched with
`informationBulk` — one call for up to 100 recipes instead of one call each,
which is the largest quota saving available — paged rather than truncated.

**Spoonacular's `intolerances` parameter is a quota and density optimisation. It
is never a verdict.** Every merged recipe is screened locally against the
canonical table regardless of which endpoint returned it. There is no code path
where a recipe skips screening because the API said it was already filtered;
`_screen_all` takes no argument that could weaken it and raises if its screened
count does not equal its candidate count.

**And the leak rate is measured, not assumed.** When complexSearch is asked to
exclude dairy and returns a recipe our screen then rejects for dairy, that is
recorded — recipe, declaration, and the exact ingredient that triggered it — and
reported in `metadata.screening` and in a log line:

```
retrieval: pantry_arm=1 filtered_arm=1 merged=2 both=0 bulk_calls=1 screened=2
           safe=1 unknown=0 unsafe=1 api_prefiltered=1 prefilter_leaks=1
           leak_rate=100.00% table=2.0.0
API PREFILTER LEAK: complexSearch was asked to exclude 'dairy' but returned
  recipe 668492 ('Creamy zucchini and ham pasta'); our screen matched
  'double cream' -> cream (found in ingredient)
```

That is the honest replacement for a percentage nobody measured: a number this
codebase computes on every request, from its own evidence.

If one arm returns nothing and the other returns plenty, the response says so
explicitly rather than presenting an empty or thin list as "nothing matched".

---

## Dietary Screening

**Read this before relying on the app for an allergy.** PantryChef screens recipes against
what you declare. It is not a medical device, it does not guarantee anything, and it cannot
see manufacturing cross-contamination, a substituted ingredient, or an incomplete ingredient
list from the recipe source. Check the ingredients yourself.

What it does do, precisely:

**One table, one decision.** All screening resolves through a single versioned file,
`backend/allergen_table.py`. It covers the UK/EU 14 declarable allergens — cereals containing
gluten, crustaceans, eggs, fish, peanuts, soybeans, milk, tree nuts, celery, mustard, sesame,
sulphites, lupin and molluscs — with peanuts and tree nuts kept separate, because they are
separate allergies. Diets (vegetarian, vegan, pescatarian) are sets of excluded categories in
that same table, not a parallel code path with its own word list. No allergen vocabulary
exists anywhere else in the codebase.

**Word boundaries, longest phrase first.** Ingredient text is tokenised and matched on whole
words, longest known phrase first. `peanut butter` resolves to peanut, not to butter.
`butternut squash` is not butter. `eggplant` is not egg. `donuts` are not nuts. `graham
crackers` are not ham. Substring containment is not used anywhere in the screening path,
because that is how a nut-allergic user's protection ends up depending on whether the recipe
author wrote "walnut" or "walnuts".

**Three verdicts, not two.** Every recipe comes back SAFE, UNSAFE, or UNKNOWN.

- UNSAFE means a declared restriction matched a resolved ingredient. The recipe is withheld,
  and that is final — no score, no model, and no third-party `glutenFree` flag can overturn it.
- UNKNOWN means the app could not check: the recipe carries no ingredient list, or an
  ingredient is not in the table, or you declared something the table has no vocabulary for.
  UNKNOWN recipes are still shown, marked "Not verified against your restrictions", naming
  what could not be resolved. They are never rendered like SAFE ones.
- SAFE means every ingredient resolved and none matched anything you declared.

**Absence of evidence is not evidence of safety.** An empty ingredient list produces UNKNOWN,
never SAFE. A restriction the table cannot screen produces UNKNOWN and says so, rather than
reporting that nothing was found.

**Titles are not evidence.** A recipe called "Vegan-Style Mac and Cheese" that lists butter
and cheddar contains butter and cheddar. A recipe called "Gluten-Free Bread" that lists wheat
flour contains wheat flour. Ingredients decide, in both directions.

**Instructions are read too.** "Grease the pan with butter" is an allergen that never appears
in the ingredient list.

**Every restriction, every time.** All declared allergens and all declared diets are evaluated
against all ingredients, and the verdict names every match rather than the first one.
Selecting more restrictions can only ever screen more, never less.

**No model in the loop.** `allergen_table.py` imports nothing that can reach a network. Every
verdict is reproducible from the recipe, your declared restrictions, and the table version,
which is recorded on the verdict. `backend/test_safety_regression.py` runs the whole suite
offline with no API key.

### What this replaced

An earlier version of this section described a three-layer design with a "safe-word list" and
a "Gemini Safety Jury". I removed all of it, because executing the code showed it did not
behave as described. The safe-word mechanism cleared real butter and real cheddar because the
word "vegan" appeared in the title, and cleared goat cheese for a dairy-intolerant user
because "oat" is a substring of "goat". Free-text allergies — which the UI routed peanuts,
tree nuts, soy and shellfish into — were checked by looking for the typed word in the recipe
text, so declaring "shellfish" on Shrimp Scampi returned "Safe". And the validator behind the
Safety Jury returned `safe_for_user: True` whenever it could not reach the API, so the
fallback for "the model could not answer" was "the model approved".

The regression suite pins each of those cases as a named test.

---

## API Quota Management

The free Spoonacular tier gives 150 points per day. Batch enrichment calls cost roughly 3 points compared to 20 individual calls for the same data — about 85% savings. The pipeline tracks usage in real time and logs a warning when the remaining quota drops below 20 points. For development without burning quota, a mock data mode is available in the Spoonacular client.

---

## Project Layout

```
PantryChef/
    LICENSE
    README.md
    PantryChef_FinalTests/
        backend/
            main.py                     FastAPI server entry point
            app_orchestrator.py         Pipeline coordinator
            pantry_chef_api.py          Spoonacular client with semantic fallback
            Logic.py                    Deterministic scoring and screening engine
            allergen_table.py           Canonical ingredient/allergen table (versioned data)
            dual_retrieval.py           Two-endpoint retrieval, merge, and leak metering
            test_safety_regression.py   Offline regression suite - no API key needed
            test_dual_retrieval.py      Offline retrieval tests - no API key needed
            Gemini_recipe_validator.py  Semantic cuisine/meal-type classifier
            gemini_integration.py       Substitutions and recommendation pitches
            substitution_helper.py      Combined API and AI substitution logic
            requirements.txt
            .env.example
        frontend/
            src/
                App.jsx                 Root component and state management
                components/
                    Sidebar.jsx         Ingredient input and filters
                    RecipeGrid.jsx      Card grid layout
                    RecipeCard.jsx      Individual card with modal
                    AIPitchBox.jsx      AI recommendation display
                    HeroSection.jsx     Landing section
            tailwind.config.js
            vite.config.js
            package.json
```

---

## Getting Started

### What You Need

- Python 3.9 or higher
- Node.js 16 or higher
- A Spoonacular API key — free tier at spoonacular.com/food-api, 150 points per day
- A Gemini API key — free tier at ai.google.dev

### Backend

```bash
cd PantryChef_FinalTests/backend
pip install -r requirements.txt
cp .env.example .env
```

Open the .env file and add your keys:

```
SPOONACULAR_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

```bash
python main.py
```

### Frontend

```bash
cd PantryChef_FinalTests/frontend
npm install
npm run dev
```

### Access Points

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

---

## API Reference

### POST /recommend

Submit ingredients and preferences, receive ranked recipes.

Request body:
```json
{
  "ingredients": ["tomato", "garlic", "onion"],
  "mood": "tired",
  "dietary_requirements": ["vegetarian"],
  "intolerances": ["dairy"],
  "user_profile": "pantry_cleaner",
  "number": 10
}
```

Response includes ranked recipes with match confidence, time, difficulty, nutritional summary, and the AI-generated pitch.

### POST /ask-chef

Submit a substitution question grounded in your pantry.

Request body:
```json
{
  "recipe_title": "Pasta Arrabiata",
  "query": "I do not have red pepper flakes",
  "ingredients": ["cayenne", "black pepper", "garlic"]
}
```

Response includes the substitution recommendation and a practical usage tip.

---

## Testing

There is one test artefact and it runs offline, with no API key and no metered calls:

```bash
cd PantryChef/PantryChef_FinalTests/backend
python3 test_safety_regression.py    # 46 cases: screening, scoring, table integrity
python3 test_dual_retrieval.py       # 40 cases: dual retrieval, merge, leak metering
python3 Logic.py                     # engine self-test
```

Every case in the regression suite is a defect that was found by executing the shipping code
and recording what it actually returned, kept so the same failure cannot come back quietly.

This section previously carried a table of percentages — "dietary safety validation accuracy
98.7%", "Gemini safety jury precision on edge cases 96.4%", "smart scoring match precision
85.3%". Those numbers were not produced by any measurement in this repository, there was no
labelled evaluation set behind them, and at the time they were written the only test in the
codebase did not pass. They are gone rather than restated more carefully, because there is
nothing to restate. If a benchmark goes back in this README, the corpus and the script that
produced it go in beside it.

---

## Roadmap

Near term: Redis caching for repeated searches, PostgreSQL for user history, async parallel API calls.

Later: A fine-tuned ranking model trained on user feedback, collaborative filtering for ingredient suggestions, WebSocket support for real-time updates.

---

## Stack

**Backend**: Python 3.9+, FastAPI, Pydantic, python-dotenv, requests

**Frontend**: React 18.2, JavaScript ES6+, Tailwind CSS 3.4, Vite 5.0

**External Services**: Spoonacular Food API, Google Gemini 2.0 Flash

---

## More Documentation

The backend and frontend each have their own detailed READMEs covering architecture decisions, component documentation, and testing procedures in depth.

- Backend README: PantryChef_FinalTests/backend/README.md
- Frontend README: PantryChef_FinalTests/frontend/README.md

---

## License

MIT. Open for anyone to use, fork, or build on.

---

## About

Built by Daksh Kumar, Statistics and Data Science student at UC Santa Barbara.

GitHub: https://github.com/dakshvk  
LinkedIn: https://www.linkedin.com/in/daksh-kumar  
Email: dakshvk786@gmail.com

I built this as a portfolio project to demonstrate full-stack development, AI integration, and systems thinking across a complete application. The problem it solves is real, the code is mine, and the architecture decisions came from actually running into the constraints of free-tier APIs and needing to engineer around them.