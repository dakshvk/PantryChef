from typing import List
from PantryChef.PantryChef_FinalTests.backend.pantry_chef_api import SpoonacularClient
from PantryChef.PC_Phase_1.SmartScoringEngine import SmartScoringEngine
from PantryChef.PC_Phase_1.filters import ProgressiveFilter


class PantryChefPhase1:
    def __init__(self, api_key: str):
        self.data_client = SpoonacularClient(api_key)
        self.scoring_engine = SmartScoringEngine()
        self.filter_system = ProgressiveFilter()

        self.default_settings = {
            'user_profile': 'balanced',
            'max_difficulty': 'hard',
            'max_time_minutes': None,
            'max_missing_ingredients': None,
            'cuisine_filter': None,
            'meal_type_filter': None

        }

    def search_recipes(
            self,
            user_ingredients: List[str],
            user_settings: dict = None) -> List[dict]:

       #Gives defualt settings with user_settings which overrides default if given
        settings = {**self.default_settings, **(user_settings or {})}
        print('Phase 1 SEARCH STARTED')
        print(f'Ingredients: {','.join(user_ingredients)}')
        print(f'Profile: {settings["user_profile"]}')
        print('-'*50)

        raw_recipes = self.data_client.search_by_ingredients(
            user_ingredients=user_ingredients,
            number=settings.get('num_results', 100),
            cuisine=settings.get('cuisine_filter'),
            meal_type=settings.get('meal_type_filter')
        )

        print(f'Received {len(raw_recipes)} recipes')
        processed_recipes = []

        for recipe in raw_recipes:
            filter_result = self.filter_system.apply_progressive_filters(
                recipe,
                settings
            )
            if not filter_result['passed']:
                continue
            scoring = self.scoring_engine.calculate_smart_score(
                recipe,
                settings['user_profile']
            )

            #recipe_id = recipe['id']
            #full_info = self.data_client.get_recipe_information(recipe_id)

            processed_recipes.append({
                **recipe,
                'phase1_enhanced': True,
                'smart_score': scoring['smart_score'],
                'score_breakdown': scoring['breakdown'],
                'profile_used': scoring['profile_used'],

                'difficulty': filter_result['filter_results']['difficulty']['level'],
                'time_estimate': filter_result['filter_results']['time']['estimate'],

                'used_count': recipe.get('usedIngredientCount', 0),
                'missed_count': recipe.get('missedIngredientCount', 0),
                'total_ingredients': (
                    recipe.get('usedIngredientCount', 0) +
                    recipe.get('missedIngredientCount', 0)),
                #'readyInMinutes': full_info.get('readyInMinutes'),
                #'cuisine': full_info.get('cuisines', []),
                #'meal_type': full_info.get('dishTypes', []),
                #'instructions': full_info.get('instructions'),

            })

        print(f'Processed {len(processed_recipes)} recipes')
        #Filter + Score
    # Sort by Smart score
        processed_recipes.sort(
            key= lambda r: r['smart_score'],
            reverse = True
        )

        top_results = processed_recipes[:10]

        print(f'Returning top {len(top_results)} recipes')
        print('=' * 50)

        return top_results