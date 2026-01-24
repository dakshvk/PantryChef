"""
Helper module that combines Spoonacular API (substitutes + similar recipes) 
with Gemini AI for smart substitution recommendations
"""

from typing import Dict, List, Optional
from pantry_chef_api import SpoonacularClient
from gemini_integration import GeminiSubstitution


class SmartSubstitutionHelper:
    """
    Combines Spoonacular API data (substitutes + similar recipes) 
    with Gemini AI for intelligent recommendations.
    """
    
    def __init__(self, spoonacular_client: SpoonacularClient, gemini_client: Optional[GeminiSubstitution] = None):
        """
        Initialize helper with API clients.
        
        Args:
            spoonacular_client: SpoonacularClient instance
            gemini_client: Optional GeminiSubstitution instance (if None, only uses Spoonacular)
        """
        self.spoonacular = spoonacular_client
        self.gemini = gemini_client or GeminiSubstitution()
    
    def get_complete_substitution_help(
        self,
        missing_item: str,
        recipe_title: str,
        recipe_id: Optional[int] = None,
        user_pantry_list: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Get complete substitution help by combining:
        1. Spoonacular substitutes API
        2. Spoonacular similar recipes API
        3. Gemini AI smart recommendations
        
        Args:
            missing_item: The ingredient that's missing
            recipe_title: Name of the recipe
            recipe_id: Optional recipe ID for finding similar recipes
            user_pantry_list: Optional list of user's pantry ingredients
            
        Returns:
            Dictionary with all substitution data:
            {
                'api_substitutes': {...},  # From Spoonacular
                'similar_recipes': [...],   # From Spoonacular
                'smart_recommendation': {...},  # From Gemini (if available)
                'best_option': str  # Recommended action
            }
        """
        result = {
            'api_substitutes': {},
            'similar_recipes': [],
            'smart_recommendation': {},
            'best_option': ''
        }
        
        # Step 1: Get Spoonacular substitutes
        print(f"  → Checking Spoonacular substitutes for '{missing_item}'...")
        api_substitutes = self.spoonacular.get_substitutes(missing_item)
        result['api_substitutes'] = api_substitutes
        
        # Step 2: Get similar recipes (if recipe_id provided)
        if recipe_id:
            print(f"  → Finding similar recipes to recipe #{recipe_id}...")
            similar_recipes = self.spoonacular.get_similar_recipes(recipe_id, number=5)
            result['similar_recipes'] = similar_recipes
        else:
            similar_recipes = []
        
        # Step 3: Get Gemini AI smart recommendation (combines both)
        if self.gemini.is_available() and user_pantry_list:
            print(f"  → Getting AI-powered smart recommendation...")
            smart_rec = self.gemini.get_smart_substitution(
                missing_item=missing_item,
                recipe_title=recipe_title,
                user_pantry_list=user_pantry_list,
                spoonacular_substitutes=api_substitutes,
                similar_recipes=similar_recipes
            )
            result['smart_recommendation'] = smart_rec
            
            # Determine best option
            if smart_rec.get('substitution'):
                result['best_option'] = smart_rec['substitution']
            elif api_substitutes.get('substitute'):
                result['best_option'] = api_substitutes['substitute']
            elif similar_recipes:
                result['best_option'] = f"Try similar recipe: {similar_recipes[0].get('title', '')}"
            else:
                result['best_option'] = f"Consider omitting {missing_item} or using pantry alternatives"
        else:
            # Fallback to Spoonacular only
            if api_substitutes.get('substitute'):
                result['best_option'] = api_substitutes['substitute']
            elif similar_recipes:
                result['best_option'] = f"Try similar recipe: {similar_recipes[0].get('title', '')}"
            else:
                result['best_option'] = f"Consider omitting {missing_item}"
        
        return result


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('SPOONACULAR_API_KEY')
    
    if not api_key:
        print("ERROR: SPOONACULAR_API_KEY not found")
    else:
        # Test the helper
        spoonacular = SpoonacularClient(api_key)
        gemini = GeminiSubstitution()
        helper = SmartSubstitutionHelper(spoonacular, gemini)
        
        print("Testing Smart Substitution Helper...")
        print("=" * 60)
        
        result = helper.get_complete_substitution_help(
            missing_item='basil',
            recipe_title='Pasta with Tomato Sauce',
            recipe_id=716429,  # Example recipe ID
            user_pantry_list=['oregano', 'thyme', 'parsley', 'garlic', 'olive oil']
        )
        
        print("\nResults:")
        print(f"API Substitutes: {result['api_substitutes']}")
        print(f"Similar Recipes: {len(result['similar_recipes'])} found")
        if result['smart_recommendation']:
            print(f"Smart Recommendation: {result['smart_recommendation'].get('substitution', 'N/A')}")
            print(f"Chef's Tip: {result['smart_recommendation'].get('chef_tip', 'N/A')}")
        print(f"\nBest Option: {result['best_option']}")

