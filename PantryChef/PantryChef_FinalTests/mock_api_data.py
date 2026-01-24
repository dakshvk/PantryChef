"""
Mock API Data for PantryChef Testing
Saves API quota during development by returning pre-saved JSON responses.

Usage:
    client = SpoonacularClient(api_key="dummy", use_mock_data=True)
    results = client.search_by_ingredients(['chicken', 'rice'], number=5)
"""

from typing import Dict, Any, List


def get_mock_response(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return mock data matching the endpoint format.
    
    Args:
        endpoint: API endpoint (e.g., 'recipes/findByIngredients')
        params: Request parameters (for context)
        
    Returns:
        Mock JSON response matching the endpoint format
    """
    if 'findByIngredients' in endpoint:
        return _get_mock_find_by_ingredients()
    elif 'informationBulk' in endpoint:
        return _get_mock_information_bulk()
    elif 'complexSearch' in endpoint:
        return _get_mock_complex_search()
    elif 'substitutes' in endpoint:
        return _get_mock_substitutes()
    elif 'similar' in endpoint:
        return _get_mock_similar_recipes()
    else:
        # Default: return empty result for unknown endpoints
        return {}


def _get_mock_find_by_ingredients() -> List[Dict[str, Any]]:
    """Mock response for recipes/findByIngredients endpoint."""
    return [
        {
            'id': 12345,
            'title': 'Chicken and Rice Casserole',
            'image': 'https://example.com/chicken-rice.jpg',
            'usedIngredientCount': 3,
            'missedIngredientCount': 2
        },
        {
            'id': 12346,
            'title': 'Tomato Chicken Rice Bowl',
            'image': 'https://example.com/tomato-chicken.jpg',
            'usedIngredientCount': 2,
            'missedIngredientCount': 3
        },
        {
            'id': 12347,
            'title': 'Simple Chicken Rice',
            'image': 'https://example.com/simple-chicken.jpg',
            'usedIngredientCount': 4,
            'missedIngredientCount': 1
        }
    ]


def _get_mock_information_bulk() -> List[Dict[str, Any]]:
    """Mock response for recipes/informationBulk endpoint."""
    return [
        {
            'id': 12345,
            'title': 'Chicken and Rice Casserole',
            'image': 'https://example.com/chicken-rice.jpg',
            'readyInMinutes': 45,
            'servings': 4,
            'summary': 'A delicious casserole with chicken and rice',
            'instructions': 'Step 1: Cook chicken. Step 2: Add rice. Step 3: Bake.',
            'analyzedInstructions': [
                {
                    'name': '',
                    'steps': [
                        {'number': 1, 'step': 'Cook chicken'},
                        {'number': 2, 'step': 'Add rice'},
                        {'number': 3, 'step': 'Bake for 30 minutes'}
                    ]
                }
            ],
            'extendedIngredients': [
                {'name': 'chicken', 'original': '2 lbs chicken breast'},
                {'name': 'rice', 'original': '1 cup white rice'},
                {'name': 'tomatoes', 'original': '2 tomatoes, diced'}
            ],
            'diets': ['Gluten Free'],
            'nutrition': {
                'nutrients': [
                    {'name': 'Calories', 'amount': 350.0},
                    {'name': 'Protein', 'amount': 25.0},
                    {'name': 'Fat', 'amount': 12.0},
                    {'name': 'Carbohydrates', 'amount': 45.0}
                ]
            }
        },
        {
            'id': 12346,
            'title': 'Tomato Chicken Rice Bowl',
            'image': 'https://example.com/tomato-chicken.jpg',
            'readyInMinutes': 30,
            'servings': 2,
            'summary': 'Quick and easy rice bowl',
            'instructions': 'Step 1: Cook rice. Step 2: Add chicken and tomatoes.',
            'analyzedInstructions': [
                {
                    'name': '',
                    'steps': [
                        {'number': 1, 'step': 'Cook rice'},
                        {'number': 2, 'step': 'Add chicken and tomatoes'}
                    ]
                }
            ],
            'extendedIngredients': [
                {'name': 'chicken', 'original': '1 lb chicken'},
                {'name': 'rice', 'original': '1 cup rice'},
                {'name': 'tomatoes', 'original': '3 tomatoes'}
            ],
            'diets': [],
            'nutrition': {
                'nutrients': [
                    {'name': 'Calories', 'amount': 400.0},
                    {'name': 'Protein', 'amount': 30.0},
                    {'name': 'Fat', 'amount': 15.0},
                    {'name': 'Carbohydrates', 'amount': 50.0}
                ]
            }
        }
    ]


def _get_mock_complex_search() -> Dict[str, Any]:
    """Mock response for recipes/complexSearch endpoint."""
    return {
        'results': [
            {
                'id': 12345,
                'title': 'Chicken Pasta',
                'readyInMinutes': 30,
                'image': 'https://example.com/chicken-pasta.jpg'
            }
        ],
        'totalResults': 1
    }


def _get_mock_substitutes() -> Dict[str, Any]:
    """Mock response for food/ingredients/substitutes endpoint."""
    return {
        'status': 'success',
        'substitute': 'oregano',
        'message': 'Oregano can be used as a substitute for basil',
        'alternatives': ['oregano', 'thyme', 'marjoram']
    }


def _get_mock_similar_recipes() -> List[Dict[str, Any]]:
    """Mock response for recipes/{id}/similar endpoint."""
    return [
        {
            'id': 12350,
            'title': 'Similar Recipe 1',
            'readyInMinutes': 35
        },
        {
            'id': 12351,
            'title': 'Similar Recipe 2',
            'readyInMinutes': 40
        }
    ]

