"""
PantryChef FastAPI - Front Desk
Receives requests from the web, hands data to the Orchestrator, and sends results back.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app_orchestrator import PantryChefOrchestrator

# 1. Initialize the App
app = FastAPI(title="PantryChef API", version="1.0.0")

# Enable CORS for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialize the Orchestrator (The Brain)
# This stays in memory so it doesn't have to reload every time
orchestrator = PantryChefOrchestrator()

# 3. Define the Request "Contract" (What the UI must send)
class RecipeRequest(BaseModel):
    ingredients: List[str]
    mood: str = "casual"
    intolerances: List[str] = []
    user_profile: str = "balanced"
    max_time_minutes: Optional[int] = None
    max_missing_ingredients: Optional[int] = None
    dietary_requirements: Optional[List[str]] = None
    number: Optional[int] = 20
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    diet: Optional[str] = None

# 4. The Main Endpoint
@app.post("/recommend")
async def get_recommendations(request: RecipeRequest):
    """
    Main endpoint for recipe recommendations.
    
    Receives ingredients and user preferences, runs the full pipeline:
    API (Spoonacular) -> Logic Engine -> Gemini AI
    
    Returns recipes with safety flags preserved (Flag, Don't Fail system).
    """
    try:
        # Build settings dictionary for the orchestrator
        settings = {
            'user_profile': request.user_profile,
            'mood': request.mood,
            'intolerances': request.intolerances,
            'max_time_minutes': request.max_time_minutes or 120,
            'max_missing_ingredients': request.max_missing_ingredients or 10,  # Increased default to 10
            'dietary_requirements': request.dietary_requirements or [],
            'skill_level': 50,  # Default skill level
            'max_time': request.max_time_minutes or 120
        }
        
        # Run the full pipeline (API -> Logic -> Gemini)
        # Orchestrator handles the "neutral" collection we built
        # CRITICAL: Orchestrator never filters recipes - all recipes with safety flags
        # (like requires_ai_validation: True) are returned so Gemini can act as Safety Jury
        results = orchestrator.run_pantry_chef(
            ingredients=request.ingredients,
            settings=settings,
            number=request.number or 20,
            cuisine=request.cuisine,
            meal_type=request.meal_type,
            diet=request.diet,
            intolerances=request.intolerances,  # Pass to API for filtering
            enrich_with_ai=True
        )
        
        if not results.get('recipes'):
            return {
                "message": "No recipes found for those ingredients.",
                "recipes": [],
                "pitch": None,
                "metadata": results.get('metadata', {})
            }
            
        return results

    except Exception as e:
        # If anything breaks in the backend, the API tells you why
        raise HTTPException(status_code=500, detail=str(e))

# 5. Ask Chef Endpoint - For ingredient substitutions
class AskChefRequest(BaseModel):
    recipe_title: str
    query: str
    ingredients: Optional[List[str]] = []

@app.post("/ask-chef")
async def ask_chef(request: AskChefRequest):
    """
    Ask Chef endpoint for ingredient substitutions.
    Receives a user query (e.g., "I don't have yogurt") and returns a substitution suggestion.
    """
    try:
        gemini = orchestrator.gemini
        if not gemini or not gemini.is_available():
            raise HTTPException(status_code=503, detail="Chef (Gemini) is not available")
        
        # Extract missing ingredient from query
        query_lower = request.query.lower()
        # Simple extraction - look for patterns like "don't have X", "missing X", "no X"
        missing_item = request.query
        if "don't have" in query_lower:
            missing_item = query_lower.split("don't have")[-1].strip()
        elif "missing" in query_lower:
            missing_item = query_lower.split("missing")[-1].strip()
        elif "no " in query_lower:
            missing_item = query_lower.split("no ")[-1].strip()
        
        # Get substitution from Gemini
        substitution_result = gemini.get_smart_substitution(
            missing_item=missing_item,
            recipe_title=request.recipe_title,
            user_pantry_list=request.ingredients or []
        )
        
        # Format response
        response_text = substitution_result.get('substitution', 'No substitution found')
        if substitution_result.get('chef_tip'):
            response_text += f"\n\n💡 Chef's Tip: {substitution_result.get('chef_tip')}"
        
        return {
            "response": response_text,
            "substitution": substitution_result.get('substitution'),
            "chef_tip": substitution_result.get('chef_tip')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error asking chef: {str(e)}")

# 6. Health Check (To see if the server is alive)
@app.get("/")
def read_root():
    """
    Health check endpoint.
    Returns API status and link to interactive docs.
    """
    return {
        "status": "PantryChef is online",
        "docs": "/docs",
        "version": "1.0.0"
    }

# 7. Additional Health Check Endpoint
@app.get("/health")
def health_check():
    """
    Detailed health check endpoint.
    Verifies that all components are initialized.
    """
    health_status = {
        "status": "healthy",
        "orchestrator": "initialized",
        "api_client": "initialized" if orchestrator.api_client else "not initialized",
        "gemini": "available" if (orchestrator.gemini and orchestrator.gemini.is_available()) else "not available"
    }
    return health_status
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

