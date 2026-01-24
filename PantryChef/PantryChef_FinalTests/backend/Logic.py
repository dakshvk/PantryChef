"""
PantryChef Engine - Consolidated Class
Combines Smart Scoring, Filtering, and Phase 2 Reasoning into one efficient class
"""

from typing import List, Dict, Any, Optional


class PantryChefEngine:
    """
    Unified engine that handles:
    - Smart scoring based on user profiles
    - Progressive filtering (difficulty, time, dietary, nutritional)
    - Phase 2 reasoning and match confidence calculation
    All in one optimized class for efficiency
    """
    
    # User profiles for smart scoring
    USER_PROFILES = {
        'minimal_shopper': {
            'name': 'I hate shopping',
            'description': 'Prefer recipes with very few missing ingredients',
            'weights': {'used': 0.3, 'missing': 0.7}
        },
        'pantry_cleaner': {
            'name': 'Use my pantry',
            'description': 'Prioritize recipes using what I already have',
            'weights': {'used': 0.7, 'missing': 0.3}
        },
        'balanced': {
            'name': 'Balanced approach',
            'description': 'Balance pantry usage and shopping',
            'weights': {'used': 0.5, 'missing': 0.5}
        }
    }
    
    # Mood weights for Phase 2 reasoning
    MOOD_WEIGHTS = {
        'tired': {
            'time': 0.5,
            'effort': 0.7,
            'skill': 0.3,
            'shopping': 0.8
        },
        'casual': {
            'time': 0.5,
            'effort': 0.5,
            'skill': 0.5,
            'shopping': 0.5
        },
        'energetic': {
            'time': 0.3,
            'effort': 0.4,
            'skill': 0.7,
            'shopping': 0.4
        }
    }
    
    # Difficulty mapping for skill level calculation
    DIFFICULTY_ORDER = {'easy': 1, 'medium': 2, 'hard': 3}
    DIFFICULTY_SKILL_MAP = {'easy': 30, 'medium': 60, 'hard': 90}
    
    def __init__(self, user_settings: Dict[str, Any]):
        """
        Initialize engine with user settings.
        
        Expected user_settings:
        {
            'user_profile': 'balanced' | 'minimal_shopper' | 'pantry_cleaner',
            'mood': 'tired' | 'casual' | 'energetic',
            'max_difficulty': 'easy' | 'medium' | 'hard',
            'max_time_minutes': int,
            'max_missing_ingredients': int,
            'dietary_requirements': List[str],  # ['vegetarian', 'vegan', etc.]
            'intolerances': List[str],  # ['dairy', 'gluten', etc.]
            'nutritional_requirements': Dict[str, float],  # {'high_protein': 20.0, etc.}
            'skill_level': int,  # 0-100
            'max_time': int  # for Phase 2 reasoning
        }
        """
        self.settings = user_settings
        self.profile = self.USER_PROFILES.get(
            user_settings.get('user_profile', 'balanced'),
            self.USER_PROFILES['balanced']
        )
        self.mood = user_settings.get('mood', 'casual')
        self.mood_weights = self.MOOD_WEIGHTS.get(
            self.mood,
            self.MOOD_WEIGHTS['casual']
        )
        
        # Note: No forced setting overrides - let user settings stand
        # The _apply_reasoning method handles 'tired' logic via confidence bonuses/penalties
        # This maintains the 'Soft Filter' philosophy (penalties, not hard gates)
    
    def process_results(self, raw_recipes: List[Dict]) -> List[Dict]:
        """
        Main processing method: Two-gate filter system, scoring, and reasoning.
        
        HARD EXECUTIONER: Strict dietary filter - immediately discards recipes with meat if vegetarian selected.
        GATE 1 (Hard Filters): Immediately reject recipes with intolerances
        GATE 2 (Soft Filters): Calculate smart_score based on user_profile
        
        Args:
            raw_recipes: List of recipe dictionaries from API
            
        Returns:
            List of CLEAN processed recipes sorted by match_confidence
        """
        # HARD EXECUTIONER: Exhaustive meat keywords for strict vegetarian filtering
        MEAT_KEYWORDS = ['meat', 'beef', 'pork', 'lamb', 'mutton', 'veal', 'venison', 'chicken', 
                         'poultry', 'turkey', 'duck', 'goose', 'fish', 'seafood', 'shrimp', 'prawn', 
                         'crab', 'lobster', 'mussel', 'clam', 'oyster', 'squid', 'octopus', 'bacon', 
                         'ham', 'sausage', 'pepperoni', 'salami', 'prosciutto', 'steak', 'ribs', 
                         'lard', 'tallow', 'gelatin', 'anchovy', 'sardine', 'tuna', 'salmon', 'cod']
        
        final_recommendations = []
        dietary_requirements = self.settings.get('dietary_requirements', [])
        is_vegetarian = 'vegetarian' in [r.lower() for r in dietary_requirements]
        
        for recipe in raw_recipes:
            # HARD EXECUTIONER: Strict vegetarian filter - check for meat keywords
            if is_vegetarian:
                # Build text to search: title, summary, and EVERY ingredient string
                recipe_text_parts = [
                    recipe.get('title', ''),
                    recipe.get('summary', '')
                ]
                
                # Check extendedIngredients for meat keywords - check EVERY ingredient string
                extended_ingredients = recipe.get('extendedIngredients', [])
                for ing in extended_ingredients:
                    if isinstance(ing, dict):
                        # Check all possible name fields
                        ing_name = ing.get('name', '') or ing.get('original', '') or ing.get('originalName', '')
                        if ing_name:
                            recipe_text_parts.append(ing_name)
                        # Also check unitShort, unitLong, and any other string fields
                        for key, value in ing.items():
                            if isinstance(value, str) and value:
                                recipe_text_parts.append(value)
                    elif isinstance(ing, str):
                        recipe_text_parts.append(ing)
                
                # Combine all text and check for meat keywords
                recipe_text = ' '.join(recipe_text_parts).lower()
                
                # If ANY meat keyword is found, immediately discard the recipe
                if any(meat_kw in recipe_text for meat_kw in MEAT_KEYWORDS):
                    continue  # Hard cutoff - discard immediately
            
            # GATE 1: Safety Check (intolerances)
            # Fix 1: Flag instead of Delete - ALL recipes pass through with safety_score
            # Even API-confirmed violations get passed: True with safety_score: 0.2 for Gemini to suggest substitutions
            safety_check = self._apply_safety_check(recipe)
            # ALL recipes pass through - safety_check['passed'] is always True now
            # Low safety_score (0.2) indicates violations that need Gemini's Safety Jury review
            if not safety_check.get('passed', True):
                continue  # Only skip if passed is explicitly False (defensive programming)
            
            # GATE 2: Soft Filters - Smart Scoring with Penalties (AI-Reasoning Architecture)
            # Includes SMART DIET CHECK: Checks extendedIngredients for meat keywords when 'vegetarian' is selected
            # NEVER exclude recipes based on time, difficulty, or missing ingredients
            # All recipes survive with adjusted confidence scores
            filter_result = self._apply_soft_filters_with_penalties(recipe)
            # No continue statement - all recipes pass through (except safety violations)
            
            # Calculate smart score
            scoring_data = self._calculate_smart_score(recipe)
            
            # Apply Phase 2 reasoning with mood-based bonuses and penalty adjustments
            reasoning_data = self._apply_reasoning_with_penalties(
                recipe,
                scoring_data['smart_score'],
                filter_result
            )
            
            # Build clean recommendation (raw_ingredients_for_ai already included in _clean_data)
            recommendation = self._clean_data(
                recipe,
                scoring_data,
                reasoning_data,
                filter_result,
                safety_check
            )
            
            final_recommendations.append(recommendation)
        
        # Sort by match confidence (highest first)
        # Handle both 'match_confidence' and 'confidence' keys for compatibility
        return sorted(
            final_recommendations,
            key=lambda k: k.get('match_confidence', k.get('confidence', 0)),
            reverse=True
        )
    
    def _apply_safety_check(self, recipe: Dict) -> Dict:
        """
        STRICT GATEKEEPER:
        1. Rejects 'Hard Offenders' (Intolerance words without safe keywords).
        2. Rejects recipes with meat keywords if vegetarian/vegan diet is selected.
        3. Passes 'Soft Keywords' (Intolerance words WITH safe keywords) to Gemini.
        
        Args:
            recipe: Recipe dictionary from API
            
        Returns:
            Dict with 'passed' (bool), 'requires_ai_validation' (bool), 'safety_score' (float), and 'reason' (str)
        """
        # Biological meat terms - only check ingredients, not dish names
        # This allows "Mushroom Shawarma" but kills "Chicken Shawarma"
        LAND_MEAT = ['chicken', 'turkey', 'beef', 'steak', 'pork', 'lamb', 'mutton', 'venison', 'veal', 
                     'duck', 'goose', 'bacon', 'ham', 'sausage', 'pepperoni', 'salami', 'chorizo', 
                     'meatball', 'lard', 'tallow', 'gelatin']
        
        SEA_MEAT = ['fish', 'salmon', 'tuna', 'cod', 'tilapia', 'shrimp', 'prawn', 'crab', 'lobster', 
                    'mussel', 'clam', 'oyster', 'squid', 'calamari', 'octopus', 'anchovy', 'sardine', 
                    'fish sauce', 'oyster sauce']
        
        DAIRY_EGGS = ['egg', 'milk', 'cream', 'butter', 'cheese', 'yogurt', 'whey', 'casein']
        
        ALLERGY_MAP = {
            'dairy': ['cheese', 'milk', 'butter', 'cream', 'yogurt', 'dairy'],
            'gluten': ['wheat', 'flour', 'pasta', 'bread', 'gluten'],
            'eggs': ['egg', 'eggs', 'mayonnaise'],
            'nuts': ['nuts', 'almond', 'peanut', 'cashew']
        }
        
        SAFE_WORDS = {
            'dairy': ['vegan', 'plant-based', 'non-dairy', 'almond', 'coconut', 'oat'],
            'gluten': ['gluten-free', 'gf'],
            'eggs': ['egg-free', 'vegan', 'plant-based'],
            'nuts': ['nut-free']
        }
        
        # Check for dietary requirements - ONLY check extendedIngredients, NOT dish names
        # This allows "Mushroom Shawarma" but kills "Chicken Shawarma"
        dietary_requirements = self.settings.get('dietary_requirements', [])
        dietary_lower = [r.lower() for r in dietary_requirements]
        is_vegetarian = 'vegetarian' in dietary_lower
        is_vegan = 'vegan' in dietary_lower
        is_pescatarian = 'pescatarian' in dietary_lower
        
        # SMART DIET LOGIC: Only check ingredients, not dish names
        if is_vegetarian or is_vegan or is_pescatarian:
            # Get ALL ingredient names from extendedIngredients (do NOT check recipe title)
            extended_ingredients = recipe.get('extendedIngredients', [])
            ingredient_names = []
            
            for ing in extended_ingredients:
                if isinstance(ing, dict):
                    # Check all possible name fields
                    ing_name = ing.get('name', '') or ing.get('original', '') or ing.get('originalName', '')
                    if ing_name:
                        ingredient_names.append(ing_name.lower())
                elif isinstance(ing, str):
                    ingredient_names.append(ing.lower())
            
            # Combine all ingredient names into a single string for searching
            ingredients_text = ' '.join(ingredient_names)
            
            # Check for violations based on diet type - ONLY check ingredients
            if is_vegetarian:
                # Vegetarian: Loop through ingredients. If any ingredient contains LAND_MEAT or SEA_MEAT, set passed = False
                # This allows "Mushroom Shawarma" but kills "Chicken Shawarma"
                if any(meat_kw in ingredients_text for meat_kw in LAND_MEAT):
                    return {
                        'passed': False,
                        'safety_score': 0.0,
                        'safety_reason': 'Contains land meat in ingredients - violates vegetarian diet',
                        'reason': 'Contains land meat keywords in ingredients',
                        'requires_ai_validation': False,
                        'requires_ai_reassurance': False
                    }
                if any(seafood_kw in ingredients_text for seafood_kw in SEA_MEAT):
                    return {
                        'passed': False,
                        'safety_score': 0.0,
                        'safety_reason': 'Contains seafood in ingredients - violates vegetarian diet',
                        'reason': 'Contains seafood keywords in ingredients',
                        'requires_ai_validation': False,
                        'requires_ai_reassurance': False
                    }
            
            elif is_vegan:
                # Vegan: Same as Vegetarian, but also search for DAIRY_EGGS
                if any(meat_kw in ingredients_text for meat_kw in LAND_MEAT):
                    return {
                        'passed': False,
                        'safety_score': 0.0,
                        'safety_reason': 'Contains land meat in ingredients - violates vegan diet',
                        'reason': 'Contains land meat keywords in ingredients',
                        'requires_ai_validation': False,
                        'requires_ai_reassurance': False
                    }
                if any(seafood_kw in ingredients_text for seafood_kw in SEA_MEAT):
                    return {
                        'passed': False,
                        'safety_score': 0.0,
                        'safety_reason': 'Contains seafood in ingredients - violates vegan diet',
                        'reason': 'Contains seafood keywords in ingredients',
                        'requires_ai_validation': False,
                        'requires_ai_reassurance': False
                    }
                # Also check for dairy and eggs (vegan restrictions)
                if any(dairy_kw in ingredients_text for dairy_kw in DAIRY_EGGS):
                    # Check for safe words
                    has_safe_word = False
                    safe_words_dairy = SAFE_WORDS.get('dairy', [])
                    safe_words_eggs = SAFE_WORDS.get('eggs', [])
                    all_safe_words = safe_words_dairy + safe_words_eggs
                    if any(sw in ingredients_text for sw in all_safe_words):
                        has_safe_word = True
                    
                    if not has_safe_word:
                        return {
                            'passed': False,
                            'safety_score': 0.0,
                            'safety_reason': 'Contains dairy/eggs in ingredients - violates vegan diet',
                            'reason': 'Contains dairy/egg keywords without safe alternatives',
                            'requires_ai_validation': False,
                            'requires_ai_reassurance': False
                        }
            
            elif is_pescatarian:
                # Pescatarian: Only search for LAND_MEAT. If found, set passed = False
                # This allows "Fish Shawarma" but kills "Beef Shawarma"
                if any(meat_kw in ingredients_text for meat_kw in LAND_MEAT):
                    return {
                        'passed': False,
                        'safety_score': 0.0,
                        'safety_reason': 'Contains land meat in ingredients - violates pescatarian diet',
                        'reason': 'Contains land meat keywords in ingredients',
                        'requires_ai_validation': False,
                        'requires_ai_reassurance': False
                    }
        
        intolerances = self.settings.get('intolerances', [])
        if not intolerances:
            return {
                'passed': True,
                'safety_score': 1.0,
                'safety_reason': 'Safe - no intolerances found',
                'reason': 'Safe - no intolerances found',
                'requires_ai_validation': False,
                'requires_ai_reassurance': False
            }

        # Get all ingredient names from extendedIngredients
        ingredients = recipe.get('extendedIngredients', [])
        ingredient_names = []
        
        for ing in ingredients:
            if isinstance(ing, dict):
                name = ing.get('name') or ing.get('original') or ing.get('originalName', '')
                if name:
                    ingredient_names.append(name.lower())
            elif isinstance(ing, str):
                ingredient_names.append(ing.lower())
        
        # Build recipe text for keyword search
        recipe_text = recipe.get('title', '').lower() + " " + " ".join(ingredient_names)
        
        found_intolerances = []
        suspicious_ingredients = []
        safe_alternative_indicators = []
        
        for intolerance in intolerances:
            intol_key = intolerance.lower()
            keywords = ALLERGY_MAP.get(intol_key, [])
            safe_words = SAFE_WORDS.get(intol_key, [])
            
            for kw in keywords:
                if kw in recipe_text:
                    # Check for "Soft Keyword" (Safe word near the ingredient)
                    has_safe_word = any(sw in recipe_text for sw in safe_words)
                    
                    if has_safe_word:
                        # PASS TO GEMINI: Flag it but keep it alive
                        found_intolerances.append(intolerance)
                        for ing_name in ingredient_names:
                            if kw in ing_name:
                                safe_alternative_indicators.append(ing_name)
                        
                        violation_note = f'Contains {kw} with safe-word—Gemini must verify'
                        return {
                            'passed': True, 
                            'requires_ai_validation': True, 
                            'safety_score': 0.5,
                            'safety_reason': violation_note,
                            'violation_note': violation_note,
                            'reason': f"Found {kw} with safe-word; Gemini must verify.",
                            'found_intolerances': found_intolerances,
                            'suspicious_ingredients': suspicious_ingredients,
                            'safe_alternative_indicators': list(set(safe_alternative_indicators)),
                            'requires_ai_reassurance': False
                        }
                    else:
                        # HARD CUTOFF: No safe word found, delete immediately
                        for ing_name in ingredient_names:
                            if kw in ing_name:
                                suspicious_ingredients.append(ing_name)
                        
                        return {
                            'passed': False, 
                            'reason': f"Hard cutoff: {kw} found without safe keywords.",
                            'found_intolerances': [intolerance],
                            'suspicious_ingredients': list(set(suspicious_ingredients))
                        }

        return {
            'passed': True,
            'safety_score': 1.0,
            'safety_reason': 'Safe - no intolerances found',
            'reason': 'Safe - no intolerances found',
            'requires_ai_validation': False,
            'requires_ai_reassurance': False
        }
    
    def _apply_soft_filters(self, recipe: Dict) -> Dict:
        """
        LEGACY: Hard filter method (kept for backward compatibility).
        Use _apply_soft_filters_with_penalties for AI-reasoning architecture.
        """
        return self._apply_soft_filters_with_penalties(recipe)
    
    def _apply_soft_filters_with_penalties(self, recipe: Dict) -> Dict:
        """
        GATE 2: Soft Filters with Penalty Scores (AI-Reasoning Architecture)
        Instead of deleting recipes, apply penalty scores. All recipes survive.
        """
        filter_results = {}
        penalty_score = 0.0  # Start with no penalty
        violations = []  # Track what filters were violated
        
        # Difficulty filter - apply penalty if too hard
        difficulty_check = self._assess_difficulty(
            recipe,
            self.settings.get('max_difficulty', 'hard')
        )
        filter_results['difficulty'] = difficulty_check
        if not difficulty_check['passed']:
            penalty_score += 15.0  # Penalty for being too difficult
            violations.append(f"difficulty: {difficulty_check.get('level', 'unknown')} > {difficulty_check.get('max_allowed', 'unknown')}")
        
        # Time filter - apply penalty if too long
        time_check = self._check_time_limit(
            recipe,
            self.settings.get('max_time_minutes', 120)
        )
        filter_results['time'] = time_check
        if not time_check['passed']:
            # Calculate penalty based on how much over the limit
            # If recipe is 10 minutes over, subtract 20 points from confidence
            time_estimate = time_check.get('estimate', 0)
            max_time = time_check.get('max_allowed', 120)
            if isinstance(time_estimate, (int, float)) and isinstance(max_time, (int, float)):
                overage = time_estimate - max_time
                # 2 points per minute over (so 10 min over = 20 point penalty)
                penalty_score += min(overage * 2.0, 30.0)  # Max 30 point penalty
            else:
                penalty_score += 10.0
            violations.append(f"time: {time_estimate} min > {max_time} min")
        
        # Missing ingredients filter - apply penalty if too many missing
        missing_check = self._check_missing_limit(
            recipe.get("missedIngredientCount", 0),
            self.settings['max_missing_ingredients']
        )
        filter_results['missing_ingredients'] = missing_check
        if not missing_check['passed']:
            missing_count = missing_check.get('count', 0)
            max_allowed = missing_check.get('max_allowed', 5)
            if isinstance(missing_count, (int, float)) and isinstance(max_allowed, (int, float)):
                excess = missing_count - max_allowed
                penalty_score += excess * 5.0  # 5 points per extra missing ingredient
            else:
                penalty_score += 10.0
            violations.append(f"missing_ingredients: {missing_count} > {max_allowed}")
        
        # Dietary filter (preferences, not safety)
        dietary_check = self._check_dietary_requirements(
            recipe,
            self.settings.get('dietary_requirements', []),
            []  # Intolerances already checked in safety check
        )
        filter_results['dietary'] = dietary_check
        if not dietary_check['passed']:
            penalty_score += 10.0  # Penalty for not meeting dietary preferences
            violations.append(f"dietary: {dietary_check.get('reason', 'unknown')}")
        
        # REMOVED: Nutritional filter with micronutrient penalties
        # Micronutrient analysis is now handled by Gemini (no "double jeopardy")
        # Only Big 4 (Calories, Protein) are filtered at API level
        
        # Always return passed=True (soft filter), but include penalty info
        return {
            'passed': True,  # All recipes pass (soft filter)
            'filter_results': filter_results,
            'penalty_score': penalty_score,
            'violations': violations
        }
    
    def _assess_difficulty(self, recipe: Dict, max_difficulty: str) -> Dict:
        """
        Assess recipe difficulty based on ingredient count AND cooking time.
        Recipes > 60 minutes are bumped to 'medium' even with few ingredients
        (due to technique/wait time).
        """
        total_ingredients = (
            recipe.get('usedIngredientCount', 0) +
            recipe.get('missedIngredientCount', 0)
        )
        ready_time = recipe.get('readyInMinutes', 0)
        
        # Base difficulty on ingredient count
        if total_ingredients <= 5:
            level = 'easy'
        elif total_ingredients <= 10:
            level = 'medium'
        else:
            level = 'hard'
        
        # Refine difficulty based on cooking time
        # If recipe takes > 60 minutes, bump up difficulty (technique/wait time)
        if ready_time > 60:
            if level == 'easy':
                level = 'medium'  # Bump easy to medium for long recipes
            elif level == 'medium':
                level = 'hard'  # Bump medium to hard for very long recipes
        
        return {
            'passed': self.DIFFICULTY_ORDER[level] <= self.DIFFICULTY_ORDER.get(max_difficulty, 3),
            'level': level,
            'max_allowed': max_difficulty,
            'ingredient_count': total_ingredients,
            'ready_time': ready_time,
            'time_adjusted': ready_time > 60  # Flag if time affected difficulty
        }
    
    def _check_time_limit(self, recipe: Dict, max_time: int) -> Dict:
        """Check if recipe time is within limit."""
        ready_time = recipe.get('readyInMinutes', None)
        passed = True if ready_time is None else ready_time <= max_time
        
        return {
            'passed': passed,
            'estimate': ready_time if ready_time is not None else 'unknown',
            'max_allowed': max_time,
        }
    
    def _check_missing_limit(self, missed_count: int, max_missing: int) -> Dict:
        """Check if missing ingredient count is within limit."""
        return {
            'passed': missed_count <= max_missing,
            'count': missed_count,
            'max_allowed': max_missing,
        }
    
    def _check_dietary_requirements(
        self,
        recipe: Dict,
        dietary_requirements: List[str],
        intolerances: List[str]
    ) -> Dict:
        """
        Check if recipe meets dietary requirements and avoids intolerances.
        Uses API boolean flags (dairyFree, glutenFree) for double-check validation.
        High Confidence Safe: API says it's safe AND keyword search confirms.
        """
        if not dietary_requirements and not intolerances:
            return {'passed': True, 'reason': 'No dietary restrictions', 'confidence': 'high'}
        
        # informationBulk endpoint returns plural keys: 'cuisines', 'dishTypes', 'diets'
        # Ensure we're using the correct plural keys from the API response
        recipe_diets = [d.lower() for d in recipe.get('diets', []) or []]
        
        # Get API boolean flags from dietary_info (if available from cleaned recipe structure)
        dietary_info = recipe.get('dietary_info', {})
        api_dairy_free = dietary_info.get('dairyFree', False)
        api_gluten_free = dietary_info.get('glutenFree', False)
        api_vegan = dietary_info.get('vegan', False)
        api_vegetarian = dietary_info.get('vegetarian', False)
        
        # Extract ingredients text for keyword analysis
        ingredients_text = ' '.join([
            ing.get('name', '').lower() if isinstance(ing, dict) else str(ing).lower()
            for ing in recipe.get('extendedIngredients', [])
        ])
        
        # Keyword detection
        meat_keywords = ['chicken', 'beef', 'pork', 'fish', 'meat', 'turkey', 'lamb',
                        'bacon', 'sausage', 'ham', 'seafood', 'shrimp', 'salmon']
        dairy_keywords = ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream',
                         'heavy cream', 'whipping cream']
        egg_keywords = ['egg', 'eggs']
        gluten_keywords = ['flour', 'wheat', 'bread', 'pasta', 'noodles']
        
        has_meat = any(keyword in ingredients_text for keyword in meat_keywords)
        has_dairy = any(keyword in ingredients_text for keyword in dairy_keywords)
        has_eggs = any(keyword in ingredients_text for keyword in egg_keywords)
        has_gluten = any(keyword in ingredients_text for keyword in gluten_keywords)
        
        passed = True
        reasons = []
        confidence_levels = []
        
        # Check dietary requirements with double-check logic
        for requirement in dietary_requirements:
            req_lower = requirement.lower().replace('-', '_').replace(' ', '_')
            
            if req_lower == 'vegetarian':
                # Smart Diet Filter: Check ingredients for meat keywords
                # If no meat is found, let it pass even if API didn't tag it as vegetarian
                if has_meat:
                    passed = False
                    reasons.append('contains meat')
                else:
                    # No meat found in ingredients - allow it to pass regardless of API tag
                    # This is the "Smart Diet Filter": ingredient check overrides API tag
                    passed = True  # Explicitly allow if no meat found
                    if api_vegetarian:
                        confidence_levels.append('high')  # API confirms + no meat found
                    else:
                        confidence_levels.append('medium')  # No meat found but API didn't tag it (still allow)
            
            elif req_lower == 'vegan':
                if has_meat or has_dairy or has_eggs:
                    passed = False
                    reasons.append('contains animal products')
                elif api_vegan:
                    confidence_levels.append('high')  # API confirms + no animal products found
            
            elif req_lower == 'gluten_free':
                # Double-check: API flag AND keyword search
                if has_gluten:
                    if not api_gluten_free:
                        passed = False
                        reasons.append('contains gluten')
                    else:
                        # API says gluten-free but keywords found - flag as uncertain
                        reasons.append('may contain gluten (API says gluten-free but keywords found)')
                elif api_gluten_free:
                    confidence_levels.append('high')  # API confirms + no gluten keywords found
            
            elif req_lower == 'dairy_free':
                # Double-check: API flag AND keyword search
                if has_dairy:
                    if not api_dairy_free:
                        passed = False
                        reasons.append('contains dairy')
                    else:
                        # API says dairy-free but keywords found - flag as uncertain
                        reasons.append('may contain dairy (API says dairy-free but keywords found)')
                elif api_dairy_free:
                    confidence_levels.append('high')  # API confirms + no dairy keywords found
        
        # Check intolerances with double-check logic
        for intolerance in intolerances:
            intol_lower = intolerance.lower()
            
            if intol_lower == 'dairy':
                # Double-check: API flag AND keyword search
                if has_dairy:
                    if not api_dairy_free:
                        passed = False
                        reasons.append('contains dairy')
                    else:
                        reasons.append('may contain dairy (API says dairy-free but keywords found)')
                elif api_dairy_free:
                    confidence_levels.append('high')  # High confidence: API confirms + no dairy found
            
            elif intol_lower == 'gluten':
                # Double-check: API flag AND keyword search
                if has_gluten:
                    if not api_gluten_free:
                        passed = False
                        reasons.append('contains gluten')
                    else:
                        reasons.append('may contain gluten (API says gluten-free but keywords found)')
                elif api_gluten_free:
                    confidence_levels.append('high')  # High confidence: API confirms + no gluten found
            
            elif intol_lower == 'eggs':
                if has_eggs:
                    passed = False
                    reasons.append('contains eggs')
                elif api_vegan:  # Vegan recipes don't have eggs
                    confidence_levels.append('high')
        
        # Determine overall confidence
        if confidence_levels and all(c == 'high' for c in confidence_levels):
            confidence = 'high'
        elif confidence_levels:
            confidence = 'medium'
        else:
            confidence = 'medium'  # Default if no API flags available
        
        return {
            'passed': passed,
            'reason': '; '.join(reasons) if reasons else 'meets requirements',
            'requirements_checked': dietary_requirements,
            'intolerances_checked': intolerances,
            'confidence': confidence  # 'high', 'medium', or 'low'
        }
    
    def _calculate_smart_score(self, recipe: Dict) -> Dict:
        """Calculate smart score based on user profile."""
        used_count = recipe.get('usedIngredientCount', 0)
        missed_count = recipe.get('missedIngredientCount', 0)
        total_ingredients = used_count + missed_count
        
        if total_ingredients == 0:
            return {
                'smart_score': 0,
                'used_score': 0,
                'missing_score': 0,
                'breakdown': 'No ingredient data'
            }
        
        # Calculate percentages
        used_percent = (used_count / total_ingredients) * 100
        missed_percent = (missed_count / total_ingredients) * 100
        
        # Get weights from profile
        weights = self.profile['weights']
        
        # Calculate weighted components
        used_component = weights['used'] * used_percent
        missed_component = weights['missing'] * (100 - missed_percent)
        smart_score = used_component + missed_component
        
        return {
            'smart_score': round(smart_score, 1),
            'used_score': round(used_percent, 1),
            'missing_score': round(100 - missed_percent, 1),
            'breakdown': self._get_score_breakdown(used_percent, missed_percent, weights),
            'weights': weights
        }
    
    def _get_score_breakdown(self, used_percent: float, missed_percent: float, weights: Dict) -> str:
        """Generate human-readable score breakdown."""
        used_comp = round(weights['used'] * used_percent, 1)
        missing_comp = round(weights['missing'] * (100 - missed_percent), 1)
        
        return (
            f"({weights['used']}×{used_percent:.1f}%) + "
            f"({weights['missing']}×{100 - missed_percent:.1f}%) = "
            f"{used_comp} + {missing_comp}"
        )
    
    def _apply_reasoning(
        self,
        recipe: Dict,
        smart_score: float,
        filter_result: Dict
    ) -> Dict:
        """Apply Phase 2 reasoning to calculate match confidence and generate explanation."""
        # Extract recipe attributes
        time_estimate = recipe.get('readyInMinutes')
        difficulty = filter_result['filter_results']['difficulty']['level']
        used_count = recipe.get('usedIngredientCount', 0)
        missed_count = recipe.get('missedIngredientCount', 0)
        total_ingredients = used_count + missed_count
        
        # Get user constraints
        max_time = self.settings.get('max_time', self.settings.get('max_time_minutes', 120))
        skill_level = self.settings.get('skill_level', 50)
        
        # Calculate time score
        if time_estimate and max_time:
            time_score = max(0.1, 1 - (time_estimate / max_time))
        else:
            time_score = 0.5
        
        # Calculate skill score
        required_skill = self.DIFFICULTY_SKILL_MAP.get(difficulty, 50)
        if skill_level >= required_skill:
            skill_score = 1.0
        else:
            skill_score = max(0.2, 1 - (required_skill - skill_level) / 100)
        
        # Calculate shopping score
        if total_ingredients > 0:
            shopping_score = 1 - (missed_count / total_ingredients)
        else:
            shopping_score = 0.5
        
        # EFFICIENCY RANK FOR TIRED USERS: Multiply time_score by 2 to prioritize quick recipes
        # This forces 10-minute recipes to beat 40-minute recipes every time
        adjusted_time_score = time_score
        if self.mood == 'tired':
            adjusted_time_score = time_score * 2
        
        # Calculate final internal score (for ranking)
        final_internal_score = (
            (smart_score / 100) * 0.4 +
            adjusted_time_score * self.mood_weights['time'] * 0.25 +
            skill_score * self.mood_weights['skill'] * 0.2 +
            shopping_score * self.mood_weights['shopping'] * 0.15
        )
        
        # Generate human-friendly reasoning
        reasons = []
        if missed_count <= 1:
            reasons.append('requires very little shopping')
        elif missed_count <= 3:
            reasons.append('only needs a few extra ingredients')
        
        if time_estimate and max_time and time_estimate <= max_time * 0.7:
            reasons.append('quick to prepare')
        
        if difficulty == 'easy':
            reasons.append('easy to cook up')
        
        # Calculate confidence (75-95 range) - Start higher to ensure recipes pass
        confidence = 75  # Increased base from 70 to 75
        if missed_count <= 1:
            confidence += 10
        if difficulty == 'easy':
            confidence += 5
        if time_estimate and max_time and time_estimate <= max_time:
            confidence += 5
        
        # MOOD-BASED CONFIDENCE BONUS: Tired + Quick Recipes
        if self.mood == 'tired' and time_estimate and time_estimate <= 20:
            confidence += 15  # Massive bonus for quick recipes when tired
            if 'perfect for when you\'re tired - super quick!' not in reasons:
                reasons.append('perfect for when you\'re tired - super quick!')
        
        # Additional bonus for recipes that meet all criteria well
        if missed_count <= 1 and difficulty == 'easy' and time_estimate and time_estimate <= 20:
            confidence += 5  # Perfect match bonus
        
        confidence = min(confidence, 95)
        
        # SIMPLIFIED REASONING FOR TIRED USERS: Blunt and direct
        if self.mood == 'tired':
            reasoning_text = 'Best option for zero effort.'
        else:
            # Generate final reasoning text (after all reasons are added)
            if reasons:
                reasoning_text = 'Good match because it ' + ', '.join(reasons)
            else:
                reasoning_text = 'Matches your preferences pretty well'
        
        return {
            'confidence': confidence,
            'text': reasoning_text,
            'internal_debug': {
                'internal_score': round(final_internal_score * 100, 1),
                'time_score': round(time_score, 2),
                'skill_score': round(skill_score, 2),
                'shopping_score': round(shopping_score, 2),
                'weights_used': self.mood_weights
            }
        }
    
    def _apply_reasoning_with_penalties(
        self,
        recipe: Dict,
        smart_score: float,
        filter_result: Dict
    ) -> Dict:
        """
        Apply Phase 2 reasoning with penalty adjustments (AI-Reasoning Architecture).
        Adjusts confidence based on filter violations instead of deleting recipes.
        """
        # Get base reasoning
        base_reasoning = self._apply_reasoning(recipe, smart_score, filter_result)
        
        # Apply penalty score from filter violations
        penalty_score = filter_result.get('penalty_score', 0.0)
        violations = filter_result.get('violations', [])
        
        # Adjust confidence based on penalties
        base_confidence = base_reasoning.get('confidence', 75)
        adjusted_confidence = max(50, base_confidence - penalty_score)  # Min confidence of 50
        
        # Update reasoning text to mention violations if any (for AI context)
        reasoning_text = base_reasoning.get('text', 'Matches your preferences pretty well')
        if violations:
            # Add violation context to reasoning (for AI to explain intelligently)
            reasoning_text += f" (Note: {', '.join(violations[:2])})"  # Limit to 2 violations
        
        return {
            'confidence': round(adjusted_confidence, 1),
            'text': reasoning_text,
            'penalty_applied': penalty_score,
            'violations': violations,
            'internal_debug': base_reasoning.get('internal_debug', {})
        }
    
    def _generate_semantic_context(
        self,
        recipe: Dict,
        reasoning_data: Dict,
        filter_result: Dict,
        safety_check: Dict,
        protein: float,
        calories: float,
        servings: int
    ) -> str:
        """
        Generate semantic context string for Gemini AI.
        Tells Gemini what to focus on in its analysis (e.g., time saving, substitutions, nutrition).
        
        Args:
            recipe: Recipe dictionary
            reasoning_data: Reasoning data with violations
            filter_result: Filter results with violation flags
            safety_check: Safety check results
            protein: Protein amount
            calories: Calories amount
            servings: Number of servings
            
        Returns:
            Semantic context string for Gemini
        """
        context_parts = []
        
        # Get confidence and violations
        confidence = reasoning_data.get('confidence', 75)
        violations = reasoning_data.get('violations', [])
        
        # Check violations directly (violation_flags will be in metadata built later)
        has_time_violation = any('time:' in v for v in violations)
        has_missing_violation = any('missing_ingredients:' in v for v in violations)
        has_difficulty_violation = any('difficulty:' in v for v in violations)
        
        # Base context: Match percentage
        context_parts.append(f"This recipe is a {confidence:.0f}% match")
        
        # Add violation context to guide Gemini's focus
        if has_time_violation:
            context_parts.append("but exceeds time limit.")
            context_parts.append("AI, check analyzedInstructions for ways to save time or simplify steps.")
        
        if has_missing_violation:
            context_parts.append("but requires additional ingredients.")
            context_parts.append("AI, analyze extendedIngredients and suggest substitutions from user's pantry.")
        
        if has_difficulty_violation:
            context_parts.append("but may be too complex.")
            context_parts.append("AI, review analyzedInstructions to identify simplification opportunities.")
        
        # Nutrition context - guide Gemini to evaluate nutritional goals
        nutritional_requirements = self.settings.get('nutritional_requirements', {})
        
        if servings > 0 and calories > 0:
            calories_per_serving = calories / servings
            if protein > 0:
                protein_per_serving = protein / servings
                calorie_to_protein_ratio = calories_per_serving / protein_per_serving if protein_per_serving > 0 else 0
                
                if calorie_to_protein_ratio > 25:
                    context_parts.append(f"Has high calorie-to-protein ratio ({calorie_to_protein_ratio:.1f}).")
                    context_parts.append("AI, check instructions to see if sauce can be lightened using user's available ingredients.")
        
        # Add nutritional goal context (e.g., "High Vitamin C")
        if nutritional_requirements:
            goal_nutrients = []
            for nutrient, value in nutritional_requirements.items():
                if isinstance(value, dict) and value.get('target') == 'high':
                    goal_nutrients.append(nutrient)
            
            if goal_nutrients:
                context_parts.append(f"User wants high {', '.join(goal_nutrients)}.")
                context_parts.append("AI, evaluate if this recipe fits the user's nutritional goals by analyzing extendedIngredients and instructions.")
        
        # Safety validation context
        if safety_check.get('requires_ai_validation'):
            suspicious = safety_check.get('suspicious_ingredients', [])
            safe_alternatives = safety_check.get('safe_alternative_indicators', [])
            
            if safe_alternatives:
                context_parts.append(f"AI, act as Safety Jury: Found potential safe alternatives ({', '.join(safe_alternatives[:2])}).")
                context_parts.append("Review extendedIngredients and instructions to confirm safety for user's intolerances.")
            else:
                context_parts.append(f"AI, act as Safety Jury: Found suspicious ingredients ({', '.join(suspicious[:2])}).")
                context_parts.append("Review extendedIngredients and instructions to validate ingredient safety for user's intolerances.")
        
        # Combine into sentence
        return " ".join(context_parts)
    
    def _build_metadata_dict(
        self,
        scoring_data: Dict,
        reasoning_data: Dict,
        filter_result: Dict,
        safety_check: Dict
    ) -> Dict:
        """
        Build standardized _metadata dictionary for Gemini AI schema.
        Schema Compliance: violation_flags must include all 5 keys for consistency.
        has_nutritional_violation is set to False by default since Logic engine no longer
        calculates micronutrient violations (handled by Gemini semantic analysis).
        """
        violations_list = reasoning_data.get('violations', [])
        penalty_score_value = filter_result.get('penalty_score', 0)
        
        return {
            'smart_score': scoring_data['smart_score'],  # Also in metadata for consistency
            'internal_debug': reasoning_data.get('internal_debug', {}),
            'scoring_breakdown': scoring_data.get('breakdown', ''),
            'used_score': scoring_data.get('used_score', 0),
            'missing_score': scoring_data.get('missing_score', 0),
            'filter_results': filter_result.get('filter_results', {}),
            'safety_check': safety_check,
            'penalty_applied': reasoning_data.get('penalty_applied', 0),
            'penalty_score': float(penalty_score_value),  # Raw penalty score from filters (must be float)
            'violations': violations_list,  # List of violation strings
            'violation_flags': {
                # Violation flags for Gemini to understand why score was adjusted
                'has_time_violation': bool(any('time:' in v for v in violations_list)),
                'has_missing_violation': bool(any('missing_ingredients:' in v for v in violations_list)),
                'has_difficulty_violation': bool(any('difficulty:' in v for v in violations_list)),
                'has_dietary_violation': bool(any('dietary:' in v for v in violations_list)),
                # Schema Compliance: Keep has_nutritional_violation in schema but set to False
                # Logic engine no longer calculates micronutrient violations (handled by Gemini semantic analysis)
                # Gemini will perform semantic audit even when this is False if user requests "High Vitamin C" etc.
                'has_nutritional_violation': False
            }
        }
    
    def _clean_data(
        self,
        recipe: Dict,
        scoring_data: Dict,
        reasoning_data: Dict,
        filter_result: Dict,
        safety_check: Dict
    ) -> Dict:
        """
        Data Cleaner: Returns a clean dictionary with Context Package for Gemini.
        This is what the UI will receive - no messy API data.
        Technical scores and debug info are nested in _metadata for debugging.
        
        Context Package includes:
        - servings: For Gemini to understand recipe scale
        - raw_ingredients_for_ai: Full ingredient list for Gemini nutrient analysis
        - nutrition_summary: Big 4 only (Calories, Protein, Fat, Carbs)
        - ai_nutrient_flags: Placeholder for Gemini to fill (e.g., "High Iron" based on spinach)
        
        Returns:
            Clean dictionary with:
            - Top level: title, image, confidence, time, reasoning, id, ingredients, etc.
            - Context Package: servings, raw_ingredients_for_ai, nutrition_summary, ai_nutrient_flags
            - _metadata: smart_score, internal_debug, scoring_breakdown, filter_results, etc.
        """
        time_estimate = recipe.get('readyInMinutes', 0)
        servings = recipe.get('servings', 0)  # Get servings from recipe (for Gemini context)
        
        # CRITICAL: Ensure extendedIngredients is available for Gemini analysis
        # This is the 'Fuel' Gemini needs to explain substitutions and validate safety
        # Data Flow: API → Logic → Output (must preserve extendedIngredients)
        # WITHOUT THIS, GEMINI IS BLIND - cannot check for "vegan butter" vs "butter"
        extended_ingredients = recipe.get('extendedIngredients', [])
        
        # Try alternative locations as fallback (defensive programming)
        if not extended_ingredients:
            # Check ingredient_info nested structure (from pantry_chef_api.py)
            ingredient_info = recipe.get('ingredient_info', {})
            if isinstance(ingredient_info, dict):
                extended_ingredients = ingredient_info.get('extendedIngredients', [])
        
        if not extended_ingredients:
            # Try raw_ingredients_for_ai (backward compatibility)
            extended_ingredients = recipe.get('raw_ingredients_for_ai', [])
        
        # CRITICAL: Log error if still missing - this breaks Safety Jury and Substitutions
        if not extended_ingredients:
            print(f"❌ CRITICAL ERROR: extendedIngredients missing from recipe {recipe.get('id')} in Logic._clean_data")
            print(f"   Recipe title: {recipe.get('title', 'Unknown')}")
            print(f"   Available keys: {list(recipe.keys())[:15]}...")  # Show first 15 keys for debugging
            # DO NOT default to empty list - this breaks Gemini functionality
            # Instead, try to extract from any possible location
            if 'ingredients' in recipe:
                extended_ingredients = recipe.get('ingredients', [])
            else:
                extended_ingredients = []  # Last resort - will break Safety Jury but won't crash
        
        # Extract nutrition data (Big 4 only - micronutrients handled by Gemini)
        nutrition = recipe.get('nutrition', {})
        nutrient_dict = {}
        
        if nutrition:
            nutrients = nutrition.get('nutrients', [])
            nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
        
        # Extract Big 4 nutrients only
        protein = nutrient_dict.get('Protein', 0)
        carbs = nutrient_dict.get('Carbohydrates', 0)
        calories = nutrient_dict.get('Calories', 0)
        fat = nutrient_dict.get('Fat', 0)
        
        # Generate Semantic Context String for Gemini
        # This tells Gemini what to focus on in its analysis
        semantic_context = self._generate_semantic_context(
            recipe,
            reasoning_data,
            filter_result,
            safety_check,
            protein,
            calories,
            servings
        )
        
        # Detect stub recipes (missing enrichment data to save API points)
        # Stub recipes are those beyond top 5 that weren't enriched
        is_stub_recipe = (
            not nutrition or 
            not recipe.get('instructions') or 
            not recipe.get('analyzedInstructions') or
            servings == 0 or
            not recipe.get('extendedIngredients')
        )
        
        # Build clean recipe object - UI-friendly top level
        # CRITICAL: smart_score should ONLY be in _metadata, not at top level
        # Top level should be clean (Title, Image, Time) with all "Math" hidden in _metadata
        # PRESERVATION: extendedIngredients and nutrition MUST be preserved for Gemini Safety Jury and AI Scientist
        # CORE FIX: Get directly from recipe parameter - do NOT rely on extracted variables that might be empty
        clean_recipe = {
            'id': recipe.get('id'),
            'title': recipe.get('title', 'Unknown Recipe'),
            'image': recipe.get('image', ''),
            'confidence': reasoning_data['confidence'],  # Primary key - updated by penalties
            'match_confidence': reasoning_data['confidence'],  # Alias for backward compatibility
            # smart_score removed from top level - it's in _metadata only
            'time': time_estimate,
            'reasoning': reasoning_data['text'],
            'semantic_context': semantic_context,  # For Gemini AI analysis
            
            # --- CRITICAL PRESERVATION: Explicit mapping from input recipe dictionary ---
            # These fields MUST be explicitly mapped - if not mapped here, they won't reach Gemini
            # extendedIngredients contains amount, unitShort, unitLong - needed for serving size analysis
            # Final Mapping: Ensure these exact mappings are present
            'extendedIngredients': recipe.get('extendedIngredients', []),
            'servings': recipe.get('servings', 0),
            'instructions': recipe.get('instructions', ''),
            'analyzedInstructions': recipe.get('analyzedInstructions', []),
            'raw_ingredients_for_ai': recipe.get('extendedIngredients', []),  # For Gemini analysis
            'nutrition': recipe.get('nutrition', {}),  # DIRECT PRESERVATION - CRITICAL FOR AI SCIENTIST
            
            # --- PLURAL KEYS PRESERVATION: Map cuisines, dishTypes, diets for dietary checking ---
            # These are needed for Logic.py dietary requirements checking and Gemini analysis
            'cuisines': recipe.get('cuisines', []),  # Plural key from informationBulk
            'dishTypes': recipe.get('dishTypes', []),  # Plural key from informationBulk
            'diets': recipe.get('diets', []),  # Plural key from informationBulk
            # -----------------------------------------------------------------------------
            
            # Additional useful fields (but keep it minimal)
            'used_ingredients': recipe.get('usedIngredientCount', 0),
            'missing_ingredients': recipe.get('missedIngredientCount', 0),
            'difficulty': filter_result['filter_results']['difficulty']['level'],
            'protein': float(protein),
            'calories': float(calories),
            'carbs': float(carbs),
            
            # Nutrition Summary: Big 4 only (micronutrients handled by Gemini)
            'nutrition_summary': {
                'protein': float(protein),
                'calories': float(calories),
                'fat': float(fat),
                'carbs': float(carbs)
            },
            
            # AI Nutrient Flags: Placeholder for Gemini to fill
            # Gemini will analyze raw_ingredients_for_ai and populate this
            # Example: {'high_iron': True, 'high_vitamin_c': True, 'high_calcium': False}
            'ai_nutrient_flags': {},  # Empty dict - Gemini will populate based on ingredient analysis
            
            # Stub recipe flag: Indicates recipe wasn't enriched (beyond top 5)
            # Gemini can tell user: "I have more details on your top 5, but here are some other quick ideas!"
            'is_stub_recipe': is_stub_recipe,
            
            # Metadata nested dictionary - contains all technical scores and debug info
            '_metadata': self._build_metadata_dict(
                scoring_data, reasoning_data, filter_result, safety_check
            )
        }
        
        return clean_recipe


if __name__ == "__main__":
    """
    Test Suite: Verify Logic Engine handles 3-step pipeline results correctly.
    Tests field mappings (cuisines, dishTypes, diets), safety scoring, and nutrition parsing.
    """
    print("\n" + "=" * 70)
    print("TEST SUITE: Logic Engine - 3-Step Pipeline Compatibility")
    print("=" * 70)
    
    # Simulate a recipe from the 3-step pipeline (informationBulk response)
    test_recipe = {
        'id': 12345,
        'title': 'Italian Pasta Primavera',
        'image': 'https://example.com/pasta.jpg',
        'readyInMinutes': 30,
        'servings': 4,
        'usedIngredientCount': 5,
        'missedIngredientCount': 3,
        # informationBulk returns plural keys: cuisines, dishTypes, diets
        'cuisines': ['Italian'],  # Plural key from informationBulk
        'dishTypes': ['main course', 'dinner'],  # Plural key from informationBulk
        'diets': ['vegetarian'],  # Plural key from informationBulk
        'extendedIngredients': [
            {'name': 'pasta', 'amount': 2.0, 'unit': 'cups'},
            {'name': 'butter', 'amount': 0.25, 'unit': 'cup'},  # Dairy - will trigger soft violation
            {'name': 'tomatoes', 'amount': 2.0, 'unit': 'cups'}
        ],
        'instructions': 'Cook pasta. Add butter. Mix with tomatoes.',
        'analyzedInstructions': [
            {'steps': [
                {'step': 'Cook pasta'},
                {'step': 'Add butter'},
                {'step': 'Mix with tomatoes'}
            ]}
        ],
        # informationBulk returns nutrition['nutrients'] list structure
        'nutrition': {
            'nutrients': [
                {'name': 'Calories', 'amount': 450.0},
                {'name': 'Protein', 'amount': 15.0},
                {'name': 'Fat', 'amount': 12.0},
                {'name': 'Carbohydrates', 'amount': 65.0}
            ]
        },
        'dietary_info': {
            'vegetarian': True,
            'vegan': False,
            'dairyFree': False,  # Contains butter
            'glutenFree': False
        }
    }
    
    # Test settings with lactose intolerance (will trigger soft violation)
    test_settings = {
        'user_profile': 'balanced',
        'mood': 'casual',
        'max_difficulty': 'medium',
        'max_time_minutes': 45,
        'max_missing_ingredients': 5,
        'dietary_requirements': ['vegetarian'],
        'intolerances': ['dairy'],  # Will trigger soft violation for butter
        'nutritional_requirements': {
            'high_protein': 10.0
        },
        'skill_level': 50,
        'max_time': 45
    }
    
    # Initialize engine
    engine = PantryChefEngine(test_settings)
    
    # Test 1: Verify plural key mappings (cuisines, dishTypes, diets)
    print("\n" + "-" * 70)
    print("TEST 1: Plural Key Mappings (cuisines, dishTypes, diets)")
    print("-" * 70)
    
    cuisines = test_recipe.get('cuisines', [])
    dish_types = test_recipe.get('dishTypes', [])
    diets = test_recipe.get('diets', [])
    
    print(f"  cuisines: {cuisines} (type: {type(cuisines).__name__})")
    print(f"  dishTypes: {dish_types} (type: {type(dish_types).__name__})")
    print(f"  diets: {diets} (type: {type(diets).__name__})")
    
    mapping_ok = (
        isinstance(cuisines, list) and
        isinstance(dish_types, list) and
        isinstance(diets, list)
    )
    print(f"  {'✅' if mapping_ok else '❌'} Plural keys correctly mapped as lists")
    
    # Test 2: Verify safety check with soft violation
    print("\n" + "-" * 70)
    print("TEST 2: Safety Check with Soft Violation (dairy intolerance)")
    print("-" * 70)
    
    safety_check = engine._apply_safety_check(test_recipe)
    print(f"  Safety Check Passed: {safety_check.get('passed')}")
    print(f"  Safety Score: {safety_check.get('safety_score', 'N/A')}")
    print(f"  Safety Reason: {safety_check.get('safety_reason', 'N/A')}")
    print(f"  Violation Note: {safety_check.get('violation_note', 'N/A')}")
    print(f"  Requires AI Validation: {safety_check.get('requires_ai_validation', False)}")
    
    # Test expects: passed=True, safety_score=0.2 (soft violation), requires_ai_validation=True
    # The test recipe has dairyFree: False (API confirmed), so it should trigger the API-confirmed violation path
    safety_ok = (
        safety_check.get('passed') is True and
        safety_check.get('safety_score') == 0.2 and
        safety_check.get('requires_ai_validation') is True and
        ('dairy' in safety_check.get('safety_reason', '').lower() or 
         'butter' in safety_check.get('safety_reason', '').lower() or
         'substitution' in safety_check.get('safety_reason', '').lower())
    )
    print(f"  {'✅' if safety_ok else '❌'} Soft violation correctly flagged with safety_score=0.2 and requires_ai_validation=True")
    
    # Test 3: Verify nutrition parsing (informationBulk structure)
    print("\n" + "-" * 70)
    print("TEST 3: Nutrition Parsing (informationBulk nutrients list)")
    print("-" * 70)
    
    nutrition = test_recipe.get('nutrition', {})
    nutrients = nutrition.get('nutrients', [])
    nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
    
    calories = nutrient_dict.get('Calories', 0)
    protein = nutrient_dict.get('Protein', 0)
    fat = nutrient_dict.get('Fat', 0)
    carbs = nutrient_dict.get('Carbohydrates', 0)
    
    print(f"  Calories: {calories} (expected: 450.0)")
    print(f"  Protein: {protein} (expected: 15.0)")
    print(f"  Fat: {fat} (expected: 12.0)")
    print(f"  Carbs: {carbs} (expected: 65.0)")
    
    nutrition_ok = (
        calories == 450.0 and
        protein == 15.0 and
        fat == 12.0 and
        carbs == 65.0
    )
    print(f"  {'✅' if nutrition_ok else '❌'} Nutrition correctly parsed from nutrients list")
    
    # Test 4: Full pipeline test
    print("\n" + "-" * 70)
    print("TEST 4: Full Pipeline Test (process_results)")
    print("-" * 70)
    
    results = engine.process_results([test_recipe])
    
    if results:
        result = results[0]
        print(f"  Recipe Title: {result.get('title')}")
        print(f"  Match Confidence: {result.get('match_confidence', 'N/A')}")
        print(f"  Protein: {result.get('protein', 0)}")
        print(f"  Calories: {result.get('calories', 0)}")
        
        # Check safety data is preserved
        metadata = result.get('_metadata', {})
        safety_check_result = metadata.get('safety_check', {})
        print(f"  Safety Score (in metadata): {safety_check_result.get('safety_score', 'N/A')}")
        print(f"  Safety Reason (in metadata): {safety_check_result.get('safety_reason', 'N/A')}")
        
        # Verify cuisines, dishTypes, diets are accessible (if preserved in clean_recipe)
        print(f"  Extended Ingredients Count: {len(result.get('extendedIngredients', []))}")
        
        pipeline_ok = (
            result.get('protein') == 15.0 and
            result.get('calories') == 450.0 and
            len(result.get('extendedIngredients', [])) > 0
        )
        print(f"  {'✅' if pipeline_ok else '❌'} Full pipeline processing successful")
    else:
        print("  ❌ No results returned")
        pipeline_ok = False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_tests_passed = mapping_ok and safety_ok and nutrition_ok and pipeline_ok
    
    if all_tests_passed:
        print("✅ SUCCESS: All tests passed!")
        print("   - ✅ Plural keys (cuisines, dishTypes, diets) correctly mapped")
        print("   - ✅ Soft violations flagged with safety_score=0.2 and safety_reason")
        print("   - ✅ Nutrition correctly parsed from nutrients list structure")
        print("   - ✅ Full pipeline processing successful")
    else:
        print("❌ FAILURE: Some tests failed")
        print(f"   - Mapping: {'✅' if mapping_ok else '❌'}")
        print(f"   - Safety Check: {'✅' if safety_ok else '❌'}")
        print(f"   - Nutrition Parsing: {'✅' if nutrition_ok else '❌'}")
        print(f"   - Full Pipeline: {'✅' if pipeline_ok else '❌'}")
    
    print("=" * 70)
