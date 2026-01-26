from typing import Dict, List, Optional

class ProgressiveFilter:
    def __init__(self):
        self.difficulty_factors = {
             'ingredient_count':{
                'easy': (1, 5),
                'medium': (6, 10),
                'hard': (11, 999)                },
             'time_estimate': {
                'easy': (1, 20),
                'medium': (21, 45),
                'hard': (46, 999)                }
         }
    def apply_progressive_filters(self, recipe: Dict, user_settings: Dict) -> Dict:
        filter_results = {}
        filter_results['difficulty'] = self._assess_difficulty(
            recipe,
            user_settings.get('max_difficulty', 'hard')
        )

        filter_results['time'] = self._check_time_limit(
            recipe,
            user_settings.get('max_time_minutes', 120)
        )

        filter_results['missing_ingredients'] = self._check_missing_limit(
            recipe.get("missedIngredientCount", 0),
            user_settings.get('max_missing_ingredients', 5)
        )
        
        # Add dietary filters
        filter_results['dietary'] = self._check_dietary_requirements(
            recipe,
            user_settings.get('dietary_requirements', []),
            user_settings.get('intolerances', [])
        )
        
        # Add nutritional filters
        filter_results['nutritional'] = self._check_nutritional_requirements(
            recipe,
            user_settings.get('nutritional_requirements', {})
        )

        all_passed = all([
            filter_results['difficulty']['passed'],
            filter_results['time']['passed'],
            filter_results['missing_ingredients']['passed'],
            filter_results['dietary']['passed'],
            filter_results['nutritional']['passed'],
        ])

        return {
            'passed': all_passed,
            'filter_results': filter_results
        }
    def _assess_difficulty(self, recipe: Dict, max_diffculty: str) -> Dict:
        total_ingredients = (recipe.get('usedIngredientCount', 0) +
                            recipe.get('missedIngredientCount', 0)
                             )
        if total_ingredients <= 5:
            level = 'easy'
        elif total_ingredients <= 10:
            level = 'medium'
        else:
            level = 'hard'
        difficulty_order = { 'easy': 1, 'medium': 2, 'hard': 3 }
        return {
            'passed': difficulty_order[level]<= difficulty_order[max_diffculty],
            'level': level,
            'max_allowed': max_diffculty,
            'ingredeient_count': total_ingredients
        }

    def _check_time_limit(self, recipe: Dict, max_time: int) -> Dict:
        ready_time = recipe.get('readyInMinutes', None)
        if ready_time is None:
            passed = True
        else: passed = ready_time <= max_time

        return {
            'passed': passed,
            'estimate': ready_time if ready_time is not None else 'unknown',
            'max_allowed': max_time,
        }


    def _check_missing_limit(self, missed_count: int, max_missing: int) -> Dict:
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
        Check if recipe meets dietary requirements (vegetarian, vegan, etc.)
        and doesn't contain intolerances.
        """
        if not dietary_requirements and not intolerances:
            return {'passed': True, 'reason': 'No dietary restrictions'}
        
        recipe_diets = [d.lower() for d in recipe.get('diets', [])]
        
        # Check ingredients for dietary classification
        ingredients_text = ' '.join([
            ing.get('name', '').lower() if isinstance(ing, dict) else str(ing).lower()
            for ing in recipe.get('extendedIngredients', [])
        ])
        
        # Meat keywords
        meat_keywords = ['chicken', 'beef', 'pork', 'fish', 'meat', 'turkey', 'lamb', 
                        'bacon', 'sausage', 'ham', 'seafood', 'shrimp', 'salmon']
        # Dairy keywords
        dairy_keywords = ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream', 
                         'heavy cream', 'whipping cream']
        # Egg keywords
        egg_keywords = ['egg', 'eggs']
        
        has_meat = any(keyword in ingredients_text for keyword in meat_keywords)
        has_dairy = any(keyword in ingredients_text for keyword in dairy_keywords)
        has_eggs = any(keyword in ingredients_text for keyword in egg_keywords)
        
        passed = True
        reasons = []
        
        # Check dietary requirements
        for requirement in dietary_requirements:
            req_lower = requirement.lower().replace('-', '_').replace(' ', '_')
            
            if req_lower == 'vegetarian':
                if has_meat:
                    passed = False
                    reasons.append('contains meat')
            
            elif req_lower == 'vegan':
                if has_meat or has_dairy or has_eggs:
                    passed = False
                    reasons.append('contains animal products')
            
            elif req_lower == 'gluten_free':
                gluten_keywords = ['flour', 'wheat', 'bread', 'pasta', 'noodles']
                if any(keyword in ingredients_text for keyword in gluten_keywords):
                    if 'gluten free' not in ' '.join(recipe_diets):
                        passed = False
                        reasons.append('may contain gluten')
            
            elif req_lower == 'dairy_free':
                if has_dairy:
                    passed = False
                    reasons.append('contains dairy')
        
        # Check intolerances
        for intolerance in intolerances:
            intol_lower = intolerance.lower()
            if intol_lower == 'dairy' and has_dairy:
                passed = False
                reasons.append('contains dairy')
            elif intol_lower == 'gluten' and 'flour' in ingredients_text:
                passed = False
                reasons.append('may contain gluten')
            elif intol_lower == 'eggs' and has_eggs:
                passed = False
                reasons.append('contains eggs')
        
        return {
            'passed': passed,
            'reason': '; '.join(reasons) if reasons else 'meets requirements',
            'requirements_checked': dietary_requirements,
            'intolerances_checked': intolerances
        }
    
    def _check_nutritional_requirements(
        self,
        recipe: Dict,
        nutritional_requirements: Dict[str, float]
    ) -> Dict:
        """
        Check if recipe meets nutritional requirements (high protein, high iron, etc.)
        
        nutritional_requirements format:
        {
            'high_protein': 20.0,  # minimum grams
            'high_iron': 3.0,      # minimum mg
            'high_calcium': 300.0, # minimum mg
            'high_vitamin_c': 60.0, # minimum mg
            'low_calorie': 300.0,   # maximum calories
            'high_fiber': 5.0       # minimum grams
        }
        """
        if not nutritional_requirements:
            return {'passed': True, 'reason': 'No nutritional requirements'}
        
        nutrition = recipe.get('nutrition', {})
        if not nutrition:
            # If no nutrition data, assume it passes (can't verify)
            return {'passed': True, 'reason': 'No nutrition data available'}
        
        nutrients = nutrition.get('nutrients', [])
        nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
        
        passed = True
        reasons = []
        checked = {}
        
        # Map requirement names to nutrient names
        nutrient_map = {
            'high_protein': 'Protein',
            'high_iron': 'Iron',
            'high_calcium': 'Calcium',
            'high_vitamin_a': 'Vitamin A',
            'high_vitamin_c': 'Vitamin C',
            'high_vitamin_d': 'Vitamin D',
            'high_vitamin_e': 'Vitamin E',
            'high_vitamin_k': 'Vitamin K',
            'high_fiber': 'Fiber',
            'high_potassium': 'Potassium',
            'low_calorie': 'Calories'
        }
        
        for req_name, threshold in nutritional_requirements.items():
            nutrient_name = nutrient_map.get(req_name)
            if not nutrient_name:
                continue
            
            actual_value = nutrient_dict.get(nutrient_name, 0)
            checked[req_name] = {
                'required': threshold,
                'actual': actual_value,
                'nutrient': nutrient_name
            }
            
            if req_name.startswith('high_'):
                if actual_value < threshold:
                    passed = False
                    reasons.append(f'{nutrient_name}: {actual_value:.1f} < {threshold:.1f}')
            elif req_name.startswith('low_'):
                if actual_value > threshold:
                    passed = False
                    reasons.append(f'{nutrient_name}: {actual_value:.1f} > {threshold:.1f}')
        
        return {
            'passed': passed,
            'reason': '; '.join(reasons) if reasons else 'meets all requirements',
            'checked': checked
        }