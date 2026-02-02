"""
Debug script to see EXACTLY what's in the recipes
"""

import os
from dotenv import load_dotenv

load_dotenv()

from pantry_chef_api import SpoonacularClient
import json

print("\n" + "=" * 70)
print("DEBUG: What's Actually in the Recipes?")
print("=" * 70)

api_key = os.getenv('SPOONACULAR_API_KEY')
client = SpoonacularClient(api_key)

print("\n🧪 Getting recipes with Italian + Vegetarian filters...")
recipes = client.search_by_ingredients(
    user_ingredients=['tomato', 'basil', 'pasta'],
    number=5,  # Just 5 for easier debugging
    cuisine='italian',
    diet='vegetarian',
    enrich_results=False
)

print(f"\n📊 Got {len(recipes)} recipes total")
print("\n" + "=" * 70)

for i, recipe in enumerate(recipes, 1):
    print(f"\n🔍 RECIPE {i}: {recipe.get('title')}")
    print("-" * 70)

    # Check all the flags we care about
    print(f"Keys in recipe: {list(recipe.keys())[:15]}")
    print(f"\nFlags:")
    print(f"  'match_confidence' in recipe: {'match_confidence' in recipe}")
    print(f"  'needs_semantic_validation' in recipe: {'needs_semantic_validation' in recipe}")
    print(f"  'semantic_validation_reason' in recipe: {'semantic_validation_reason' in recipe}")

    if 'match_confidence' in recipe:
        print(f"\n  match_confidence = {recipe['match_confidence']}")
    else:
        print(f"\n  ❌ match_confidence NOT FOUND")

    if 'needs_semantic_validation' in recipe:
        print(f"  needs_semantic_validation = {recipe['needs_semantic_validation']}")
    else:
        print(f"  ❌ needs_semantic_validation NOT FOUND")

    if 'semantic_validation_reason' in recipe:
        print(f"  semantic_validation_reason = {recipe['semantic_validation_reason']}")
    else:
        print(f"  ❌ semantic_validation_reason NOT FOUND")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Now try different ways to filter
print("\n1. Count by match_confidence == 0.6:")
rescue_by_confidence = [r for r in recipes if r.get('match_confidence') == 0.6]
print(f"   Found: {len(rescue_by_confidence)}")

print("\n2. Count by needs_semantic_validation == True:")
rescue_by_flag = [r for r in recipes if r.get('needs_semantic_validation') == True]
print(f"   Found: {len(rescue_by_flag)}")

print("\n3. Count by needs_semantic_validation is True (identity check):")
rescue_by_identity = [r for r in recipes if r.get('needs_semantic_validation') is True]
print(f"   Found: {len(rescue_by_identity)}")

print("\n4. Count recipes with semantic_validation_reason:")
rescue_by_reason = [r for r in recipes if 'semantic_validation_reason' in r]
print(f"   Found: {len(rescue_by_reason)}")

print("\n" + "=" * 70)

if len(rescue_by_confidence) > 0:
    print("\n✅ Recipes have confidence = 0.6")
elif len(rescue_by_flag) > 0:
    print("\n✅ Recipes have needs_semantic_validation = True")
elif len(rescue_by_reason) > 0:
    print("\n✅ Recipes have semantic_validation_reason")
else:
    print("\n❌ NO FLAGS FOUND - This is the problem!")
    print("\nPossible causes:")
    print("1. Flags not being set in pantry_chef_api.py")
    print("2. Recipes being copied/transformed and losing flags")
    print("3. Logic error in flag-setting code")

print("\n" + "=" * 70)
