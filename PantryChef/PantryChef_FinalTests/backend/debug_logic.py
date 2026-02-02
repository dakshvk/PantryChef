"""
Debug Script - Test Logic.py with exact curl settings
This will show exactly why recipes are being filtered out
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pantry_chef_api import SpoonacularClient
from Logic import PantryChefEngine
from dotenv import load_dotenv

load_dotenv()

print("\n" + "=" * 70)
print("DEBUG: Testing Logic.py with curl request settings")
print("=" * 70)

# Step 1: Get recipes from API (same as your test)
print("\n📡 Step 1: Fetching recipes from API...")
api_key = os.getenv('SPOONACULAR_API_KEY')
client = SpoonacularClient(api_key)

raw_recipes = client.search_by_ingredients(
    user_ingredients=['chicken'],
    number=20,
    enrich_results=True
)

print(f"✅ API returned {len(raw_recipes)} recipes")

if not raw_recipes:
    print("❌ No recipes from API - cannot continue test")
    exit(1)

# Print first recipe details
print(f"\n📋 First recipe from API:")
r = raw_recipes[0]
print(f"   ID: {r.get('id')}")
print(f"   Title: {r.get('title')}")
print(f"   Used ingredients: {r.get('usedIngredientCount')}")
print(f"   Missed ingredients: {r.get('missedIngredientCount')}")

# Step 2: Set up Logic.py with EXACT same settings as curl request
print("\n🔧 Step 2: Initializing Logic Engine...")
print("Settings:")
settings = {
    'user_profile': 'balanced',
    'mood': 'casual',
    'intolerances': [],
    'max_time_minutes': 120,
    'max_missing_ingredients': 10,
    'dietary_requirements': [],  # ← No vegetarian requirement!
    'skill_level': 50,
    'max_time': 120
}

for key, value in settings.items():
    print(f"   {key}: {value}")

engine = PantryChefEngine(settings)

# Step 3: Process recipes through Logic.py
print("\n🧠 Step 3: Processing through Logic Engine...")
print(f"Processing {len(raw_recipes)} recipes...")

# Add debug output to see what's happening
processed = []
filtered_out = []

for i, recipe in enumerate(raw_recipes):
    title = recipe.get('title', 'Unknown')

    # Check if recipe would be filtered by vegetarian check
    dietary_requirements = settings.get('dietary_requirements', [])
    is_vegetarian = 'vegetarian' in [r.lower() for r in dietary_requirements]

    print(f"\n   Recipe {i + 1}: {title}")
    print(f"      Is vegetarian filter active? {is_vegetarian}")

    if is_vegetarian:
        # Check for meat in title
        MEAT_KEYWORDS = ['chicken', 'beef', 'pork', 'fish', 'shrimp']
        recipe_text = title.lower()
        has_meat = any(meat in recipe_text for meat in MEAT_KEYWORDS)
        print(f"      Contains meat keyword? {has_meat}")
        if has_meat:
            print(f"      ❌ FILTERED OUT by vegetarian check")
            filtered_out.append(title)
            continue

    processed.append(recipe)

print(f"\n📊 Results BEFORE Logic.py:")
print(f"   Total recipes: {len(raw_recipes)}")
print(f"   Would be filtered: {len(filtered_out)}")
print(f"   Should pass: {len(processed)}")

# Now actually process through Logic.py
print("\n🔄 Actually processing through Logic.py...")
processed_recipes = engine.process_results(raw_recipes)

print(f"\n✅ Results AFTER Logic.py:")
print(f"   Recipes returned: {len(processed_recipes)}")

if len(processed_recipes) == 0:
    print("\n❌ PROBLEM FOUND: Logic.py returned 0 recipes!")
    print("\nDebugging further...")

    # Test with a single recipe
    print("\n🔍 Testing with first recipe only:")
    test_recipe = raw_recipes[0]
    print(f"   Title: {test_recipe.get('title')}")
    print(f"   Ingredients count: {len(test_recipe.get('extendedIngredients', []))}")
    print(f"   Has nutrition: {'nutrition' in test_recipe}")

    # Try processing just one
    single_result = engine.process_results([test_recipe])
    print(f"   Result: {len(single_result)} recipes returned")

    if len(single_result) == 0:
        print("\n   Even single recipe was filtered!")
        print("\n   Possible issues:")
        print("   1. Recipe missing required fields (extendedIngredients, nutrition)")
        print("   2. Safety check is rejecting it")
        print("   3. Hard vegetarian filter is somehow active")
        print("\n   Checking recipe structure:")
        print(f"   Keys in recipe: {list(test_recipe.keys())[:10]}...")

else:
    print(f"\n✅ SUCCESS: Logic.py returned {len(processed_recipes)} recipes")
    print(f"\nFirst processed recipe:")
    pr = processed_recipes[0]
    print(f"   Title: {pr.get('title')}")
    print(f"   Score: {pr.get('score', 'N/A')}")
    print(f"   Confidence: {pr.get('match_confidence', 'N/A')}")

print("\n" + "=" * 70)
print("DEBUG TEST COMPLETE")
print("=" * 70 + "\n")