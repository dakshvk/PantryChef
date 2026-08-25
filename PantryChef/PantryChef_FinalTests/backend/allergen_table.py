"""
Canonical ingredient and allergen table — the single source of truth.

This module is deliberately dependency-free and offline. It imports nothing but
the standard library, has no network access and no LLM client. That is a design
constraint, not an accident: a model must never be able to influence a safety
verdict, and a verdict must be reproducible from
(recipe, declared_allergens, TABLE_VERSION) alone.

Three ideas do the work here:

1. **Word-boundary, longest-phrase-first resolution.** Ingredient text is
   normalised into tokens and scanned for the longest known phrase at each
   position. "peanut butter" resolves to peanut butter (peanuts), never to
   butter (milk). "eggplant" is one token and never matches "egg".

2. **A known-safe vocabulary, not just a danger list.** An ingredient that
   matches nothing at all is UNRESOLVED, and an UNRESOLVED ingredient makes the
   recipe UNKNOWN rather than SAFE. Absence of evidence is not evidence of
   safety. The safe vocabulary is what lets a recipe earn a SAFE verdict.

3. **Declarations resolve through the same table.** A user who types
   "shellfish" is screened against the crustaceans and molluscs categories. A
   user who types something the table does not know gets UNKNOWN and is told
   the app cannot screen for it — never "safe".

Deliberately absent: any notion of a "safe word" that downgrades a match. A
recipe titled "Vegan-Style Mac and Cheese" that lists butter and cheddar
contains butter and cheddar. Titles are marketing text and are never evidence.
"""

from typing import Dict, List, Set, Tuple
import re

# Bump this whenever the vocabulary below changes. Every verdict records it.
TABLE_VERSION = "2.0.0"

# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------
# The UK/EU 14 declarable allergens. Peanuts and tree nuts are separate
# categories because they are separate allergies.
ALLERGEN_CATEGORIES: Tuple[str, ...] = (
    "cereals_gluten", "crustaceans", "eggs", "fish", "peanuts", "soybeans",
    "milk", "tree_nuts", "celery", "mustard", "sesame", "sulphites",
    "lupin", "molluscs",
)

# Diet-relevant memberships. Not allergens, but they exclude a recipe under a
# declared diet, and they resolve through this same table so that there is only
# ever one vocabulary.
DIET_CATEGORIES: Tuple[str, ...] = ("land_meat", "poultry", "animal_slaughter", "honey")

ALL_CATEGORIES: Tuple[str, ...] = ALLERGEN_CATEGORIES + DIET_CATEGORIES

# --------------------------------------------------------------------------
# Diets, expressed as sets of excluded categories
# --------------------------------------------------------------------------
DIET_EXCLUSIONS: Dict[str, Set[str]] = {
    "vegetarian": {"land_meat", "poultry", "fish", "crustaceans", "molluscs",
                   "animal_slaughter"},
    "vegan": {"land_meat", "poultry", "fish", "crustaceans", "molluscs",
              "animal_slaughter", "milk", "eggs", "honey"},
    "pescatarian": {"land_meat", "poultry", "animal_slaughter"},
}

# --------------------------------------------------------------------------
# What a user's declared restriction means in table terms
# --------------------------------------------------------------------------
# Everything a user can type that this table can actually screen. Anything not
# listed here is reported as unscreenable — it is never silently satisfied.
DECLARATION_ALIASES: Dict[str, Set[str]] = {
    # milk
    "dairy": {"milk"}, "milk": {"milk"}, "lactose": {"milk"},
    "dairy free": {"milk"}, "dairy-free": {"milk"}, "cows milk": {"milk"},
    # gluten
    "gluten": {"cereals_gluten"}, "wheat": {"cereals_gluten"},
    "celiac": {"cereals_gluten"}, "coeliac": {"cereals_gluten"},
    "gluten free": {"cereals_gluten"}, "gluten-free": {"cereals_gluten"},
    # eggs
    "egg": {"eggs"}, "eggs": {"eggs"},
    # nuts
    "tree nut": {"tree_nuts"}, "tree nuts": {"tree_nuts"},
    "treenuts": {"tree_nuts"}, "nut": {"tree_nuts", "peanuts"},
    "nuts": {"tree_nuts", "peanuts"}, "peanut": {"peanuts"},
    "peanuts": {"peanuts"}, "groundnut": {"peanuts"}, "groundnuts": {"peanuts"},
    # soy
    "soy": {"soybeans"}, "soya": {"soybeans"}, "soybean": {"soybeans"},
    "soybeans": {"soybeans"},
    # seafood
    "shellfish": {"crustaceans", "molluscs"},
    "crustacean": {"crustaceans"}, "crustaceans": {"crustaceans"},
    "mollusc": {"molluscs"}, "molluscs": {"molluscs"},
    "mollusk": {"molluscs"}, "mollusks": {"molluscs"},
    "shrimp": {"crustaceans"}, "prawn": {"crustaceans"}, "prawns": {"crustaceans"},
    "fish": {"fish"}, "seafood": {"fish", "crustaceans", "molluscs"},
    # the rest of the 14
    "sesame": {"sesame"}, "tahini": {"sesame"},
    "mustard": {"mustard"}, "celery": {"celery"},
    "sulphites": {"sulphites"}, "sulfites": {"sulphites"},
    "sulphur dioxide": {"sulphites"}, "sulfur dioxide": {"sulphites"},
    "lupin": {"lupin"}, "lupine": {"lupin"},
}

# --------------------------------------------------------------------------
# Canonical ingredients
# --------------------------------------------------------------------------
# (canonical_id, categories, aliases)
#
# Longest-phrase-first resolution means a multi-word entry always beats the
# single words inside it, so "peanut butter" and "butternut squash" are simply
# listed as their own entries and the ambiguity disappears.
#
# Entries with an empty category tuple are the known-safe vocabulary. They carry
# no allergen, but listing them is what allows a recipe to be resolved fully and
# therefore to earn a SAFE verdict rather than UNKNOWN.

_ENTRIES: List[Tuple[str, Tuple[str, ...], Tuple[str, ...]]] = [

    # ---------------- phrases that must beat their own substrings -----------
    ("peanut_butter",     ("peanuts",),        ("peanut butter", "peanutbutter")),
    ("butternut_squash",  (),                  ("butternut squash", "butternut")),
    ("coconut_milk",      (),                  ("coconut milk", "coconut cream", "creamed coconut")),
    ("coconut",           (),                  ("coconut", "coconuts", "desiccated coconut", "coconut oil", "coconut flakes")),
    ("almond_milk",       ("tree_nuts",),      ("almond milk", "almondmilk")),
    ("soy_milk",          ("soybeans",),       ("soy milk", "soymilk", "soya milk")),
    ("oat_milk",          ("cereals_gluten",), ("oat milk", "oatmilk")),
    ("rice_milk",         (),                  ("rice milk", "ricemilk")),
    ("graham_cracker",    ("cereals_gluten",), ("graham cracker", "graham crackers", "graham cracker crumbs")),
    ("eggplant",          (),                  ("eggplant", "eggplants", "aubergine", "aubergines")),
    ("doughnut",          ("cereals_gluten",), ("donut", "donuts", "doughnut", "doughnuts")),
    ("water_chestnut",    (),                  ("water chestnut", "water chestnuts")),
    ("nutmeg",            (),                  ("nutmeg",)),
    ("butter_lettuce",    (),                  ("butter lettuce", "butterhead lettuce")),
    ("buttercup_squash",  (),                  ("buttercup squash",)),
    ("butterbean",        (),                  ("butter bean", "butter beans", "butterbean", "butterbeans", "lima bean", "lima beans")),
    ("buttermilk",        ("milk",),           ("buttermilk", "butter milk")),
    ("peanut_oil",        ("peanuts",),        ("peanut oil", "groundnut oil")),
    ("nutritional_yeast", (),                  ("nutritional yeast", "nooch")),
    ("chestnut",          (),                  ("chestnut", "chestnuts", "water chestnut flour")),
    ("nut_free_spread",   (),                  ("sunflower seed butter", "sunbutter", "seed butter")),

    # ---------------- milk --------------------------------------------------
    ("milk",              ("milk",), ("milk", "whole milk", "skim milk", "skimmed milk",
                                      "semi skimmed milk", "2% milk", "full fat milk",
                                      "evaporated milk", "condensed milk", "sweetened condensed milk",
                                      "powdered milk", "milk powder", "dry milk")),
    ("butter",            ("milk",), ("butter", "unsalted butter", "salted butter",
                                      "clarified butter", "browned butter", "brown butter")),
    ("ghee",              ("milk",), ("ghee",)),
    ("cream",             ("milk",), ("cream", "heavy cream", "double cream", "single cream",
                                      "whipping cream", "heavy whipping cream", "light cream",
                                      "sour cream", "creme fraiche", "half and half",
                                      "half-and-half", "clotted cream")),
    ("cheese",            ("milk",), ("cheese", "cheddar", "cheddar cheese", "mozzarella",
                                      "parmesan", "parmigiano reggiano", "gruyere", "brie",
                                      "feta", "goat cheese", "goats cheese", "chevre",
                                      "cream cheese", "blue cheese", "gorgonzola", "ricotta",
                                      "mascarpone", "provolone", "swiss cheese", "monterey jack",
                                      "pecorino", "halloumi", "paneer", "queso fresco",
                                      "cottage cheese", "grated cheese", "shredded cheese")),
    ("yogurt",            ("milk",), ("yogurt", "yoghurt", "greek yogurt", "greek yoghurt",
                                      "curd", "curds", "dahi", "skyr", "kefir")),
    ("whey",              ("milk",), ("whey", "whey protein", "whey protein isolate",
                                      "whey powder")),
    ("casein",            ("milk",), ("casein", "caseinate", "sodium caseinate",
                                      "micellar casein", "caseinates")),
    ("custard",           ("milk", "eggs"), ("custard", "creme anglaise", "creme patissiere",
                                             "pastry cream")),
    ("milk_chocolate",    ("milk",), ("milk chocolate", "white chocolate")),
    ("lactose",           ("milk",), ("lactose",)),
    ("rennet",            ("milk", "animal_slaughter"), ("rennet", "animal rennet")),

    # ---------------- eggs --------------------------------------------------
    ("egg",               ("eggs",), ("egg", "eggs", "egg white", "egg whites", "egg yolk",
                                      "egg yolks", "whole egg", "whole eggs", "beaten egg",
                                      "egg wash", "free range egg", "free range eggs",
                                      "dried egg", "egg powder")),
    ("mayonnaise",        ("eggs",), ("mayonnaise", "mayo", "japanese mayonnaise", "kewpie")),
    ("aioli",             ("eggs",), ("aioli", "garlic aioli")),
    ("hollandaise",       ("eggs",), ("hollandaise", "hollandaise sauce", "bearnaise",
                                      "bearnaise sauce")),
    ("meringue",          ("eggs",), ("meringue", "meringues", "italian meringue")),
    ("albumin",           ("eggs",), ("albumin", "albumen", "ovalbumin", "egg albumin")),
    ("lecithin_egg",      ("eggs",), ("egg lecithin",)),

    # ---------------- cereals containing gluten -----------------------------
    ("wheat",             ("cereals_gluten",), ("wheat", "wheat flour", "whole wheat",
                                                "wholewheat", "wheat germ", "wheat bran",
                                                "cracked wheat", "wheat starch", "durum",
                                                "durum wheat", "triticale", "einkorn")),
    ("flour",             ("cereals_gluten",), ("flour", "all purpose flour", "all-purpose flour",
                                                "plain flour", "self raising flour",
                                                "self-raising flour", "bread flour",
                                                "cake flour", "pastry flour", "00 flour")),
    ("bread",             ("cereals_gluten",), ("bread", "breadcrumbs", "bread crumbs", "panko",
                                                "baguette", "brioche", "ciabatta", "sourdough",
                                                "pita", "pitta", "naan", "focaccia", "croutons",
                                                "toast", "bun", "buns", "roll", "rolls")),
    ("pasta",             ("cereals_gluten",), ("pasta", "spaghetti", "penne", "macaroni",
                                                "fusilli", "linguine", "fettuccine", "tagliatelle",
                                                "lasagne", "lasagna", "orzo", "farfalle",
                                                "rigatoni", "noodles", "egg noodles", "ramen noodles",
                                                "udon", "couscous", "semolina")),
    ("barley",            ("cereals_gluten",), ("barley", "pearl barley", "barley malt",
                                                "malt", "malt extract", "malted barley",
                                                "malt vinegar", "malted")),
    ("rye",               ("cereals_gluten",), ("rye", "rye flour", "rye bread", "pumpernickel")),
    ("spelt",             ("cereals_gluten",), ("spelt", "farro", "emmer", "kamut", "bulgur",
                                                "bulghur", "freekeh")),
    ("seitan",            ("cereals_gluten",), ("seitan", "vital wheat gluten", "wheat gluten",
                                                "gluten")),
    ("oats",              ("cereals_gluten",), ("oat", "oats", "rolled oats", "oatmeal",
                                                "porridge oats", "steel cut oats", "oat flour",
                                                "oat bran")),
    ("soy_sauce",         ("soybeans", "cereals_gluten"), ("soy sauce", "soya sauce", "shoyu",
                                                           "dark soy sauce", "light soy sauce")),
    ("beer",              ("cereals_gluten",), ("beer", "ale", "lager", "stout")),

    # ---------------- peanuts ----------------------------------------------
    ("peanut",            ("peanuts",), ("peanut", "peanuts", "groundnut", "groundnuts",
                                         "peanut flour", "roasted peanuts", "peanut sauce",
                                         "satay sauce")),

    # ---------------- tree nuts --------------------------------------------
    ("almond",            ("tree_nuts",), ("almond", "almonds", "almond flour", "almond meal",
                                           "almond extract", "almond butter", "flaked almonds",
                                           "ground almonds", "marzipan", "amaretti", "frangipane")),
    ("walnut",            ("tree_nuts",), ("walnut", "walnuts", "walnut oil", "walnut halves")),
    ("pecan",             ("tree_nuts",), ("pecan", "pecans", "pecan halves")),
    ("cashew",            ("tree_nuts",), ("cashew", "cashews", "cashew butter", "cashew cream")),
    ("pistachio",         ("tree_nuts",), ("pistachio", "pistachios")),
    ("hazelnut",          ("tree_nuts",), ("hazelnut", "hazelnuts", "filbert", "filberts",
                                           "gianduja", "nutella", "praline", "pralines")),
    ("macadamia",         ("tree_nuts",), ("macadamia", "macadamias", "macadamia nut",
                                           "macadamia nuts")),
    ("brazil_nut",        ("tree_nuts",), ("brazil nut", "brazil nuts")),
    ("pine_nut",          ("tree_nuts",), ("pine nut", "pine nuts", "pignoli")),
    ("nougat",            ("tree_nuts",), ("nougat",)),
    ("mixed_nuts",        ("tree_nuts", "peanuts"), ("mixed nuts", "nut mix", "chopped nuts",
                                                     "toasted nuts")),

    # ---------------- soy ---------------------------------------------------
    ("soybean",           ("soybeans",), ("soy", "soya", "soybean", "soybeans", "soy bean",
                                          "soy beans", "edamame", "soy protein",
                                          "textured vegetable protein", "tvp", "soy lecithin")),
    ("tofu",              ("soybeans",), ("tofu", "silken tofu", "firm tofu", "bean curd")),
    ("tempeh",            ("soybeans",), ("tempeh",)),
    ("miso",              ("soybeans",), ("miso", "miso paste", "white miso", "red miso")),
    ("tamari",            ("soybeans",), ("tamari",)),
    ("hoisin",            ("soybeans",), ("hoisin", "hoisin sauce")),

    # ---------------- sesame -------------------------------------------------
    ("sesame",            ("sesame",), ("sesame", "sesame seed", "sesame seeds", "sesame oil",
                                        "toasted sesame oil", "tahini", "tahina", "halva",
                                        "gomashio", "benne")),

    # ---------------- fish, crustaceans, molluscs ---------------------------
    ("fish",              ("fish",), ("fish", "salmon", "tuna", "cod", "haddock", "tilapia",
                                      "trout", "mackerel", "halibut", "sea bass", "seabass",
                                      "snapper", "pollock", "monkfish", "swordfish", "sardine",
                                      "sardines", "anchovy", "anchovies", "herring", "smoked salmon",
                                      "fish sauce", "nam pla", "worcestershire sauce",
                                      "fish stock", "surimi")),
    ("shrimp",            ("crustaceans",), ("shrimp", "shrimps", "prawn", "prawns",
                                             "king prawns", "tiger prawns", "shrimp paste")),
    ("crab",              ("crustaceans",), ("crab", "crabs", "crab meat", "crabmeat",
                                             "soft shell crab")),
    ("lobster",           ("crustaceans",), ("lobster", "lobsters", "langoustine", "langoustines")),
    ("crayfish",          ("crustaceans",), ("crayfish", "crawfish", "krill")),
    ("mussel",            ("molluscs",), ("mussel", "mussels")),
    ("clam",              ("molluscs",), ("clam", "clams", "clam juice")),
    ("oyster",            ("molluscs",), ("oyster", "oysters", "oyster sauce")),
    ("scallop",           ("molluscs",), ("scallop", "scallops")),
    ("squid",             ("molluscs",), ("squid", "calamari", "octopus", "cuttlefish")),
    ("snail",             ("molluscs",), ("snail", "snails", "escargot")),

    # ---------------- celery, mustard, sulphites, lupin ---------------------
    ("celery",            ("celery",), ("celery", "celeriac", "celery salt", "celery seed",
                                        "celery seeds", "celery root")),
    ("mustard",           ("mustard",), ("mustard", "dijon", "dijon mustard", "wholegrain mustard",
                                         "mustard seed", "mustard seeds", "mustard powder",
                                         "english mustard", "yellow mustard")),
    ("sulphites",         ("sulphites",), ("sulphites", "sulfites", "sulphur dioxide",
                                           "sulfur dioxide", "sodium metabisulphite",
                                           "potassium metabisulphite", "e220")),
    ("wine",              ("sulphites",), ("wine", "white wine", "red wine", "cooking wine",
                                           "sherry", "vermouth", "marsala", "port")),
    ("dried_fruit",       ("sulphites",), ("dried apricot", "dried apricots", "sultanas",
                                           "golden raisins")),
    ("lupin",             ("lupin",), ("lupin", "lupine", "lupin flour", "lupini", "lupini beans")),

    # ---------------- land meat and poultry (diet only) ---------------------
    ("beef",              ("land_meat",), ("beef", "ground beef", "minced beef", "beef mince",
                                           "steak", "sirloin", "ribeye", "rib eye", "brisket",
                                           "chuck", "short ribs", "ribs", "veal", "oxtail",
                                           "beef stock", "beef broth", "corned beef")),
    ("pork",              ("land_meat",), ("pork", "pork chop", "pork chops", "pork belly",
                                           "pork shoulder", "ground pork", "bacon", "pancetta",
                                           "ham", "prosciutto", "sausage", "sausages", "chorizo",
                                           "pepperoni", "salami", "guanciale", "lardons",
                                           "gammon", "speck", "mortadella")),
    ("lamb",              ("land_meat",), ("lamb", "mutton", "lamb chop", "lamb chops",
                                           "ground lamb", "leg of lamb")),
    ("game",              ("land_meat",), ("venison", "rabbit", "boar", "wild boar", "goat meat")),
    ("meat_generic",      ("land_meat",), ("meat", "meatball", "meatballs", "meatloaf",
                                           "minced meat", "ground meat", "cold cuts", "charcuterie")),
    ("chicken",           ("poultry",), ("chicken", "chicken breast", "chicken breasts",
                                         "chicken thigh", "chicken thighs", "chicken stock",
                                         "chicken broth", "rotisserie chicken", "ground chicken",
                                         "chicken wings", "poultry")),
    ("turkey",            ("poultry",), ("turkey", "ground turkey", "turkey breast")),
    ("duck",              ("poultry",), ("duck", "duck breast", "duck fat", "goose", "foie gras")),

    # ---------------- other animal-derived (diet only) ----------------------
    ("gelatin",           ("animal_slaughter",), ("gelatin", "gelatine", "leaf gelatine")),
    ("lard",              ("animal_slaughter",), ("lard", "tallow", "suet", "schmaltz",
                                                  "bacon fat", "dripping")),
    ("honey",             ("honey",), ("honey", "raw honey", "manuka honey", "honeycomb")),

    # ---------------- known-safe vocabulary ---------------------------------
    # Ordinary ingredients confirmed to carry none of the categories above.
    # This list is what makes a SAFE verdict possible; an ingredient outside it
    # resolves to UNRESOLVED and the recipe becomes UNKNOWN.
    ("water",             (), ("water", "cold water", "warm water", "boiling water", "ice", "ice water")),
    ("salt",              (), ("salt", "sea salt", "kosher salt", "table salt", "flaky salt", "rock salt")),
    ("pepper",            (), ("pepper", "black pepper", "white pepper", "peppercorn", "peppercorns",
                               "ground black pepper", "cracked black pepper")),
    ("olive_oil",         (), ("olive oil", "extra virgin olive oil", "evoo")),
    ("oil_generic",       (), ("oil", "vegetable oil", "sunflower oil", "canola oil", "rapeseed oil",
                               "avocado oil", "grapeseed oil", "cooking spray")),
    ("garlic",            (), ("garlic", "garlic clove", "garlic cloves", "cloves of garlic",
                               "minced garlic", "garlic powder", "garlic paste")),
    ("onion",             (), ("onion", "onions", "red onion", "red onions", "white onion",
                               "yellow onion", "spring onion", "spring onions", "scallion",
                               "scallions", "shallot", "shallots", "leek", "leeks", "chive", "chives")),
    ("tomato",            (), ("tomato", "tomatoes", "cherry tomatoes", "plum tomatoes",
                               "canned tomatoes", "tinned tomatoes", "chopped tomatoes",
                               "tomato paste", "tomato puree", "passata", "sun dried tomatoes",
                               "tomato sauce", "sundried tomatoes")),
    ("potato",            (), ("potato", "potatoes", "new potatoes", "baby potatoes",
                               "sweet potato", "sweet potatoes", "yam", "yams")),
    ("carrot",            (), ("carrot", "carrots", "baby carrots")),
    ("rice",              (), ("rice", "white rice", "brown rice", "basmati rice", "jasmine rice",
                               "arborio rice", "sushi rice", "wild rice", "rice noodles",
                               "rice vinegar", "rice flour")),
    ("lettuce",           (), ("lettuce", "romaine", "romaine lettuce", "iceberg lettuce",
                               "salad leaves", "mixed greens", "rocket", "arugula", "watercress")),
    ("spinach",           (), ("spinach", "baby spinach", "kale", "chard", "swiss chard",
                               "collard greens", "cabbage", "red cabbage", "bok choy", "pak choi")),
    ("pepper_veg",        (), ("bell pepper", "bell peppers", "red pepper", "green pepper",
                               "yellow pepper", "capsicum", "chilli", "chili", "chillies",
                               "chilies", "jalapeno", "jalapenos", "chilli flakes",
                               "red pepper flakes", "chili powder", "cayenne", "paprika",
                               "smoked paprika")),
    ("mushroom",          (), ("mushroom", "mushrooms", "button mushrooms", "cremini",
                               "portobello", "shiitake", "porcini", "chestnut mushrooms")),
    ("courgette",         (), ("zucchini", "courgette", "courgettes", "zucchinis", "squash",
                               "pumpkin", "cucumber", "cucumbers")),
    ("broccoli",          (), ("broccoli", "cauliflower", "brussels sprouts", "green beans",
                               "asparagus", "peas", "frozen peas", "sugar snap peas",
                               "mangetout", "snow peas", "corn", "sweetcorn", "sweet corn")),
    ("beans",             (), ("black beans", "kidney beans", "cannellini beans", "white beans",
                               "chickpeas", "chick peas", "garbanzo beans", "lentils",
                               "red lentils", "green lentils", "pinto beans", "borlotti beans",
                               "hummus", "houmous", "haricot beans")),
    ("herbs",             (), ("basil", "parsley", "flat leaf parsley", "coriander", "cilantro",
                               "mint", "thyme", "rosemary", "sage", "oregano", "dill", "tarragon",
                               "bay leaf", "bay leaves", "herbs", "mixed herbs", "italian seasoning")),
    ("spices",            (), ("cumin", "coriander seed", "turmeric", "cinnamon", "clove",
                               "cloves", "cardamom", "ginger", "fresh ginger", "ground ginger",
                               "allspice", "star anise", "fennel seeds", "saffron", "curry powder",
                               "garam masala", "vanilla", "vanilla extract", "vanilla essence",
                               "curry paste", "za'atar", "sumac")),
    ("sugar",             (), ("sugar", "caster sugar", "granulated sugar", "brown sugar",
                               "icing sugar", "powdered sugar", "confectioners sugar",
                               "demerara sugar", "maple syrup", "golden syrup", "agave",
                               "agave nectar", "molasses", "treacle", "corn syrup")),
    ("chocolate",         (), ("dark chocolate", "cocoa", "cocoa powder", "cacao",
                               "unsweetened chocolate", "bittersweet chocolate",
                               "dark chocolate chips")),
    ("vinegar",           (), ("vinegar", "white vinegar", "cider vinegar", "apple cider vinegar",
                               "balsamic vinegar", "red wine vinegar", "white wine vinegar")),
    ("citrus",            (), ("lemon", "lemons", "lemon juice", "lemon zest", "lime", "limes",
                               "lime juice", "lime zest", "orange", "oranges", "orange juice",
                               "orange zest", "grapefruit")),
    ("fruit",             (), ("apple", "apples", "banana", "bananas", "pear", "pears",
                               "strawberry", "strawberries", "blueberry", "blueberries",
                               "raspberry", "raspberries", "blackberries", "grapes", "mango",
                               "pineapple", "peach", "peaches", "plum", "plums", "cherry",
                               "cherries", "avocado", "avocados", "raisins", "dates", "figs",
                               "cranberries", "pomegranate")),
    ("leavening",         (), ("baking powder", "baking soda", "bicarbonate of soda", "yeast",
                               "active dry yeast", "instant yeast", "cream of tartar",
                               "cornstarch", "cornflour", "corn starch", "xanthan gum",
                               "arrowroot", "tapioca starch", "potato starch")),
    ("stock_veg",         (), ("vegetable stock", "vegetable broth", "stock", "broth",
                               "stock cube", "bouillon", "vegetable bouillon")),
    ("olives",            (), ("olive", "olives", "black olives", "green olives", "capers",
                               "gherkins", "pickles", "sauerkraut", "kimchi")),
    ("seeds",             (), ("sunflower seeds", "pumpkin seeds", "chia seeds", "flax seeds",
                               "flaxseed", "linseed", "poppy seeds", "hemp seeds", "quinoa",
                               "millet", "buckwheat", "amaranth", "polenta", "cornmeal", "grits")),
    ("gluten_free_flour", (), ("gluten free flour", "gluten-free flour", "chickpea flour",
                               "gram flour", "besan", "coconut flour", "cassava flour")),
    ("misc_safe",         (), ("salsa", "guacamole", "sriracha", "hot sauce", "tabasco",
                               "harissa", "pesto rosso", "tomato ketchup", "ketchup",
                               "vegetable", "vegetables", "mixed vegetables", "salad",
                               "parchment paper", "aluminium foil")),
]


# --------------------------------------------------------------------------
# Index construction
# --------------------------------------------------------------------------

def _normalise(text: str) -> List[str]:
    """Lowercase, strip punctuation, split hyphens, drop measurement noise."""
    text = text.lower()
    # Keep % and & out; turn everything non-alphanumeric into a space so that
    # hyphens, slashes, commas and parentheses all become token boundaries.
    text = re.sub(r"[^a-z0-9']+", " ", text)
    text = text.replace("'", "")
    return [t for t in text.split() if t]


# Quantity, unit and preparation words are removed before resolution so that
# "2 tbsp finely chopped fresh parsley" resolves on "parsley".
_NOISE_WORDS = {
    "a", "an", "the", "of", "or", "and", "to", "for", "into", "plus", "about",
    "approximately", "roughly", "such", "as", "optional", "taste", "needed",
    "cup", "cups", "tablespoon", "tablespoons", "tbsp", "tbs", "teaspoon",
    "teaspoons", "tsp", "gram", "grams", "g", "kg", "kilogram", "kilograms",
    "ounce", "ounces", "oz", "pound", "pounds", "lb", "lbs", "ml", "millilitre",
    "millilitres", "litre", "litres", "liter", "liters", "l", "pinch", "dash",
    "handful", "can", "cans", "tin", "tins", "package", "packages", "packet",
    "jar", "jars", "bunch", "bunches", "sprig", "sprigs", "slice", "slices",
    "piece", "pieces", "serving", "servings", "large", "small", "medium",
    "extra", "fresh", "freshly", "frozen", "dried", "ground", "chopped",
    "finely", "coarsely", "thinly", "sliced", "diced", "minced", "grated",
    "shredded", "crushed", "peeled", "seeded", "trimmed", "halved", "quartered",
    "cubed", "melted", "softened", "room", "temperature", "cooked", "uncooked",
    "raw", "warm", "cold", "hot", "boiling", "toasted", "roasted", "washed",
    "rinsed", "drained", "divided", "packed", "level", "heaped", "heaping",
    "quality", "good", "best", "organic", "free", "range", "unsalted", "salted",
    "plain", "whole", "half", "quarter", "third", "cut", "torn", "beaten",
    "lightly", "well", "very", "your", "favourite", "favorite", "store",
    "bought", "homemade", "leftover", "thawed", "juice", "zest",
}
# Words that are part of a canonical alias must never be filtered as noise.
# "unsalted butter", "lemon juice", "whole milk", "free range egg" all depend
# on this, so the noise list is applied only to leftover tokens, never to a
# phrase that already matched.


def _build_index():
    index: Dict[str, str] = {}
    categories: Dict[str, Set[str]] = {}
    display: Dict[str, str] = {}
    aliases_by_id: Dict[str, List[str]] = {}
    max_len = 1
    for cid, cats, aliases in _ENTRIES:
        categories[cid] = set(cats)
        display[cid] = cid.replace("_", " ")
        aliases_by_id[cid] = list(aliases)
        for alias in aliases:
            toks = _normalise(alias)
            if not toks:
                continue
            key = " ".join(toks)
            # First writer wins; the table is ordered so that specific entries
            # precede general ones where an alias is shared.
            index.setdefault(key, cid)
            max_len = max(max_len, len(toks))
            # Regular plural, generated at build time so it lives in the table
            # and is covered by the alias round-trip test.
            if not key.endswith("s"):
                index.setdefault(key + "s", cid)
                if key.endswith(("ch", "sh", "x", "z", "ss")):
                    index.setdefault(key + "es", cid)
    return index, categories, display, aliases_by_id, max_len


PHRASE_INDEX, CATEGORIES_BY_ID, DISPLAY_BY_ID, ALIASES_BY_ID, MAX_PHRASE_LEN = _build_index()


# --------------------------------------------------------------------------
# Resolution
# --------------------------------------------------------------------------

def resolve_text(text: str) -> Tuple[List[str], List[str]]:
    """
    Resolve a piece of ingredient text into canonical ids.

    Longest-phrase-first over a word-boundary token stream. Returns
    (canonical_ids, unresolved_tokens). Substring containment is never used.
    """
    tokens = _normalise(text)
    resolved: List[str] = []
    unresolved: List[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        hit = None
        span = 0
        for length in range(min(MAX_PHRASE_LEN, n - i), 0, -1):
            key = " ".join(tokens[i:i + length])
            if key in PHRASE_INDEX:
                hit = PHRASE_INDEX[key]
                span = length
                break
        if hit is not None:
            if hit not in resolved:
                resolved.append(hit)
            i += span
        else:
            tok = tokens[i]
            if tok not in _NOISE_WORDS and not tok.isdigit() and tok not in unresolved:
                unresolved.append(tok)
            i += 1
    return resolved, unresolved


def categories_for(canonical_id: str) -> Set[str]:
    return CATEGORIES_BY_ID.get(canonical_id, set())


def resolve_declaration(declared: str) -> Set[str]:
    """
    Map a user's declared restriction onto table categories.

    Returns an empty set when the table cannot screen for it. An empty set is a
    signal to report UNKNOWN and say so — it is never treated as "nothing to
    check" and therefore never as safe.
    """
    key = " ".join(_normalise(declared))
    if key in DECLARATION_ALIASES:
        return set(DECLARATION_ALIASES[key])
    if key in ALL_CATEGORIES:
        return {key}
    # A declaration naming a specific ingredient the table knows is screened as
    # that ingredient's categories, e.g. "cashew" -> tree_nuts.
    ids, _ = resolve_text(declared)
    cats: Set[str] = set()
    for cid in ids:
        cats |= categories_for(cid)
    return cats
