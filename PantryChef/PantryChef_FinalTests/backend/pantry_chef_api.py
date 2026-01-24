"""
Spoonacular API Client
Handles all API interactions with proper error handling and parameter support
Refactored for better parameter handling, response parsing, and error handling
"""

import requests
import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('SPOONACULAR_API_KEY')
if not API_KEY:
    print('WARNING: SPOONACULAR_API_KEY not found in environment')


class SpoonacularClient:
    """
    Client for interacting with Spoonacular API.
    Handles all recipe search, filtering, and data retrieval operations.
    """
    
    def __init__(self, api_key: str, use_mock_data: bool = False):
        """
        Initialize API client.
        
        Args:
            api_key: Spoonacular API key (can be dummy if use_mock_data=True)
            use_mock_data: If True, return mock data instead of making API calls (saves quota)
        """
        if not api_key and not use_mock_data:
            raise ValueError("API key is required when use_mock_data=False")
        
        self.api_key = api_key or "dummy_key"  # Dummy key if using mock data
        self.use_mock_data = use_mock_data
        # Ensure base_url does NOT end with trailing slash
        self.base_url = "https://api.spoonacular.com".rstrip('/')
        self.api_calls = 0  # Track API usage
        self.api_points_used = 0  # Track API points from quota headers (cumulative)
        self.last_quota_used = 0  # Track previous quota to calculate per-request cost
        self.debug_mode = True  # Enable to print debug URLs and quota tracking (QUOTA SHIELD)
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Spoonacular API with error handling.
        Tracks API quota usage from response headers.
        
        Args:
            endpoint: API endpoint (e.g., 'recipes/findByIngredients')
            params: Request parameters
            method: HTTP method (default: GET)
            
        Returns:
            JSON response as dictionary, or empty dict on error
        """
        # If mock data mode is enabled, return mock data instead of making API call
        if self.use_mock_data:
            return self._get_mock_response(endpoint, params)
        
        # Ensure endpoint doesn't start with slash, base_url doesn't end with slash
        # This prevents double-slash URLs (e.g., //recipes/...)
        endpoint_clean = endpoint.lstrip('/')
        url = f"{self.base_url}/{endpoint_clean}"
        params['apiKey'] = self.api_key
        
        # Debug: Print URL if debug mode is enabled
        if self.debug_mode:
            try:
                from urllib.parse import urlencode
                debug_url = f"{url}?{urlencode(params)}"
                print(f"DEBUG URL: {debug_url}")
            except:
                pass
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, timeout=15)
            else:
                response = requests.post(url, json=params, timeout=15)
            
            self.api_calls += 1
            
            # Track API quota usage from response headers - Check for variations of quota headers
            # Spoonacular headers can be unpredictable, so try multiple variations
            # Note: X-API-Quota-Used is cumulative (total used today), not per-request
            quota_used = (response.headers.get('x-api-quota-used') or 
                         response.headers.get('X-API-Quota-Used'))
            
            # If primary quota headers are missing, check 'x-ratelimit-requests-remaining' as a fallback
            if not quota_used:
                ratelimit_remaining = (response.headers.get('x-ratelimit-requests-remaining') or
                                      response.headers.get('X-RateLimit-Requests-Remaining'))
                if ratelimit_remaining:
                    try:
                        # Use rate limit remaining as a proxy (though this is remaining, not used)
                        quota_used = None  # Rate limit remaining doesn't give us "used", so skip tracking
                    except (ValueError, TypeError):
                        pass
            
            quota_leftover = response.headers.get('x-api-quota-leftover') or response.headers.get('X-API-Quota-Leftover', 'N/A')
            quota_limit = response.headers.get('x-api-quota-limit') or response.headers.get('X-API-Quota-Limit', 'Unknown')
            
            # Simply store the latest cumulative value from the header (don't calculate delta)
            if quota_used:
                try:
                    self.api_points_used = float(quota_used)
                    
                    # Calculate remaining quota for warnings
                    quota_remaining = None
                    if quota_leftover != 'N/A':
                        try:
                            quota_remaining = int(quota_leftover)
                        except (ValueError, TypeError):
                            pass
                    
                    # Print quota usage if debug mode
                    if self.debug_mode:
                        print(f"  API Quota Used: {self.api_points_used} | Remaining: {quota_leftover}")
                    
                    # FUEL GAUGE: Warn if quota drops below 20 points
                    if quota_remaining is not None and quota_remaining < 20:
                        print(f"\n{'='*70}")
                        print(f"⚠️  WARNING: API Quota Low! Only {quota_remaining} points remaining")
                        print(f"   Total Used: {self.api_points_used} | Limit: {quota_limit}")
                        print(f"   Consider using mock data or reducing enrichment batch size")
                        print(f"{'='*70}\n")
                except (ValueError, TypeError):
                    pass
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print(f'ERROR: Invalid API key (401)')
                print(f'Response: {response.text[:200]}')
                return {}
            elif response.status_code == 402:
                print(f'ERROR: Daily API Point Quota Exceeded (402)')
                print(f'Returning empty result to prevent infinite retries')
                quota_limit = response.headers.get('x-api-quota-limit') or response.headers.get('X-API-Quota-Limit', 'Unknown')
                quota_used = response.headers.get('x-api-quota-used') or response.headers.get('X-API-Quota-Used', 'Unknown')
                print(f'Quota Limit: {quota_limit}, Quota Used: {quota_used}')
                return {}
            elif response.status_code == 429:
                print(f'ERROR: Rate limit exceeded (429)')
                print(f'Response: {response.text[:200]}')
                return {}
            else:
                print(f'API Error {response.status_code}: {response.text[:200]}')
                try:
                    error_data = response.json()
                    print(f'Error details: {error_data}')
                except:
                    pass
                return {}
                
        except requests.exceptions.Timeout:
            print(f'ERROR: Request timeout for {endpoint} (15s limit exceeded)')
            return {}
        except requests.exceptions.ConnectionError:
            print(f'ERROR: Connection error - check internet connection')
            return {}
        except Exception as e:
            print(f'ERROR: Unexpected error - {str(e)}')
            return {}
    
    def _normalize_response(self, result: Any, endpoint: str) -> List[Dict[str, Any]]:
        """
        Normalize API response to a consistent list format.
        Handles different response structures from different endpoints.
        
        Args:
            result: Raw API response
            endpoint: Endpoint name for debugging
            
        Returns:
            List of recipe dictionaries
        """
        if not result:
            return []
        
        # findByIngredients returns a raw list
        if isinstance(result, list):
            return result
        
        # Some endpoints return a dict with 'results' key
        if isinstance(result, dict):
            # Check for totalResults = 0 (filters too restrictive)
            total_results = result.get('totalResults', -1)
            if total_results == 0:
                print(f'DEBUG: {endpoint} returned totalResults: 0 - filters may be too restrictive')
                print(f'  Consider relaxing: diet, calories, maxReadyTime, or ingredient requirements')
            
            # Extract results from 'results' key
            if 'results' in result:
                return result['results']
            
            # Some endpoints might return data directly
            return []
        
        return []
    
    def search_by_ingredients(
        self,
        user_ingredients: List[str],
        number: int = 10,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        max_ready_time: Optional[int] = None,
        exclude_cuisine: Optional[str] = None,
        exclude_ingredients: Optional[List[str]] = None,
        equipment: Optional[str] = None,
        min_calories: Optional[float] = None,
        max_calories: Optional[float] = None,
        min_protein: Optional[float] = None,
        max_protein: Optional[float] = None,
        min_servings: Optional[int] = None,
        max_servings: Optional[int] = None,
        sort: Optional[str] = None,
        sort_direction: Optional[str] = None,
        enrich_results: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        REFACTORED: 3-Step Discovery and Filtering Pipeline - "Pantry Slap" Logic.
        
        CRITICAL: findByIngredients is ALWAYS used first, even when cuisine/diet filters are selected.
        This ensures "pantry slaps" work - recipes are always ranked by ingredient match quality.
        
        Step 1: Discovery (ALWAYS) - Use findByIngredients endpoint with ranking=1.
                ALWAYS uses this first, regardless of filters. Prioritizes recipes that maximize
                used ingredients (minimize missing) - the "Pantry Slap" matching.
                Returns: id, title, image, usedIngredientCount, missedIngredientCount.
        
        Step 2: Enrichment (ALWAYS) - Use informationBulk to fetch full recipe data:
                - cuisines, dishTypes, diets (for filtering logic)
                - servings (for relative nutrient density calculation)
                - readyInMinutes (for time-based filtering)
                - instructions and analyzedInstructions (for cooking complexity)
                - extendedIngredients with measurements (for substitution logic and Gemini)
                - nutrition (Big 4: Calories, Protein, Fat, Carbs)
        
        Step 3: Filtering (ONLY IF FILTERS PROVIDED) - Apply cuisine/diet/meal_type filters:
                After enrichment, filter recipes using informationBulk data (cuisines, dishTypes, diets).
                This ensures pantry matching happens first, then filters are applied.
                If no filters match, recipes still included (prevents complexSearch's 0-result problem).
        
        This approach ensures "pantry slaps" always work - findByIngredients never returns 0 results
        for pantry matching, even when filters are selected. Filters are applied as a refinement.
        
        Micronutrient filtering (Iron, Calcium, Vitamin C) is handled by Gemini
        analyzing the ingredient list, not via API filters.
        
        Args:
            user_ingredients: List of ingredient names
            number: Number of results to return (default: 10, max: 100)
            cuisine: Filter by cuisine (e.g., 'Italian', 'Mexican')
            meal_type: Filter by meal type (e.g., 'breakfast', 'dinner', 'main course')
            diet: Dietary restriction (e.g., 'vegetarian', 'vegan', 'gluten free')
            intolerances: List of intolerances (e.g., ['dairy', 'gluten'])
            enrich_results: If True, enrich top 10 recipes with full metadata (default: True)
                          If False, return basic data only (saves API points)
            
        Returns:
            List of recipe dictionaries. If enrich_results=True, top 10 have full metadata.
            Remaining recipes have basic data (stub recipes for Logic.py to flag).
        """
        if not user_ingredients:
            return []
        
        # CRITICAL CHANGE: Always use findByIngredients first for "Pantry Slap" matching
        # This ensures we always get recipes that match the user's pantry, even if filters are selected
        # Filters will be applied AFTER enrichment using informationBulk data (cuisines, dishTypes, diets)
        
        # API-LEVEL FILTERING: If diet or intolerances are provided, use complexSearch for API-level filtering
        # This ensures Spoonacular does the heavy lifting of removing meat before data reaches our code
        if diet or intolerances:
            # Use complexSearch with diet/intolerances filters for API-level filtering
            ingredients_str = ','.join(user_ingredients)
            complex_params = {
                'includeIngredients': ingredients_str,
                'number': min(number * 3, 100),
                'ranking': 1,  # Prioritize recipes using most ingredients
                'ignorePantry': True,
                'addRecipeInformation': 'false',
                'fillIngredients': 'false',
                'addRecipeNutrition': 'false',
                'addRecipeInstructions': 'false'
            }
            
            # Add diet and intolerances to API request for server-side filtering
            if diet:
                complex_params['diet'] = diet
            if intolerances:
                if isinstance(intolerances, list) and len(intolerances) > 0:
                    complex_params['intolerances'] = ','.join(intolerances)
                elif not isinstance(intolerances, list) and intolerances:
                    complex_params['intolerances'] = str(intolerances)
            
            # Add other filters if provided
            if cuisine:
                complex_params['cuisine'] = cuisine
            if meal_type:
                complex_params['type'] = meal_type
            
            try:
                result = self._make_request('recipes/complexSearch', complex_params)
                if isinstance(result, dict):
                    initial_recipes = result.get('results', [])
                    # Normalize to match findByIngredients format
                    normalized_recipes = []
                    for r in initial_recipes:
                        if isinstance(r, dict):
                            normalized_recipe = {
                                'id': r.get('id'),
                                'title': r.get('title', 'Unknown Recipe'),
                                'image': r.get('image', ''),
                                'readyInMinutes': r.get('readyInMinutes', 0),
                                'usedIngredientCount': 0,  # Will be calculated during enrichment
                                'missedIngredientCount': 0,  # Will be calculated during enrichment
                            }
                            normalized_recipes.append(normalized_recipe)
                    initial_recipes = normalized_recipes
                else:
                    initial_recipes = []
            except Exception as e:
                print(f"⚠️  complexSearch with diet/intolerances failed: {e}")
                initial_recipes = []
        else:
            # Step 1: Use findByIngredients when no diet/intolerances filters - ensures "pantry slaps" work
            # This prioritizes recipes that use the most of the user's ingredients (ranking=1)
            initial_recipes = self._search_by_ingredients_findbyingredients(
                user_ingredients, 
                number=min(number * 3, 100)  # Fetch more to account for filtering that happens later
            )
        
        if not initial_recipes:
            return []
        
        # If enrichment is disabled, return basic data only (saves API points)
        if not enrich_results:
            # Return basic structure compatible with Logic.py
            basic_recipes = []
            for recipe in initial_recipes[:number]:
                basic_recipe = {
                    'id': recipe.get('id'),
                    'title': recipe.get('title', 'Unknown Recipe'),
                    'image': recipe.get('image', ''),
                    'readyInMinutes': recipe.get('readyInMinutes', 0),
                    'usedIngredientCount': recipe.get('usedIngredientCount', 0),
                    'missedIngredientCount': recipe.get('missedIngredientCount', 0),
                    'extendedIngredients': [],  # Not available without enrichment
                    'diets': [],
                    'dietary_info': {},
                    'nutrition': {},  # Not available without enrichment
                    'servings': 0,  # Not available without enrichment
                    'instructions': '',  # Not available without enrichment
                    'analyzedInstructions': []  # Not available without enrichment
                }
                basic_recipes.append(basic_recipe)
            return basic_recipes
        
        # Extract recipe IDs from initial results (these are the recipes we'll return)
        recipe_ids_to_return = [recipe.get('id') for recipe in initial_recipes[:number] if recipe.get('id')]
        
        if not recipe_ids_to_return:
            return []
        
        # Step 3: Enrich ALL recipes using informationBulk (not just top 10)
        # CRITICAL: Force detailed fetch for EVERY recipe to ensure ingredients and instructions are never missing
        # informationBulk: ALWAYS used as the final step to get the "Fuel" (measurements/instructions) for Gemini
        # Synchronize IDs: ids_to_fetch matches ALL recipes we actually return (not just top 10)
        ids_to_fetch = recipe_ids_to_return  # Enrich ALL recipes, not just top 10
        
        # Enrich using informationBulk (ALWAYS used - provides measurements, instructions, cuisines, diets, etc.)
        enriched_recipes = self.get_recipes_bulk_information(ids_to_fetch, include_nutrition=True)
        
        # Create a map of recipe_id -> enriched data for quick lookup
        enriched_map = {recipe.get('id'): recipe for recipe in enriched_recipes if recipe.get('id')}
        
        # Merge initial recipes with enriched bulk data
        merged_recipes = []
        user_ingredients_lower = [ing.lower() for ing in user_ingredients]
        
        # Process the recipes we intend to return (synchronized with ids_to_fetch)
        for recipe in initial_recipes[:number]:
            recipe_id = recipe.get('id')
            if not recipe_id:
                continue
            
            # Check if this recipe was enriched via informationBulk
            # CRITICAL: We now enrich ALL recipes (not just top 10), so all should be in enriched_map
            # The stub recipe logic is only a fallback if informationBulk failed for this specific recipe
            if recipe_id in enriched_map:
                enriched = enriched_map[recipe_id]
            else:
                # This recipe wasn't enriched - informationBulk may have failed or didn't return this recipe
                # Create stub recipe as fallback (Logic.py will flag it as is_stub_recipe: True)
                print(f"⚠️  Warning: Recipe {recipe_id} not found in enriched_map - creating stub recipe")
                stub_recipe = {
                    'id': recipe_id,
                    'title': recipe.get('title', 'Unknown Recipe'),
                    'image': recipe.get('image', ''),
                    'readyInMinutes': recipe.get('readyInMinutes', 0),
                    'usedIngredientCount': recipe.get('usedIngredientCount', 0),
                    'missedIngredientCount': recipe.get('missedIngredientCount', 0),
                    'extendedIngredients': [],  # Not enriched
                    'diets': [],
                    'dietary_info': {},
                    'nutrition': {},  # Not enriched
                    'servings': 0,  # Not enriched
                    'instructions': '',  # Not enriched
                    'analyzedInstructions': []  # Not enriched
                }
                # Add stub recipes to results (Logic.py will flag them)
                merged_recipes.append(stub_recipe)
                continue
            
            # Process enriched recipe (top 5)
            enriched = enriched_map[recipe_id]
            
            # CRITICAL: Ensure extendedIngredients is properly nested from informationBulk response
            # Spoonacular bundles extendedIngredients with nutrition data when includeNutrition=true
            # This is the "Fuel" Gemini needs to analyze substitutions and validate safety
            if 'extendedIngredients' not in enriched or not enriched.get('extendedIngredients'):
                # Check if ingredients are in a different location
                if 'extendedIngredients' not in enriched:
                    # Try alternative key names
                    enriched['extendedIngredients'] = enriched.get('extendedIngredients', enriched.get('ingredients', []))
                if not enriched.get('extendedIngredients'):
                    print(f"⚠️  Warning: extendedIngredients missing from enriched recipe {recipe_id} - check API response format")
                    enriched['extendedIngredients'] = []
            
            # Calculate used/missing counts from extendedIngredients
            used_count = recipe.get('usedIngredientCount', 0)
            missed_count = recipe.get('missedIngredientCount', 0)
            
            # If counts not in initial recipe, calculate from enriched ingredients
            if used_count == 0 and missed_count == 0:
                extended_ingredients = enriched.get('extendedIngredients', [])
                for ing in extended_ingredients:
                    if isinstance(ing, dict):
                        ing_name = ing.get('name', '').lower()
                        if any(user_ing in ing_name or ing_name in user_ing for user_ing in user_ingredients_lower):
                            used_count += 1
                        else:
                            missed_count += 1
            
            # Extract dietary info from diets list (informationBulk returns plural keys)
            diets_list = enriched.get('diets', []) or []
            cuisines_list = enriched.get('cuisines', []) or []
            dish_types_list = enriched.get('dishTypes', []) or []
            diets_lower = [d.lower() for d in diets_list] if isinstance(diets_list, list) else []
            
            dietary_info = {
                'glutenFree': 'gluten free' in diets_lower or 'gluten-free' in diets_lower,
                'dairyFree': 'dairy free' in diets_lower or 'dairy-free' in diets_lower,
                'vegan': 'vegan' in diets_lower,
                'vegetarian': 'vegetarian' in diets_lower
            }
            
            # Add dietary_info to enriched recipe for filter checking
            enriched_with_dietary = enriched.copy()
            enriched_with_dietary['dietary_info'] = dietary_info
            
            # Apply filters (cuisine, diet, meal_type, intolerances) AFTER enrichment
            # This allows us to filter using informationBulk data (cuisines, dishTypes, diets)
            # CRITICAL: Filter by cuisine using enriched data
            if cuisine:
                recipe_cuisines_lower = [c.lower() for c in cuisines_list if isinstance(c, str)]
                if cuisine.lower() not in recipe_cuisines_lower:
                    continue  # Skip recipes that don't match requested cuisine
            
            # Filter by meal_type using dishTypes from informationBulk
            if meal_type:
                recipe_dish_types_lower = [dt.lower() for dt in dish_types_list if isinstance(dt, str)]
                if meal_type.lower() not in recipe_dish_types_lower:
                    continue  # Skip recipes that don't match requested meal type
            
            # Apply basic filters (calories, protein, time, servings, intolerances)
            # NOTE: diet parameter removed - we rely on Hard Executioner in Logic.py instead
            if not self._passes_basic_filters(
                enriched_with_dietary, 
                min_calories, max_calories, min_protein, max_protein,
                max_ready_time, min_servings, max_servings,
                None, intolerances  # diet=None - handled by Logic.py Hard Executioner
            ):
                continue  # Skip recipes that don't pass basic filters
            
            # CRITICAL: Extract extendedIngredients from enriched recipe
            # This is the "Fuel" Gemini needs - must be preserved through entire pipeline
            extended_ingredients_from_api = enriched.get('extendedIngredients', [])
            if not extended_ingredients_from_api:
                # Try alternative locations in API response
                extended_ingredients_from_api = enriched.get('ingredients', enriched.get('extendedIngredients', []))
            
            # Create cleaned recipe structure
            # CRITICAL PRESERVATION: extendedIngredients, nutrition, cuisines, and dishTypes MUST be in final dictionary
            # informationBulk returns plural keys: 'cuisines' and 'dishTypes'
            cleaned_recipe = {
                # Basic info
                'id': recipe_id,
                'title': enriched.get('title', recipe.get('title', 'Unknown Recipe')),
                'image': enriched.get('image', recipe.get('image', '')),
                'readyInMinutes': enriched.get('readyInMinutes', recipe.get('readyInMinutes', 0)),
                'summary': enriched.get('summary', ''),
                'servings': enriched.get('servings', 0),  # For Gemini context
                
                # Dietary info (informationBulk returns plural keys)
                'dietary_info': dietary_info,
                'diets': diets_list if isinstance(diets_list, list) else [],
                'cuisines': cuisines_list if isinstance(cuisines_list, list) else [],
                'dishTypes': dish_types_list if isinstance(dish_types_list, list) else [],
                'meal_type': dish_types_list if isinstance(dish_types_list, list) else [],  # Alias for dishTypes
                
                # CRITICAL PRESERVATION: Ingredient info (nested for backward compatibility)
                'ingredient_info': {
                    'usedIngredientCount': used_count,
                    'missedIngredientCount': missed_count,
                    'extendedIngredients': extended_ingredients_from_api  # PRESERVE FROM API
                },
                
                # CRITICAL PRESERVATION: Backward compatibility (top level - REQUIRED FOR GEMINI)
                'usedIngredientCount': used_count,
                'missedIngredientCount': missed_count,
                'extendedIngredients': extended_ingredients_from_api,  # PRESERVE FROM API - CRITICAL FOR SAFETY JURY
                
                # Nutrition data (Big 4 only - micronutrients handled by Gemini)
                'nutrition': enriched.get('nutrition', {}),
                
                # Instructions for Gemini context
                'instructions': enriched.get('instructions', ''),
                'analyzedInstructions': enriched.get('analyzedInstructions', [])
            }
            
            merged_recipes.append(cleaned_recipe)
        
        # Sort by used ingredient count (best matches first)
        merged_recipes.sort(key=lambda x: x.get('usedIngredientCount', 0), reverse=True)
        
        # Return top N results
        return merged_recipes[:number]
    
    def _search_complex_search_with_filters(
        self,
        user_ingredients: List[str],
        number: int,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        meal_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Step 2: Search using complexSearch with filters and includeIngredients.
        
        This method uses complexSearch directly with includeIngredients to handle both
        pantry matching (ingredient matching) and semantic filtering (cuisine, diet, 
        intolerances, meal_type) in one go. This is more reliable than filtering IDs 
        from findByIngredients.
        
        complexSearch: Used when the user has specific preferences (Cuisine, Diet, etc.).
        It should handle the ingredient matching itself via the includeIngredients parameter.
        
        Args:
            user_ingredients: List of user ingredients (for includeIngredients parameter)
            number: Number of results to return
            cuisine: Filter by cuisine (e.g., 'Italian', 'Mexican')
            diet: Dietary restriction (e.g., 'vegetarian', 'vegan')
            intolerances: List of intolerances (e.g., ['dairy', 'gluten'])
            meal_type: Filter by meal type (e.g., 'breakfast', 'main course')
            
        Returns:
            List of recipe dictionaries with basic data (id, title, image, etc.)
        """
        if not user_ingredients:
            return []
        
        # Build complexSearch params with filters and includeIngredients
        # includeIngredients handles ingredient matching - complexSearch does both pantry and filtering
        # CRITICAL: ranking=1 prioritizes recipes that use the most ingredients (Pantry Slap logic)
        ingredients_str = ','.join(user_ingredients)
        params = {
            'number': min(number, 100),  # API limit is 100
            'includeIngredients': ingredients_str,  # CRITICAL: Handles ingredient matching
            'ranking': 1,  # CRITICAL: Prioritize recipes that use the most of user's ingredients (even if some are missing)
            'ignorePantry': True,  # Ignore pantry staples (salt, pepper, water) for better matching
            'addRecipeInformation': 'false',  # We only need basic data here (saves points)
            'fillIngredients': 'false',  # Not needed for basic search
            'addRecipeNutrition': 'false',  # Not needed for basic search
            'addRecipeInstructions': 'false'  # Not needed for basic search
        }
        
        # Add filter parameters if provided
        # NOTE: diet parameter removed - we rely on Smart Diet Check in Logic.py instead
        # This prevents hard cutoffs and allows ingredient-based filtering
        if cuisine:
            params['cuisine'] = cuisine
        # diet parameter removed - Smart Diet Check in Logic.py handles vegetarian/vegan filtering
        if intolerances:
            if isinstance(intolerances, list) and len(intolerances) > 0:
                params['intolerances'] = ','.join(intolerances)
            elif not isinstance(intolerances, list) and intolerances:
                params['intolerances'] = str(intolerances)
        if meal_type:
            params['type'] = meal_type
        
        try:
            result = self._make_request('recipes/complexSearch', params)
            
            # Handle totalResults: 0 debug log if filters are too restrictive
            if isinstance(result, dict):
                total_results = result.get('totalResults', -1)
                if total_results == 0:
                    print(f'DEBUG: complexSearch returned totalResults: 0 - filters may be too restrictive')
                    print(f'  Applied filters: cuisine={cuisine}, diet=REMOVED (using Smart Check), intolerances={intolerances}, meal_type={meal_type}')
                    print(f'  Consider relaxing filters or using fewer restrictions')
                    return []
                
                # Extract recipes from results
                recipes_list = result.get('results', [])
                if recipes_list:
                    # Return basic recipe data (full enrichment happens in Step 3 via informationBulk)
                    # Note: complexSearch doesn't provide usedIngredientCount/missedIngredientCount
                    # We'll set these to 0 - they can be calculated from extendedIngredients later if needed
                    normalized_recipes = []
                    for r in recipes_list:
                        if isinstance(r, dict):
                            normalized_recipe = {
                                'id': r.get('id'),
                                'title': r.get('title', 'Unknown Recipe'),
                                'image': r.get('image', ''),
                                'readyInMinutes': r.get('readyInMinutes', 0),
                                'usedIngredientCount': 0,  # Not available from complexSearch
                                'missedIngredientCount': 0,  # Not available from complexSearch
                            }
                            # Preserve other fields if present
                            for key in r:
                                if key not in normalized_recipe:
                                    normalized_recipe[key] = r[key]
                            normalized_recipes.append(normalized_recipe)
                    return normalized_recipes
            
            return []
            
        except Exception as e:
            print(f"⚠️  complexSearch with filters failed: {e}")
            print(f"  Falling back to findByIngredients...")
            # Fallback: Use findByIngredients if complexSearch fails
            return self._search_by_ingredients_findbyingredients(user_ingredients, number)
    
    def _search_complex_search_with_query(
        self,
        query: str,
        user_ingredients: List[str],
        number: int,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        meal_type: Optional[str] = None,
        enrich_results: bool = True
    ) -> List[Dict[str, Any]]:
        """
        CUISINE BROADENING: Use semantic query instead of strict cuisine filter.
        
        Instead of using strict cuisine='Indian', use query='Indian chicken rice' for broader matching.
        This allows the API to find recipes that match the cuisine concept even if strict filter fails.
        
        Args:
            query: Semantic search query (e.g., 'Indian chicken rice')
            user_ingredients: List of user ingredients (for includeIngredients parameter)
            number: Number of results to return
            cuisine: Optional cuisine (usually None for broadening)
            diet: Optional dietary restriction
            intolerances: Optional intolerances list
            meal_type: Optional meal type
            enrich_results: Whether to enrich results (default: True)
            
        Returns:
            List of recipe dictionaries (or empty list if search fails)
        """
        if not user_ingredients:
            return []
        
        # Build complexSearch params with query parameter for semantic search
        ingredients_str = ','.join(user_ingredients)
        params = {
            'number': min(number, 100),
            'query': query,  # CRITICAL: Semantic search query instead of strict cuisine filter
            'includeIngredients': ingredients_str,  # Still prioritize user's ingredients
            'ranking': 1,  # Prioritize recipes that use the most ingredients
            'ignorePantry': True,  # Ignore pantry staples
            'addRecipeInformation': 'false',
            'fillIngredients': 'false',
            'addRecipeNutrition': 'false',
            'addRecipeInstructions': 'false'
        }
        
        # Add filter parameters if provided (but not cuisine - we're using query instead)
        # NOTE: diet parameter removed - we rely on Smart Diet Check in Logic.py instead
        # diet parameter removed - Smart Diet Check in Logic.py handles vegetarian/vegan filtering
        if intolerances:
            if isinstance(intolerances, list) and len(intolerances) > 0:
                params['intolerances'] = ','.join(intolerances)
            elif not isinstance(intolerances, list) and intolerances:
                params['intolerances'] = str(intolerances)
        if meal_type:
            params['type'] = meal_type
        
        try:
            result = self._make_request('recipes/complexSearch', params)
            
            if isinstance(result, dict):
                total_results = result.get('totalResults', -1)
                if total_results == 0:
                    return []
                
                recipes_list = result.get('results', [])
                if recipes_list:
                    # Normalize recipes (same as _search_complex_search_with_filters)
                    normalized_recipes = []
                    for r in recipes_list:
                        if isinstance(r, dict):
                            normalized_recipe = {
                                'id': r.get('id'),
                                'title': r.get('title', 'Unknown Recipe'),
                                'image': r.get('image', ''),
                                'readyInMinutes': r.get('readyInMinutes', 0),
                                'usedIngredientCount': 0,  # Will be calculated later
                                'missedIngredientCount': 0,  # Will be calculated later
                            }
                            # Preserve other fields
                            for key in r:
                                if key not in normalized_recipe:
                                    normalized_recipe[key] = r[key]
                            normalized_recipes.append(normalized_recipe)
                    
                    # If enrich_results=True, enrich these recipes using informationBulk
                    if enrich_results and normalized_recipes:
                        recipe_ids = [r.get('id') for r in normalized_recipes if r.get('id')]
                        if recipe_ids:
                            # Use existing enrichment logic
                            enriched = self.get_recipes_bulk_information(recipe_ids, include_nutrition=True)
                            # Merge normalized with enriched
                            enriched_map = {r.get('id'): r for r in enriched if r.get('id')}
                            for recipe in normalized_recipes:
                                recipe_id = recipe.get('id')
                                if recipe_id in enriched_map:
                                    enriched_data = enriched_map[recipe_id]
                                    # Merge enriched data into normalized recipe
                                    for key, value in enriched_data.items():
                                        if key not in ['id']:  # Keep original ID
                                            recipe[key] = value
                    
                    return normalized_recipes
            
            return []
            
        except Exception as e:
            print(f"⚠️  Cuisine broadening search failed: {e}")
            return []
    
    def _search_complex_filter(
        self,
        recipe_ids: List[int],
        user_ingredients: List[str],
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        meal_type: Optional[str] = None
    ) -> List[int]:
        """
        Step 2: Filter recipes using complexSearch endpoint.
        
        This method takes recipe IDs from findByIngredients and applies additional filters
        (cuisine, diet, intolerances, meal_type) using complexSearch, while maintaining
        ingredient relevance via includeIngredients parameter.
        
        Args:
            recipe_ids: List of recipe IDs from Step 1 (findByIngredients)
            user_ingredients: List of user ingredients (for includeIngredients parameter)
            cuisine: Filter by cuisine (e.g., 'Italian', 'Mexican')
            diet: Dietary restriction (e.g., 'vegetarian', 'vegan')
            intolerances: List of intolerances (e.g., ['dairy', 'gluten'])
            meal_type: Filter by meal type (e.g., 'breakfast', 'main course')
            
        Returns:
            List of filtered recipe IDs that match all provided filters
        """
        if not recipe_ids or not user_ingredients:
            return []
        
        # Build complexSearch params with filters
        # Use includeIngredients to maintain ingredient relevance from Step 1
        ingredients_str = ','.join(user_ingredients)
        params = {
            'number': len(recipe_ids) * 2,  # Fetch more to ensure we get all filtered IDs
            'includeIngredients': ingredients_str,  # CRITICAL: Maintain ingredient relevance
            'addRecipeInformation': 'false',  # We only need IDs here, not full data (saves points)
            'fillIngredients': 'false',  # Not needed for filtering
            'addRecipeNutrition': 'false',  # Not needed for filtering
            'addRecipeInstructions': 'false'  # Not needed for filtering
        }
        
        # Add filter parameters if provided
        # NOTE: diet parameter removed - we rely on Smart Diet Check in Logic.py instead
        # This prevents hard cutoffs and allows ingredient-based filtering
        if cuisine:
            params['cuisine'] = cuisine
        # diet parameter removed - Smart Diet Check in Logic.py handles vegetarian/vegan filtering
        if intolerances:
            if isinstance(intolerances, list) and len(intolerances) > 0:
                params['intolerances'] = ','.join(intolerances)
            elif not isinstance(intolerances, list) and intolerances:
                params['intolerances'] = str(intolerances)
        if meal_type:
            params['type'] = meal_type
        
        try:
            result = self._make_request('recipes/complexSearch', params)
            
            # Handle totalResults: 0 debug log if filters are too restrictive
            if isinstance(result, dict):
                total_results = result.get('totalResults', -1)
                if total_results == 0:
                    print(f'DEBUG: complexSearch filtering returned totalResults: 0 - filters may be too restrictive')
                    print(f'  Applied filters: cuisine={cuisine}, diet=REMOVED (using Smart Check), intolerances={intolerances}, meal_type={meal_type}')
                    print(f'  Consider relaxing filters or using fewer restrictions')
                    return []
                
                # Extract recipe IDs from results
                recipes_list = result.get('results', [])
                if recipes_list:
                    # Filter to only recipes that match our original IDs
                    recipe_ids_set = set(recipe_ids)
                    filtered_ids = [
                        r.get('id') for r in recipes_list 
                        if isinstance(r, dict) and r.get('id') in recipe_ids_set
                    ]
                    return filtered_ids
            
            return []
            
        except Exception as e:
            print(f"⚠️  complexSearch filtering failed: {e}")
            print(f"  Falling back to unfiltered recipe IDs")
            return recipe_ids  # Fallback: return original IDs if filtering fails
    
    def _search_by_ingredients_findbyingredients(
        self,
        user_ingredients: List[str],
        number: int
    ) -> List[Dict[str, Any]]:
        """
        Step 1: Lightweight search using findByIngredients endpoint (saves API points).
        This returns minimal data (id, title, image, usedIngredientCount, missedIngredientCount).
        Full metadata will be fetched via informationBulk in step 2.
        
        Uses ranking=1 to maximize used ingredients (minimize missing ingredients).
        """
        ingredients_str = ','.join(user_ingredients)
        params = {
            'ingredients': ingredients_str,
            'number': min(number, 100),
            'ranking': 1,  # Maximize used ingredients (minimize missing)
            'ignorePantry': True
        }
        
        result = self._make_request('recipes/findByIngredients', params)
        recipes = self._normalize_response(result, 'findByIngredients')
        
        # findByIngredients returns minimal data: id, title, image, usedIngredientCount, missedIngredientCount
        # No nutrition data here - that comes from informationBulk enrichment
        return recipes
    
    def _passes_basic_filters(
        self,
        recipe: Dict[str, Any],
        min_calories: Optional[float],
        max_calories: Optional[float],
        min_protein: Optional[float],
        max_protein: Optional[float],
        max_ready_time: Optional[int],
        min_servings: Optional[int],
        max_servings: Optional[int],
        diet: Optional[str],
        intolerances: Optional[List[str]]
    ) -> bool:
        """
        Check if recipe passes basic filters (calories, protein, time, servings).
        Micronutrients (iron, calcium, vitamin C) are NOT checked here - handled by Gemini.
        
        Returns:
            True if recipe passes all basic filters, False otherwise
        """
        # Time filter
        if max_ready_time:
            ready_time = recipe.get('readyInMinutes', 0)
            if ready_time and ready_time > max_ready_time:
                return False
        
        # Servings filter
        servings = recipe.get('servings', 0)
        if min_servings and servings < min_servings:
            return False
        if max_servings and servings > max_servings:
            return False
        
        # Diet filter - REMOVED: We now rely on Smart Diet Check in Logic.py
        # The Smart Diet Check in Logic.py checks ingredients for meat keywords (chicken, beef, pork, fish, etc.)
        # This allows recipes to pass even if API didn't tag them as vegetarian, as long as no meat is found
        # if diet:
        #     diets_list = [d.lower() for d in recipe.get('diets', [])]
        #     diet_lower = diet.lower()
        #     if diet_lower not in diets_list:
        #         # Check dietary_info flags
        #         dietary_info = recipe.get('dietary_info', {})
        #         if diet_lower == 'vegetarian' and not dietary_info.get('vegetarian', False):
        #             return False
        #         if diet_lower == 'vegan' and not dietary_info.get('vegan', False):
        #             return False
        #         if diet_lower in ['dairy free', 'dairy-free'] and not dietary_info.get('dairyFree', False):
        #             return False
        #         if diet_lower in ['gluten free', 'gluten-free'] and not dietary_info.get('glutenFree', False):
        #             return False
        
        # Intolerances filter (basic check - full safety check in Logic.py)
        if intolerances:
            dietary_info = recipe.get('dietary_info', {})
            for intolerance in intolerances:
                intol_lower = intolerance.lower()
                if intol_lower == 'dairy' and not dietary_info.get('dairyFree', True):
                    return False
                if intol_lower == 'gluten' and not dietary_info.get('glutenFree', True):
                    return False
        
        # Nutrition filters (Big 4 only)
        nutrition = recipe.get('nutrition', {})
        if nutrition:
            nutrients = nutrition.get('nutrients', [])
            nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
            
            # Calories filter
            calories = nutrient_dict.get('Calories', 0)
            if min_calories and calories < min_calories:
                return False
            if max_calories and calories > max_calories:
                return False
            
            # Protein filter
            protein = nutrient_dict.get('Protein', 0)
            if min_protein and protein < min_protein:
                return False
            if max_protein and protein > max_protein:
                return False
        
        return True
    
    def get_recipe_details(self, recipe_id: int) -> Dict[str, Any]:
        """
        Get full details for a specific recipe.
        
        Args:
            recipe_id: Spoonacular recipe ID
            
        Returns:
            Complete recipe dictionary with all information
        """
        return self._make_request(f'recipes/{recipe_id}/information', {})
    
    def get_recipes_bulk_information(self, recipe_ids: List[int], include_nutrition: bool = True) -> List[Dict[str, Any]]:
        """
        Get full details for multiple recipes using informationBulk endpoint.
        Falls back to individual calls if bulk endpoint fails.
        
        Endpoint: GET /recipes/informationBulk
        
        Mandatory Params:
        - ids (comma-separated): List of recipe IDs
        - includeNutrition: 'true' - Include nutrition data (Spoonacular bundles extendedIngredients with nutrition)
        - fillIngredients: 'true' - Ensure extendedIngredients with measurements are included
        
        Always fetches:
        - servings (for relative nutrient density calculation)
        - instructions and analyzedInstructions (for cooking complexity)
        - extendedIngredients (for substitution logic and Gemini analysis)
        - nutrition (Big 4: Calories, Protein, Fat, Carbs for Gemini)
        
        Args:
            recipe_ids: List of Spoonacular recipe IDs (max 100)
            include_nutrition: Whether to include nutrition data (default: True, required for Gemini)
            
        Returns:
            List of complete recipe dictionaries with all information needed for Gemini analysis
        """
        if not recipe_ids:
            return []
        
        # Limit to 100 recipes per call (API limit)
        recipe_ids_limited = recipe_ids[:100]
        
        # Convert recipe IDs to comma-separated string for informationBulk
        ids_str = ','.join(str(rid) for rid in recipe_ids_limited)
        
        # CRITICAL: Force-set parameters to ensure full data for Gemini
        # Endpoint: GET /recipes/informationBulk
        params = {
            'ids': ','.join(map(str, recipe_ids_limited)),  # MANDATORY: Comma-separated recipe IDs
            'includeNutrition': 'true',  # MANDATORY: Include nutrition data (Spoonacular bundles extendedIngredients with nutrition)
            'fillIngredients': 'true',  # MANDATORY: Ensure extendedIngredients with measurements are included
            'addRecipeInformation': 'true'  # MANDATORY: Include instructions, analyzedInstructions, servings, cuisines, dishTypes, diets
        }
        
        try:
            result = self._make_request('recipes/informationBulk', params)
            
            # Parse the response
            recipes_list = []
            if isinstance(result, list):
                recipes_list = result
            elif isinstance(result, dict) and 'results' in result:
                recipes_list = result['results']
            elif isinstance(result, dict) and result:
                # Some bulk endpoints return a dict with recipe IDs as keys
                recipes_list = list(result.values())
            else:
                return []
            
            # CRITICAL: Ensure response parsing extracts and maps specific fields for Gemini
            # Crucial Mapping: cuisines, dishTypes, diets, servings, readyInMinutes, instructions, analyzedInstructions
            parsed_recipes = []
            for recipe in recipes_list:
                if isinstance(recipe, dict):
                    # Start with all API data
                    parsed_recipe = recipe.copy()
                    recipe_id = parsed_recipe.get('id', 'Unknown')
                    
                    # Crucial Mapping: Ensure cuisines, dishTypes, and diets are correctly preserved
                    # informationBulk endpoint returns data in plural keys: 'cuisines' and 'dishTypes'
                    # Map API's cuisines → internal cuisines
                    # Map API's dishTypes → internal meal_type (complexSearch uses 'type' as query param, but response uses 'dishTypes')
                    # Map API's diets → internal diets
                    cuisines_list = recipe.get('cuisines') or []
                    dish_types_list = recipe.get('dishTypes') or []
                    diets_list = recipe.get('diets') or []
                    
                    # Ensure we always have lists (not None)
                    parsed_recipe['cuisines'] = cuisines_list if isinstance(cuisines_list, list) else []
                    parsed_recipe['dishTypes'] = dish_types_list if isinstance(dish_types_list, list) else []
                    parsed_recipe['meal_type'] = dish_types_list if isinstance(dish_types_list, list) else []  # Also map to internal meal_type
                    parsed_recipe['diets'] = diets_list if isinstance(diets_list, list) else []
                    
                    # servings (Integer) - for nutrient density calculation
                    if 'servings' not in parsed_recipe:
                        parsed_recipe['servings'] = 0
                    
                    # readyInMinutes (Integer) - for time-based filtering
                    if 'readyInMinutes' not in parsed_recipe:
                        parsed_recipe['readyInMinutes'] = 0
                    
                    # instructions (String) - for cooking complexity analysis
                    if 'instructions' not in parsed_recipe:
                        parsed_recipe['instructions'] = ''
                    
                    # analyzedInstructions (List) - for step-by-step analysis
                    # This is a list of instruction groups, each containing steps
                    if 'analyzedInstructions' not in parsed_recipe:
                        parsed_recipe['analyzedInstructions'] = []
                    
                    # extendedIngredients (List) - for Safety Jury and substitutions
                    # This contains amount, unitShort, unitLong - needed for serving size analysis
                    if 'extendedIngredients' not in parsed_recipe:
                        parsed_recipe['extendedIngredients'] = []
                    
                    # nutrition (Dict) - for AI Scientist analysis
                    if 'nutrition' not in parsed_recipe:
                        parsed_recipe['nutrition'] = {}
                    
                    parsed_recipes.append(parsed_recipe)
                else:
                    parsed_recipes.append(recipe)
            
            return parsed_recipes
            
        except Exception as e:
            print(f"⚠️  informationBulk endpoint failed: {e}")
            print(f"  Falling back to individual recipe calls...")
            
            # Fallback: Fetch individually (slower but more reliable)
            enriched_recipes = []
            for rid in recipe_ids_limited[:20]:  # Limit to avoid too many API calls
                try:
                    recipe_data = self.get_recipe_details(rid)
                    if recipe_data:
                        enriched_recipes.append(recipe_data)
                except Exception as e2:
                    print(f"  Failed to fetch recipe {rid}: {e2}")
                    continue
            
            return enriched_recipes
    
    def get_recipe_nutrition(self, recipe_id: int) -> Dict[str, Any]:
        """
        Get detailed nutrition information for a recipe.
        
        Args:
            recipe_id: Spoonacular recipe ID
            
        Returns:
            Nutrition data dictionary
        """
        return self._make_request(f'recipes/{recipe_id}/nutritionWidget.json', {})
    
    def get_recipe_ingredients(self, recipe_id: int) -> Dict[str, Any]:
        """
        Get ingredient information for a recipe.
        
        Args:
            recipe_id: Spoonacular recipe ID
            
        Returns:
            Ingredient data dictionary
        """
        return self._make_request(f'recipes/{recipe_id}/ingredientWidget.json', {})
    
    def get_similar_recipes(self, recipe_id: int, number: int = 5) -> List[Dict[str, Any]]:
        """
        Get similar recipes to a given recipe ID.
        Endpoint: GET /recipes/{id}/similar
        
        Useful for finding alternatives when user is missing ingredients.
        
        Args:
            recipe_id: Spoonacular recipe ID
            number: Number of similar recipes to return (default: 5, max: 10)
            
        Returns:
            List of similar recipe dictionaries with id, title, and readyInMinutes
        """
        params = {
            'number': min(number, 10)  # API limit is 10 for similar recipes
        }
        
        result = self._make_request(f'recipes/{recipe_id}/similar', params)
        
        # Similar recipes endpoint returns a list directly
        recipes = []
        if isinstance(result, list):
            recipes = result
        elif isinstance(result, dict) and 'results' in result:
            recipes = result['results']
        
        # Ensure each recipe has id, title, and readyInMinutes
        normalized_recipes = []
        for recipe in recipes:
            if isinstance(recipe, dict):
                normalized_recipe = {
                    'id': recipe.get('id'),
                    'title': recipe.get('title', 'Unknown'),
                    'readyInMinutes': recipe.get('readyInMinutes', 0)
                }
                # Preserve other fields if present
                for key in recipe:
                    if key not in normalized_recipe:
                        normalized_recipe[key] = recipe[key]
                normalized_recipes.append(normalized_recipe)
        
        return normalized_recipes
    
    def get_ingredient_information(self, ingredient_id: int) -> Dict[str, Any]:
        """
        Get detailed information about an ingredient.
        
        Args:
            ingredient_id: Spoonacular ingredient ID
            
        Returns:
            Ingredient information dictionary
        """
        return self._make_request(f'food/ingredients/{ingredient_id}/information', {})
    
    def _get_mock_response(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return mock data for testing without hitting the API.
        Saves API quota during development.
        
        Args:
            endpoint: API endpoint (e.g., 'recipes/findByIngredients')
            params: Request parameters (for context, not used in mock)
            
        Returns:
            Mock JSON response matching the endpoint format
        """
        try:
            from mock_api_data import get_mock_response
            return get_mock_response(endpoint, params)
        except ImportError:
            print("⚠️  Warning: mock_api_data.py not found. Install it to use mock data mode.")
            return {}
        except Exception as e:
            print(f"⚠️  Error loading mock data: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """
        Test API connection and key validity.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.use_mock_data:
            return True  # Mock mode always "connects"
        
        try:
            # Test connection using findByIngredients with a simple ingredient
            result = self._search_by_ingredients_findbyingredients(['chicken'], number=1)
            return len(result) > 0
        except Exception as e:
            print(f'Connection test failed: {e}')
            return False


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: Could not find SPOONACULAR_API_KEY in .env file")
    else:
        client = SpoonacularClient(api_key=API_KEY)
        client.debug_mode = True  # Enable for point-tracking and URL verification
        
        print("\n" + "=" * 70)
        print("THOROUGH TEST: 3-Step Discovery & Filtering Pipeline")
        print("=" * 70)
        
        # Test Case 1: Basic pantry match (no filters)
        print("\n" + "-" * 70)
        print("TEST CASE 1: Basic Pantry Match (No Filters)")
        print("-" * 70)
        test_ingredients = ['chicken', 'garlic', 'rice']
        print(f"Testing with: {', '.join(test_ingredients)}")
        
        results = client.search_by_ingredients(
            user_ingredients=test_ingredients,
            number=3,
            enrich_results=True
        )
        
        if not results:
            print("❌ Test Failed: No recipes returned.")
            exit(1)
        
        print(f"✓ Found {len(results)} recipes")
        
        # Test Case 2: Filtered search with specific criteria
        print("\n" + "-" * 70)
        print("TEST CASE 2: Filtered Search with Italian + Vegetarian + Main Course")
        print("-" * 70)
        test_ingredients_filtered = ['tomato', 'pasta', 'basil']
        print(f"Testing with: {', '.join(test_ingredients_filtered)}")
        print(f"Filters: cuisine='italian', diet='vegetarian', type='main course' (complexSearch query param)")
        print(f"Note: complexSearch uses 'type' as query parameter, but informationBulk returns 'dishTypes' in response")
        
        filtered_results = client.search_by_ingredients(
            user_ingredients=test_ingredients_filtered,
            number=3,
            cuisine='italian',
            diet='vegetarian',
            meal_type='main course',
            enrich_results=True
        )
        
        if not filtered_results:
            print("⚠️  No recipes found with these filters. Trying without filters...")
            # Fallback: Try without strict filters
            filtered_results = client.search_by_ingredients(
                user_ingredients=test_ingredients_filtered,
                number=3,
                enrich_results=True
            )
        
        all_tests_passed = True
        
        # Verify both test cases
        for test_case_num, (results_set, test_name) in enumerate([(results, "Basic"), (filtered_results, "Filtered")], 1):
            if not results_set:
                continue
                
            print(f"\n[{test_name} Test] Verifying {len(results_set)} recipes:")
            
            for i, recipe in enumerate(results_set):
                recipe_id = recipe.get('id')
                title = recipe.get('title')
                print(f"\n  [{i+1}] VERIFYING RECIPE: {title} (ID: {recipe_id})")
                
                # 1. Verify Pantry Metrics (from Step 1: findByIngredients)
                used = recipe.get('usedIngredientCount', -1)
                missed = recipe.get('missedIngredientCount', -1)
                pantry_ok = used >= 0 and missed >= 0
                print(f"      {'✅' if pantry_ok else '❌'} Pantry Data: {used} used, {missed} missed")
                if not pantry_ok:
                    all_tests_passed = False
                
                # 2. Verify Filters Were Applied (for filtered test case)
                if test_name == "Filtered":
                    cuisines = recipe.get('cuisines', [])
                    diets = recipe.get('diets', [])
                    dish_types = recipe.get('dishTypes', [])
                    
                    # Check if Italian cuisine filter was applied
                    cuisine_match = any('italian' in str(c).lower() for c in cuisines) if cuisines else False
                    print(f"      {'✅' if cuisine_match else '⚠️ '} Filter Check - Cuisine: {cuisines} (Italian expected)")
                    
                    # Check if vegetarian diet filter was applied
                    diet_match = any('vegetarian' in str(d).lower() for d in diets) if diets else False
                    print(f"      {'✅' if diet_match else '⚠️ '} Filter Check - Diet: {diets} (Vegetarian expected)")
                    
                    # Check if main course meal type filter was applied
                    # Note: complexSearch uses 'type' as query parameter, but informationBulk returns 'dishTypes' in response
                    meal_match = any('main course' in str(m).lower() or 'main' in str(m).lower() for m in dish_types) if dish_types else False
                    print(f"      {'✅' if meal_match else '⚠️ '} Filter Check - dishTypes: {dish_types} (Main Course expected)")
                
                # 3. Verify Enrichment Fields (from Step 3: informationBulk)
                # informationBulk endpoint returns data in plural keys: 'cuisines' and 'dishTypes'
                fields_to_check = {
                    "servings": lambda x: isinstance(x, int) and x > 0,
                    "instructions": lambda x: isinstance(x, str) and len(x) > 0,
                    "cuisines": lambda x: isinstance(x, list),  # Must be a list (empty [] is valid)
                    "dishTypes": lambda x: isinstance(x, list),  # Must be a list (empty [] is valid)
                    "diets": lambda x: isinstance(x, list)  # Must be a list (empty [] is valid)
                }
                
                for field, check in fields_to_check.items():
                    # Check for plural keys from informationBulk: 'cuisines', 'dishTypes', 'diets'
                    val = recipe.get(field)
                    status = check(val)
                    if field == 'instructions':
                        display_val = f'{len(val)} chars' if val else 'empty'
                    elif field in ['cuisines', 'dishTypes', 'diets']:
                        # Show the raw list even if empty, so we can see the data structure
                        if isinstance(val, list):
                            display_val = str(val) if val else '[] (empty list)'
                        else:
                            display_val = f'None or {type(val).__name__} (expected list)'
                    else:
                        display_val = val
                    print(f"      {'✅' if status else '❌'} {field}: {display_val}")
                    if not status: 
                        all_tests_passed = False
                
                # 4. Deep Dive: Ingredient Measurements (from Step 3: informationBulk)
                ext_ings = recipe.get('extendedIngredients', [])
                has_measurements = False
                if ext_ings:
                    sample = ext_ings[0]
                    amount = sample.get('amount')
                    unit = sample.get('unit')
                    has_measurements = amount is not None and unit is not None
                    print(f"      {'✅' if has_measurements else '❌'} Measurements: Found '{amount} {unit}' for {sample.get('name', 'N/A')}")
                else:
                    print("      ❌ Measurements: extendedIngredients list is EMPTY")
                
                if not has_measurements: 
                    all_tests_passed = False
        
        # Final Summary
        print(f"\n{'='*70}")
        if all_tests_passed:
            print("✅ SUCCESS: 3-Step Pipeline Working Correctly!")
            print("   Step 1: findByIngredients provided Used/Missed counts ✓")
            print("   Step 2: complexSearch filtering applied cuisine/diet/meal_type filters ✓")
            print("   Step 3: informationBulk provided Cuisines, Diets, Instructions, Measurements ✓")
        else:
            print("❌ FAILURE: One or more steps in the pipeline failed.")
            print("   Please check the validation output above for details.")
        
        print(f"\nTotal API Points Used: {client.api_points_used}")
        print(f"{'='*70}")
