"""
PantryChef Engine - Consolidated Class
Combines Smart Scoring, Filtering, and Phase 2 Reasoning into one efficient class
"""

from typing import List, Dict, Any, Optional

from allergen_table import (
    TABLE_VERSION,
    ALLERGEN_CATEGORIES,
    DIET_EXCLUSIONS,
    resolve_text,
    categories_for,
    resolve_declaration,
    DISPLAY_BY_ID,
)

# Three-state safety verdict. There is no boolean "is it safe" anywhere in the
# safety path, because a boolean cannot express "we could not tell".
SAFE = 'SAFE'
UNKNOWN = 'UNKNOWN'
UNSAFE = 'UNSAFE'

# Ordering used to combine per-allergen verdicts and to assert monotonicity:
# adding a restriction can only ever move a verdict up this scale.
_VERDICT_ORDER = {SAFE: 0, UNKNOWN: 1, UNSAFE: 2}


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
        Main processing method: two gates, then scoring and reasoning.

        GATE 1 (safety): the only gate that removes a recipe. It returns one of
            three verdicts. UNSAFE is dropped. UNKNOWN is kept and carried to the
            UI clearly labelled, because hiding an unscreenable recipe and
            silently calling a screened one safe are both lies, and only one of
            them is visible to the user.
        GATE 2 (preferences): time, difficulty, missing ingredients and dietary
            preference become rank penalties. A penalty never hides a recipe and
            never sets a safety verdict.

        There is exactly one place in this file that decides exclusion, and it is
        _apply_safety_check. The old "HARD EXECUTIONER" pre-gate that lived here
        was a fourth competing keyword list that read image URLs and aisle labels
        as if they were ingredients; it has been folded into the single gate.

        Args:
            raw_recipes: List of recipe dictionaries from API

        Returns:
            List of CLEAN processed recipes, ranked best-first.
        """
        final_recommendations = []

        for recipe in raw_recipes:
            # GATE 1: the safety gate. UNSAFE is terminal and nothing downstream
            # -- no score, no penalty, no model -- can overturn it.
            safety_check = self._apply_safety_check(recipe)
            if safety_check.get('safety_state') == UNSAFE:
                continue

            # GATE 2: Soft Filters - Smart Scoring with Penalties (AI-Reasoning Architecture)
            # Includes SMART DIET CHECK: Checks extendedIngredients for meat keywords when 'vegetarian' is selected
            # NEVER exclude recipes based on time, difficulty, or missing ingredients
            # All recipes survive with adjusted confidence scores
            filter_result = self._apply_soft_filters_with_penalties(recipe)
            # No continue statement - all recipes pass through (except safety violations)
            
            # Calculate smart score
            scoring_data = self._calculate_smart_score(recipe)

            # NEW: Apply semantic bonus if recipe needs validation
            if recipe.get('needs_semantic_validation', False):
                # Lower initial score, will be upgraded by Gemini if semantic match
                scoring_data['smart_score'] *= 0.8  # 20% penalty until Gemini validates
                scoring_data['pending_semantic_validation'] = True

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
        
        # Rank by the score the engine actually computed.
        #
        # This used to sort on k.get('match_confidence', ...), which _clean_data
        # read straight off the raw upstream recipe. Nothing upstream ever sets
        # that key, so it was 1.0 for every recipe and the sort was a no-op over
        # a constant: every score in this file was calculated, formatted and then
        # discarded before ranking.
        #
        # rank_score is the mood-weighted blend from _apply_reasoning. It is an
        # ordinal, not a percentage -- the mood weights stop the terms summing to
        # 1.0 -- so it is used for ordering only and never displayed.
        return sorted(
            final_recommendations,
            key=lambda k: (
                k.get('_metadata', {}).get('internal_debug', {}).get('rank_score', 0.0),
                k.get('confidence', 0),
            ),
            reverse=True
        )
    
    def _collect_ingredient_texts(self, recipe: Dict) -> List[str]:
        """
        Pull the text the safety gate is allowed to read.

        Ingredient *names* and cooking instructions, and nothing else.

        Two deliberate exclusions:

        - Non-name ingredient fields. Spoonacular ingredient objects carry
          `aisle`, `consistency` and an `image` URL. The old pre-gate scanned
          every string value in the dict, so an image path ending `/ham.jpg` or
          an aisle labelled "Meat" rejected a tomato.
        - The recipe title. "Vegan-Style Mac and Cheese" and "Gluten-Free Bread"
          are marketing text, and the prototype treated the claim in the title as
          evidence about the contents. Titles are never evidence, in either
          direction. Ingredients decide.

        Instructions *are* read, because "grease the pan with butter" and "dust
        with flour" are how allergens get into a dish without appearing in the
        ingredient list.
        """
        texts: List[str] = []

        for ing in recipe.get('extendedIngredients') or []:
            if isinstance(ing, dict):
                name = (ing.get('nameClean') or ing.get('name')
                        or ing.get('originalName') or ing.get('original') or '')
                if name:
                    texts.append(str(name))
            elif isinstance(ing, str) and ing:
                texts.append(ing)

        return texts

    def _collect_method_texts(self, recipe: Dict) -> List[str]:
        """Instruction text, from either shape the API returns it in."""
        texts: List[str] = []

        instructions = recipe.get('instructions')
        if isinstance(instructions, str) and instructions.strip():
            texts.append(instructions)

        for block in recipe.get('analyzedInstructions') or []:
            if not isinstance(block, dict):
                continue
            for step in block.get('steps') or []:
                if isinstance(step, dict) and step.get('step'):
                    texts.append(str(step['step']))

        return texts

    def _apply_safety_check(self, recipe: Dict) -> Dict:
        """
        THE safety gate. The only thing in this file that excludes a recipe.

        Returns a three-state verdict -- SAFE, UNSAFE or UNKNOWN -- computed
        purely from (recipe, declared restrictions, allergen table version). It
        makes no network calls, consults no model, and reads no third-party
        "isGlutenFree" boolean. Given the same three inputs it returns the same
        answer every time.

        What changed from the prototype, and why:

        - **Free text no longer returns a claim of safety.** Declaring
          "shellfish" used to test whether the literal string "shellfish"
          appeared in the recipe; the word does not appear in a shellfish
          recipe, so Shrimp Scampi came back "Safe, score 1.0". Declarations now
          resolve through the same canonical table as ingredients, and a
          declaration the table cannot screen returns UNKNOWN naming itself.
        - **No SAFE_WORDS.** The idea that finding the token "vegan" anywhere in
          a recipe downgrades a real butter-and-cheddar match to "ask the model"
          is not fixable; it is deleted.
        - **No early return.** Every declared restriction is evaluated against
          every ingredient, and the verdict names all of them, not the first.
        - **No if/elif over diets.** Selecting vegetarian *and* vegan used to run
          only the vegetarian branch, which checks neither dairy nor eggs, so
          asking for more restriction produced less screening.
        - **Empty is not safe.** No ingredient data yields UNKNOWN. The pipeline
          deliberately leaves recipes past the top 5 un-enriched, and those stubs
          were being certified safe from no evidence at all.

        Returns a dict with:
            safety_state            SAFE | UNSAFE | UNKNOWN
            safety_reason           human-readable summary
            per_restriction         one structured entry per declared restriction
            matched_allergens       every match found, not just the first
            unresolved_ingredients  ingredient words the table does not know
            unscreenable_declarations  restrictions the table cannot check
            table_version           for reproducibility
            passed                  False only when UNSAFE (kept so existing
                                    callers that test `passed` still behave)
        """
        declared: List[str] = []
        for value in (self.settings.get('intolerances') or []):
            if isinstance(value, str) and value.strip():
                declared.append(value.strip())

        diets: List[str] = []
        for value in (self.settings.get('dietary_requirements') or []):
            if isinstance(value, str) and value.strip():
                cleaned = value.strip()
                if cleaned.lower() not in ('none', 'null', ''):
                    diets.append(cleaned)

        # ------------------------------------------------------------------
        # Resolve the recipe
        # ------------------------------------------------------------------
        ingredient_texts = self._collect_ingredient_texts(recipe)
        method_texts = self._collect_method_texts(recipe)

        resolved: List[Dict[str, Any]] = []   # {raw_text, canonical_id, categories, source}
        unresolved: List[str] = []

        for raw, source in ([(t, 'ingredient') for t in ingredient_texts] +
                            [(t, 'instructions') for t in method_texts]):
            ids, misses = resolve_text(raw)
            for cid in ids:
                resolved.append({
                    'raw_text': raw,
                    'canonical_id': cid,
                    'display': DISPLAY_BY_ID.get(cid, cid),
                    'categories': sorted(categories_for(cid)),
                    'source': source,
                })
            # Only unrecognised *ingredient* words make a recipe UNKNOWN.
            # Instruction prose is full of ordinary English ("stir", "until
            # golden") that will never be in a food table, so an unknown word
            # there is not evidence of anything. Instructions can only ever add
            # an UNSAFE match, never withhold a SAFE verdict.
            if source == 'ingredient':
                for miss in misses:
                    if miss not in unresolved:
                        unresolved.append(miss)

        has_ingredient_data = bool(ingredient_texts)

        # ------------------------------------------------------------------
        # Evaluate every restriction against every ingredient. No short
        # circuit, no elif chain: adding a restriction must never screen less.
        # ------------------------------------------------------------------
        per_restriction: List[Dict[str, Any]] = []
        matched_allergens: List[Dict[str, Any]] = []
        unscreenable: List[str] = []
        states: List[str] = []

        def evaluate(label: str, kind: str, excluded_categories: set):
            hits = []
            for item in resolved:
                overlap = excluded_categories.intersection(item['categories'])
                if overlap:
                    hits.append({
                        'raw_text': item['raw_text'],
                        'canonical_id': item['canonical_id'],
                        'display': item['display'],
                        'categories': sorted(overlap),
                        'source': item['source'],
                    })

            if hits:
                state = UNSAFE
            elif not excluded_categories:
                # The table has no vocabulary for this declaration. Saying
                # nothing was found would be a claim we have not earned.
                state = UNKNOWN
                unscreenable.append(label)
            elif not has_ingredient_data:
                state = UNKNOWN
            elif unresolved:
                state = UNKNOWN
            else:
                state = SAFE

            states.append(state)
            per_restriction.append({
                'restriction': label,
                'kind': kind,
                'state': state,
                'screened_categories': sorted(excluded_categories),
                'matched_ingredients': hits,
            })
            for hit in hits:
                if hit not in matched_allergens:
                    matched_allergens.append(hit)

        for allergen in declared:
            evaluate(allergen, 'allergen', resolve_declaration(allergen))

        for diet in diets:
            key = diet.lower().replace('-', '_').replace(' ', '_')
            if key in DIET_EXCLUSIONS:
                evaluate(diet, 'diet', set(DIET_EXCLUSIONS[key]))
            else:
                # An unrecognised diet ("keto", "halal", free text) is not
                # something this table can screen. Say so.
                evaluate(diet, 'diet', set())

        # ------------------------------------------------------------------
        # Combine. UNSAFE dominates; UNKNOWN beats SAFE.
        # ------------------------------------------------------------------
        if not per_restriction:
            overall = SAFE
            reason = 'No dietary restrictions declared'
        else:
            overall = max(states, key=lambda s: _VERDICT_ORDER[s])
            if overall == UNSAFE:
                named = sorted({f"{h['display']} ({', '.join(h['categories'])})"
                                for h in matched_allergens})
                reason = 'Contains ' + '; '.join(named)
            elif overall == UNKNOWN:
                parts = []
                if unscreenable:
                    parts.append('cannot screen for ' + ', '.join(sorted(set(unscreenable))))
                if not has_ingredient_data:
                    parts.append('no ingredient data for this recipe')
                elif unresolved:
                    parts.append('unrecognised ingredient(s): ' + ', '.join(unresolved[:5]))
                reason = 'Not verified - ' + '; '.join(parts) if parts else 'Not verified'
            else:
                reason = 'No declared restriction matched any ingredient'

        return {
            'safety_state': overall,
            'safety_reason': reason,
            'reason': reason,
            'per_restriction': per_restriction,
            'matched_allergens': matched_allergens,
            # Kept for the existing orchestrator and UI, now derived rather than
            # invented: the list of restrictions that actually matched.
            'found_intolerances': sorted({e['restriction'] for e in per_restriction
                                          if e['state'] == UNSAFE}),
            'suspicious_ingredients': sorted({h['raw_text'] for h in matched_allergens}),
            'unresolved_ingredients': unresolved,
            'unscreenable_declarations': sorted(set(unscreenable)),
            'table_version': TABLE_VERSION,
            'passed': overall != UNSAFE,
            # No model is consulted for any verdict, so nothing is ever deferred
            # to one. These stay False so downstream code that reads them keeps
            # working and can never be asked to adjudicate safety.
            'requires_ai_validation': False,
            'requires_ai_reassurance': False,
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
        # .get with a default: this was the one setting read without one, so any
        # caller that did not happen to supply it crashed the whole request.
        missing_check = self._check_missing_limit(
            recipe.get("missedIngredientCount", 0),
            self.settings.get('max_missing_ingredients', 10)
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
        Report on dietary fit for the *preference* path -- rank only.

        This used to be a fourth independent keyword list with its own opinions,
        disagreeing with the three others in the file, and it contained an escape
        hatch structurally identical to SAFE_WORDS: when gluten or dairy keywords
        were found *and* the third-party `glutenFree`/`dairyFree` boolean said
        otherwise, the flag won and the recipe was annotated "may contain" rather
        than excluded. A vendor's metadata field was allowed to overrule the
        ingredient list.

        It now resolves through the same canonical table as the safety gate, so
        there is one vocabulary, and it never reads the API booleans at all. It
        also cannot exclude anything: its only output is a rank penalty. The
        safety gate above is the only thing that removes a recipe.
        """
        if not dietary_requirements and not intolerances:
            return {'passed': True, 'reason': 'No dietary restrictions',
                    'confidence': 'high', 'table_version': TABLE_VERSION}

        excluded = set()
        for requirement in dietary_requirements or []:
            key = str(requirement).lower().replace('-', '_').replace(' ', '_')
            excluded |= set(DIET_EXCLUSIONS.get(key, set()))
        for intolerance in intolerances or []:
            excluded |= resolve_declaration(str(intolerance))

        if not excluded:
            # Nothing here that this table can express. Say so rather than
            # reporting "meets requirements", which would be a claim.
            return {
                'passed': True,
                'reason': 'not evaluated - no table vocabulary for the declared preferences',
                'requirements_checked': dietary_requirements,
                'intolerances_checked': intolerances,
                'confidence': 'low',
                'table_version': TABLE_VERSION,
            }

        hits = []
        for text in self._collect_ingredient_texts(recipe):
            ids, _ = resolve_text(text)
            for cid in ids:
                overlap = excluded.intersection(categories_for(cid))
                if overlap:
                    hits.append(f"{DISPLAY_BY_ID.get(cid, cid)} ({', '.join(sorted(overlap))})")

        if hits:
            return {
                'passed': False,
                'reason': 'contains ' + '; '.join(sorted(set(hits))),
                'requirements_checked': dietary_requirements,
                'intolerances_checked': intolerances,
                'confidence': 'high',
                'table_version': TABLE_VERSION,
            }

        return {
            'passed': True,
            'reason': 'meets requirements',
            'requirements_checked': dietary_requirements,
            'intolerances_checked': intolerances,
            'confidence': 'high' if recipe.get('extendedIngredients') else 'low',
            'table_version': TABLE_VERSION,
        }
    
    def _calculate_smart_score(self, recipe: Dict) -> Dict:
        """
        Score a recipe against the user's chosen profile.

        The profile is the product's signature idea -- naming the shop-vs-use-
        pantry tradeoff instead of showing a slider -- and it had never once
        changed a result. The old formula was:

            missed_percent   = 100 - used_percent          (by construction)
            missed_component = w_missing * (100 - missed_percent)
                             = w_missing * used_percent
            smart_score      = w_used * used_percent + w_missing * used_percent
                             = (w_used + w_missing) * used_percent

        and every profile's weights sum to 1.0, so smart_score was just
        used_percent and all three profiles returned the same number for every
        recipe.

        The fix is to make the two weighted components measure genuinely
        different things:

            coverage  = used / total          how much of it you already have
            shopping  = 1 - missing / N_cap   how little you have to go and buy

        Coverage is a ratio of the recipe; shopping is an absolute count against
        the user's own tolerance for a shopping trip (max_missing_ingredients,
        floored at 1). A recipe you half-own that needs two items and one you
        half-own that needs twenty now score differently, which is the entire
        point of having a profile.
        """
        used_count = recipe.get('usedIngredientCount', 0) or 0
        missed_count = recipe.get('missedIngredientCount', 0) or 0
        total_ingredients = used_count + missed_count

        if total_ingredients == 0:
            return {
                'smart_score': 0,
                'used_score': 0,
                'missing_score': 0,
                'breakdown': 'No ingredient data',
                'weights': self.profile['weights'],
            }

        try:
            n_cap = max(1, int(self.settings.get('max_missing_ingredients') or 5))
        except (TypeError, ValueError):
            n_cap = 5

        coverage = used_count / total_ingredients                 # 0..1
        shopping = max(0.0, min(1.0, 1 - (missed_count / n_cap)))  # 0..1

        weights = self.profile['weights']
        smart_score = 100 * (weights['used'] * coverage + weights['missing'] * shopping)

        return {
            'smart_score': round(smart_score, 1),
            'used_score': round(coverage * 100, 1),
            'missing_score': round(shopping * 100, 1),
            'breakdown': self._get_score_breakdown(coverage * 100, shopping * 100, weights),
            'weights': weights
        }

    def _get_score_breakdown(self, coverage_percent: float, shopping_percent: float,
                             weights: Dict) -> str:
        """
        Human-readable derivation of the score. This is user-facing on purpose:
        showing the arithmetic behind a recommendation is worth more than the
        recommendation.
        """
        used_comp = round(weights['used'] * coverage_percent, 1)
        shopping_comp = round(weights['missing'] * shopping_percent, 1)

        return (
            f"({weights['used']}×{coverage_percent:.1f}% pantry coverage) + "
            f"({weights['missing']}×{shopping_percent:.1f}% little-shopping) = "
            f"{used_comp} + {shopping_comp}"
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

        # Effort score. 'effort' has always been one of the four mood weights and
        # nothing has ever read it -- a quarter of the mood model was decorative.
        # Bind it to the one effort signal the recipe actually carries: how many
        # steps the method has. 12+ steps scores 0, a 1-step recipe scores 1.
        step_count = 0
        for block in recipe.get('analyzedInstructions') or []:
            if isinstance(block, dict):
                step_count += len(block.get('steps') or [])
        if step_count:
            effort_score = max(0.0, min(1.0, 1 - (step_count - 1) / 12))
        else:
            effort_score = 0.5  # no method data; do not reward or punish

        # Ranking blend. The 'tired' branch used to multiply time_score by 2
        # *before* the weighted sum, which broke the 0..1 normalisation and let
        # the time term alone reach the full weight of a supposedly-capped blend.
        # Three separate mechanisms encoded "tired users like fast recipes" -- the
        # weight table, that multiplier, and a +15 confidence bonus -- and only
        # the table was inspectable. The multiplier is gone; if tired users should
        # weight time more, change MOOD_WEIGHTS['tired']['time']. That is what the
        # table is for.
        #
        # Note this is an ordinal, not a percentage: the mood weights stop the
        # four terms summing to 1.0. It is used to sort and is never displayed.
        final_internal_score = (
            (smart_score / 100) * 0.40 +
            time_score * self.mood_weights['time'] * 0.25 +
            effort_score * self.mood_weights['effort'] * 0.15 +
            skill_score * self.mood_weights['skill'] * 0.10 +
            shopping_score * self.mood_weights['shopping'] * 0.10
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
                # rank_score is the sort key used by process_results.
                'rank_score': round(final_internal_score, 6),
                'internal_score': round(final_internal_score * 100, 1),
                'time_score': round(time_score, 2),
                'effort_score': round(effort_score, 2),
                'skill_score': round(skill_score, 2),
                'shopping_score': round(shopping_score, 2),
                'step_count': step_count,
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
        
        # There is deliberately no "Safety Jury" clause here any more.
        #
        # This block used to instruct the model to "act as Safety Jury" and
        # "confirm safety for user's intolerances" on recipes the keyword matcher
        # had flagged. That is asking a language model to clear an allergen, and
        # the validator behind it returned safe_for_user: True whenever it could
        # not reach the API -- so the fallback for "the model could not answer"
        # was "the model approved".
        #
        # The safety verdict is now computed deterministically before this
        # function runs, and nothing in this prompt can move it. What the model
        # is still asked for -- substitutions, nutrition commentary, the pitch --
        # is presentation, and presentation is allowed to be wrong.
        if safety_check.get('safety_state') == UNKNOWN:
            context_parts.append(
                "This recipe could not be verified against the user's declared "
                "restrictions. Do not tell the user it is safe; tell them to check "
                "the ingredient list themselves."
            )

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
            # smart_score removed from top level - it's in _metadata only
            # match_confidence used to be read off the raw upstream recipe, which
            # never carries the key, so it was 1.0 for everything. It is the same
            # concept as `confidence`, so it is now the same number rather than a
            # second name for a constant.
            'match_confidence': reasoning_data['confidence'],

            # --- Safety, kept in its own vocabulary and never blended with the
            # confidence numbers above. `confidence` answers "does this match
            # what you asked for". It never answers "is this safe to eat".
            'safety_state': safety_check.get('safety_state', UNKNOWN),
            'safety_reason': safety_check.get('safety_reason', ''),
            # Retrieval provenance, when the recipe came through dual_retrieval:
            # which endpoint(s) returned it, and what the API was asked to
            # pre-filter on. _clean_data builds a fresh dict, so this has to be
            # carried explicitly or it is lost before it reaches the UI.
            '_retrieval': recipe.get('_retrieval', {}),
            'safety_unresolved_ingredients': safety_check.get('unresolved_ingredients', []),
            'safety_unscreenable_declarations': safety_check.get('unscreenable_declarations', []),
            'safety_table_version': safety_check.get('table_version', ''),
            'needs_semantic_validation': recipe.get('needs_semantic_validation', False),
            'semantic_validation_reason': recipe.get('semantic_validation_reason', ''),
            'pending_semantic_validation': scoring_data.get('pending_semantic_validation', False),
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
    
    # This assertion used to require safety_score == 0.2, a value no branch of
    # _apply_safety_check could return -- the reachable scores were 0.0, 0.3, 0.5
    # and 1.0. The shipped self-test had therefore never passed. It now asserts
    # the behaviour that matters: butter is dairy, the user declared dairy, so
    # the verdict is UNSAFE, it names the offending ingredient, and no model was
    # consulted to reach it.
    safety_ok = (
        safety_check.get('safety_state') == 'UNSAFE' and
        safety_check.get('passed') is False and
        safety_check.get('requires_ai_validation') is False and
        'butter' in safety_check.get('safety_reason', '').lower()
    )
    print(f"  Safety State: {safety_check.get('safety_state')}")
    print(f"  Matched: {[h['raw_text'] for h in safety_check.get('matched_allergens', [])]}")
    print(f"  Table Version: {safety_check.get('table_version')}")
    print(f"  {'✅' if safety_ok else '❌'} Dairy intolerance on a butter recipe is UNSAFE, deterministically")
    
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
    
    # The fixture above contains butter and the declared intolerance is dairy, so
    # the safety gate must remove it. That is the whole point of the gate, and it
    # is asserted here rather than treated as a disappointing empty result.
    excluded = engine.process_results([test_recipe])
    print(f"  Dairy-intolerant user, recipe contains butter -> returned {len(excluded)} recipe(s)")
    exclusion_ok = len(excluded) == 0
    print(f"  {'✅' if exclusion_ok else '❌'} Unsafe recipe correctly withheld")

    # Same recipe, same settings, minus the butter: it should now come through
    # with its data intact.
    safe_recipe = dict(test_recipe)
    safe_recipe['extendedIngredients'] = [
        {'name': 'pasta', 'amount': 2.0, 'unit': 'cups'},
        {'name': 'olive oil', 'amount': 0.25, 'unit': 'cup'},
        {'name': 'tomatoes', 'amount': 2.0, 'unit': 'cups'}
    ]
    safe_recipe['instructions'] = 'Cook pasta. Add olive oil. Mix with tomatoes.'
    safe_recipe['analyzedInstructions'] = [
        {'steps': [
            {'step': 'Cook pasta'},
            {'step': 'Add olive oil'},
            {'step': 'Mix with tomatoes'}
        ]}
    ]

    results = engine.process_results([safe_recipe])

    if results:
        result = results[0]
        print(f"  Recipe Title: {result.get('title')}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        print(f"  Safety State: {result.get('safety_state', 'N/A')}")
        print(f"  Safety Reason: {result.get('safety_reason', 'N/A')}")
        print(f"  Protein: {result.get('protein', 0)}")
        print(f"  Calories: {result.get('calories', 0)}")
        print(f"  Extended Ingredients Count: {len(result.get('extendedIngredients', []))}")
        print(f"  Rank Score: {result.get('_metadata', {}).get('internal_debug', {}).get('rank_score')}")

        pipeline_ok = (
            exclusion_ok and
            result.get('protein') == 15.0 and
            result.get('calories') == 450.0 and
            len(result.get('extendedIngredients', [])) > 0 and
            result.get('safety_state') == 'SAFE'
        )
        print(f"  {'✅' if pipeline_ok else '❌'} Full pipeline processing successful")
    else:
        print("  ❌ No results returned for the butter-free variant")
        pipeline_ok = False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_tests_passed = mapping_ok and safety_ok and nutrition_ok and pipeline_ok
    
    if all_tests_passed:
        print("✅ SUCCESS: All tests passed!")
        print("   - ✅ Plural keys (cuisines, dishTypes, diets) correctly mapped")
        print("   - ✅ Dairy on a butter recipe is UNSAFE and the recipe is withheld")
        print("   - ✅ Nutrition correctly parsed from nutrients list structure")
        print("   - ✅ Full pipeline processing successful")
    else:
        print("❌ FAILURE: Some tests failed")
        print(f"   - Mapping: {'✅' if mapping_ok else '❌'}")
        print(f"   - Safety Check: {'✅' if safety_ok else '❌'}")
        print(f"   - Nutrition Parsing: {'✅' if nutrition_ok else '❌'}")
        print(f"   - Full Pipeline: {'✅' if pipeline_ok else '❌'}")
    
    print("=" * 70)
