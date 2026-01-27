"""
Spoonacular API Reference Configuration
Use this file to map UI inputs to API parameters.
"""

SPOONACULAR_PARAMS = {
    "complex_search": {
        "query": {"type": "string", "example": "pasta", "desc": "The recipe search query."},
        "cuisine": {"type": "string", "example": "italian", "desc": "Comma separated list of cuisines (OR logic)."},
        "excludeCuisine": {"type": "string", "example": "greek", "desc": "Cuisine(s) recipes must NOT match."},
        "diet": {"type": "string", "example": "vegetarian", "desc": "Diets (',' for AND, '|' for OR logic)."},
        "intolerances": {"type": "string", "example": "gluten",
                         "desc": "Comma-separated list of allergens to exclude."},
        "equipment": {"type": "string", "example": "pan", "desc": "Required equipment (OR logic)."},
        "includeIngredients": {"type": "string", "example": "tomato,cheese", "desc": "Ingredients that MUST be used."},
        "excludeIngredients": {"type": "string", "example": "eggs", "desc": "Ingredients that MUST NOT be used."},
        "type": {"type": "string", "example": "main course", "desc": "Meal type (breakfast, snack, etc.)."},
        "instructionsRequired": {"type": "boolean", "default": True, "desc": "Must have instructions."},
        "fillIngredients": {"type": "boolean", "default": False, "desc": "Returns used/missing ingredient lists."},
        "addRecipeInformation": {"type": "boolean", "default": False, "desc": "Returns scores, time, and health info."},
        "addRecipeInstructions": {"type": "boolean", "default": False, "desc": "Returns step-by-step steps."},
        "addRecipeNutrition": {"type": "boolean", "default": False, "desc": "Returns nutritional data per serving."},
        "maxReadyTime": {"type": "number", "example": 20, "desc": "Maximum minutes for prep + cook."},
        "minServings": {"type": "number", "example": 1, "desc": "Minimum amount of servings."},
        "maxServings": {"type": "number", "example": 8, "desc": "Maximum amount of servings."},
        "ignorePantry": {"type": "boolean", "default": True, "desc": "Ignores staples like salt, water, flour."},
        "sort": {"type": "string", "example": "calories", "desc": "Strategy: popularity, healthiness, price, time."},
        "sortDirection": {"type": "string", "example": "asc", "desc": "asc (ascending) or desc (descending)."},
        "minCalories": {"type": "number", "range": [50, 800], "desc": "Calories per serving."},
        "maxCalories": {"type": "number", "range": [50, 800], "desc": "Calories per serving."},
        "minProtein": {"type": "number", "range": [10, 100], "desc": "Protein grams per serving."},
        "maxProtein": {"type": "number", "range": [10, 100], "desc": "Protein grams per serving."},
        "number": {"type": "number", "default": 10, "desc": "Results to return (1-100)."}
    },

    "substitutes": {
        "ingredientName": {"type": "string", "example": "butter", "desc": "Ingredient to replace."}
    },

    "similar": {
        "id": {"type": "number", "example": 715538, "desc": "The source recipe ID."},
        "number": {"type": "number", "default": 1, "desc": "Number of similar recipes (1-100)."}
    }
}

# --- VALIDATION LISTS ---
SUPPORTED_DIETS = [
    "Gluten Free", "Ketogenic", "Vegetarian", "Lacto-Vegetarian",
    "Ovo-Vegetarian", "Vegan", "Pescetarian", "Paleo", "Primal", "Low FODMAP", "Whole30"
]

SUPPORTED_INTOLERANCES = [
    "Dairy", "Egg", "Gluten", "Grain", "Peanut", "Seafood",
    "Sesame", "Shellfish", "Soy", "Sulfite", "Tree Nut", "Wheat"
]