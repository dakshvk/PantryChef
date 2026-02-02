"""Test the complete semantic fallback + Gemini validation pipeline"""

import os
from dotenv import load_dotenv
load_dotenv()

from app_orchestrator import PantryChefOrchestrator

print("\n" + "="*70)
print("TEST: Full Semantic Pipeline (API → Logic → Gemini)")
print("="*70)

# Initialize orchestrator
orchestrator = PantryChefOrchestrator()

# Test settings
settings = {
    'user_profile': 'balanced',
    'mood': 'casual',
    'max_time_minutes': 120,
    'max_missing_ingredients': 10,
    'dietary_requirements': [],
    'skill_level': 50,
    'max_time': 120
}

print("\n🧪 Test Case: Italian cuisine filter")
print("Expected: Some recipes fail 'Italian' tag but Gemini validates them")
print("-"*70)

result = orchestrator.run_pantry_chef(
    ingredients=['tomato', 'basil', 'garlic'],
    settings=settings,
    number=10,
    cuisine='italian',
    enrich_with_ai=True  # Enable Gemini
)

recipes = result.get('recipes', [])

print(f"\n📊 Results:")
print(f"Total recipes returned: {len(recipes)}")

# Analyze confidence distribution
# Count golden (1.0 confidence)
golden = [r for r in recipes if r.get('match_confidence', 0.0) >= 0.95]

# Count upgraded by Gemini (0.9 confidence)
upgraded = [r for r in recipes if 0.85 <= r.get('match_confidence', 0.0) < 0.95]

# Count low/rejected (0.6 or lower)
rescue = [r for r in recipes if r.get('match_confidence', 0.0) < 0.85]

print(f"\nConfidence Distribution:")
print(f"  Golden (1.0): {len(golden)} recipes")
print(f"  Upgraded (0.9): {len(upgraded)} recipes - Gemini validated!")
print(f"  Low (0.6): {len(rescue)} recipes - Failed validation")

if upgraded:
    print(f"\n✅ Recipes Upgraded by Gemini:")
    for r in upgraded:
        print(f"   - {r.get('title')} (confidence: {r.get('match_confidence')})")
        if r.get('semantic_validated'):
            print(f"     ✅ Gemini semantically validated!")

print(f"\n📝 Chef's Pitch:")
print(result.get('pitch', 'No pitch generated'))

print("\n" + "="*70)