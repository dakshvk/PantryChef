"""
Spoonacular API Client
Handles all API interactions with proper error handling and parameter support
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
    
    def __init__(self, api_key: str):
        """
        Initialize API client.
        
        Args:
            api_key: Spoonacular API key
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = "https://api.spoonacular.com"
        self.api_calls = 0  # Track API usage
        
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Spoonacular API with error handling.
        
        Args:
            endpoint: API endpoint (e.g., 'recipes/complexSearch')
            params: Request parameters
            method: HTTP method (default: GET)
            
        Returns:
            JSON response as dictionary, or empty dict on error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params['apiKey'] = self.api_key
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, timeout=15)
            else:
                response = requests.post(url, json=params, timeout=15)
            
            self.api_calls += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print(f'ERROR: Invalid API key (401)')
                return {}
            elif response.status_code == 402:
                print(f'ERROR: API quota exceeded (402)')
                return {}
            elif response.status_code == 429:
                print(f'ERROR: Rate limit exceeded (429)')
                return {}
            else:
                print(f'API Error {response.status_code}: {response.text[:200]}')
                return {}
                
        except requests.exceptions.Timeout:
            print(f'ERROR: Request timeout for {endpoint}')
            return {}
        except requests.exceptions.ConnectionError:
            print(f'ERROR: Connection error - check internet connection')
            return {}
        except Exception as e:
            print(f'ERROR: Unexpected error - {str(e)}')
            return {}
    
    def search_by_ingredients(
        self,
        user_ingredients: List[str],
        number: int = 10,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        ranking: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Search recipes by ingredients using findByIngredients endpoint.
        This is the primary method for ingredient-based recipe search.
        
        Args:
            user_ingredients: List of ingredient names
            number: Number of results to return (default: 10)
            cuisine: Optional cuisine filter (e.g., 'Italian', 'Mexican')
            meal_type: Optional meal type filter (e.g., 'breakfast', 'dinner')
            ranking: Ranking mode (1=minimize missing, 2=maximize used)
            
        Returns:
            List of recipe dictionaries with used/missed ingredient info
        """
        if not user_ingredients:
            return []
        
        # Convert list to comma-separated string
        ingredients_param = ','.join(user_ingredients)
        
        params = {
            'ingredients': ingredients_param,
            'number': min(number, 100),  # API limit is 100
            'ranking': ranking,
            'ignorePantry': True  # Don't count pantry staples
        }
        
        url = f"{self.base_url}/recipes/findByIngredients"
        params['apiKey'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=15)
            self.api_calls += 1
            
            if response.status_code == 200:
                recipes = response.json()
                
                # Apply additional filters if needed (requires fetching full details)
                if cuisine or meal_type:
                    filtered_recipes = []
                    for recipe in recipes[:number]:  # Limit to avoid too many API calls
                        recipe_id = recipe.get('id')
                        if recipe_id:
                            details = self.get_recipe_details(recipe_id)
                            if details:
                                # Check cuisine filter
                                if cuisine:
                                    cuisines = [c.lower() for c in details.get('cuisines', [])]
                                    if cuisine.lower() not in cuisines:
                                        continue
                                
                                # Check meal type filter
                                if meal_type:
                                    dish_types = [dt.lower() for dt in details.get('dishTypes', [])]
                                    if meal_type.lower() not in dish_types:
                                        continue
                                
                                # Merge basic info with details
                                filtered_recipes.append({**recipe, **details})
                    return filtered_recipes[:number]
                
                return recipes if isinstance(recipes, list) else []
            else:
                print(f'API Error {response.status_code}: {response.text[:200]}')
                return []
        except Exception as e:
            print(f'Network Error: {e}')
            return []
    
    def search_recipes(
        self,
        query: Optional[str] = None,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        include_ingredients: Optional[List[str]] = None,
        exclude_ingredients: Optional[List[str]] = None,
        max_ready_time: Optional[int] = None,
        min_protein: Optional[float] = None,
        max_protein: Optional[float] = None,
        min_calories: Optional[float] = None,
        max_calories: Optional[float] = None,
        min_iron: Optional[float] = None,
        min_calcium: Optional[float] = None,
        min_vitamin_c: Optional[float] = None,
        number: int = 20,
        add_recipe_information: bool = True,
        add_recipe_nutrition: bool = True,
        fill_ingredients: bool = True
    ) -> Dict[str, Any]:
        """
        Advanced recipe search with comprehensive filtering options.
        Uses complexSearch endpoint for maximum flexibility.
        
        Args:
            query: Search query string
            cuisine: Filter by cuisine (e.g., 'Italian', 'Mexican')
            meal_type: Filter by meal type (e.g., 'breakfast', 'dinner')
            diet: Dietary restriction (e.g., 'vegetarian', 'vegan', 'gluten free')
            intolerances: List of intolerances (e.g., ['dairy', 'gluten'])
            include_ingredients: Ingredients that must be included
            exclude_ingredients: Ingredients to exclude
            max_ready_time: Maximum cooking time in minutes
            min_protein: Minimum protein in grams
            max_protein: Maximum protein in grams
            min_calories: Minimum calories
            max_calories: Maximum calories
            min_iron: Minimum iron in mg
            min_calcium: Minimum calcium in mg
            min_vitamin_c: Minimum vitamin C in mg
            number: Number of results (max 100)
            add_recipe_information: Include full recipe info
            add_recipe_nutrition: Include nutrition data
            fill_ingredients: Include ingredient details
            
        Returns:
            Dictionary with 'results' key containing recipe list
        """
        params = {
            'number': min(number, 100),
            'addRecipeInformation': add_recipe_information,
            'addRecipeNutrition': add_recipe_nutrition,
            'fillIngredients': fill_ingredients
        }
        
        # Add optional parameters
        if query:
            params['query'] = query
        if cuisine:
            params['cuisine'] = cuisine
        if meal_type:
            params['type'] = meal_type
        if diet:
            params['diet'] = diet
        if intolerances:
            params['intolerances'] = ','.join(intolerances) if isinstance(intolerances, list) else intolerances
        if include_ingredients:
            params['includeIngredients'] = ','.join(include_ingredients) if isinstance(include_ingredients, list) else include_ingredients
        if exclude_ingredients:
            params['excludeIngredients'] = ','.join(exclude_ingredients) if isinstance(exclude_ingredients, list) else exclude_ingredients
        if max_ready_time:
            params['maxReadyTime'] = max_ready_time
        if min_protein:
            params['minProtein'] = min_protein
        if max_protein:
            params['maxProtein'] = max_protein
        if min_calories:
            params['minCalories'] = min_calories
        if max_calories:
            params['maxCalories'] = max_calories
        if min_iron:
            params['minIron'] = min_iron
        if min_calcium:
            params['minCalcium'] = min_calcium
        if min_vitamin_c:
            params['minVitaminC'] = min_vitamin_c
        
        return self._make_request('recipes/complexSearch', params)
    
    def get_recipe_details(self, recipe_id: int) -> Dict[str, Any]:
        """
        Get full details for a specific recipe.
        
        Args:
            recipe_id: Spoonacular recipe ID
            
        Returns:
            Complete recipe dictionary with all information
        """
        return self._make_request(f'recipes/{recipe_id}/information', {})
    
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
    
    def get_substitutes(self, ingredient_name: str) -> Dict[str, Any]:
        """
        Get ingredient substitution suggestions.
        
        Args:
            ingredient_name: Name of ingredient to find substitutes for
            
        Returns:
            Dictionary with substitution suggestions
        """
        return self._make_request(
            'food/ingredients/substitutes',
            {'ingredientName': ingredient_name}
        )
    
    def get_ingredient_information(self, ingredient_id: int) -> Dict[str, Any]:
        """
        Get detailed information about an ingredient.
        
        Args:
            ingredient_id: Spoonacular ingredient ID
            
        Returns:
            Ingredient information dictionary
        """
        return self._make_request(f'food/ingredients/{ingredient_id}/information', {})
    
    def test_connection(self) -> bool:
        """
        Test API connection and key validity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = self.search_recipes(query="test", number=1)
            return 'results' in result or len(result) > 0
        except Exception as e:
            print(f'Connection test failed: {e}')
            return False


if __name__ == "__main__":
    # Test the API client
    if not API_KEY:
        print("ERROR: Could not find SPOONACULAR_API_KEY in .env file")
    else:
        client = SpoonacularClient(api_key=API_KEY)
        
        # Test connection
        print("Testing API connection...")
        if client.test_connection():
            print("✓ API connection successful")
        else:
            print("✗ API connection failed")
            exit(1)
        
        # Test search_by_ingredients
        print("\nTesting search_by_ingredients...")
        results = client.search_by_ingredients(
            user_ingredients=['chicken', 'rice', 'tomatoes'],
            number=3
        )
        print(f"✓ Found {len(results)} recipes")
        if results:
            print(f"  Example: {results[0].get('title', 'Unknown')}")
        
        # Test advanced search
        print("\nTesting advanced search...")
        advanced_results = client.search_recipes(
            query="pasta",
            cuisine="Italian",
            diet="vegetarian",
            max_ready_time=30,
            number=2
        )
        if 'results' in advanced_results:
            print(f"✓ Found {len(advanced_results['results'])} recipes")
        else:
            print("✗ Advanced search failed")
        
        print(f"\nTotal API calls made: {client.api_calls}")
