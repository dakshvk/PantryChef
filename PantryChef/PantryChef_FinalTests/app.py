"""
PantryChef - Bold Minimalist UI with Fluid Motion
Discover Global Cuisines From Your Kitchen
"""

import streamlit as st
import os
import warnings
from dotenv import load_dotenv

# Suppress ScriptRunContext warnings
warnings.filterwarnings('ignore', message='.*ScriptRunContext.*')

# Load environment variables
load_dotenv()

# Import after load_dotenv
from PantryChef.PantryChef_FinalTests.backend.pantry_chef_api import SpoonacularClient
from PantryChef.PantryChef_FinalTests.backend.Logic import PantryChefEngine
from database import PantryChefDB
from PantryChef.PantryChef_FinalTests.backend.substitution_helper import SmartSubstitutionHelper
from PantryChef.PantryChef_FinalTests.backend.gemini_integration import GeminiSubstitution

# Page config
st.set_page_config(
    page_title="PantryChef",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bold Minimalist Design with Fluid Motion
st.markdown("""
    <style>
    /* Import Google Fonts for bold typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');
    
    /* Bold Minimalist Color Palette */
    :root {
        --primary: #2E7D32;
        --primary-light: #4CAF50;
        --accent: #66BB6A;
        --background: #FAFAFA;
        --surface: #FFFFFF;
        --text-primary: #1A1A1A;
        --text-secondary: #666666;
        --border: #E0E0E0;
        --success: #4CAF50;
        --warning: #FF9800;
    }
    
    /* Clean, minimal main background */
    .main {
        background: var(--background);
        padding: 0;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Bold Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
    }
    
    h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Clean buttons with micro-interactions */
    .stButton>button {
        border-radius: 12px !important;
        border: none !important;
        padding: 0.875rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.15) !important;
        background: var(--primary) !important;
        color: white !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 4px 16px rgba(46, 125, 50, 0.25) !important;
        background: var(--primary-light) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Minimalist recipe cards with fluid motion */
    .recipe-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid var(--border);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .recipe-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--primary);
        transform: scaleY(0);
        transition: transform 0.3s ease;
    }
    
    .recipe-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        border-color: var(--primary-light);
    }
    
    .recipe-card:hover::before {
        transform: scaleY(1);
    }
    
    /* Clean badges with subtle animations */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .badge:hover {
        transform: scale(1.05);
    }
    
    .badge-protein {
        background: rgba(46, 125, 50, 0.1);
        color: var(--primary);
        border-color: rgba(46, 125, 50, 0.2);
    }
    
    .badge-carbs {
        background: rgba(255, 193, 7, 0.1);
        color: #F57C00;
        border-color: rgba(255, 193, 7, 0.2);
    }
    
    .badge-low-cal {
        background: rgba(76, 175, 80, 0.1);
        color: var(--primary-light);
        border-color: rgba(76, 175, 80, 0.2);
    }
    
    .badge-vitamin {
        background: rgba(255, 152, 0, 0.1);
        color: #E65100;
        border-color: rgba(255, 152, 0, 0.2);
    }
    
    /* Minimalist input fields */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1) !important;
        outline: none !important;
    }
    
    .stSelectbox>div>div {
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
    }
    
    /* Clean sidebar */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    
    /* Confidence score with bold typography */
    .confidence-score {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }
    
    /* Minimalist pantry chips */
    .pantry-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s ease;
        border: 1.5px solid;
    }
    
    .chip-green {
        background: rgba(76, 175, 80, 0.1);
        color: var(--primary);
        border-color: rgba(76, 175, 80, 0.3);
    }
    
    .chip-green:hover {
        background: rgba(76, 175, 80, 0.15);
        transform: scale(1.05);
    }
    
    /* Clean expander */
    .streamlit-expanderHeader {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Hero section with bold typography */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.05) 0%, rgba(76, 175, 80, 0.02) 100%);
        border-radius: 24px;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.03em;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.25rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    /* Smooth transitions for all elements */
    * {
        transition: color 0.2s ease, background-color 0.2s ease;
    }
    
    /* Clean metrics */
    .stMetric {
        background: transparent;
        padding: 0;
    }
    
    .stMetric label {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
    
    .stMetric value {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    /* Minimalist filters section */
    .filters-section {
        background: var(--surface);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        margin-bottom: 2rem;
    }
    
    /* Clean form styling */
    .stForm {
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def init_clients():
    """Initialize API clients"""
    api_key = os.getenv('SPOONACULAR_API_KEY')
    if not api_key:
        return None, None, None, None
    
    try:
        db = PantryChefDB()
        api_client = SpoonacularClient(api_key)
        gemini = GeminiSubstitution()
        helper = SmartSubstitutionHelper(api_client, gemini)
        return db, api_client, gemini, helper
    except Exception as e:
        return None, None, None, None

def get_clients():
    """Get clients, initializing if needed"""
    return init_clients()

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'recipes' not in st.session_state:
        st.session_state.recipes = []
    if 'selected_recipe' not in st.session_state:
        st.session_state.selected_recipe = None
    if 'substitution_data' not in st.session_state:
        st.session_state.substitution_data = {}
    if 'selected_recipe_id' not in st.session_state:
        st.session_state.selected_recipe_id = None
    if 'raw_recipe_data' not in st.session_state:
        st.session_state.raw_recipe_data = {}
    if 'favorites' not in st.session_state:
        db, _, _, _ = get_clients()
        if db:
            try:
                st.session_state.favorites = db.get_favorite_recipe_ids()
            except:
                st.session_state.favorites = []
        else:
            st.session_state.favorites = []
    if 'show_similar' not in st.session_state:
        st.session_state.show_similar = False
    if 'pantry' not in st.session_state:
        db, _, _, _ = get_clients()
        if db:
            try:
                st.session_state.pantry = db.get_pantry()
            except:
                st.session_state.pantry = []
        else:
            st.session_state.pantry = []
    if 'pantry_initialized' not in st.session_state:
        st.session_state.pantry_initialized = True

init_session_state()

def get_nutritional_badges(recipe):
    """Generate nutritional info badges"""
    badges = []
    nutrition = recipe.get('nutrition', {})
    nutrients = {}
    if nutrition:
        for nut in nutrition.get('nutrients', []):
            nutrients[nut.get('name', '')] = nut.get('amount', 0)
    
    protein = nutrients.get('Protein', 0)
    if protein >= 20:
        badges.append(('<span class="badge badge-protein">High Protein</span>', 'protein'))
    
    carbs = nutrients.get('Carbohydrates', 0)
    if carbs >= 50:
        badges.append(('<span class="badge badge-carbs">High Carbs</span>', 'carbs'))
    elif carbs < 20:
        badges.append(('<span class="badge badge-carbs">Low Carbs</span>', 'low-carbs'))
    
    calories = nutrients.get('Calories', 0)
    if calories <= 300:
        badges.append(('<span class="badge badge-low-cal">Low Calorie</span>', 'low-cal'))
    
    vit_c = nutrients.get('Vitamin C', 0)
    if vit_c >= 60:
        badges.append(('<span class="badge badge-vitamin">High Vitamin C</span>', 'vit-c'))
    
    if protein >= 20 and carbs < 20:
        badges.append(('<span class="badge badge-protein">High Protein, Low Carbs</span>', 'combo'))
    
    return badges

def render_recipe_card(recipe, index):
    """Render minimalist recipe card with fluid motion"""
    recipe_id = recipe.get('id')
    
    with st.container():
        st.markdown(f"""
            <div class="recipe-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;">
                    <div style="flex: 1;">
                        <h2 style="margin: 0; font-size: 1.75rem; color: #1A1A1A;">{recipe.get('title', 'Unknown Recipe')}</h2>
                        <p style="color: #666666; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 400;">{recipe.get('reasoning', 'Great match for you')}</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="confidence-score">{recipe.get('confidence', 0)}%</div>
                        <p style="color: #666666; font-size: 0.875rem; margin: 0; font-weight: 500;">Match</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            if recipe.get('image'):
                st.image(recipe['image'], use_container_width=True)
        
        with col2:
            st.metric("Time", f"{recipe.get('time', 0)} min")
            # Get smart_score from _metadata (technical data is nested)
            # Fallback to confidence if smart_score not in metadata
            metadata = recipe.get('_metadata', {})
            smart_score = metadata.get('smart_score', recipe.get('confidence', 0))
            st.metric("Score", f"{smart_score}%")
        
        with col3:
            difficulty = recipe.get('difficulty', 'medium').upper()
            st.metric("Difficulty", difficulty)
            st.metric("Used", f"{recipe.get('used_ingredients', 0)}")
        
        with col4:
            badges = get_nutritional_badges(recipe)
            if badges:
                st.markdown("**Nutrition**")
                badge_html = " ".join([badge[0] for badge in badges])
                st.markdown(badge_html, unsafe_allow_html=True)
        
        # Favorite button and View Recipe button
        col_fav, col_view = st.columns([1, 3])
        
        with col_fav:
            db, _, _, _ = get_clients()
            is_favorite = db.is_favorite(recipe_id) if db and recipe_id else False
            
            if is_favorite:
                if st.button("❤️ Favorited", key=f"unfav_{recipe_id}_{index}", use_container_width=True):
                    if db:
                        db.remove_favorite(recipe_id)
                        st.session_state.favorites = db.get_favorite_recipe_ids()
                    st.rerun()
            else:
                if st.button("🤍 Favorite", key=f"fav_{recipe_id}_{index}", use_container_width=True):
                    if db:
                        db.add_favorite(recipe_id, recipe.get('title', ''), recipe)
                        st.session_state.favorites = db.get_favorite_recipe_ids()
                    st.success(f"Added {recipe.get('title', 'recipe')} to favorites!")
                    st.rerun()
        
        with col_view:
            if st.button("📖 View Full Recipe & Instructions", key=f"view_recipe_{recipe_id}_{index}", use_container_width=True):
                st.session_state.selected_recipe_id = recipe_id
                st.rerun()
        
        with st.expander("Quick Preview", expanded=False):
            used_count = recipe.get('used_ingredients', 0)
            missing_count = recipe.get('missing_ingredients', 0)
            
            col_used, col_missing = st.columns(2)
            with col_used:
                st.markdown(f"**You Have ({used_count})**")
                # Safely handle extendedIngredients - use .get() to prevent crashes
                extended_ingredients = recipe.get('extendedIngredients', [])
                if extended_ingredients and used_count > 0:
                    for ing in extended_ingredients[:used_count]:
                        if isinstance(ing, dict):
                            name = ing.get('name', ing.get('original', ''))
                            if name:
                                st.markdown(f"• {name}")
            
            with col_missing:
                st.markdown(f"**Need to Buy ({missing_count})**")
                # Safely handle extendedIngredients - use .get() to prevent crashes
                extended_ingredients = recipe.get('extendedIngredients', [])
                if extended_ingredients and missing_count > 0:
                    for ing in extended_ingredients[used_count:used_count+missing_count]:
                        if isinstance(ing, dict):
                            name = ing.get('name', ing.get('original', ''))
                            if name:
                                st.markdown(f"• {name}")
                                if st.button(f"💡 Get Substitutes", key=f"fix_{recipe_id}_{name}_{index}"):
                                    st.session_state.selected_recipe = recipe
                                    st.session_state.substitution_data = {
                                        'missing_item': name,
                                        'recipe_id': recipe_id
                                    }
                                    st.rerun()
        
        st.markdown("---")

# Sidebar - Clean & Minimal
with st.sidebar:
    st.markdown("""
        <div style="padding: 2rem 0 1rem 0;">
            <h1 style="font-size: 2rem; margin: 0; color: #2E7D32;">PantryChef</h1>
            <p style="color: #666666; margin: 0.5rem 0; font-size: 0.95rem;">Discover Global Cuisines</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🥘 My Pantry")
    st.caption("Type your ingredients below (separated by spaces)")
    
    # Large, clear ingredient input area - VERY PROMINENT
    st.markdown("**Add Ingredients:**")
    ingredient_input = st.text_area(
        "",
        placeholder="chicken rice tomatoes onions garlic",
        key="ingredient_input_area",
        height=120,
        help="Type ingredients separated by spaces. Example: chicken rice tomatoes"
    )
    
    col_add, col_clear = st.columns(2)
    with col_add:
        add_clicked = st.button("➕ Add Ingredients", use_container_width=True, type="primary")
    with col_clear:
        clear_clicked = st.button("🗑️ Clear All", use_container_width=True)
    
    # Process ingredient input - split by spaces and handle commas if user adds them
    if add_clicked and ingredient_input:
        # Split by spaces and commas, then clean
        ingredients_text = ingredient_input.replace(',', ' ').replace('\n', ' ')
        ingredients_list = [ing.strip().lower() for ing in ingredients_text.split() if ing.strip()]
        
        added_count = 0
        for ingredient in ingredients_list:
            if ingredient and ingredient not in st.session_state.pantry:
                st.session_state.pantry.append(ingredient)
                db, _, _, _ = get_clients()
                if db:
                    db.add_ingredient(ingredient)
                added_count += 1
        
        if added_count > 0:
            st.success(f"✅ Added {added_count} ingredient(s)!")
            st.rerun()
        elif ingredients_list:
            st.info("All ingredients are already in your pantry")
    
    if clear_clicked:
        st.session_state.pantry = []
        db, _, _, _ = get_clients()
        if db:
            db.clear_pantry()
        st.success("✅ Pantry cleared!")
        st.rerun()
    
    if st.session_state.pantry:
        for ing in st.session_state.pantry:
            col_ing, col_del = st.columns([4, 1])
            with col_ing:
                st.markdown(f'<span class="pantry-chip chip-green">{ing.title()}</span>', unsafe_allow_html=True)
            with col_del:
                if st.button("×", key=f"del_{ing}_{hash(ing)}"):
                    st.session_state.pantry.remove(ing)
                    db, _, _, _ = get_clients()
                    if db:
                        db.remove_ingredient(ing)
                    st.rerun()
    else:
        st.caption("Add ingredients to get started")
    
    st.divider()
    
    # Similar Recipes based on Favorites
    if st.session_state.favorites:
        st.markdown("### 💡 Recommendations")
        st.caption(f"You have {len(st.session_state.favorites)} favorite recipe(s)")
        if st.button("🔍 Get Similar Recipes", use_container_width=True, key="get_similar"):
            st.session_state.show_similar = True
            st.rerun()
    
    st.divider()
    
    st.markdown("### Mood")
    mood = st.radio(
        "How are you feeling?",
        options=['tired', 'casual', 'energetic'],
        format_func=lambda x: {'tired': 'Tired', 'casual': 'Casual', 'energetic': 'Energetic'}[x],
        key="mood_selector",
        label_visibility="collapsed"
    )
    
    st.markdown("### Goal")
    profile = st.selectbox(
        "Cooking goal",
        options=['balanced', 'minimal_shopper', 'pantry_cleaner'],
        format_func=lambda x: {
            'balanced': 'Balanced',
            'minimal_shopper': 'Minimize Shopping',
            'pantry_cleaner': 'Use My Pantry'
        }[x],
        key="profile_selector"
    )

# Main Content - Bold Hero Section
st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">PantryChef</h1>
        <p class="hero-subtitle">Discover Global Cuisines From Your Kitchen</p>
    </div>
""", unsafe_allow_html=True)

# Clean Filters Section
# Initialize nutritional preferences
nutritional_prefs = {}

with st.container():
    st.markdown("### Your Preferences")
    
    # Basic filters
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        st.markdown("#### Basic Settings")
        max_time = st.number_input("⏱️ Max Time (min)", min_value=0, value=60, step=5, key="max_time")
        difficulty = st.selectbox("🎯 Difficulty", ['easy', 'medium', 'hard'], key="difficulty")
        cuisine = st.text_input("🌍 Cuisine", placeholder="Italian, Mexican, Indian", key="cuisine_filter")
        meal_type = st.selectbox("🍽️ Meal Type", ['', 'breakfast', 'lunch', 'dinner', 'snack', 'main course', 'side dish'], key="meal_type", format_func=lambda x: 'Any' if x == '' else x.title())
        skill_level = st.slider("👨‍🍳 Skill Level", 0, 100, 50, key="skill_level")
    
    with filter_col2:
        st.markdown("#### Dietary & Health")
        # Import supported diets and intolerances from API_PARAMS
        from API_PARAMS import SUPPORTED_INTOLERANCES
        
        # Dietary preferences - map UI options to API format
        dietary_options = {
            'vegetarian': 'vegetarian',
            'vegan': 'vegan',
            'pescatarian': 'pescetarian',  # Note: API uses 'pescetarian'
            'gluten_free': 'gluten free',
            'dairy_free': None  # Handle via intolerances
        }
        dietary_ui = st.multiselect(
            "🥗 Dietary Preferences", 
            options=list(dietary_options.keys()),
            key="dietary_filter"
        )
        dietary = [dietary_options[d] for d in dietary_ui if dietary_options[d]]
        
        # Intolerances - use supported list from API
        st.markdown("**⚠️ Intolerances**")
        # Convert to lowercase for UI, but keep original for API
        intolerance_options_lower = [intol.lower() for intol in SUPPORTED_INTOLERANCES]
        selected_intolerances_ui = st.multiselect(
            "Select from supported list:",
            options=intolerance_options_lower,
            key="intolerances_multiselect",
            help="Select from API-supported intolerances"
        )
        
        # Also allow custom intolerances (for manual checking)
        custom_intolerances_text = st.text_input(
            "Or type custom intolerances:", 
            placeholder="e.g., tomatoes, peppers",
            key="intolerances_custom",
            help="For intolerances not in the API list, we'll manually check ingredients"
        )
        
        # Combine API-supported and custom intolerances
        # API-supported ones go to API, custom ones for manual checking
        api_intolerances = [intol.capitalize() for intol in selected_intolerances_ui]  # API format
        if custom_intolerances_text:
            custom_intolerances = [intol.strip().lower() for intol in custom_intolerances_text.split(',') if intol.strip()]
        else:
            custom_intolerances = []
        
        # Store both separately for Logic.py to handle
        intolerances = {
            'api_supported': api_intolerances,
            'custom': custom_intolerances
        }
        
        # Nutritional preferences
        st.markdown("#### Nutritional Goals")
        nutritional_prefs = {}  # Reset each time
        
        col_nut1, col_nut2 = st.columns(2)
        with col_nut1:
            high_protein = st.checkbox("High Protein", key="high_protein")
            if high_protein:
                nutritional_prefs['high_protein'] = 20.0  # grams minimum
            
            high_calories = st.checkbox("High Calories", key="high_calories")
            if high_calories:
                nutritional_prefs['high_calories'] = 400.0  # calories minimum
            
            high_vitamin_c = st.checkbox("High Vitamin C", key="high_vitamin_c")
            if high_vitamin_c:
                nutritional_prefs['high_vitamin_c'] = 60.0  # mg minimum
        
        with col_nut2:
            high_iron = st.checkbox("High Iron", key="high_iron")
            if high_iron:
                nutritional_prefs['high_iron'] = 3.0  # mg minimum
            
            high_calcium = st.checkbox("High Calcium", key="high_calcium")
            if high_calcium:
                nutritional_prefs['high_calcium'] = 200.0  # mg minimum
            
            low_calorie = st.checkbox("Low Calorie", key="low_calorie")
            if low_calorie:
                nutritional_prefs['low_calorie'] = 300.0  # calories maximum

# Search Button
col_search, _ = st.columns([1, 4])
with col_search:
    search_clicked = st.button("Search Recipes", use_container_width=True, type="primary")

# Substitution Help - Uses substitutes API
if st.session_state.substitution_data and st.session_state.selected_recipe:
    st.markdown("---")
    st.markdown("### 💡 Substitution Help")
    
    missing_item = st.session_state.substitution_data.get('missing_item')
    recipe_id = st.session_state.substitution_data.get('recipe_id')
    recipe_title = st.session_state.selected_recipe.get('title', 'Recipe')
    
    db, api_client, _, substitution_helper = get_clients()
    
    # First, get substitutes from API directly
    if api_client:
        with st.spinner("Getting substitution suggestions..."):
            # Get API substitutes
            api_substitutes = api_client.get_substitutes(missing_item)
            
            # Get complete substitution help (includes Gemini if available)
            if substitution_helper and st.session_state.pantry:
                sub_result = substitution_helper.get_complete_substitution_help(
                    missing_item=missing_item,
                    recipe_title=recipe_title,
                    recipe_id=recipe_id,
                    user_pantry_list=st.session_state.pantry
                )
            else:
                sub_result = {'best_option': '', 'api_substitutes': api_substitutes}
        
        # Display API substitutes
        if api_substitutes:
            st.markdown("#### 🥄 Spoonacular Substitutes")
            if api_substitutes.get('substitute'):
                st.success(f"**Primary Substitute:** {api_substitutes['substitute']}")
            if api_substitutes.get('message'):
                st.info(api_substitutes['message'])
            if api_substitutes.get('alternatives'):
                st.markdown("**Other Options:**")
                for alt in api_substitutes['alternatives'][:5]:
                    st.markdown(f"• {alt}")
        
        # Display smart recommendation if available
        if sub_result.get('smart_recommendation'):
            st.markdown("#### 🤖 AI-Powered Recommendation")
            smart = sub_result['smart_recommendation']
            st.success(f"**Best Option:** {smart.get('substitution', 'N/A')}")
            if smart.get('chef_tip'):
                st.caption(f"💡 **Chef's Tip:** {smart.get('chef_tip')}")
        
        # Display best option summary
        if sub_result.get('best_option'):
            st.markdown("---")
            st.markdown(f"### ✅ Recommended Action")
            st.success(sub_result['best_option'])
        
        # Show similar recipes as alternative
        if recipe_id and api_client:
            with st.expander("🔍 See Similar Recipes (Alternative Options)"):
                similar = api_client.get_similar_recipes(recipe_id, number=3)
                if similar:
                    for sim_recipe in similar:
                        st.markdown(f"• **{sim_recipe.get('title', 'Unknown')}**")
                        if st.button(f"View Recipe #{sim_recipe.get('id')}", key=f"view_sim_{sim_recipe.get('id')}"):
                            st.session_state.selected_recipe_id = sim_recipe.get('id')
                            st.session_state.substitution_data = {}
                            st.rerun()
                else:
                    st.info("No similar recipes found")
        
        if st.button("Close Substitution Help"):
            st.session_state.substitution_data = {}
            st.session_state.selected_recipe = None
            st.rerun()

# Search Logic - OPTIMIZED: Use complexSearch with all parameters upfront
if search_clicked:
    if not st.session_state.pantry:
        st.warning("Add ingredients to your pantry first")
    else:
        db, api_client, _, _ = get_clients()
        if not api_client:
            st.error("API client not initialized")
        else:
            with st.spinner("Searching for perfect recipes..."):
                # Build user settings with nutritional requirements
                user_settings = {
                    'user_profile': profile,
                    'mood': mood,
                    'max_difficulty': difficulty,
                    'max_time_minutes': max_time,
                    'max_missing_ingredients': 999,  # No limit - show best results
                    'dietary_requirements': dietary,
                    'intolerances': custom_intolerances,  # Custom ones for manual checking
                    'intolerances_api': api_intolerances,  # API-supported ones
                    'nutritional_requirements': nutritional_prefs,
                    'skill_level': skill_level,
                    'max_time': max_time
                }
                
                # Handle meal_type - convert empty string to None
                meal_type_filter = meal_type if meal_type and meal_type != '' else None
                
                # Convert dietary preferences to API format
                diet_api = None
                if dietary:
                    # dietary is already in API format from the UI mapping
                    # Filter out None values (like dairy_free which is handled via intolerances)
                    api_diets = [d for d in dietary if d]
                    if api_diets:
                        diet_api = ','.join(api_diets)
                
                # Handle intolerances - separate API-supported and custom
                if isinstance(intolerances, dict):
                    api_intolerances = intolerances.get('api_supported', [])
                    custom_intolerances = intolerances.get('custom', [])
                else:
                    # Legacy format - treat all as custom for manual checking
                    api_intolerances = []
                    custom_intolerances = intolerances if isinstance(intolerances, list) else []
                
                # Pass to API only the supported ones
                api_intolerances_param = api_intolerances if api_intolerances else None
                
                # Build nutritional API parameters
                min_protein = nutritional_prefs.get('high_protein')
                min_calories = nutritional_prefs.get('high_calories')
                max_calories = nutritional_prefs.get('low_calorie')
                min_vitamin_c = nutritional_prefs.get('high_vitamin_c')
                min_iron = nutritional_prefs.get('high_iron')
                min_calcium = nutritional_prefs.get('high_calcium')
                
                # OPTIMIZED: Use complexSearch with ALL parameters upfront - single API call
                # This gets us recipes with full info already included
                raw_recipes = api_client.search_by_ingredients(
                    user_ingredients=st.session_state.pantry,
                    number=25,  # Get more results, filter down later
                    cuisine=cuisine if cuisine else None,
                    meal_type=meal_type_filter,
                    diet=diet_api,
                    intolerances=api_intolerances_param,
                    max_ready_time=max_time if max_time > 0 else None,
                    min_protein=min_protein,
                    min_calories=min_calories,
                    max_calories=max_calories,
                    min_vitamin_c=min_vitamin_c,
                    min_iron=min_iron,
                    min_calcium=min_calcium
                )
                
                if raw_recipes:
                    # Process recipes - complexSearch already includes most data we need
                    # Only store recipe IDs for detail fetching when user clicks
                    engine = PantryChefEngine(user_settings)
                    st.session_state.recipes = engine.process_results(raw_recipes)
                    
                    # Store raw recipe data for detail view (without making extra API calls)
                    st.session_state.raw_recipe_data = {r.get('id'): r for r in raw_recipes if r.get('id')}
                    
                    if st.session_state.recipes:
                        st.success(f"Found {len(st.session_state.recipes)} recipes matching your preferences!")
                        
                        # Generate AI-powered recommendation pitch using Gemini
                        _, _, gemini, _ = get_clients()
                        if gemini and gemini.is_available():
                            with st.spinner("Getting personalized recommendations..."):
                                pitch = gemini.generate_recommendation_pitch(
                                    st.session_state.recipes,
                                    user_mood=mood
                                )
                                
                                if pitch.get('pitch_text'):
                                    st.markdown("---")
                                    st.markdown("### 👨‍🍳 Chef's Recommendation")
                                    st.info(pitch['pitch_text'])
                                    
                                    # For tired users, highlight the single best recipe
                                    if mood == 'tired' and pitch.get('top_recipe'):
                                        top = pitch['top_recipe']
                                        st.success(f"**Best for you right now:** {top.get('title', 'Recipe')}")
                else:
                    st.error("No recipes found. Try different ingredients or preferences.")

# Recipe Detail View - Show when user clicks on a recipe
if st.session_state.get('selected_recipe_id'):
    recipe_id = st.session_state.selected_recipe_id
    db, api_client, _, _ = get_clients()
    
    # Get full recipe details (only when user clicks)
    with st.spinner("Loading full recipe details..."):
        # First check if we have it in raw data
        recipe_data = st.session_state.get('raw_recipe_data', {}).get(recipe_id)
        
        # If we don't have full details, fetch them
        if not recipe_data or 'analyzedInstructions' not in recipe_data:
            recipe_data = api_client.get_recipe_details(recipe_id)
        
        if recipe_data:
            st.markdown("---")
            st.markdown(f"# {recipe_data.get('title', 'Recipe')}")
            
            col_img, col_info = st.columns([2, 1])
            
            with col_img:
                if recipe_data.get('image'):
                    st.image(recipe_data['image'], use_container_width=True)
            
            with col_info:
                st.metric("⏱️ Time", f"{recipe_data.get('readyInMinutes', 0)} min")
                st.metric("👥 Servings", f"{recipe_data.get('servings', 0)}")
                st.metric("⭐ Score", f"{recipe_data.get('spoonacularScore', 0)}")
                
                if recipe_data.get('healthScore'):
                    st.metric("💚 Health", f"{recipe_data.get('healthScore', 0)}")
            
            # Ingredients
            st.markdown("## 📋 Ingredients")
            if recipe_data.get('extendedIngredients'):
                for ing in recipe_data['extendedIngredients']:
                    if isinstance(ing, dict):
                        amount = ing.get('amount', 0)
                        unit = ing.get('unit', '')
                        name = ing.get('name', ing.get('original', ''))
                        st.markdown(f"• **{amount} {unit}** {name}")
            
            # Instructions
            st.markdown("## 👨‍🍳 Instructions")
            if recipe_data.get('analyzedInstructions'):
                for instruction_group in recipe_data['analyzedInstructions']:
                    if isinstance(instruction_group, dict) and 'steps' in instruction_group:
                        for step in instruction_group['steps']:
                            step_num = step.get('number', 0)
                            step_text = step.get('step', '')
                            st.markdown(f"### Step {step_num}")
                            st.markdown(step_text)
                            
                            # Show equipment if available
                            if step.get('equipment'):
                                equipment_names = [eq.get('name', '') for eq in step['equipment'] if isinstance(eq, dict)]
                                if equipment_names:
                                    st.caption(f"Equipment: {', '.join(equipment_names)}")
            elif recipe_data.get('instructions'):
                st.markdown(recipe_data['instructions'])
            else:
                st.info("Instructions not available for this recipe")
            
            # Nutrition Info - Using Gemini for clean formatting
            if recipe_data.get('nutrition'):
                st.markdown("## 🥗 Nutrition (per serving)")
                nutrition = recipe_data['nutrition']
                
                # Use Gemini to format nutrition label with AI summary
                _, _, gemini, _ = get_clients()
                if gemini and gemini.is_available():
                    nutrition_label = gemini.format_nutrition_label(nutrition)
                    
                    # Display AI summary
                    if nutrition_label.get('summary'):
                        st.info(nutrition_label['summary'])
                    
                    # Display formatted nutrition data
                    label = nutrition_label.get('label', {})
                    if label:
                        col_nut1, col_nut2, col_nut3 = st.columns(3)
                        
                        with col_nut1:
                            st.metric("Calories", f"{label.get('calories', 0):.0f}")
                            st.metric("Protein", f"{label.get('protein', 0):.1f}g")
                        
                        with col_nut2:
                            st.metric("Carbs", f"{label.get('carbs', 0):.1f}g")
                            st.metric("Fat", f"{label.get('fat', 0):.1f}g")
                        
                        with col_nut3:
                            st.metric("Fiber", f"{label.get('fiber', 0):.1f}g")
                            if label.get('vitamin_c', 0) > 0:
                                st.metric("Vitamin C", f"{label.get('vitamin_c', 0):.1f}mg")
                            if label.get('iron', 0) > 0:
                                st.metric("Iron", f"{label.get('iron', 0):.2f}mg")
                            if label.get('calcium', 0) > 0:
                                st.metric("Calcium", f"{label.get('calcium', 0):.1f}mg")
                else:
                    # Fallback: Display raw nutrition data
                    nutrients = nutrition.get('nutrients', [])
                    if nutrients:
                        col_nut1, col_nut2, col_nut3 = st.columns(3)
                        important_nutrients = ['Calories', 'Protein', 'Carbohydrates', 'Fat', 'Fiber', 'Vitamin C', 'Iron', 'Calcium']
                        
                        nutrient_dict = {nut.get('name', ''): nut.get('amount', 0) for nut in nutrients}
                        
                        for i, nut_name in enumerate(important_nutrients):
                            if nut_name in nutrient_dict:
                                col = col_nut1 if i % 3 == 0 else (col_nut2 if i % 3 == 1 else col_nut3)
                                with col:
                                    st.metric(nut_name, f"{nutrient_dict[nut_name]:.1f}")
            
            # Back button
            if st.button("← Back to Recipe List"):
                st.session_state.selected_recipe_id = None
                st.rerun()
        else:
            st.error("Could not load recipe details")
            if st.button("← Back"):
                st.session_state.selected_recipe_id = None
                st.rerun()

# Similar Recipes based on Favorites
if st.session_state.get('show_similar') and st.session_state.favorites:
    st.markdown("---")
    st.markdown("### 💡 Similar Recipes Based on Your Favorites")
    
    db, api_client, _, _ = get_clients()
    if api_client:
        with st.spinner("Finding similar recipes..."):
            all_similar = []
            # Get similar recipes for each favorite
            for fav_id in st.session_state.favorites[:5]:  # Limit to first 5 favorites
                similar = api_client.get_similar_recipes(fav_id, number=3)
                all_similar.extend(similar)
            
            # Remove duplicates by recipe ID
            seen_ids = set()
            unique_similar = []
            for recipe in all_similar:
                recipe_id = recipe.get('id')
                if recipe_id and recipe_id not in seen_ids:
                    seen_ids.add(recipe_id)
                    unique_similar.append(recipe)
            
            if unique_similar:
                st.success(f"Found {len(unique_similar)} similar recipes!")
                # Process through engine for consistency
                user_settings = {
                    'user_profile': 'balanced',
                    'mood': 'casual',
                    'max_difficulty': 'hard',
                    'max_time_minutes': 120,
                    'max_missing_ingredients': 999,
                    'dietary_requirements': [],
                    'intolerances': [],
                    'nutritional_requirements': {},
                    'skill_level': 50,
                    'max_time': 120
                }
                engine = PantryChefEngine(user_settings)
                processed_similar = engine.process_results(unique_similar)
                
                for i, recipe in enumerate(processed_similar[:10]):  # Show top 10
                    render_recipe_card(recipe, f"similar_{i}")
            else:
                st.info("No similar recipes found. Try favoriting more recipes!")
    
    if st.button("Close Similar Recipes", key="close_similar"):
        st.session_state.show_similar = False
        st.rerun()

# Display Recipes List
elif st.session_state.recipes:
    st.markdown("---")
    st.markdown(f"### Recipes ({len(st.session_state.recipes)})")
    
    for i, recipe in enumerate(st.session_state.recipes):
        render_recipe_card(recipe, i)
else:
    if not search_clicked:
        st.info("Add ingredients and search for recipes")
