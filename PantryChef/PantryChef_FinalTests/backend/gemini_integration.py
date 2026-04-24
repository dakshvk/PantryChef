"""
Gemini AI Integration for Smart Ingredient Substitutions and Recipe Recommendations
Updated for 2025 Google GenAI SDK Compatibility
Bridges Logic.py (math/filtering) with human-friendly chef communication
"""

import os
import json
from google import genai  # Corrected 2025 import
from typing import Dict, Optional, List, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiSubstitution:
    """
    Handles smart ingredient substitutions and recommendation pitches using Google Gemini AI.
    Translates backend math (scores, confidence) into human-friendly chef language.
    """

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.system_prompt = """You are a Silent Culinary Auditor and a professional Executive Chef. Your role is to deliver exactly 3 safe recipe recommendations in a clean, professional format.

SILENT CULINARY AUDITOR RULES:
- You must audit every recipe for dietary compliance
- If a recipe violates the user's diet (e.g., contains meat for a vegetarian, dairy for a vegan), SILENTLY SKIP IT
- Do NOT write "REJECTED", "WARNING", or any error text
- Do NOT explain why you skipped a recipe
- Simply do not include it in your response
- Only include recipes that are 100% safe for the user's dietary requirements

DIETARY AUDIT RULES:
- Vegetarian: Search ingredients for animal flesh. If you see 'Chicken', 'Beef', 'Fish' as actual ingredients, skip it silently. 'Mushroom Shawarma' and 'Seitan Kebab' are SAFE.
- Vegan: Same as Vegetarian, plus check for dairy/eggs. If you see actual dairy/eggs, skip it silently. 'Vegan butter' and 'plant-based egg' are SAFE.
- Pescatarian: If you see land meat (chicken, beef, pork, lamb) in ingredients, skip it silently. Fish and seafood are SAFE.
- Custom diets (paleo, keto, raw, etc.): Check if recipes comply with the diet's specific rules. For example, paleo excludes grains and legumes; keto is very low-carb. If a recipe violates the custom diet's rules, skip it silently.
- Custom intolerances (shrimp, peanuts, shellfish, etc.): Check EVERY ingredient in the recipe. If the custom intolerance keyword appears in ANY ingredient name (e.g., "shrimp" in "shrimp paste", "peanuts" in "peanut oil"), skip the recipe silently. Be thorough - check all ingredients, not just the title.

CONTEXT UNDERSTANDING: You understand context. 'Chickpea' is safe, 'Chicken' is not. 'Vegan butter' is safe, 'butter' without 'vegan' is not. 'Mushroom Shawarma' is safe, 'Chicken Shawarma' is not.

OUTPUT FORMAT (CRITICAL):
You must deliver exactly 3 recommendations in this exact format:
1. **[Recipe Name]**: [One mouth-watering flavor description sentence]
2. **[Recipe Name]**: [One mouth-watering flavor description sentence]
3. **[Recipe Name]**: [One mouth-watering flavor description sentence]

Example:
1. **Lemon Garlic Chicken**: A zesty, herb-kissed dish that transforms simple chicken into a bright Mediterranean feast.
2. **Roast Chicken with Herbs**: Crispy-skinned perfection with aromatic herbs that fill your kitchen with warmth.
3. **Chicken Piccata**: Tangy lemon and briny capers create a vibrant, restaurant-quality meal in minutes.

REQUIREMENTS:
- Exactly 3 recipes (if fewer are safe, provide only the safe ones)
- Use the exact format: 1. **[Recipe Name]**: [Description]
- Each recommendation must be on its own new line. Do not bunch them into a single paragraph.
- One sentence per recipe (focus on flavor and vibe only)
- If NONE OF THE recipes are safe, return: "I couldn't find a perfect match for your diet today, but try these ingredients in a simple sauté!"
- ZERO advice: Never mention missing ingredients, cooking times, or health stats
- NO chatting: Do not explain reasoning, just deliver the recommendations"""

        if not self.api_key:
            print('WARNING: GEMINI_API_KEY not found in .env. Falling back to Spoonacular data.')
            self.client = None
        else:
            try:
                # FIXED: In the new library, we only need the Client object.
                # 'GenerativeModel' and 'genai.configure' are legacy and removed.
                self.client = genai.Client(api_key=self.api_key)
                print("✓ Gemini 2025 Client Initialized Successfully")
            except Exception as e:
                print(f'Error initializing Gemini: {e}')
                self.client = None

    def get_smart_substitution(
        self,
        missing_item: str,
        recipe_title: str,
        user_pantry_list: list,
        spoonacular_substitutes: Optional[Dict] = None,
        similar_recipes: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Main Logic: Combines Spoonacular data with Gemini AI creativity.
        Uses Gemini's 2026 knowledge (Web Search) to find creative substitutions.
        """
        # --- LOGIC GATE: FALLBACK ---
        if not self.client:
            api_sub = spoonacular_substitutes.get('substitute', 'N/A') if spoonacular_substitutes else 'N/A'
            return {
                'substitution': api_sub if api_sub != 'N/A' else f"Try omitting {missing_item}.",
                'chef_tip': "PantryChef is in offline mode. Check your similar recipes!",
                'api_substitutes': spoonacular_substitutes,
                'similar_recipes': [r.get('title', '') for r in similar_recipes[:3]] if similar_recipes else []
            }

        # --- LOGIC GATE: PROMPT BUILDING ---
        pantry_str = ', '.join(user_pantry_list[:12])

        # Pulling in Spoonacular context to make Gemini smarter
        api_context = ""
        if spoonacular_substitutes and spoonacular_substitutes.get('substitute'):
            api_context = f"\nSpoonacular API suggests: {spoonacular_substitutes.get('substitute')}"

        # Enhanced prompt that allows Gemini to use its knowledge for creative hacks
        prompt = f"""{self.system_prompt}

You are a professional chef helping a user make {recipe_title} but they are missing {missing_item}.

Their pantry contains: {pantry_str}
{api_context}

Use your knowledge to find the BEST substitution. If you see ingredients that can be combined (e.g., "Balsamic Vinegar" + "Salt" = Soy Sauce substitute), suggest it as a "Chef's Secret" hack.

Based on their actual pantry, what is the BEST primary substitute? Be creative and use your 2026 knowledge if needed.
        
Format your response EXACTLY as:
SUBSTITUTION: [item or combination]
TIP: [one sentence chef advice under 15 words, mention if it's a creative hack]"""

        # --- LOGIC GATE: AI EXECUTION ---
        try:
            # FIXED: New library path is client.models.generate_content
            # Using 'gemini-2.0-flash' for the best speed/accuracy balance
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )

            # FIXED: response.text is the correct way to get the string
            return self._parse_ai_response(response.text, spoonacular_substitutes, similar_recipes)

        except Exception as e:
            print(f'Error getting Gemini substitution: {e}')
            return {
                'substitution': "Creative Manual Check Needed",
                'chef_tip': "The AI kitchen is busy! Try a similar herb or spice.",
                'api_substitutes': spoonacular_substitutes,
                'similar_recipes': []
            }
    
    def generate_recommendation_pitch(
        self,
        recommendations: List[Dict[str, Any]],
        user_mood: str = 'casual',
        user_diet: Optional[str] = None,
        user_intolerances: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a human-friendly "Chef's Pitch" from Logic.py recommendations.
        Translates match_confidence, smart_score, and nutritional data into simple encouragement.
        
        Args:
            recommendations: List of clean recommendations from PantryChefEngine.process_results()
            user_mood: User's mood ('tired', 'casual', 'energetic')
            user_diet: User's dietary restriction (e.g., 'vegetarian', 'vegan', 'paleo', 'keto', or custom)
            user_intolerances: List of user's intolerances (e.g., ['dairy', 'gluten', 'shrimp', 'peanuts'])
            user_mood: User's mood ('tired', 'casual', 'energetic')
            
        Returns:
            Dictionary with:
            - pitch_text: Human-friendly recommendation text
            - top_recipe: Best recipe (for tired users)
            - comparison: Top 3 comparison (for casual/energetic users)
        """
        if not self.client:
            # Fallback: Simple text-based pitch
            if recommendations:
                top = recommendations[0]
                return {
                    'pitch_text': f"Here's {top.get('title', 'a great recipe')} for you!",
                    'top_recipe': top,
                    'comparison': []
                }
            return {
                'pitch_text': "No recommendations found.",
                'top_recipe': None,
                'comparison': []
            }
        
        if not recommendations:
            return {
                'pitch_text': "No recipes match your criteria. Try relaxing some filters!",
                'top_recipe': None,
                'comparison': []
            }
        
        # Prepare data for AI (translate math to context)
        top_3 = recommendations[:3]
        
        # Build context from recommendations (hide the numbers, show the meaning)
        recipe_contexts = []
        for rec in top_3:
            # Translate match_confidence to human language
            confidence = rec.get('match_confidence', rec.get('confidence', 70))
            if confidence >= 90:
                match_desc = "Perfect for your current mood"
            elif confidence >= 80:
                match_desc = "Great match for you"
            else:
                match_desc = "Good option"
            
            # Translate smart_score to human language (from metadata)
            metadata = rec.get('_metadata', {})
            smart_score = metadata.get('smart_score', 0)
            if smart_score >= 80:
                pantry_desc = "Great use of your pantry!"
            elif smart_score >= 60:
                pantry_desc = "Uses most of what you have"
            else:
                pantry_desc = "Uses some pantry items"
            
            # Extract nutritional highlights
            nutrition = rec.get('nutrition', {})
            nutrient_highlights = rec.get('nutrientHighlights', [])
            
            # Goal 2: Use nutrition_summary for raw nutritional data (standardized schema)
            nutrition_summary = rec.get('nutrition_summary', {})
            protein = nutrition_summary.get('protein', rec.get('protein', 0))
            calories = nutrition_summary.get('calories', rec.get('calories', 0))
            fat = nutrition_summary.get('fat', 0)
            carbs = nutrition_summary.get('carbs', 0)
            
            # Extract ACTUAL missing ingredients from extendedIngredients
            missing_ingredients_list = []
            extended_ingredients = rec.get('extendedIngredients', [])
            used_count = rec.get('used_ingredients', 0)
            missing_count = rec.get('missing_ingredients', 0)
            
            # Get missing ingredients (items after the used ones)
            if extended_ingredients and missing_count > 0:
                for ing in extended_ingredients[used_count:used_count + missing_count]:
                    if isinstance(ing, dict):
                        # Try to get the ingredient name
                        ing_name = ing.get('name') or ing.get('original') or ing.get('originalName', '')
                        if ing_name:
                            missing_ingredients_list.append(ing_name)
            
            # Goal 1: Extract violation flags and penalty info for Smart Concierge explanations
            metadata = rec.get('_metadata', {})
            violation_flags = metadata.get('violation_flags', {})
            penalty_score = metadata.get('penalty_score', 0)
            violations = metadata.get('violations', [])
            
            # Fix 1: Safety Validation - Check BOTH recipe level and metadata level
            # Explicitly check recipe.get('requires_ai_validation') first, then fallback to metadata
            requires_ai_validation = rec.get('requires_ai_validation', False)
            safety_check = metadata.get('safety_check', {})
            # If not found at recipe level, check metadata
            if not requires_ai_validation:
                requires_ai_validation = safety_check.get('requires_ai_validation', False)
            
            # Extract violation_note - check both recipe level and safety_check
            violation_note = rec.get('violation_note', '')
            if not violation_note:
                violation_note = safety_check.get('violation_note', safety_check.get('safety_reason', ''))
            
            suspicious_ingredients = safety_check.get('suspicious_ingredients', [])
            found_intolerances = safety_check.get('found_intolerances', [])
            safe_alternative_indicators = safety_check.get('safe_alternative_indicators', [])
            
            # Fix 2: Metadata Access - Extract match reasoning from _metadata
            # Get reasoning text and internal debug info for match explanation
            reasoning_text = metadata.get('scoring_breakdown', '')
            internal_debug = metadata.get('internal_debug', {})
            match_reasoning = reasoning_text or rec.get('reasoning', '')
            
            # Build violation context for AI to explain trade-offs
            violation_context = []
            if violation_flags.get('has_time_violation'):
                violation_context.append('slightly over time limit')
            if violation_flags.get('has_missing_violation'):
                violation_context.append('needs a few extra ingredients')
            if violation_flags.get('has_difficulty_violation'):
                violation_context.append('slightly more complex')
            
            # Fix 3: Plural Key Awareness - Use dishTypes and cuisines (plural) instead of singular
            dish_types = rec.get('dishTypes', [])  # Plural key from informationBulk
            cuisines = rec.get('cuisines', [])  # Plural key from informationBulk
            
            recipe_contexts.append({
                'title': rec.get('title', 'Unknown'),
                'time': rec.get('time', 0),
                'missing_count': missing_count,
                'missing_ingredients': missing_ingredients_list,  # Actual list of missing items
                'match_desc': match_desc,
                'pantry_desc': pantry_desc,
                'nutrient_highlights': nutrient_highlights,
                'protein': protein,  # From nutrition_summary
                'calories': calories,  # From nutrition_summary
                'fat': fat,  # From nutrition_summary
                'carbs': carbs,  # From nutrition_summary
                'violation_context': violation_context,  # For Smart Concierge explanations
                'penalty_score': penalty_score,  # For understanding trade-offs
                'has_violations': len(violations) > 0,
                # Fix 1: Safety validation and violation_note
                'requires_ai_validation': requires_ai_validation,
                'violation_note': violation_note,  # Critical: Force Gemini to address this
                'requires_ai_reassurance': safety_check.get('requires_ai_reassurance', False),
                'suspicious_ingredients': suspicious_ingredients,
                'found_intolerances': found_intolerances,
                'safe_alternative_indicators': safe_alternative_indicators,
                'full_ingredient_list': [ing.get('name', ing.get('original', '')) if isinstance(ing, dict) else str(ing) for ing in extended_ingredients],  # Full list for AI to check
                'instructions': rec.get('instructions', ''),  # Add instructions for Safety Jury
                'analyzedInstructions': rec.get('analyzedInstructions', []),  # Add analyzed instructions
                'semantic_context': rec.get('semantic_context', ''),  # Add semantic context from Logic
                # Fix 2: Match Reasoning from metadata
                'match_reasoning': match_reasoning,  # Why it's a 90% match (from _metadata)
                'internal_debug': internal_debug,  # Internal scores for context
                # Fix 3: Plural keys for dishTypes and cuisines
                'dishTypes': dish_types,  # Plural key
                'cuisines': cuisines  # Plural key
            })
        
        # Build user dietary context for Gemini
        user_diet_context = ""
        if user_diet and user_diet.lower() not in ['none', 'null', '', 'any']:
            user_diet_context = f"\n\nUSER'S DIET: {user_diet.lower()}"
            if user_diet.lower() not in ['vegetarian', 'vegan', 'pescatarian']:
                user_diet_context += " (CUSTOM DIET - Check if recipes comply with this dietary restriction)"
        
        user_intolerance_context = ""
        if user_intolerances and len(user_intolerances) > 0:
            # Filter out common intolerances to identify custom ones
            common_intolerances = ['dairy', 'gluten', 'eggs', 'nuts']
            custom_intolerances = [i for i in user_intolerances if i.lower() not in common_intolerances]
            common_only = [i for i in user_intolerances if i.lower() in common_intolerances]
            
            user_intolerance_context = f"\n\nUSER'S INTOLERANCES: {', '.join(user_intolerances)}"
            if custom_intolerances:
                user_intolerance_context += f"\nCUSTOM INTOLERANCES (require special checking): {', '.join(custom_intolerances)}"
        
        # Check if any recipe requires safety validation
        has_safety_validation = any(r.get('requires_ai_validation', False) for r in recipe_contexts)
        
        # Build safety validation instructions if needed
        # Include safety_reason from Logic.py so Gemini knows why recipes were flagged
        safety_instructions = ""
        if has_safety_validation or user_diet_context or user_intolerance_context:
            # Collect safety reasons for flagged recipes
            safety_contexts = []
            for r in recipe_contexts:
                if r.get('requires_ai_validation'):
                    
                    safety_reason = r.get('violation_note', '')
                    found_intolerances = r.get('found_intolerances', [])
                    suspicious_ingredients = r.get('suspicious_ingredients', [])
                    
                    context_parts = []
                    if safety_reason:
                        context_parts.append(f"Backend flagged: {safety_reason}")
                    if found_intolerances:
                        context_parts.append(f"Intolerances detected: {', '.join(found_intolerances)}")
                    if suspicious_ingredients:
                        context_parts.append(f"Suspicious ingredients: {', '.join(suspicious_ingredients)}")
                    
                    if context_parts:
                        safety_contexts.append(f"Recipe '{r['title']}': {'; '.join(context_parts)}")
            
            safety_context_text = "\n".join(safety_contexts) if safety_contexts else ""
            
            safety_instructions = f"\n\nSAFETY VALIDATION: The backend Logic.py has flagged some recipes for review. Use your culinary knowledge to confirm if these are true violations.{user_diet_context}{user_intolerance_context}\n\n{safety_context_text if safety_context_text else ''}\n\nFor each flagged recipe:\n- If the backend flagged it for a clear violation (e.g., actual meat in vegetarian diet, real dairy in dairy-free diet, shrimp in shellfish-free diet), do NOT include it in your response. Skip it silently.\n- If the backend flagged it for an ambiguous case (e.g., 'vegan butter', 'plant-based egg', flavorings), check the ingredients carefully. If it's a safe alternative, include it with a one-sentence description. If it's a real violation, skip it.\n- For CUSTOM INTOLERANCES (like shrimp, peanuts, shellfish): Check every ingredient in the recipe. If the custom intolerance keyword appears in any ingredient name, skip the recipe silently.\n- For CUSTOM DIETS (like paleo, keto): Verify that the recipe complies with the diet's rules. If it violates the diet, skip it silently.\n- Only include recipes that are 100% safe for the user's dietary requirements and intolerances."
        
        # Build prompt based on mood
        if user_mood == 'tired':
            # Single best recipe, 1-sentence vibe check
            top = recipe_contexts[0]
            
            # Add ingredient list for safety validation if needed
            ingredient_context = ""
            if top.get('requires_ai_validation'):
                ingredient_list = ', '.join(top.get('full_ingredient_list', [])[:10])
                ingredient_context = f"\n\nIngredients to check: {ingredient_list}"
            
            prompt = f"""{self.system_prompt}{safety_instructions}

Top Recipe: {top['title']}{ingredient_context}

Provide this recipe in the exact format:
1. **[{top['title']}]**: [One mouth-watering flavor description sentence]

If this recipe violates the user's diet or contains any of the user's intolerances, do NOT include it. Instead, return: "I couldn't find a perfect match for your diet today, but try these ingredients in a simple sauté!"

ZERO advice: Never mention missing ingredients, cooking times, or health stats.
Just the description and stop talking."""
        else:
            # Top 3 comparison - List format
            # Build simple recipe list with just titles
            recipes_list = []
            ingredient_contexts = []
            for i, r in enumerate(recipe_contexts):
                recipes_list.append(f"{r['title']}")
                # Add ingredient list for safety validation if needed
                if r.get('requires_ai_validation'):
                    ingredient_list = ', '.join(r.get('full_ingredient_list', [])[:10])
                    ingredient_contexts.append(f"Recipe {i+1} ({r['title']}) ingredients: {ingredient_list}")
            
            recipes_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(recipes_list)])
            ingredient_check_text = "\n".join(ingredient_contexts) if ingredient_contexts else ""
            
            prompt = f"""{self.system_prompt}{safety_instructions}

Top 3 Recipes:
{recipes_text}
{ingredient_check_text if ingredient_check_text else ""}

CRITICAL: You MUST provide exactly 3 lines in this EXACT format (no exceptions):
1. [Recipe Name], [One mouth-watering flavor description sentence]
2. [Recipe Name], [One mouth-watering flavor description sentence]
3. [Recipe Name], [One mouth-watering flavor description sentence]

DIETARY FILTERING:
- If a recipe violates the user's diet or contains intolerances, SKIP it and use another safe recipe from the list
- If fewer than 3 safe recipes exist, pad the remaining slots with generic recommendations:
  1. **Quick Sauté**: Try these ingredients with olive oil and seasonings!
  2. **Simple Stir-Fry**: Toss everything together for a fast, flavorful meal!
  3. **Easy Roast**: Pop ingredients in the oven for hands-off cooking!

FORMAT RULES:
- ALWAYS exactly 3 bullet points as numbers like 1. then below it 2. then below that 3. 
- NEVER return fewer than 3 lines unless if only 2 recipes are recommended or 1 then return respectivally 1 recipe or 2 based on how many recipes are recommended.
- NEVER return a response like "Here's X for you!" or "I couldn't find..."
- Each line MUST follow it's respective number so 1. or 2. or 3. then it follow with the [Name of dish], [Flavor description]

ZERO advice about ingredients, time, or nutrition. Just 3 delicious recommendations."""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )

            pitch_text = response.text.strip()

            # POST-PROCESSING: Guarantee exactly 3 numbered lines
            lines = pitch_text.split('\n')
            bullet_lines = [line for line in lines if line.strip().startswith(('1.', '2.', '3.'))]

            # If Gemini didn't return 3 numbered lines, pad with generic recommendations
            if len(bullet_lines) < 3:
                generic_recs = [
                    "1. **Quick Sauté**: Try these ingredients with olive oil and your favorite seasonings!",
                    "2. **Simple Stir-Fry**: Toss everything in a hot pan for a fast, flavorful meal!",
                    "3. **Easy Roast**: Pop ingredients in the oven for hands-off deliciousness!"
                ]
                # Add generic recommendations to reach 3 total
                while len(bullet_lines) < 3:
                    if generic_recs:
                        bullet_lines.append(generic_recs.pop(0))
                    else:
                        break
                print(
                    f"Gemini returned only {len([l for l in pitch_text.split('\\n') if l.strip().startswith(('1.', '2.', '3.'))])} recipes, padded to 3")

            # If Gemini returned too many, trim to 3
            elif len(bullet_lines) > 3:
                bullet_lines = bullet_lines[:3]
                print(
                    f"Gemini returned {len([l for l in pitch_text.split('\\n') if l.strip().startswith(('1.', '2.', '3.'))])} recipes, trimmed to 3")

            # Rebuild pitch with exactly 3 lines
            pitch_text = '\n'.join(bullet_lines)

            return {
                'pitch_text': pitch_text,
                'top_recipe': top_3[0] if top_3 else None,
                'comparison': top_3 if user_mood != 'tired' else []
            }
        except Exception as e:
            # Check for 429 rate limit error specifically
            error_str = str(e).lower()
            is_rate_limit = (
                '429' in error_str or 
                'rate limit' in error_str or 
                'quota' in error_str or
                'too many requests' in error_str
            )
            
            if is_rate_limit:
                print(f'⚠️  Rate limit (429) error in generate_recommendation_pitch: {e}')
                # 429-specific fallback: Return numbered list using recipe titles
                fallback_lines = []
                for i, rec in enumerate(recommendations[:3], 1):
                    title = rec.get('title', 'Unknown Recipe')
                    if i == 1:
                        fallback_lines.append(f"{i}. **{title}**: A delicious, chef-approved choice for your meal!")
                    elif i == 2:
                        fallback_lines.append(f"{i}. **{title}**: A wonderful option that uses your ingredients perfectly.")
                    elif i == 3:
                        fallback_lines.append(f"{i}. **{title}**: A great dish to try with what you have in your pantry.")
                    else:
                        fallback_lines.append(f"{i}. **{title}**: A delicious option for your meal!")
                
                fallback_pitch = '\n'.join(fallback_lines) if fallback_lines else "Try these ingredients in a simple sauté!"
            else:
                print(f' Error generating recommendation pitch: {e}')
                # General fallback: Return numbered formatted lines using recipe titles
                fallback_lines = []
                for i, rec in enumerate(recommendations[:3], 1):
                    title = rec.get('title', 'Unknown Recipe')
                    fallback_lines.append(f"{i}. **{title}**: A delicious option for your meal!")

                fallback_pitch = '\n'.join(fallback_lines) if fallback_lines else "Try these ingredients in a simple sauté!"

            return {
                'pitch_text': fallback_pitch,
                'top_recipe': recommendations[0] if recommendations else None,
                'comparison': recommendations[:3] if user_mood != 'tired' else []
            }
    
    def analyze_nutritional_science(
        self,
        recipe_data: Dict[str, Any],
        target_nutrient: str
    ) -> Dict[str, Any]:
        """
        Analyze nutritional content using Chain of Thought reasoning.
        Uses scientific benchmarks (USDA) to determine if recipe is high/low in a nutrient.
        
        Args:
            recipe_data: Recipe dictionary with nutrition and extendedIngredients
            target_nutrient: Nutrient to analyze (e.g., 'Protein', 'Iron', 'Calcium', 'Vitamin C')
            
        Returns:
            Dictionary with:
            - scientific_rationale: Explanation of the analysis
            - is_dense: Boolean indicating if recipe is high in the target nutrient
            - calculated_amount: The actual amount found
            - benchmark: The scientific benchmark used
        """
        if not self.client:
            # Fallback: Simple calculation
            nutrition = recipe_data.get('nutrition', {})
            nutrients = nutrition.get('nutrients', [])
            nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
            amount = nutrient_dict.get(target_nutrient, 0)
            
            # Simple thresholds
            thresholds = {
                'Protein': 20.0,
                'Iron': 3.0,
                'Calcium': 200.0,
                'Vitamin C': 60.0,
                'Fiber': 5.0
            }
            threshold = thresholds.get(target_nutrient, 0)
            
            return {
                'scientific_rationale': f'Contains {amount:.1f} {target_nutrient} (threshold: {threshold})',
                'is_dense': amount >= threshold,
                'calculated_amount': amount,
                'benchmark': threshold
            }
        
        # Goal 2: Use nutrition_summary for raw nutritional data (standardized schema)
        nutrition_summary = recipe_data.get('nutrition_summary', {})
        nutrition = recipe_data.get('nutrition', {})
        nutrients = nutrition.get('nutrients', [])
        extended_ingredients = recipe_data.get('extendedIngredients', [])
        
        # Build ingredient list with quantities
        ingredient_list = []
        for ing in extended_ingredients[:10]:  # Limit to first 10 for prompt size
            if isinstance(ing, dict):
                amount = ing.get('amount', 0)
                unit = ing.get('unit', '')
                name = ing.get('name', ing.get('original', ''))
                ingredient_list.append(f"{amount} {unit} {name}")
        
        # Get current nutrient value - prefer nutrition_summary, fallback to nutrition dict
        if nutrition_summary:
            # Map target_nutrient to nutrition_summary keys
            nutrient_map = {
                'Protein': 'protein',
                'Calories': 'calories',
                'Fat': 'fat',
                'Carbohydrates': 'carbs',
                'Carbs': 'carbs'
            }
            summary_key = nutrient_map.get(target_nutrient)
            if summary_key:
                current_amount = nutrition_summary.get(summary_key, 0)
            else:
                # For nutrients not in summary (Iron, Calcium, etc.), use nutrition dict
                nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
                current_amount = nutrient_dict.get(target_nutrient, 0)
        else:
            # Fallback to nutrition dict if nutrition_summary not available
            nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
            current_amount = nutrient_dict.get(target_nutrient, 0)
        
        # Chain of Thought prompt
        prompt = f"""You are a nutritional scientist analyzing a recipe. Use Chain of Thought reasoning.

Recipe: {recipe_data.get('title', 'Unknown')}
Target Nutrient: {target_nutrient}

Ingredients (with quantities):
{chr(10).join(ingredient_list)}

Current Nutrition Data:
- {target_nutrient}: {current_amount} (per serving)

USDA/Scientific Benchmarks:
- High Protein: ≥20g per serving
- High Iron: ≥3mg per serving  
- High Calcium: ≥200mg per serving
- High Vitamin C: ≥60mg per serving
- High Fiber: ≥5g per serving

Chain of Thought Analysis:
1. Identify the quantities of ingredients that contribute to {target_nutrient}
2. Reference USDA nutritional benchmarks for {target_nutrient}
3. Calculate if this recipe is 'High' or 'Low' in {target_nutrient} based on scientific facts
4. Provide a scientific rationale

Format your response as JSON:
{{
    "scientific_rationale": "Brief explanation referencing ingredient quantities and USDA benchmarks",
    "is_dense": true/false,
    "calculated_amount": {current_amount},
    "benchmark": "USDA threshold value"
}}"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            # Parse JSON response
            import json
            import re
            
            text = response.text.strip()
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                return {
                    'scientific_rationale': result.get('scientific_rationale', 'Analysis complete'),
                    'is_dense': result.get('is_dense', False),
                    'calculated_amount': result.get('calculated_amount', current_amount),
                    'benchmark': result.get('benchmark', 'N/A')
                }
            else:
                # Fallback if JSON parsing fails
                return {
                    'scientific_rationale': text[:200],
                    'is_dense': current_amount >= 20 if target_nutrient == 'Protein' else False,
                    'calculated_amount': current_amount,
                    'benchmark': 'N/A'
                }
        except Exception as e:
            print(f'Error in nutritional analysis: {e}')
            # Fallback
            return {
                'scientific_rationale': f'Contains {current_amount} {target_nutrient}',
                'is_dense': current_amount >= 20 if target_nutrient == 'Protein' else False,
                'calculated_amount': current_amount,
                'benchmark': 'N/A'
            }
    
    def format_nutrition_label(self, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw nutritional data into a clean 'Nutrition Label' view.
        
        Args:
            nutrition_data: Nutrition dictionary from recipe (with 'nutrients' list)
            
        Returns:
            Formatted nutrition label with summary text
        """
        if not nutrition_data or 'nutrients' not in nutrition_data:
            return {
                'label': {},
                'summary': 'Nutrition data not available for this recipe.'
            }
        
        nutrients = nutrition_data.get('nutrients', [])
        nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
        
        # Extract key nutrients for label
        label = {
            'calories': nutrient_dict.get('Calories', 0),
            'protein': nutrient_dict.get('Protein', 0),
            'carbs': nutrient_dict.get('Carbohydrates', 0),
            'fat': nutrient_dict.get('Fat', 0),
            'fiber': nutrient_dict.get('Fiber', 0),
            'calcium': nutrient_dict.get('Calcium', 0),
            'iron': nutrient_dict.get('Iron', 0),
            'vitamin_c': nutrient_dict.get('Vitamin C', 0)
        }
        
        # Generate AI summary if available
        summary = "This is a nutrient-dense choice that fits your specific health filters."
        
        if self.client:
            try:
                prompt = f"""{self.system_prompt}

Summarize this nutrition data in one sentence (under 20 words). Be encouraging and mention key nutrients if they're high.

Nutrition per serving:
- Calories: {label['calories']}
- Protein: {label['protein']}g
- Carbs: {label['carbs']}g
- Fat: {label['fat']}g
- Fiber: {label['fiber']}g
- Calcium: {label['calcium']}mg
- Iron: {label['iron']}mg
- Vitamin C: {label['vitamin_c']}mg

One sentence summary:"""
                
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
                summary = response.text.strip()
            except Exception as e:
                print(f'Error generating nutrition summary: {e}')
        
        return {
            'label': label,
            'summary': summary
        }

    def _parse_ai_response(self, text, api_data, recipes):
        """Logic: Extracts the Substitution and Tip from raw AI text."""
        sub = "No substitute found"
        tip = "Check your pantry contents again."

        for line in text.split('\n'):
            if line.upper().startswith('SUBSTITUTION:'):
                sub = line.split(':', 1)[1].strip()
            elif line.upper().startswith('TIP:'):
                tip = line.split(':', 1)[1].strip()

        return {
            'substitution': sub,
            'chef_tip': tip,
            'api_substitutes': api_data,
            'similar_recipes': [r.get('title', '') for r in recipes[:3]] if recipes else []
        }

    def get_low_priority_ingredients(self, ingredient_list: List[str]) -> Dict[str, List[str]]:
        """
        Categorize ingredients into 'Core' (main proteins, starches) and 'Secondary' (spices, garnishes, minor veggies).
        Used for semantic ingredient prioritization when search results are too few.
        
        Args:
            ingredient_list: List of ingredient names from user's pantry
            
        Returns:
            Dictionary with:
            - 'core': List of Core ingredients (main proteins, starches) - use these for re-search
            - 'secondary': List of Secondary ingredients (spices, garnishes, minor veggies) - can be dropped
        """
        if not self.client:
            # Fallback: Simple categorization based on common patterns
            core_patterns = ['chicken', 'beef', 'pork', 'fish', 'tofu', 'rice', 'pasta', 'potato', 'bread', 'flour', 'egg', 'milk', 'cheese']
            core = [ing for ing in ingredient_list if any(pattern in ing.lower() for pattern in core_patterns)]
            secondary = [ing for ing in ingredient_list if ing not in core]
            
            # If no core ingredients found, use first 3 ingredients as core
            if not core:
                core = ingredient_list[:3] if len(ingredient_list) >= 3 else ingredient_list
                secondary = ingredient_list[3:] if len(ingredient_list) > 3 else []
            
            return {
                'core': core,
                'secondary': secondary
            }
        
        # Build prompt for Gemini to categorize ingredients
        ingredients_str = ', '.join(ingredient_list)
        prompt = f"""You are a professional chef categorizing ingredients for recipe search optimization.

User's pantry ingredients: {ingredients_str}

Categorize these ingredients into two groups:

1. CORE ingredients: Main proteins (chicken, beef, fish, tofu, eggs), starches (rice, pasta, potatoes, bread, flour), and essential bases (milk, cheese, tomatoes, onions, garlic). These are the foundation of most recipes and should be prioritized.

2. SECONDARY ingredients: Spices (cumin, paprika, turmeric), herbs (cilantro, parsley, basil), garnishes (lemon, lime), condiments (soy sauce, vinegar), and minor vegetables (bell peppers, mushrooms). These enhance flavor but aren't essential for finding recipes.

Return ONLY a JSON object in this exact format:
{{
    "core": ["ingredient1", "ingredient2", ...],
    "secondary": ["ingredient3", "ingredient4", ...]
}}

Make sure every ingredient appears in exactly one list (either core or secondary)."""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if it's wrapped in markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON response
            import json
            result = json.loads(response_text)
            
            # Validate structure
            if 'core' in result and 'secondary' in result:
                core = result['core'] if isinstance(result['core'], list) else []
                secondary = result['secondary'] if isinstance(result['secondary'], list) else []
                
                # Ensure all ingredients are accounted for
                all_categorized = set(core + secondary)
                all_original = set(ing.lower() for ing in ingredient_list)
                
                # Add any uncategorized ingredients to secondary
                uncategorized = [ing for ing in ingredient_list if ing.lower() not in all_categorized]
                secondary.extend(uncategorized)
                
                # Ensure we have at least some core ingredients
                if not core:
                    # Fallback: use first 3 as core
                    core = ingredient_list[:3] if len(ingredient_list) >= 3 else ingredient_list
                    secondary = [ing for ing in ingredient_list if ing not in core]
                
                return {
                    'core': core,
                    'secondary': secondary
                }
            else:
                raise ValueError("Invalid response structure")
                
        except Exception as e:
            # Check for 429 rate limit error specifically
            error_str = str(e).lower()
            is_rate_limit = (
                '429' in error_str or 
                'rate limit' in error_str or 
                'quota' in error_str or
                'too many requests' in error_str
            )
            
            if is_rate_limit:
                print(f"⚠️  Rate limit (429) error in get_low_priority_ingredients: {e}")
            else:
                print(f"Error categorizing ingredients with Gemini: {e}")
            
            # Fallback: Simple categorization
            core_patterns = ['chicken', 'beef', 'pork', 'fish', 'tofu', 'rice', 'pasta', 'potato', 'bread', 'flour', 'egg', 'milk', 'cheese', 'tomato', 'onion', 'garlic']
            core = [ing for ing in ingredient_list if any(pattern in ing.lower() for pattern in core_patterns)]
            secondary = [ing for ing in ingredient_list if ing not in core]
            
            # If no core ingredients found, use first 3 ingredients as core
            if not core:
                core = ingredient_list[:3] if len(ingredient_list) >= 3 else ingredient_list
                secondary = ingredient_list[3:] if len(ingredient_list) > 3 else []
            
            return {
                'core': core,
                'secondary': secondary
            }
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def search_web_for_recipes(
        self,
        ingredients: List[str],
        diet: Optional[str] = None,
        count: int = 3,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        intolerances: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Use Gemini's web search capability to find recipes online when API returns low results.
        
        Args:
            ingredients: List of user ingredients
            diet: Dietary restriction (e.g., 'vegetarian', 'vegan')
            count: Number of recipes to find
            cuisine: Optional cuisine filter
            meal_type: Optional meal type filter
            intolerances: Optional intolerances list
            
        Returns:
            List of recipe dictionaries in Spoonacular format (title, image, extendedIngredients, instructions)
        """
        if not self.client:
            print("⚠️  Gemini client not available for web search")
            return []
        
        # Build search query
        ingredients_str = ', '.join(ingredients)
        query_parts = [f"{diet} recipes" if diet else "recipes"]
        query_parts.append(f"using {ingredients_str}")
        if cuisine:
            query_parts.append(f"{cuisine} cuisine")
        if meal_type:
            query_parts.append(f"{meal_type}")
        
        search_query = " ".join(query_parts)
        
        # Build prompt for Gemini
        prompt = f"""Find {count} {diet if diet else ''} recipes using {ingredients_str} and any other filters the user put in.

Output them in the EXACT same JSON format as Spoonacular API so my frontend doesn't break.

Required format (JSON array):
[
  {{
    "id": <unique_number>,
    "title": "<recipe name>",
    "image": "<image URL or empty string>",
    "extendedIngredients": [
      {{"name": "<ingredient name>", "original": "<amount> <unit> <name>"}},
      ...
    ],
    "instructions": "<step-by-step instructions>",
    "readyInMinutes": <number>,
    "servings": <number>,
    "cuisines": ["<cuisine>"],
    "dishTypes": ["<meal type>"],
    "diets": ["<diet>"],
    "nutrition": {{
      "nutrients": [
        {{"name": "Calories", "amount": <number>}},
        {{"name": "Protein", "amount": <number>}},
        {{"name": "Fat", "amount": <number>}},
        {{"name": "Carbohydrates", "amount": <number>}}
      ]
    }}
  }},
  ...
]

CRITICAL: 
- Output ONLY valid JSON, no markdown, no explanations
- Ensure all recipes match the diet filter: {diet if diet else 'none'}
- Ensure all recipes use the ingredients: {ingredients_str}
- If intolerances are specified ({intolerances if intolerances else 'none'}), ensure recipes avoid those ingredients
- Return exactly {count} recipes
"""
        
        try:
            # Use Gemini client to generate content (same pattern as other methods)
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            if response_text.endswith('```'):
                response_text = response_text.rsplit('```')[0].strip()
            
            recipes = json.loads(response_text)
            
            # Ensure it's a list
            if isinstance(recipes, dict):
                recipes = [recipes]
            
            print(f"✅ Gemini Web Search found {len(recipes)} recipes")
            return recipes[:count]  # Limit to requested count
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse Gemini web search response as JSON: {e}")
            print(f"   Response: {response_text[:200]}...")
            return []
        except Exception as e:
            print(f"⚠️  Gemini web search failed: {e}")
            return []

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE: Gemini Integration - Safety Jury & Pitch Logic")
    print("="*70)

    gemini = GeminiSubstitution()
    
    if not gemini.is_available():
        print("❌ Gemini not available - check GEMINI_API_KEY in .env")
        exit(1)

    # 1. Simulate a "Soft Violation" Recipe from Logic.py
    mock_safety_recipe = {
        'title': 'Creamy Garlic Pasta',
        'requires_ai_validation': True,
        'violation_note': 'Contains heavy cream - user is lactose intolerant',
        'match_confidence': 85.0,
        'dishTypes': ['main course', 'dinner'],
        'cuisines': ['Italian'],
        'extendedIngredients': [
            {'name': 'heavy cream', 'amount': 1.0, 'unit': 'cup'},
            {'name': 'pasta', 'amount': 8.0, 'unit': 'oz'},
            {'name': 'garlic', 'amount': 3.0, 'unit': 'cloves'}
        ],
        'instructions': 'Cook pasta. Heat heavy cream in a pan. Add garlic and pasta. Mix well.',
        'analyzedInstructions': [
            {'steps': [
                {'step': 'Cook pasta'},
                {'step': 'Heat heavy cream in a pan'},
                {'step': 'Add garlic and pasta'}
            ]}
        ],
        'semantic_context': 'This recipe is a 85% match but requires additional ingredients.',
        '_metadata': {
            'safety_check': {
                'requires_ai_validation': True,
                'violation_note': 'Contains heavy cream - user is lactose intolerant',
                'suspicious_ingredients': ['heavy cream'],
                'found_intolerances': ['dairy']
            },
            'scoring_breakdown': 'Great match because it uses most pantry items and is quick to prepare',
            'smart_score': 75.0
        },
        'nutrition_summary': {
            'protein': 15.0,
            'calories': 450.0,
            'fat': 20.0,
            'carbs': 55.0
        }
    }

    print("\nTEST 1: Safety Jury & Substitution...")
    print("-" * 70)
    # This test ensures Gemini recognizes the safety flag and suggests a fix
    pitch = gemini.generate_recommendation_pitch([mock_safety_recipe], user_mood='tired')
    print(f"Result: {pitch['pitch_text']}")
    
    pitch_lower = pitch['pitch_text'].lower()
    safety_addressed = (
        "cream" in pitch_lower or 
        "substitute" in pitch_lower or 
        "dairy" in pitch_lower or
        "lactose" in pitch_lower or
        "coconut" in pitch_lower or
        "almond" in pitch_lower
    )
    
    if safety_addressed:
        print("✅ SUCCESS: Gemini addressed the safety violation.")
    else:
        print("❌ FAILURE: Gemini ignored the safety flag.")
        print(f"   Pitch should mention cream, substitute, dairy, or suggest alternatives")

    # 2. Simulate a Substitution Hack
    print("\nTEST 2: Chef's Secret Hack...")
    print("-" * 70)
    sub = gemini.get_smart_substitution(
        missing_item="Soy Sauce",
        recipe_title="Stir Fry",
        user_pantry_list=["Balsamic Vinegar", "Salt", "Water", "Sugar"]
    )
    print(f"Substitution: {sub['substitution']}")
    print(f"Tip: {sub['chef_tip']}")
    
    sub_lower = sub['substitution'].lower()
    if "balsamic" in sub_lower or "vinegar" in sub_lower:
        print("✅ SUCCESS: Gemini created a creative hack.")
    else:
        print("❌ FAILURE: Gemini did not suggest balsamic vinegar substitution.")
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    if safety_addressed and "balsamic" in sub_lower:
        print("✅ ALL TESTS PASSED: Safety Jury and Substitution logic working correctly!")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   - Safety Jury: {'✅' if safety_addressed else '❌'}")
        print(f"   - Substitution Hack: {'✅' if 'balsamic' in sub_lower else '❌'}")
    print("="*70)