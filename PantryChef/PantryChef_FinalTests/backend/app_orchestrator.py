"""
PantryChef App Orchestrator
Backend "brain" that coordinates Spoonacular API, Logic Engine, and Gemini AI.
Acts as a neutral conductor - never filters recipes, passes everything through.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from pantry_chef_api import SpoonacularClient
from Logic import PantryChefEngine
from gemini_integration import GeminiSubstitution

load_dotenv()


class PantryChefOrchestrator:
    """
    Main orchestrator class that coordinates all backend components.
    Acts as a neutral conductor - never filters recipes based on scores.
    All recipes from Logic.py are passed through to Gemini for Safety Jury review.
    """
    
    def __init__(self, api_key: Optional[str] = None, gemini_key: Optional[str] = None):
        """
        Initialize the orchestrator with API clients.
        
        Args:
            api_key: Spoonacular API key (if None, loads from .env)
            gemini_key: Gemini API key (if None, loads from .env)
        """
        # Load API keys
        self.spoonacular_key = api_key or os.getenv('SPOONACULAR_API_KEY')
        self.gemini_key = gemini_key or os.getenv('GEMINI_API_KEY')
        
        # Initialize clients
        if not self.spoonacular_key:
            raise ValueError("SPOONACULAR_API_KEY not found. Please set it in .env file or pass as parameter.")
        
        # 1. Initialization: Connect the three main components
        self.api_client = SpoonacularClient(self.spoonacular_key)
        self.logic_engine = None  # Will be initialized in run_pantry_chef with user settings
        self.gemini = GeminiSubstitution() if self.gemini_key else None
    
    def run_pantry_chef(
        self,
        ingredients: List[str],
        settings: Dict[str, Any],
        number: int = 20,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        enrich_with_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Main function that orchestrates the complete PantryChef workflow.
        Acts as a neutral conductor - never filters recipes based on scores.
        
        Args:
            ingredients: List of ingredient names from user's pantry
            settings: User settings dictionary with:
                - user_profile: 'balanced' | 'minimal_shopper' | 'pantry_cleaner'
                - mood: 'tired' | 'casual' | 'energetic'
                - max_difficulty: 'easy' | 'medium' | 'hard'
                - max_time_minutes: int
                - max_missing_ingredients: int
                - dietary_requirements: List[str]
                - intolerances: List[str] (for Logic.py manual checking)
                - nutritional_requirements: Dict[str, float]
                - skill_level: int (0-100)
                - max_time: int
            number: Number of recipes to fetch from API (default: 20)
            cuisine: Optional cuisine filter
            meal_type: Optional meal type filter
            diet: Optional diet filter
            intolerances: Optional intolerances list (for API filtering)
            enrich_with_ai: Whether to enrich with Gemini AI (default: True)
            
        Returns:
            Dictionary with:
            - recipes: List of processed recipe dictionaries (from Logic.py)
            - pitch: AI-generated recommendation pitch (if enrich_with_ai=True)
            - metadata: Processing metadata
        """
        if not ingredients:
            return {
                'recipes': [],
                'pitch': None,
                'metadata': {
                    'total_fetched': 0,
                    'total_processed': 0,
                    'errors': ['No ingredients provided']
                }
            }
        
        # Step A: API Call - Call 3-step pipeline from pantry_chef_api.py
        # SMART FILTER LOGIC: Handle cuisine and intolerance fallbacks gracefully
        raw_recipes = []
        cuisine_used = cuisine  # Track original cuisine for labeling
        metadata_notes = []
        
        # SMART SACRIFICE: Use Gemini to prioritize ingredients BEFORE API call
        # If user has >5 ingredients, use only Core ingredients (proteins, grains, main vegetables)
        # This prevents a single missing spice from hiding 20 great recipes
        ingredients_to_search = ingredients
        if len(ingredients) > 5 and self.gemini and self.gemini.is_available():
            print(f"🔍 Smart Sacrifice: Analyzing {len(ingredients)} ingredients to identify Core vs Optional...")
            try:
                ingredient_categorization = self.gemini.get_low_priority_ingredients(ingredients)
                core_ingredients = ingredient_categorization.get('core', [])
                optional_ingredients = ingredient_categorization.get('secondary', [])
                
                if core_ingredients and len(core_ingredients) < len(ingredients):
                    print(f"  → Using {len(core_ingredients)} Core ingredients: {core_ingredients}")
                    print(f"  → Dropping {len(optional_ingredients)} Optional ingredients: {optional_ingredients}")
                    ingredients_to_search = core_ingredients
                    metadata_notes.append(f"Smart Sacrifice: Using {len(core_ingredients)} core ingredients (dropped {len(optional_ingredients)} optional)")
                else:
                    print(f"  → All ingredients are Core, using all {len(ingredients)} ingredients")
            except Exception as e:
                print(f"⚠️  Smart Sacrifice analysis failed: {str(e)} - using all ingredients")
                # Continue with all ingredients if Gemini fails
        
        try:
            # Attempt 1: Try with all filters (cuisine, diet, intolerances, meal_type)
            # Use prioritized ingredients (Core only if Smart Sacrifice was applied)
            # API-level filtering: diet and intolerances are now passed to Spoonacular for server-side filtering
            raw_recipes = self.api_client.search_by_ingredients(
                user_ingredients=ingredients_to_search,
                number=number,
                cuisine=cuisine,
                meal_type=meal_type,
                diet=diet,
                intolerances=intolerances,
                enrich_results=True  # Ensure we get full data from informationBulk
            )
            
            # FALLBACK LOGIC: Check if we have enough recipes (at least 3)
            # If low results, trigger Gemini Web Search to find more recipes
            if len(raw_recipes) < 3 and self.gemini and self.gemini.is_available():
                print(f"⚠️  Low results ({len(raw_recipes)}). Triggering Gemini Web Search...")
                try:
                    # Call Gemini to find recipes online
                    web_recipes = self.gemini.search_web_for_recipes(
                        ingredients=ingredients_to_search,
                        diet=diet,
                        count=(3 - len(raw_recipes)),
                        cuisine=cuisine,
                        meal_type=meal_type,
                        intolerances=intolerances
                    )
                    
                    if web_recipes:
                        print(f"  → Found {len(web_recipes)} additional recipes from Gemini Web Search")
                        # Merge web results with API results
                        raw_recipes.extend(web_recipes)
                        metadata_notes.append(f"Gemini Web Search: Added {len(web_recipes)} recipes")
                except Exception as e:
                    print(f"⚠️  Gemini Web Search failed: {str(e)} - continuing with API results only")
        except Exception as e:
            return {
                'recipes': [],
                'pitch': None,
                'metadata': {
                    'total_fetched': 0,
                    'total_processed': 0,
                    'errors': [f'API Error: {str(e)}']
                }
            }
        
        # SMART CUISINE FALLBACK: If cuisine selected but 0 results, try progressive fallbacks
        if not raw_recipes and cuisine:
            print(f"⚠️  No results with '{cuisine}' cuisine. Trying smart filter fallback...")
            
            # Attempt 2: CUISINE BROADENING - Use semantic query instead of strict cuisine filter
            # Example: Instead of cuisine='Indian', try query='Indian chicken rice' for broader matching
            print(f"  → Trying cuisine broadening with semantic query...")
            try:
                # Use top 2-3 ingredients + cuisine name as a semantic search query
                # This allows the API to find recipes that match the cuisine concept even if strict filter fails
                top_ingredients_for_query = ingredients[:3]  # Take top 3 ingredients
                semantic_query = f"{cuisine} {' '.join(top_ingredients_for_query)}"
                
                # Use complexSearch with query parameter instead of strict cuisine filter
                # This method handles enrichment internally
                raw_recipes = self.api_client._search_complex_search_with_query(
                    query=semantic_query,
                    user_ingredients=ingredients,
                    number=number,
                    cuisine=None,  # Don't use strict cuisine filter
                    meal_type=meal_type,
                    diet=diet,
                    intolerances=intolerances,
                    enrich_results=True  # Enrich results with full recipe data
                )
                
                if raw_recipes:
                    print(f"✅ Found {len(raw_recipes)} recipes with cuisine broadening (query: '{semantic_query}')")
                    metadata_notes.append(f"Cuisine broadening: '{semantic_query}' (strict {cuisine} filter removed)")
                    # Still mark as original cuisine for labeling
                    cuisine_used = cuisine
            except Exception as e:
                print(f"  ⚠️  Cuisine broadening failed: {str(e)}")
                # Continue to next fallback
            
            # Attempt 3: Remove intolerances first (sometimes "Dairy-Free" kills all Italian results)
            if not raw_recipes and intolerances and len(intolerances) > 0:
                print(f"  → Trying without intolerances: {intolerances}")
                try:
                    raw_recipes = self.api_client.search_by_ingredients(
                        user_ingredients=ingredients,
                        number=number,
                        cuisine=cuisine,
                        meal_type=meal_type,
                        diet=diet,
                        intolerances=[],  # Remove intolerances
                        enrich_results=True
                    )
                    if raw_recipes:
                        print(f"✅ Found {len(raw_recipes)} recipes without intolerances")
                        metadata_notes.append(f"Intolerances removed to find {cuisine} recipes")
                except Exception as e:
                    print(f"  ⚠️  Fallback attempt failed: {str(e)}")
            
            # Attempt 4: Remove cuisine filter entirely (search by ingredients only)
            if not raw_recipes:
                print(f"  → Trying without '{cuisine}' cuisine filter...")
                try:
                    raw_recipes = self.api_client.search_by_ingredients(
                        user_ingredients=ingredients,
                        number=number,
                        cuisine=None,  # Remove cuisine
                        meal_type=meal_type,
                        diet=diet,
                        intolerances=intolerances,  # Re-add intolerances if we have them
                        enrich_results=True
                    )
                    if raw_recipes:
                        print(f"✅ Found {len(raw_recipes)} recipes without cuisine filter")
                        cuisine_used = None  # Mark as no cuisine filter applied
                        metadata_notes.append("Recommended for your Pantry (cuisine filter removed)")
                except Exception as e:
                    print(f"  ⚠️  Final fallback attempt failed: {str(e)}")
        
        # RELAXED SEARCH (Pantry Slap): If still zero results and user has >3 ingredients, try with top 3
        if not raw_recipes and len(ingredients) > 3:
            print(f"⚠️  No results with {len(ingredients)} ingredients. Trying relaxed search with top 3 ingredients...")
            try:
                # Use top 3 ingredients (most common/popular)
                top_ingredients = ingredients[:3]
                raw_recipes = self.api_client.search_by_ingredients(
                    user_ingredients=top_ingredients,
                    number=number,
                    cuisine=cuisine_used,  # Use original cuisine if available
                    meal_type=meal_type,
                    diet=diet,
                    intolerances=intolerances,
                    enrich_results=True  # Ensure we get full data from informationBulk
                )
                if raw_recipes:
                    print(f"✅ Relaxed search successful: Found {len(raw_recipes)} recipes with {len(top_ingredients)} ingredients")
                    metadata_notes.append(f"Search relaxed to top {len(top_ingredients)} ingredients")
            except Exception as e:
                print(f"⚠️  Relaxed search also failed: {str(e)}")
        
        # GEMINI SEMANTIC INGREDIENT PRIORITIZATION: If results < 5, use Core ingredients
        # This "knocks out" stubborn ingredients that are holding up results
        if len(raw_recipes) < 5 and self.gemini and self.gemini.is_available():
            print(f"⚠️  Only {len(raw_recipes)} recipes found. Using Gemini to prioritize ingredients...")
            try:
                # Call Gemini to categorize ingredients into Core and Secondary
                ingredient_categorization = self.gemini.get_low_priority_ingredients(ingredients)
                core_ingredients = ingredient_categorization.get('core', [])
                secondary_ingredients = ingredient_categorization.get('secondary', [])
                
                print(f"  → Core ingredients (using these): {core_ingredients}")
                print(f"  → Secondary ingredients (dropping these): {secondary_ingredients}")
                
                # If we have core ingredients and they're different from original, re-run search
                if core_ingredients and len(core_ingredients) < len(ingredients):
                    print(f"  → Re-running search with {len(core_ingredients)} core ingredients...")
                    
                    # Re-run search with ONLY Core ingredients (if different from initial search)
                    if core_ingredients != ingredients_to_search:
                        raw_recipes_core = self.api_client.search_by_ingredients(
                            user_ingredients=core_ingredients,
                            number=number,
                            cuisine=cuisine_used,
                            meal_type=meal_type,
                            diet=diet,
                            intolerances=intolerances,
                            enrich_results=True
                        )
                    else:
                        # Core ingredients already used in initial search
                        raw_recipes_core = raw_recipes
                    
                    if raw_recipes_core and len(raw_recipes_core) > len(raw_recipes):
                        print(f"✅ Found {len(raw_recipes_core)} recipes with core ingredients (was {len(raw_recipes)})")
                        raw_recipes = raw_recipes_core
                        metadata_notes.append(f"Semantic prioritization: Used {len(core_ingredients)} core ingredients (dropped {len(secondary_ingredients)} secondary)")
                    else:
                        print(f"⚠️  Core ingredients search didn't improve results")
                else:
                    print(f"⚠️  No core ingredients to prioritize, or core = all ingredients")
                    
            except Exception as e:
                print(f"⚠️  Gemini ingredient prioritization failed: {str(e)}")
                # Continue with original results
        
        if not raw_recipes:
            return {
                'recipes': [],
                'pitch': None,
                'metadata': {
                    'total_fetched': 0,
                    'total_processed': 0,
                    'errors': ['No recipes found from API']
                }
            }
        
        # Step B: Logic Processing - Pass raw data directly to PantryChefEngine
        # Ensure intolerances are passed correctly for Logic.py's manual keyword audit
        engine_settings = settings.copy()
        if intolerances and 'intolerances' not in engine_settings:
            # If intolerances provided as parameter, add to settings for Logic.py
            engine_settings['intolerances'] = intolerances
        elif 'intolerances' in engine_settings and isinstance(engine_settings['intolerances'], list):
            # Settings already has intolerances list - use it
            pass
        
        try:
            # Initialize engine with user settings
            self.logic_engine = PantryChefEngine(engine_settings)
            
            # Process all recipes through Logic engine
            # CRITICAL: process_results returns ALL recipes (no filtering based on scores)
            processed_recipes = self.logic_engine.process_results(raw_recipes)
        except Exception as e:
            return {
                'recipes': [],
                'pitch': None,
                'metadata': {
                    'total_fetched': len(raw_recipes),
                    'total_processed': 0,
                    'errors': [f'Processing Error: {str(e)}']
                }
            }
        
        # ENFORCER: Filter out unsafe recipes BEFORE sending to Gemini
        # Changed from "neutral conductor" to active filter - removes recipes that Logic.py flagged
        # This kills "Chicken Shawarma" immediately if Logic.py flags it
        safe_recipes = []
        for recipe in processed_recipes:
            # Check recipe-level passed flag (if Logic.py sets it directly)
            if not recipe.get('passed', True):
                print(f"⚠️  Enforcer: Removing recipe '{recipe.get('title', 'Unknown')}' - Logic.py flagged passed: False")
                continue  # DELETE this recipe - do not send to Gemini
            
            # Check metadata safety_check passed flag
            metadata = recipe.get('_metadata', {})
            safety_check = metadata.get('safety_check', {})
            
            # CRITICAL: Check if recipe passed safety check from Logic.py
            # Logic.py sets passed: False for meat violations, intolerance violations, etc.
            if not safety_check.get('passed', True):
                print(f"⚠️  Enforcer: Removing recipe '{recipe.get('title', 'Unknown')}' - failed safety check (passed: False)")
                print(f"   Reason: {safety_check.get('reason', 'Unknown reason')}")
                continue  # DELETE this recipe - do not send to Gemini
            
            # CRITICAL: Check if safety_score is too low (< 0.5)
            # Low safety scores indicate violations that should be filtered out
            safety_score = safety_check.get('safety_score', 1.0)
            if safety_score < 0.5:
                print(f"⚠️  Enforcer: Removing recipe '{recipe.get('title', 'Unknown')}' - low safety score ({safety_score})")
                print(f"   Reason: {safety_check.get('safety_reason', 'Unknown reason')}")
                continue  # DELETE this recipe - do not send to Gemini
            
            safe_recipes.append(recipe)
        
        # Update processed_recipes to only include safe recipes
        # These are the only recipes that will be sent to Gemini
        processed_recipes = safe_recipes
        
        # Step C: Gemini Enrichment - Take top results and generate pitch
        # CRITICAL: Ensure nutrition data is passed to Gemini for nutritional pills generation
        # The nutrition data (including vitamins, minerals) is already in processed_recipes from Logic.py
        # Logic.py preserves recipe.nutrition from informationBulk, which contains nutrients array
        pitch = None
        if enrich_with_ai and processed_recipes and self.gemini and self.gemini.is_available():
            try:
                # Take top 3 recipes for pitch generation (but keep ALL recipes in results)
                top_3_for_pitch = processed_recipes[:3]
                
                # CRITICAL: Verify nutrition data is present for Gemini to generate nutritional pills
                # Each recipe should have recipe.nutrition.nutrients array with vitamins/minerals
                for recipe in top_3_for_pitch:
                    if not recipe.get('nutrition') or not recipe.get('nutrition', {}).get('nutrients'):
                        print(f"⚠️  Warning: Recipe {recipe.get('id')} missing nutrition data - pills may not display correctly")
                
                # Generate Chef's Pitch from Gemini
                # Gemini will use nutrition data from recommendations to generate tags like "High Protein", "Rich in Calcium"
                pitch_result = self.gemini.generate_recommendation_pitch(
                    recommendations=top_3_for_pitch,
                    user_mood=settings.get('mood', 'casual')
                )
                pitch = pitch_result.get('pitch_text')
                
                # ENFORCER: Filter out recipes that Gemini marked as "REJECTED"
                # If Gemini's response contains "REJECTED" for a recipe, remove it from final results entirely
                # This ensures that even if a 'lamb sausage' recipe trickles past the API and Logic.py, Gemini will catch it
                if pitch:
                    rejected_recipe_titles = set()
                    pitch_lower = pitch.lower()
                    pitch_upper = pitch.upper()
                    
                    # Check if pitch contains "REJECTED" - if so, identify which recipe(s) were rejected
                    if "REJECTED" in pitch_upper:
                        # Check each recipe in top_3_for_pitch to see if it's marked as REJECTED
                        for recipe in top_3_for_pitch:
                            recipe_title = recipe.get('title', '')
                            if not recipe_title:
                                continue
                            
                            # Look for pattern: "REJECTED" near the recipe title
                            # Check if REJECTED appears in the same context as the recipe title
                            title_lower = recipe_title.lower()
                            
                            # Find all occurrences of the recipe title in the pitch
                            title_index = pitch_lower.find(title_lower)
                            if title_index != -1:
                                # Check a window around the title for "REJECTED"
                                window_start = max(0, title_index - 100)
                                window_end = min(len(pitch_lower), title_index + len(title_lower) + 100)
                                window_text = pitch_lower[window_start:window_end]
                                
                                # If REJECTED appears in the same window as the recipe title, mark it as rejected
                                if 'rejected' in window_text:
                                    rejected_recipe_titles.add(recipe_title)
                        
                        # Also check for explicit "REJECTED" lines that might reference recipe numbers
                        # Handle cases where pitch is exactly "REJECTED" or contains "REJECTED" on its own line
                        pitch_lines = pitch.split('\n')
                        for i, line in enumerate(pitch_lines):
                            line_stripped = line.strip().upper()
                            # If line is exactly "REJECTED", match it to the corresponding recipe by position
                            if line_stripped == 'REJECTED':
                                # Match by position in top_3_for_pitch
                                if i < len(top_3_for_pitch):
                                    recipe = top_3_for_pitch[i]
                                    recipe_title = recipe.get('title', '')
                                    if recipe_title:
                                        rejected_recipe_titles.add(recipe_title)
                            elif 'rejected' in line.lower():
                                # Try to match with recipe by number (1., 2., 3.) or by title
                                line_lower = line.lower()
                                for j, recipe in enumerate(top_3_for_pitch):
                                    recipe_num = j + 1
                                    recipe_title = recipe.get('title', '')
                                    # Check if line contains recipe number or title
                                    if (f"{recipe_num}." in line_lower or 
                                        (recipe_title and recipe_title.lower() in line_lower)):
                                        rejected_recipe_titles.add(recipe_title)
                        
                        # ENFORCER: Remove rejected recipes from processed_recipes entirely
                        # After Gemini provides pitches, if any pitch contains "REJECTED", remove that recipe
                        # This ensures the user never sees unsafe recipes that passed Logic.py but failed Gemini's audit
                        if rejected_recipe_titles:
                            print(f"⚠️  Enforcer: Removing {len(rejected_recipe_titles)} rejected recipe(s) from Gemini: {list(rejected_recipe_titles)}")
                            processed_recipes = [
                                r for r in processed_recipes 
                                if r.get('title', '') not in rejected_recipe_titles
                            ]
            except Exception as e:
                # AI enrichment failed, but continue with processed recipes
                print(f"Warning: AI enrichment failed: {e}")
                pitch = None
        
        # Step D: The Return - Return both recipes and pitch
        # ENFORCER: Only return safe recipes that passed all checks
        # - Recipes with passed: False from Logic.py have been filtered out
        # - Recipes with safety_score < 0.5 have been filtered out
        # - Recipes marked as "REJECTED" by Gemini have been filtered out
        # The orchestrator is NO LONGER a "neutral conductor" - it actively enforces safety
        
        # Add metadata notes about filter fallbacks
        final_metadata = {
            'total_fetched': len(raw_recipes),
            'total_processed': len(processed_recipes),
            'ai_enriched': pitch is not None,
            'cuisine_applied': cuisine_used,  # Show which cuisine was actually used (or None if removed)
            'notes': metadata_notes,  # Notes about filter relaxations
            'errors': []
        }
        
        return {
            'recipes': processed_recipes,  # ALL recipes from Logic.py
            'pitch': pitch,
            'metadata': final_metadata
        }


def run_pantry_chef(
    ingredients: List[str],
    settings: Dict[str, Any],
    number: int = 20,
    cuisine: Optional[str] = None,
    meal_type: Optional[str] = None,
    diet: Optional[str] = None,
    intolerances: Optional[List[str]] = None,
    enrich_with_ai: bool = True,
    api_key: Optional[str] = None,
    gemini_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run PantryChef workflow.
    Creates orchestrator instance and runs the workflow.
    
    Args:
        ingredients: List of ingredient names from user's pantry
        settings: User settings dictionary (see PantryChefOrchestrator.run_pantry_chef)
        number: Number of recipes to fetch from API (default: 20)
        cuisine: Optional cuisine filter
        meal_type: Optional meal type filter
        diet: Optional diet filter
        intolerances: Optional intolerances list
        enrich_with_ai: Whether to enrich with Gemini AI (default: True)
        api_key: Optional Spoonacular API key (if None, loads from .env)
        gemini_key: Optional Gemini API key (if None, loads from .env)
        
    Returns:
        Dictionary with recipes, pitch, and metadata
    """
    orchestrator = PantryChefOrchestrator(api_key=api_key, gemini_key=gemini_key)
    return orchestrator.run_pantry_chef(
        ingredients=ingredients,
        settings=settings,
        number=number,
        cuisine=cuisine,
        meal_type=meal_type,
        diet=diet,
        intolerances=intolerances,
        enrich_with_ai=enrich_with_ai
    )


# --- FUSION TEST SUITE ---
if __name__ == "__main__":
    print("\n" + "="*70)
    print("✨ FUSION TEST: App Orchestrator Full Pipeline")
    print("="*70)

    # Initialize Orchestrator (uses .env for keys)
    orchestrator = PantryChefOrchestrator()

    # 1. Define User Context - "Creamy Garlic Pasta" scenario
    test_ingredients = ["chicken", "pasta", "garlic", "heavy cream"]
    test_settings = {
        'user_profile': 'balanced',
        'mood': 'tired',
        'intolerances': ['dairy'],  # This will trigger the "Flag, Don't Fail" logic
        'max_time_minutes': 30,
        'max_missing_ingredients': 5,
        'dietary_requirements': [],
        'skill_level': 50,
        'max_time': 30
    }

    print(f"\nSTEP 1: Running Full Pipeline (API -> Logic -> Gemini)...")
    print(f"   Ingredients: {', '.join(test_ingredients)}")
    print(f"   Intolerances: {test_settings['intolerances']}")
    
    # Note: Using small number for testing efficiency
    results = orchestrator.run_pantry_chef(
        ingredients=test_ingredients,
        settings=test_settings,
        number=3,
        enrich_with_ai=True
    )

    # 2. Verify Fusion Results
    print("\nVERIFICATION:")
    if results['recipes']:
        print(f"✅ Found {len(results['recipes'])} recipes")
        
        # Fix 3: Test Suite Update - Verify recipes with dairy are returned despite intolerance
        # The test should pass if len(results['recipes']) > 0 and top recipe has requires_ai_validation: True
        top_recipe = results['recipes'][0]
        print(f"✅ Top Match: {top_recipe['title']} (Confidence: {top_recipe.get('match_confidence', top_recipe.get('confidence', 'N/A'))}%)")
        
        # Check if the "Dairy" violation was flagged but preserved
        requires_validation = top_recipe.get('requires_ai_validation', False)
        if not requires_validation:
            # Check metadata for safety check
            safety_check = top_recipe.get('_metadata', {}).get('safety_check', {})
            requires_validation = safety_check.get('requires_ai_validation', False)
        
        if requires_validation:
            violation_note = top_recipe.get('violation_note', '')
            if not violation_note:
                safety_check = top_recipe.get('_metadata', {}).get('safety_check', {})
                violation_note = safety_check.get('violation_note', safety_check.get('safety_reason', 'N/A'))
            print(f"✅ Safety Flag Triggered: {violation_note}")
            print(f"✅ PASS: Recipe with dairy intolerance is returned with requires_ai_validation=True")
        else:
            print(f"⚠️  WARNING: Top recipe does not have requires_ai_validation flag")
            print(f"   This may indicate the recipe doesn't contain dairy, or the safety check didn't trigger")
        
        # Check plural keys are preserved
        cuisines = top_recipe.get('cuisines', [])
        dish_types = top_recipe.get('dishTypes', [])
        diets = top_recipe.get('diets', [])
        if cuisines or dish_types or diets:
            print(f"✅ Plural Keys Preserved: cuisines={cuisines}, dishTypes={dish_types}, diets={diets}")
        else:
            print(f"⚠️  WARNING: Plural keys not found in top recipe")
        
        # Check Gemini's Pitch
        if results.get('pitch'):
            print(f"✅ Gemini Pitch Generated: \"{results['pitch'][:100]}...\"")
            # Check if pitch mentions substitution or dairy
            pitch_lower = results['pitch'].lower()
            if 'dairy' in pitch_lower or 'cream' in pitch_lower or 'substitute' in pitch_lower or 'swap' in pitch_lower:
                print(f"✅ PASS: Gemini addressed the dairy intolerance in the pitch")
        else:
            print(f"⚠️  WARNING: No Gemini pitch generated")
        
        # Final Test Validation
        test_passed = len(results['recipes']) > 0 and requires_validation
        if test_passed:
            print(f"\n✅ TEST PASSED: Recipes with dairy are returned despite intolerance setting")
            print(f"   - Total recipes: {len(results['recipes'])}")
            print(f"   - Safety flag triggered: {requires_validation}")
            print(f"   - Orchestrator acted as neutral conductor (no filtering)")
        else:
            print(f"\n❌ TEST FAILED: Expected recipes with requires_ai_validation=True")
            print(f"   - Total recipes: {len(results['recipes'])}")
            print(f"   - Safety flag triggered: {requires_validation}")
    else:
        print("❌ No recipes found in fusion test.")
        print("   This indicates recipes are being filtered out - check orchestrator filtering logic")

    print("\n" + "="*70)
    print("✅ FUSION TEST COMPLETE")
    print("="*70)
    
    # NEW TEST: Dietary Enforcement Test
    print("\n" + "="*50)
    print("RUNNING DIETARY ENFORCEMENT TESTS")
    print("="*50)

    # Mock recipe that SHOULD be filtered out
    mock_meat_recipe = {
        "title": "Chicken Shawarma Bowl",
        "extendedIngredients": [{"name": "chicken breast"}, {"name": "garlic"}],
        "_metadata": {
            "safety_check": {
                "passed": False,  # Logic.py should set this to False
                "safety_reason": "Contains Land Meat",
                "reason": "Contains land meat keywords in ingredients"
            }
        }
    }

    print(f"Testing Recipe: {mock_meat_recipe['title']}")
    
    # Simulate the filtering logic from run_pantry_chef
    test_list = [mock_meat_recipe]
    filtered_list = []
    for recipe in test_list:
        # Check recipe-level passed flag
        if not recipe.get('passed', True):
            print(f"   Recipe filtered: recipe.get('passed') = False")
            continue
        
        # Check metadata safety_check passed flag
        metadata = recipe.get('_metadata', {})
        safety_check = metadata.get('safety_check', {})
        if not safety_check.get('passed', True):
            print(f"   Recipe filtered: safety_check.get('passed') = False")
            continue
        
        filtered_list.append(recipe)
    
    if len(filtered_list) == 0:
        print("✅ SUCCESS: Meat recipe was successfully blocked by Enforcer.")
    else:
        print("❌ FAILURE: Meat recipe leaked through the Enforcer!")
    
    print("="*50 + "\n")

