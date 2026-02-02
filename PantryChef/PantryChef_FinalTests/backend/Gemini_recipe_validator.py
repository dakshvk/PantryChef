"""
Gemini Dual-Purpose Recipe Validator
Efficiently handles BOTH classification AND safety validation in one API call

This replaces the separate classifier and safety checker with a unified system.
"""

import os
from typing import List, Dict, Any, Optional
from google import genai
from dotenv import load_dotenv
import json
import time

load_dotenv()


class GeminiRecipeValidator:
    """
    Unified Gemini validator that does BOTH:
    1. Classification: Determines actual cuisine, diet, meal_type (fixing Spoonacular's mistakes)
    2. Safety Validation: Checks if "almond milk" is OK but "dairy milk" is NOT for vegan diet

    Does this efficiently in ONE API call per recipe.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini validator using the new Google GenAI SDK."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            print("⚠️  WARNING: GEMINI_API_KEY not found. Validator will be disabled.")
            self.client = None
            return

        try:
            # NEW SDK SYNTAX
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-2.0-flash' # or 'gemini-1.5-flash'
            print("✅ Gemini Recipe Validator initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini: {str(e)}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Gemini validator is available."""
        return self.client is not None

    def validate_and_classify_recipe(
            self,
            recipe_title: str,
            ingredients: List[str],
            instructions: str = "",
            user_diet: Optional[str] = None,
            user_intolerances: Optional[List[str]] = None,
            user_cuisine: Optional[str] = None,
            user_meal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        DUAL-PURPOSE: Classify recipe AND validate against user's dietary needs.
        Classify and validate recipe with automatic retry for 429 rate limits.

        Does BOTH in ONE API call for efficiency.

        Args:
            recipe_title: Recipe name
            ingredients: List of ingredient strings
            instructions: Cooking instructions
            user_diet: User's diet preference (e.g., 'vegetarian', 'vegan')
            user_intolerances: User's intolerances (e.g., ['dairy', 'gluten'])
            user_cuisine: User's desired cuisine
            user_meal_type: User's desired meal type

        Returns:
            {
                # CLASSIFICATION (what the recipe actually is):
                'actual_cuisines': ['italian', 'mediterranean'],
                'actual_diets': ['vegetarian', 'gluten-free'],
                'actual_meal_types': ['main course', 'dinner'],
                'is_vegetarian': True/False,
                'is_vegan': True/False,
                'is_gluten_free': True/False,
                'is_dairy_free': True/False,

                # SAFETY VALIDATION (does it match user's requirements?):
                'matches_user_diet': True/False,
                'matches_user_cuisine': True/False,
                'matches_user_meal_type': True/False,
                'intolerance_safe': True/False,
                'intolerance_violations': ['dairy milk in recipe but user is dairy-free'],

                # OVERALL:
                'safe_for_user': True/False,  # Can we show this recipe?
                'rejection_reason': str,  # Why rejected (if safe_for_user = False)
                'confidence': 'high' | 'medium' | 'low'
            }
        """
        if not self.is_available():
            return self._get_default_validation()

        # Build unified prompt that does BOTH classification AND validation
        prompt = self._build_unified_prompt(
            recipe_title, ingredients, instructions,
            user_diet, user_intolerances, user_cuisine, user_meal_type
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                return json.loads(response.text)

            except Exception as e:
                # Check for rate limit (429) or resource exhaustion
                error_msg = str(e).upper()
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    # Exponential Backoff: Wait 10s, then 20s
                    wait_time = (attempt + 1) * 10
                    print(f"⏳ Rate limit hit. Retrying in {wait_time}s (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    # For all other errors, fail gracefully with default response
                    print(f"⚠️ Gemini validation failed: {str(e)}")
                    return self._get_default_validation()

        # If we exhausted all retries
        print("❌ Maximum retries reached for Gemini API.")
        return self._get_default_validation()

    def validate_batch(
            self,
            recipes: List[Dict[str, Any]],
            user_diet: Optional[str] = None,
            user_intolerances: Optional[List[str]] = None,
            user_cuisine: Optional[str] = None,
            user_meal_type: Optional[str] = None,
            max_recipes: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Validate and classify multiple recipes.

        Returns recipes with added 'gemini_validation' field.
        Recipes that fail safety checks are FLAGGED but NOT removed.
        """
        if not self.is_available():
            print("⚠️  Gemini not available - skipping validation")
            return recipes

        validated_recipes = []

        for i, recipe in enumerate(recipes[:max_recipes]):
            # Extract recipe data
            title = recipe.get('title', 'Unknown Recipe')

            # Get ingredients as strings
            ingredients = []
            extended_ingredients = recipe.get('extendedIngredients', [])
            if extended_ingredients:
                ingredients = [ing.get('original', '') for ing in extended_ingredients if ing.get('original')]

            # Get instructions
            instructions = recipe.get('instructions', '')

            print(f"🔍 Validating recipe {i + 1}/{min(len(recipes), max_recipes)}: {title}")

            # Validate and classify
            validation = self.validate_and_classify_recipe(
                recipe_title=title,
                ingredients=ingredients,
                instructions=instructions,
                user_diet=user_diet,
                user_intolerances=user_intolerances,
                user_cuisine=user_cuisine,
                user_meal_type=user_meal_type
            )

            # Add validation to recipe
            recipe['gemini_validation'] = validation

            # Add flag for frontend
            recipe['safe_for_user'] = validation.get('safe_for_user', True)
            recipe['rejection_reason'] = validation.get('rejection_reason', '')

            validated_recipes.append(recipe)

        return validated_recipes

    def filter_unsafe_recipes(
            self,
            recipes: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Separate safe recipes from unsafe ones.

        Returns:
            (safe_recipes, unsafe_recipes)
        """
        safe = []
        unsafe = []

        for recipe in recipes:
            validation = recipe.get('gemini_validation', {})
            if validation.get('safe_for_user', True):
                safe.append(recipe)
            else:
                unsafe.append(recipe)

        return safe, unsafe

    def _build_unified_prompt(
            self,
            title: str,
            ingredients: List[str],
            instructions: str,
            user_diet: Optional[str],
            user_intolerances: Optional[List[str]],
            user_cuisine: Optional[str],
            user_meal_type: Optional[str]
    ) -> str:
        """Build prompt that does BOTH classification AND validation."""

        # Truncate instructions if too long
        instructions_preview = instructions[:500] if instructions else "No instructions provided"

        # Build user requirements section
        user_requirements = []
        if user_diet:
            user_requirements.append(f"Diet: {user_diet}")
        if user_intolerances:
            user_requirements.append(f"Intolerances: {', '.join(user_intolerances)}")
        if user_cuisine:
            user_requirements.append(f"Preferred Cuisine: {user_cuisine}")
        if user_meal_type:
            user_requirements.append(f"Preferred Meal Type: {user_meal_type}")

        requirements_text = "\n".join(user_requirements) if user_requirements else "None specified"

        prompt = f"""You are a culinary expert analyzing a recipe for classification AND dietary safety.

Recipe Title: {title}

Ingredients:
{chr(10).join(f"- {ing}" for ing in ingredients[:25])}

Instructions (preview): {instructions_preview}

User's Dietary Requirements:
{requirements_text}

Your task is to:
1. CLASSIFY the recipe (what it actually is)
2. VALIDATE if it's safe for the user's requirements

CRITICAL RULES:

**DIET CLASSIFICATION:**
- Vegetarian = NO meat, fish, or poultry (eggs/dairy OK)
- Vegan = NO animal products whatsoever (no meat, fish, eggs, dairy, honey)
- Pescatarian = Fish/seafood OK, but no other meat
- If recipe has chicken → NOT vegetarian, NOT vegan
- If recipe has dairy milk → NOT vegan (but almond milk IS vegan)
- If recipe has eggs → NOT vegan (but vegetarian OK)

**INTOLERANCE VALIDATION:**
- "Dairy-free" means NO: milk, cheese, butter, cream, yogurt, whey, casein
- BUT "almond milk", "coconut milk", "oat milk" ARE dairy-free ✅
- "Gluten-free" means NO: wheat, barley, rye, regular flour, pasta, bread
- BUT "rice flour", "almond flour", "corn tortillas" ARE gluten-free ✅
- Check ACTUAL ingredients, not just recipe name

**CUISINE MATCHING:**
- "Chicken Tikka Masala" = Indian cuisine (even if Spoonacular says otherwise)
- "Spaghetti Carbonara" = Italian cuisine
- Use ingredient clues: soy sauce → Asian, cumin → Indian/Mexican

Return ONLY valid JSON:
{{
  "actual_cuisines": ["cuisine1", "cuisine2"],
  "actual_diets": ["diet1", "diet2"],
  "actual_meal_types": ["type1", "type2"],
  "is_vegetarian": true/false,
  "is_vegan": true/false,
  "is_gluten_free": true/false,
  "is_dairy_free": true/false,

  "matches_user_diet": true/false,
  "matches_user_cuisine": true/false,
  "matches_user_meal_type": true/false,
  "intolerance_safe": true/false,
  "intolerance_violations": ["specific violation1", "specific violation2"],

  "safe_for_user": true/false,
  "rejection_reason": "Brief explanation if safe_for_user is false",
  "confidence": "high" | "medium" | "low"
}}

VALIDATION LOGIC:
- matches_user_diet: Does recipe's actual diet match user's requirement?
  Example: User wants vegan, recipe has dairy milk → FALSE
  Example: User wants vegan, recipe has almond milk → TRUE

- intolerance_safe: Does recipe avoid user's intolerances?
  Example: User is dairy-free, recipe has "milk" → FALSE, violation: "Contains dairy milk"
  Example: User is dairy-free, recipe has "almond milk" → TRUE, no violation
"IMPORTANT: Distinguish between dairy and plant-based alternatives. "
"For example Almond milk, soy milk, and oat milk are 100% SAFE for 'dairy-free' and 'vegan' users."

- safe_for_user: TRUE only if ALL requirements are met
  FALSE if ANY of: diet mismatch, cuisine mismatch (if user specified), intolerance violation
  FALSE if ANY of: diet mismatch, cuisine mismatch (if user specified), intolerance violation

Return ONLY the JSON, no markdown formatting.
"""
        return prompt

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response."""
        try:
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            validation = json.loads(response_text)

            return validation

        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse Gemini response as JSON: {str(e)}")
            print(f"   Response: {response_text[:200]}")
            return self._get_default_validation()
        except Exception as e:
            print(f"⚠️  Unexpected error parsing validation: {str(e)}")
            return self._get_default_validation()

    def _get_default_validation(self) -> Dict[str, Any]:
        """Return default validation when Gemini is unavailable or fails."""
        return {
            'actual_cuisines': [],
            'actual_diets': [],
            'actual_meal_types': [],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': False,
            'matches_user_diet': True,  # Assume safe if Gemini unavailable
            'matches_user_cuisine': True,
            'matches_user_meal_type': True,
            'intolerance_safe': True,
            'intolerance_violations': [],
            'safe_for_user': True,  # Don't filter if Gemini unavailable
            'rejection_reason': '',
            'confidence': 'low'
        }


# ==========================================
# TEST SUITE
# ==========================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GEMINI DUAL-PURPOSE VALIDATOR - TEST SUITE")
    print("=" * 70)

    validator = GeminiRecipeValidator()

    if not validator.is_available():
        print("\n❌ Gemini not available - cannot run tests")
        exit(1)

    # Test Case 1: Vegan user + Recipe with dairy milk
    print("\n" + "-" * 70)
    print("TEST 1: Vegan user + Recipe with regular milk (should REJECT)")
    print("-" * 70)

    result1 = validator.validate_and_classify_recipe(
        recipe_title="Creamy Pasta",
        ingredients=[
            "pasta",
            "1 cup milk",  # ← Regular milk, NOT vegan!
            "garlic",
            "olive oil"
        ],
        user_diet='vegan'
    )

    print(f"\n📋 Classification:")
    print(f"   Actual diets: {result1['actual_diets']}")
    print(f"   Is vegan: {result1['is_vegan']}")
    print(f"\n🔒 Safety Check:")
    print(f"   Matches user diet: {result1['matches_user_diet']}")
    print(f"   Intolerance safe: {result1['intolerance_safe']}")
    print(f"   Violations: {result1['intolerance_violations']}")
    print(f"\n✅ SAFE FOR USER: {result1['safe_for_user']}")
    print(f"   Reason: {result1['rejection_reason']}")

    expected_safe = False
    actual_safe = result1['safe_for_user']
    if actual_safe == expected_safe:
        print(f"\n✅ TEST PASSED: Recipe correctly rejected")
    else:
        print(f"\n❌ TEST FAILED: Expected safe={expected_safe}, got {actual_safe}")

    time.sleep(5)

    # Test Case 2: Vegan user + Recipe with almond milk
    print("\n" + "-" * 70)
    print("TEST 2: Vegan user + Recipe with almond milk (should APPROVE)")
    print("-" * 70)

    result2 = validator.validate_and_classify_recipe(
        recipe_title="Creamy Vegan Pasta",
        ingredients=[
            "pasta",
            "1 cup almond milk",  # ← Almond milk IS vegan!
            "garlic",
            "olive oil"
        ],
        user_diet='vegan'
    )

    print(f"\n📋 Classification:")
    print(f"   Actual diets: {result2['actual_diets']}")
    print(f"   Is vegan: {result2['is_vegan']}")
    print(f"\n🔒 Safety Check:")
    print(f"   Matches user diet: {result2['matches_user_diet']}")
    print(f"   Intolerance safe: {result2['intolerance_safe']}")
    print(f"\n✅ SAFE FOR USER: {result2['safe_for_user']}")

    expected_safe = True
    actual_safe = result2['safe_for_user']
    if actual_safe == expected_safe:
        print(f"\n✅ TEST PASSED: Recipe correctly approved")
    else:
        print(f"\n❌ TEST FAILED: Expected safe={expected_safe}, got {actual_safe}")

    time.sleep(5)

    # Test Case 3: Dairy-free user + Cheese
    print("\n" + "-" * 70)
    print("TEST 3: Dairy-free user + Recipe with cheese (should REJECT)")
    print("-" * 70)

    result3 = validator.validate_and_classify_recipe(
        recipe_title="Margherita Pizza",
        ingredients=[
            "pizza dough",
            "tomato sauce",
            "mozzarella cheese",  # ← Dairy!
            "basil"
        ],
        user_intolerances=['dairy']
    )

    print(f"\n🔒 Safety Check:")
    print(f"   Intolerance safe: {result3['intolerance_safe']}")
    print(f"   Violations: {result3['intolerance_violations']}")
    print(f"\n✅ SAFE FOR USER: {result3['safe_for_user']}")
    print(f"   Reason: {result3['rejection_reason']}")

    expected_safe = False
    actual_safe = result3['safe_for_user']
    if actual_safe == expected_safe:
        print(f"\n✅ TEST PASSED: Recipe correctly rejected for dairy")
    else:
        print(f"\n❌ TEST FAILED: Expected safe={expected_safe}, got {actual_safe}")

    # Test Case 4: Italian cuisine filter
    print("\n" + "-" * 70)
    print("TEST 4: User wants Italian + Recipe is Chinese (should REJECT)")
    print("-" * 70)

    time.sleep(5)

    result4 = validator.validate_and_classify_recipe(
        recipe_title="Kung Pao Chicken",
        ingredients=[
            "chicken",
            "soy sauce",
            "ginger",
            "peanuts"
        ],
        user_cuisine='italian'
    )

    print(f"\n📋 Classification:")
    print(f"   Actual cuisines: {result4['actual_cuisines']}")
    print(f"\n🔒 Safety Check:")
    print(f"   Matches user cuisine: {result4['matches_user_cuisine']}")
    print(f"\n✅ SAFE FOR USER: {result4['safe_for_user']}")
    print(f"   Reason: {result4['rejection_reason']}")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 70)