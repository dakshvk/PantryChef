import os
from dotenv import load_dotenv
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PantryChef.PC_Phase_1.Phase_1 import PantryChefPhase1
from PantryChef.PC_Phase_2.Phase2_Reasoning import ReasoningEngine
from Phase_2_Interface import UserIntent, Phase1Recipe, Phase2Recommendation

app = FastAPI(title='PantryChef API', version='1.0')

load_dotenv()
API_KEY = os.getenv('SPOONACULAR_API_KEY')

reasoning_engine = ReasoningEngine()
# Model for incoming request to recommend
class RecommendationsRequest(BaseModel):
    ingredients: List[str]
    user_intent: dict # user preferences or intent will be converted to UserIntent
    filters: Optional[dict] = None # Optional filters

class RecommendationsResponse(BaseModel):
    recommendations: List[dict] # list of recomennded recipes
    reasoning_summary: str # Summary of how recommendations were chosen
    follow_up_questions: List[dict] # follow up questions for user

@app.post("/recommend", response_model=RecommendationsResponse)
async def get_recommend(request: RecommendationsRequest):
    '''
    accepts list of ingredients and user intent,
    returns recommended recipes with reasoning
    '''
        try: # converts user intent dict to UserIntent object
        # allows phase 2 engine to understand preferences like 'tired' or 'skill level'
        user_intent = UserIntent(**request.user_intent)
        
        # Initialize Phase 1 engine
        pantry_chef = PantryChefPhase1(API_KEY)
        result = pantry_chef.search_recipes(
            user_ingredients=request.ingredients,
            user_settings=request.user_intent  # Pass dict directly, not UserIntent object
        )

        phase1_recipes: List[Phase1Recipe] = []
        for recipe in result:
            phase1_recipes.append(Phase1Recipe(
                id=recipe.get('id'),
                title=recipe.get('title'),
                smart_score=recipe.get('smart_score', 0),# from phase 1
                used_count = recipe.get('used_count', 0),
                missed_count = recipe.get('missed_count', 0),
                #total_ingredients = recipe.get('total_ingredients', 0),
                difficulty = recipe.get('difficulty', 'medium'),
                time_estimate=recipe.get('time_estimate', 30),
                #cuisine = recipe.get('cuisine', None),
               # meal_type=recipe.get('meal_type', 'main_course')
            ))

            # Phase 2 applying reasoning engine to adjust recommendations based on new given user intent
            recommendations = reasoning_engine.process_recommendations(
                phase1_recipes, user_intent
            )

            # Convert recommendations to dict format
            rec_dicts = []
            for rec in recommendations:
                rec_dict = {
                    'recipe': {
                        'id': rec.recipe.id,
                        'title': rec.recipe.title,
                        'smart_score': rec.recipe.smart_score,
                        'used_count': rec.recipe.used_count,
                        'missed_count': rec.recipe.missed_count,
                        'difficulty': rec.recipe.difficulty,
                        'time_estimate': rec.recipe.time_estimate
                    },
                    'match_confidence': rec.match_confidence
                }
                rec_dicts.append(rec_dict)
            
            return RecommendationsResponse(
                recommendations=rec_dicts,
                reasoning_summary=f'Analyzed {len(recommendations)} recipes based on your preferences',
                follow_up_questions=[]  # Can be implemented later
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get('/health')
async def health_check():
    #just checks if server is running
    return {'status': 'healthy'}