"""Test the semantic fallback system"""

import os
from dotenv import load_dotenv
load_dotenv()

from pantry_chef_api import SpoonacularClient

print("\n" + "="*70)
print("TEST: Semantic Fallback System")
print("="*70)

# Initialize client
api_key = os.getenv('SPOONACULAR_API_KEY')
client = SpoonacularClient(api_key)

# Test with Italian + Vegetarian filters
# Many recipes will fail "Italian" tag but are semantically Italian
print("\n🧪 Test Case: Italian + Vegetarian (should find rescue candidates)")
print("-"*70)

recipes = client.search_by_ingredients(
    user_ingredients=['tomato', 'basil', 'pasta'],
    number=10,
    cuisine='italian',
    diet='vegetarian',
    enrich_results=False  # Skip enrichment for faster test
)

print(f"\n📊 Results:")
print(f"Total recipes: {len(recipes)}")

golden = [r for r in recipes if r.get('match_confidence') == 1.0 and not r.get('needs_semantic_validation', False)]
rescue = [r for r in recipes if r.get('needs_semantic_validation', False) == True]

print(f"Golden matches (confidence 1.0): {len(golden)}")
print(f"Rescue candidates (confidence 0.6): {len(rescue)}")

if rescue:
    print(f"\n🔍 Rescue Candidates (need Gemini validation):")
    for r in rescue[:5]:
        print(f"   - {r.get('title')}")
        print(f"     Reason: {r.get('semantic_validation_reason', 'N/A')}")

if len(golden) > 0 or len(rescue) > 0:
    print(f"\n✅ TEST PASSED: System found {len(golden)} golden + {len(rescue)} rescue")
else:
    print(f"\n❌ TEST FAILED: No recipes found")

print("\n" + "="*70)