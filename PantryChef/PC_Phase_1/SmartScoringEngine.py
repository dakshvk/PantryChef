from typing import Dict, Tuple

class SmartScoringEngine:
    USER_PROFILES = {
        'minimal_shopper':{
            'name': 'I hate shopping',
            'description': 'Prefer recipes with very few missing ingredients',
            'weights': {'used': 0.3, 'missing': 0.7}
        },

        'pantry_cleaner': {
            'name': 'Use my pantry ',
            'description': 'Priortize recipes using what I already have',
            'weights': {'used': 0.7, 'missing': 0.3}
        },

        'balanced': {
            'name': 'Balanced approach',
            'description': 'Balance pantry usage and shopping',
            'weights': {'used': 0.5, 'missing': 0.5}
        }
    }

    def calculate_smart_score(self,
                        recipe_data: Dict,
                        user_profile: str = 'balanced') -> Dict:
        # calculates smart scor 0-100
        # used score which is just percent ingredients user already has
        # missing score which percent you do not need to shop for

        used_count = recipe_data.get('usedIngredientCount', 0)
        missed_count = recipe_data.get('missedIngredientCount', 0)
        total_ingredients = used_count + missed_count
        if total_ingredients == 0:
            return {
                'smart_score': 0,
                'used_score': 0,
                'missed_score': 0,
                'breakdown': 'No ingredient data'
            }
        # calculates percentages of ingredients user already has and is missing
        used_percent = (used_count/ total_ingredients) * 100
        missed_percent = (missed_count/ total_ingredients) * 100
        profile = self.USER_PROFILES.get(user_profile, self.USER_PROFILES['balanced'])
        # if given profile doesn't exist default to balanced
        weights = profile['weights']
        #extracts the weight values from chosen profile
        used_component =  (weights['used'] * used_percent)
        missed_component = weights['missing'] *(100-missed_percent)
        smart_score = used_component + missed_component
#calculates weighted components for missing and used ingredients and then adds them to get the final smart score
        # returns all scoring details in dictionary so app can read easily
        return {
            'smart_score': round(smart_score, 1), #% of ingreidents user alr has
            'used_score': round(used_percent, 1), #% of ingreidents user does not need to buy
            'missing_score': round(100- missed_percent, 1),
            'breakdown': self._get_score_beakdown(used_percent, missed_percent, weights),
            'profile_used': profile['name'],
            'weights': weights

        }
#helper function to smooth out the calculations
    def _get_score_beakdown(self, used_percent: float, missed_percent: float, weights: Dict) -> str:
       used_comp = round(weights['used'] * used_percent, 1)
       missing_comp = round(weights['missing'] * (100 - missed_percent), 1)

    #string explaining the math
       return (
           f"({weights['used']}×{used_percent:.1f}%) + "
           f"({weights['missing']}×{100 - missed_percent:.1f}%) = "
           f"{used_comp} + {missing_comp}"
       )