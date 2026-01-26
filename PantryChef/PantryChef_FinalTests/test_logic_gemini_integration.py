"""
Test Logic → Gemini Integration
Verifies that Logic.py correctly processes recipes and passes the right data to Gemini.
This test ensures the handshake between Logic engine and Gemini AI works correctly.
"""

import os
import unittest
from dotenv import load_dotenv
from PantryChef.PantryChef_FinalTests.backend.Logic import PantryChefEngine
from PantryChef.PantryChef_FinalTests.backend.gemini_integration import GeminiSubstitution

load_dotenv()


class TestLogicGeminiIntegration(unittest.TestCase):
    """Test that Logic.py output is correctly formatted for Gemini integration."""
    
    def setUp(self):
        """Set up test fixtures with enriched data structure."""
        self.default_settings = {
            'user_profile': 'balanced',
            'mood': 'tired',
            'max_difficulty': 'medium',
            'max_time_minutes': 30,
            'max_missing_ingredients': 2,
            'dietary_requirements': [],
            'intolerances': [],
            'nutritional_requirements': {},
            'skill_level': 50,
            'max_time': 30
        }
        
        # Initialize Gemini (if available)
        self.gemini = GeminiSubstitution()
        self.gemini_available = self.gemini.is_available()
    
    def _create_enriched_mock_recipe(self, **kwargs):
        """Helper to create enriched mock recipes with all required fields."""
        defaults = {
            'id': 12345,
            'title': 'Test Recipe',
            'image': 'test.jpg',
            'readyInMinutes': 25,
            'servings': 2,  # Enriched field
            'summary': 'A test recipe',
            'usedIngredientCount': 5,
            'missedIngredientCount': 2,
            'extendedIngredients': [
                {'name': 'chicken', 'amount': 200, 'unit': 'g', 'original': '200g chicken'},
                {'name': 'rice', 'amount': 100, 'unit': 'g', 'original': '100g rice'}
            ],
            'instructions': 'Step 1: Cook chicken. Step 2: Add rice.',  # Enriched field
            'analyzedInstructions': [  # Enriched field
                {
                    'name': '',
                    'steps': [
                        {'number': 1, 'step': 'Cook chicken'},
                        {'number': 2, 'step': 'Add rice'}
                    ]
                }
            ],
            'diets': [],
            'dietary_info': {},
            'nutrition': {
                'nutrients': [
                    {'name': 'Protein', 'amount': 25.0},
                    {'name': 'Calories', 'amount': 350.0},
                    {'name': 'Fat', 'amount': 12.0},
                    {'name': 'Carbohydrates', 'amount': 45.0}
                ]
            }
        }
        defaults.update(kwargs)
        return defaults
    
    def test_logic_output_structure_for_gemini(self):
        """Test that Logic.py output has the structure Gemini expects."""
        engine = PantryChefEngine(self.default_settings)
        
        # Create a mock recipe with ENRICHED data (as Logic would receive from refactored API)
        mock_recipe = {
            'id': 12345,
            'title': 'Chicken Stir Fry',
            'image': 'test.jpg',
            'readyInMinutes': 25,
            'servings': 2,  # Enriched field
            'summary': 'A quick stir fry',
            'usedIngredientCount': 5,
            'missedIngredientCount': 2,
            'extendedIngredients': [
                {'name': 'chicken', 'amount': 200, 'unit': 'g', 'original': '200g chicken breast'},
                {'name': 'rice', 'amount': 100, 'unit': 'g', 'original': '100g white rice'},
                {'name': 'soy sauce', 'amount': 2, 'unit': 'tbsp', 'original': '2 tbsp soy sauce'},
                {'name': 'garlic', 'amount': 2, 'unit': 'cloves', 'original': '2 cloves garlic'},
                {'name': 'onion', 'amount': 1, 'unit': 'medium', 'original': '1 medium onion'},
                {'name': 'ginger', 'amount': 1, 'unit': 'tsp', 'original': '1 tsp ginger'},  # Missing
                {'name': 'cilantro', 'amount': 10, 'unit': 'g', 'original': '10g cilantro'}  # Missing
            ],
            'instructions': 'Step 1: Heat oil in pan. Step 2: Cook chicken. Step 3: Add vegetables and rice.',  # Enriched field
            'analyzedInstructions': [  # Enriched field - for Gemini to read
                {
                    'name': '',
                    'steps': [
                        {'number': 1, 'step': 'Heat oil in a large pan over medium heat'},
                        {'number': 2, 'step': 'Cook chicken until golden brown, about 5 minutes'},
                        {'number': 3, 'step': 'Add vegetables and rice, stir fry for 3 minutes'}
                    ]
                }
            ],
            'diets': [],
            'dietary_info': {},
            'nutrition': {
                'nutrients': [
                    {'name': 'Protein', 'amount': 25.0},
                    {'name': 'Calories', 'amount': 350.0},
                    {'name': 'Fat', 'amount': 12.0},
                    {'name': 'Carbohydrates', 'amount': 45.0},
                    {'name': 'Iron', 'amount': 3.5}  # Micronutrient - Gemini will analyze
                ]
            }
        }
        
        # Process through Logic engine
        results = engine.process_results([mock_recipe])
        
        # Verify Logic output structure
        self.assertEqual(len(results), 1, "Logic should return 1 recipe")
        recipe = results[0]
        
        # Check that extendedIngredients are preserved (needed for Gemini substitution)
        self.assertIn('extendedIngredients', recipe, 
                     "Logic must preserve extendedIngredients for Gemini")
        self.assertEqual(len(recipe['extendedIngredients']), 7,
                        "All ingredients should be preserved")
        
        # Check that nutrition data is preserved (needed for Gemini nutritional analysis)
        self.assertIn('nutrition', recipe, 
                     "Logic must preserve nutrition data for Gemini")
        
        # Check that metadata exists (where technical data lives)
        self.assertIn('_metadata', recipe,
                     "Logic must include _metadata for technical data")
        
        # Check that confidence score exists (Gemini uses this for pitches)
        self.assertIn('confidence', recipe,
                     "Logic must include confidence score for Gemini")
        self.assertIsInstance(recipe['confidence'], (int, float),
                             "Confidence should be numeric")
        
        # Check that reasoning text exists (Gemini may reference this)
        self.assertIn('reasoning', recipe,
                     "Logic must include reasoning text")
        self.assertIsInstance(recipe['reasoning'], str,
                             "Reasoning should be a string")
        
        # Verify clean output (no technical scores at top level, except smart_score which is now top-level)
        forbidden_keys = ['internal_debug', 'penalty_score']  # smart_score is now at top level
        for key in forbidden_keys:
            self.assertNotIn(key, recipe,
                           f"Technical key '{key}' should not be at top level")
        
        # Goal 2: Verify nutrition_summary exists with raw floats (Big 4 only)
        self.assertIn('nutrition_summary', recipe,
                     "Logic must include nutrition_summary for Gemini AI analysis")
        nutrition_summary = recipe['nutrition_summary']
        self.assertIsInstance(nutrition_summary, dict,
                             "nutrition_summary should be a dictionary")
        
        # Verify Big 4 nutrients only (Calories, Protein, Fat, Carbs)
        # Micronutrients (Iron, Calcium, Vitamin C) are NOT in nutrition_summary - Gemini analyzes these semantically
        self.assertIn('protein', nutrition_summary,
                     "nutrition_summary must include protein (Big 4)")
        self.assertIn('calories', nutrition_summary,
                     "nutrition_summary must include calories (Big 4)")
        self.assertIn('fat', nutrition_summary,
                     "nutrition_summary must include fat (Big 4)")
        self.assertIn('carbs', nutrition_summary,
                     "nutrition_summary must include carbs (Big 4)")
        
        # Verify all values are floats
        for key in ['protein', 'calories', 'fat', 'carbs']:
            self.assertIsInstance(nutrition_summary[key], (int, float),
                                 f"{key} should be numeric (float/int)")
        
        # Verify enriched fields are present (for Gemini Safety Jury and Nutritional Auditor)
        self.assertIn('servings', recipe,
                     "Logic must preserve servings for Gemini to understand recipe scale")
        self.assertIn('instructions', recipe,
                     "Logic must preserve instructions for Gemini Safety Jury")
        self.assertIn('analyzedInstructions', recipe,
                     "Logic must preserve analyzedInstructions for Gemini to read step-by-step")
        self.assertIn('semantic_context', recipe,
                     "Logic must include semantic_context to guide Gemini's analysis")
        
        # Goal 1: Verify violation flags and penalty_score in metadata
        metadata = recipe.get('_metadata', {})
        self.assertIn('penalty_score', metadata,
                     "penalty_score must be in _metadata for Soft-Failure Data Preservation")
        self.assertIn('violation_flags', metadata,
                     "violation_flags must be in _metadata for Soft-Failure Data Preservation")
        self.assertIn('violations', metadata,
                     "violations list must be in _metadata")
        
        # Verify violation_flags structure (schema compliance - all 5 keys must exist)
        violation_flags = metadata.get('violation_flags', {})
        self.assertIsInstance(violation_flags, dict,
                             "violation_flags should be a dictionary")
        expected_flags = ['has_time_violation', 'has_missing_violation', 
                         'has_difficulty_violation', 'has_dietary_violation', 
                         'has_nutritional_violation']  # Schema compliance: all 5 keys required
        for flag in expected_flags:
            self.assertIn(flag, violation_flags,
                         f"violation_flags should include {flag} (schema compliance)")
            self.assertIsInstance(violation_flags[flag], bool,
                                 f"{flag} should be a boolean")
        
        # has_nutritional_violation should be False by default (Logic engine no longer calculates it)
        # Gemini performs semantic audit even when this is False
        self.assertFalse(violation_flags.get('has_nutritional_violation', True),
                        "has_nutritional_violation should be False by default (handled by Gemini)")
    
    def test_logic_passes_missing_ingredients_to_gemini(self):
        """Test that Logic correctly identifies missing ingredients for Gemini."""
        engine = PantryChefEngine(self.default_settings)
        
        mock_recipe = {
            'id': 12345,
            'title': 'Test Recipe',
            'image': 'test.jpg',
            'readyInMinutes': 20,
            'summary': 'Test',
            'usedIngredientCount': 3,
            'missedIngredientCount': 2,
            'extendedIngredients': [
                {'name': 'chicken'},
                {'name': 'rice'},
                {'name': 'soy sauce'},
                {'name': 'ginger'},  # Missing
                {'name': 'cilantro'}  # Missing
            ],
            'diets': [],
            'dietary_info': {},
            'nutrition': {}
        }
        
        results = engine.process_results([mock_recipe])
        recipe = results[0]
        
        # Verify missing ingredients can be extracted for Gemini
        extended_ingredients = recipe.get('extendedIngredients', [])
        used_count = recipe.get('used_ingredients', 0)
        missing_count = recipe.get('missing_ingredients', 0)
        
        # Logic should preserve enough info for Gemini to identify missing items
        self.assertGreater(len(extended_ingredients), used_count,
                          "Should have more total ingredients than used")
        self.assertEqual(missing_count, 2,
                        "Should correctly identify 2 missing ingredients")
        
        # Missing ingredients should be extractable from extendedIngredients
        if len(extended_ingredients) > used_count:
            missing_items = extended_ingredients[used_count:]
            self.assertEqual(len(missing_items), 2,
                           "Can extract 2 missing ingredients for Gemini")
    
    def test_logic_confidence_scores_for_gemini_pitch(self):
        """Test that Logic confidence scores are appropriate for Gemini pitch generation."""
        engine = PantryChefEngine(self.default_settings)
        
        # Recipe that slightly exceeds time limit (should get penalty but survive)
        recipe_over_time = {
            'id': 1,
            'title': 'Slow Recipe',
            'readyInMinutes': 35,  # Exceeds 30 min limit
            'usedIngredientCount': 5,
            'missedIngredientCount': 1,
            'extendedIngredients': [],
            'diets': [],
            'dietary_info': {},
            'nutrition': {}
        }
        
        # Recipe within limits (perfect match)
        recipe_perfect = {
            'id': 2,
            'title': 'Perfect Recipe',
            'readyInMinutes': 15,  # Within limit
            'usedIngredientCount': 5,
            'missedIngredientCount': 0,
            'extendedIngredients': [],
            'diets': [],
            'dietary_info': {},
            'nutrition': {}
        }
        
        results = engine.process_results([recipe_over_time, recipe_perfect])
        
        # Both should survive (soft filter)
        self.assertEqual(len(results), 2, "Both recipes should survive processing")
        
        # Perfect recipe should have higher confidence
        perfect_recipe = next(r for r in results if r['id'] == 2)
        over_time_recipe = next(r for r in results if r['id'] == 1)
        
        self.assertGreater(perfect_recipe['confidence'], over_time_recipe['confidence'],
                          "Perfect match should have higher confidence than penalized recipe")
        
        # Both should have confidence scores (for Gemini to use)
        self.assertGreater(perfect_recipe['confidence'], 0,
                          "Perfect recipe should have positive confidence")
        self.assertGreater(over_time_recipe['confidence'], 0,
                          "Penalized recipe should still have positive confidence (soft filter)")
        
        # Goal 1: Verify violation flags for over-time recipe
        over_time_metadata = over_time_recipe.get('_metadata', {})
        violation_flags = over_time_metadata.get('violation_flags', {})
        self.assertTrue(violation_flags.get('has_time_violation', False),
                       "Over-time recipe should have has_time_violation flag")
        self.assertGreater(over_time_metadata.get('penalty_score', 0), 0,
                          "Over-time recipe should have penalty_score > 0")
        
        # Perfect recipe should have no violations
        perfect_metadata = perfect_recipe.get('_metadata', {})
        perfect_violation_flags = perfect_metadata.get('violation_flags', {})
        self.assertFalse(perfect_violation_flags.get('has_time_violation', False),
                        "Perfect recipe should not have time violation flag")
    
    def test_logic_nutritional_data_for_gemini_analysis(self):
        """Test that Logic preserves nutritional data in format Gemini can analyze."""
        engine = PantryChefEngine(self.default_settings)
        
        mock_recipe = {
            'id': 12345,
            'title': 'High Protein Meal',
            'readyInMinutes': 20,
            'usedIngredientCount': 5,
            'missedIngredientCount': 1,
            'extendedIngredients': [
                {'name': 'chicken', 'amount': 200, 'unit': 'g'},
                {'name': 'rice', 'amount': 100, 'unit': 'g'}
            ],
            'diets': [],
            'dietary_info': {},
            'nutrition': {
                'nutrients': [
                    {'name': 'Protein', 'amount': 35.0},
                    {'name': 'Iron', 'amount': 4.2},
                    {'name': 'Calories', 'amount': 450.0}
                ]
            }
        }
        
        results = engine.process_results([mock_recipe])
        recipe = results[0]
        
        # Goal 2: Verify nutrition_summary with raw floats (standardized schema)
        self.assertIn('nutrition_summary', recipe,
                     "nutrition_summary must exist for Gemini AI analysis")
        nutrition_summary = recipe['nutrition_summary']
        
        # Verify raw float values
        self.assertEqual(nutrition_summary.get('protein'), 35.0,
                        "Protein should match nutrition data (35.0g)")
        self.assertEqual(nutrition_summary.get('calories'), 450.0,
                        "Calories should match nutrition data (450.0)")
        self.assertIsInstance(nutrition_summary.get('fat'), (int, float),
                             "Fat should be numeric")
        self.assertIsInstance(nutrition_summary.get('carbs'), (int, float),
                             "Carbs should be numeric")
        
        # Verify nutrition data is also preserved (for detailed analysis)
        self.assertIn('nutrition', recipe, "Nutrition data must be preserved")
        nutrients = recipe['nutrition'].get('nutrients', [])
        
        # Should have nutrient data for Gemini to analyze
        self.assertGreater(len(nutrients), 0, "Should have nutrient data")
        
        # Check that specific nutrients are accessible
        nutrient_names = [n.get('name') for n in nutrients]
        self.assertIn('Protein', nutrient_names,
                     "Protein data should be available for Gemini analysis")
        
        # Verify extendedIngredients have amounts (needed for Gemini nutritional science)
        extended = recipe.get('extendedIngredients', [])
        if extended:
            first_ing = extended[0]
            self.assertIn('name', first_ing,
                         "Ingredients should have names for Gemini")
            # Amount and unit are helpful but not always present
            if 'amount' in first_ing:
                self.assertIsInstance(first_ing['amount'], (int, float),
                                     "Amount should be numeric if present")
    
    @unittest.skipUnless(
        os.getenv('GEMINI_API_KEY'),
        "GEMINI_API_KEY not set - skipping Gemini integration test"
    )
    def test_logic_to_gemini_handshake(self):
        """End-to-end test: Logic output → Gemini input (requires Gemini API key)."""
        if not self.gemini_available:
            self.skipTest("Gemini AI not available")
        
        engine = PantryChefEngine(self.default_settings)
        
        # Create a realistic recipe with ENRICHED data
        mock_recipe = {
            'id': 12345,
            'title': 'Chicken and Rice Bowl',
            'readyInMinutes': 25,
            'servings': 2,  # Enriched field
            'summary': 'A quick and healthy meal',
            'usedIngredientCount': 4,
            'missedIngredientCount': 1,
            'extendedIngredients': [
                {'name': 'chicken', 'amount': 200, 'unit': 'g', 'original': '200g chicken breast'},
                {'name': 'rice', 'amount': 150, 'unit': 'g', 'original': '150g white rice'},
                {'name': 'soy sauce', 'amount': 2, 'unit': 'tbsp', 'original': '2 tbsp soy sauce'},
                {'name': 'garlic', 'amount': 2, 'unit': 'cloves', 'original': '2 cloves garlic'},
                {'name': 'ginger', 'amount': 1, 'unit': 'tsp', 'original': '1 tsp ginger'}  # Missing
            ],
            'instructions': 'Step 1: Cook rice. Step 2: Season chicken. Step 3: Combine and serve.',  # Enriched
            'analyzedInstructions': [  # Enriched - for Gemini to read
                {
                    'name': '',
                    'steps': [
                        {'number': 1, 'step': 'Cook rice according to package instructions'},
                        {'number': 2, 'step': 'Season chicken with soy sauce and garlic'},
                        {'number': 3, 'step': 'Combine chicken and rice, serve hot'}
                    ]
                }
            ],
            'diets': [],
            'dietary_info': {},
            'nutrition': {
                'nutrients': [
                    {'name': 'Protein', 'amount': 28.0},
                    {'name': 'Calories', 'amount': 380.0},
                    {'name': 'Fat', 'amount': 15.0},
                    {'name': 'Carbohydrates', 'amount': 50.0}
                ]
            }
        }
        
        # Process through Logic
        results = engine.process_results([mock_recipe])
        self.assertEqual(len(results), 1)
        logic_output = results[0]
        
        # Goal 3: Verify standardized schema compliance
        required_top_level = ['title', 'time', 'confidence', 'smart_score', 
                             'used_ingredients', 'missing_ingredients', 
                             'extendedIngredients', 'nutrition', 'nutrition_summary', '_metadata']
        for key in required_top_level:
            self.assertIn(key, logic_output,
                         f"Standardized schema must include '{key}' at top level")
        
        # Verify nutrition_summary structure
        self.assertIsInstance(logic_output['nutrition_summary'], dict,
                             "nutrition_summary must be a dictionary")
        self.assertIn('protein', logic_output['nutrition_summary'])
        self.assertIn('calories', logic_output['nutrition_summary'])
        self.assertIn('fat', logic_output['nutrition_summary'])
        self.assertIn('carbs', logic_output['nutrition_summary'])
        
        # Verify _metadata structure
        metadata = logic_output.get('_metadata', {})
        self.assertIn('penalty_score', metadata)
        self.assertIn('violation_flags', metadata)
        self.assertIn('violations', metadata)
        
        # Test Gemini can use Logic output for pitch generation
        try:
            pitch_result = self.gemini.generate_recommendation_pitch(
                recommendations=[logic_output],
                user_mood=self.default_settings['mood']
            )
            
            # Verify Gemini returned a pitch
            self.assertIn('pitch_text', pitch_result,
                         "Gemini should return pitch_text")
            self.assertIsInstance(pitch_result['pitch_text'], str,
                                 "Pitch should be a string")
            self.assertGreater(len(pitch_result['pitch_text']), 0,
                              "Pitch should not be empty")
            
            # Test Gemini can use nutrition_summary for nutritional analysis
            analysis_result = self.gemini.analyze_nutritional_science(
                recipe_data=logic_output,
                target_nutrient='Protein'
            )
            
            # Verify Gemini returned analysis
            self.assertIn('scientific_rationale', analysis_result,
                         "Gemini should return scientific_rationale")
            self.assertIn('is_dense', analysis_result,
                         "Gemini should return is_dense boolean")
            self.assertIsInstance(analysis_result['is_dense'], bool,
                                 "is_dense should be boolean")
            
        except Exception as e:
            self.fail(f"Gemini failed to process Logic output: {e}")
    
    def test_standardized_schema_compliance(self):
        """Test that Logic output follows the standardized AI-Input Schema."""
        engine = PantryChefEngine(self.default_settings)
        
        mock_recipe = {
            'id': 9999,
            'title': 'Schema Test Recipe',
            'readyInMinutes': 30,
            'usedIngredientCount': 4,
            'missedIngredientCount': 1,
            'extendedIngredients': [
                {'name': 'chicken', 'amount': 200, 'unit': 'g'},
                {'name': 'rice', 'amount': 100, 'unit': 'g'},
                {'name': 'soy sauce', 'amount': 2, 'unit': 'tbsp'},
                {'name': 'garlic', 'amount': 2, 'unit': 'cloves'},
                {'name': 'ginger', 'amount': 1, 'unit': 'tsp'}  # Missing
            ],
            'diets': [],
            'dietary_info': {},
            'nutrition': {
                'nutrients': [
                    {'name': 'Protein', 'amount': 28.0},
                    {'name': 'Calories', 'amount': 380.0},
                    {'name': 'Fat', 'amount': 12.0},
                    {'name': 'Carbohydrates', 'amount': 45.0}
                ]
            }
        }
        
        results = engine.process_results([mock_recipe])
        recipe = results[0]
        
        # Goal 3: Verify standardized schema
        schema_fields = {
            'title': str,
            'time': (int, float),
            'confidence': (int, float),
            'smart_score': (int, float),
            'used_ingredients': int,
            'missing_ingredients': int,
            'extendedIngredients': list,
            'nutrition': dict,
            'nutrition_summary': dict,
            '_metadata': dict
        }
        
        for field, expected_type in schema_fields.items():
            self.assertIn(field, recipe,
                         f"Standardized schema must include '{field}'")
            if isinstance(expected_type, tuple):
                self.assertIsInstance(recipe[field], expected_type,
                                    f"'{field}' should be one of {expected_type}")
            else:
                self.assertIsInstance(recipe[field], expected_type,
                                    f"'{field}' should be {expected_type}")
        
        # Verify nutrition_summary has all required keys with correct types
        nutrition_summary = recipe['nutrition_summary']
        for key in ['protein', 'calories', 'fat', 'carbs']:
            self.assertIn(key, nutrition_summary,
                         f"nutrition_summary must include '{key}'")
            self.assertIsInstance(nutrition_summary[key], (int, float),
                                f"nutrition_summary['{key}'] should be numeric")
        
        # Verify _metadata has required keys
        metadata = recipe['_metadata']
        required_metadata = ['penalty_score', 'violation_flags', 'violations', 'smart_score']
        for key in required_metadata:
            self.assertIn(key, metadata,
                         f"_metadata must include '{key}'")
        
        # Verify violation_flags structure (schema compliance - all 5 keys must exist)
        violation_flags = metadata['violation_flags']
        self.assertIsInstance(violation_flags, dict,
                             "violation_flags should be a dictionary")
        for flag_key in ['has_time_violation', 'has_missing_violation', 
                        'has_difficulty_violation', 'has_dietary_violation', 
                        'has_nutritional_violation']:  # Schema compliance: all 5 keys required
            self.assertIn(flag_key, violation_flags,
                         f"violation_flags should include '{flag_key}' (schema compliance)")
            self.assertIsInstance(violation_flags[flag_key], bool,
                                f"violation_flags['{flag_key}'] should be boolean")
        
        # has_nutritional_violation should be False by default (Logic engine no longer calculates it)
        # Gemini performs semantic audit even when this is False
        self.assertFalse(violation_flags.get('has_nutritional_violation', True),
                        "has_nutritional_violation should be False by default (handled by Gemini semantic analysis)")


if __name__ == '__main__':
    unittest.main()

