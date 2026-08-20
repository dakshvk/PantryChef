# How to Build Your Own Recipe Corpus

_August 2026. Companion to `COMPETITIVE_ANALYSIS.md` and `PRODUCT_STRATEGY.md`._

---

## The insight that makes this possible

Google gives recipe sites rich results — the photo, star rating, and cook time that show up directly
in search — but only if the page publishes **schema.org/Recipe structured data**, usually as JSON-LD
in a `<script>` tag. Rich results drive enormous traffic, so essentially every food blog and recipe
site on the internet **voluntarily publishes a clean, machine-readable version of every recipe**, in
a standardized schema, for free.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Recipe",
  "name": "Pasta Arrabiata",
  "recipeIngredient": ["200g penne", "3 cloves garlic", "1 tsp red pepper flakes"],
  "recipeInstructions": [{"@type": "HowToStep", "text": "Boil the pasta..."}],
  "cookTime": "PT20M",
  "recipeYield": "2 servings",
  "nutrition": {"@type": "NutritionInformation", "calories": "450 calories"}
}
</script>
```

That is the entire technical answer to "how did they get millions of recipes." It is not exotic
scraping — it is reading a standardized format that publishers put there on purpose.

Mature open-source tooling already does the parsing:

- **`recipe-scrapers`** (Python) — the standard library for this, hundreds of site-specific parsers
  with schema.org fallback.
- **`scrape-schema-recipe`** (Python) — parses schema.org Recipe from Microdata/JSON-LD into dicts.

---

## How each company actually did it

| Company | Method | What it cost them | Can you copy it? |
|---|---|---|---|
| **SuperCook** | Crawls ~18,000 sites for schema.org Recipe data → ~11M recipes in 20 languages. **Indexes ingredients, links out to the source site for instructions.** | Years of crawler engineering and maintenance | Yes — but see the legal structure below |
| **Allrecipes / Food.com** | User-generated content. Users submit recipes; the ToS grants the platform a license. | Two decades of community building | Yes, slowly — and you own the result forever |
| **Yummly** | Aggregation + publisher partnerships + acquisition by Whirlpool. Shut down Dec 2024. | Real BD spend | Partially |
| **Paprika / Samsung Food** | Users import recipes from URLs; the app parses the JSON-LD. The user brings the corpus. | Near zero | **Yes — this is your cheapest path** |
| **Spoonacular / Edamam** | Aggregate, structure, and license the data to developers like you | It's their whole business | You're currently a customer of this |
| **Tier-3 AI apps** | Generate recipes with an LLM. No corpus at all. | Nothing — and it shows in quality | Don't |

### The legal structure that makes SuperCook work

This is the part that matters most for you.

SuperCook is **a search engine, not a publisher**. It indexes the *ingredient lists* — which are
uncopyrightable facts — and when you click a recipe it sends you to the original site for the
instructions. The source sites get traffic, so they don't object; SuperCook never republishes
protected expression, so there's nothing to sue over.

That's the trick: **index the facts, link for the prose.** It's the same structure Google Search
operates under, and it's been stable for 15 years.

You can legally do exactly this today.

---

## Your four viable sources, ranked

### 1. User imports — cheapest, and it compounds (do this first)

Ship "paste a recipe URL." Parse the JSON-LD. Save the structured result to the user's account.

Why this is the best option available to you:

- **Users build your corpus for you**, one recipe at a time, at zero marginal cost.
- It is a **retention feature in its own right** — the single most-loved feature in Paprika and
  Samsung Food. You'd build it anyway.
- Your ToS grants you a license to what users import, so the legal position is clean.
- Every import tells you what people actually cook — that's ranking signal no competitor has.
- It seeds the ingredient ontology: every import surfaces real-world ingredient strings to canonicalize.

Start here. It's a weekend of work and it's the only source that gets better the more users you have.

### 2. Index-and-link crawl — breadth, SuperCook's model

Crawl sites publishing schema.org Recipe. Store **only**: ingredient lists (facts), times, yields,
cuisine tags, nutrition, and the source URL. Do **not** store instruction prose. Link out to cook.

- Respect `robots.txt`, rate-limit, identify your crawler honestly.
- This gets you breadth fast and is how you'd ever reach SuperCook-scale coverage.
- Cost: ongoing crawler maintenance forever. Sites change, parsers break.

Do this in phase 2, once imports have proven the parsing pipeline.

### 3. Your own written recipes — the differentiated core

For your top few hundred recipes — the ones that actually get cooked — **write the instructions
yourself**. You then own that content outright, with no attribution, no link-out, and no risk.

This is where the product becomes genuinely yours: consistent voice, tested, correctly scaled, with
proper allergen tagging from the start. A curated 500 you own beats 11M you rent, for the segment
you're targeting. It's also the only content you can safely put in a cook mode, read aloud, or feed
to the conversational chef.

### 4. Public domain — useful for the ontology, not the corpus

As of 2026, US works published in **1930 or earlier** are in the public domain. Project Gutenberg
and the Internet Archive have hundreds of digitized cookbooks (Mrs. Beeton, the 1896 Boston
Cooking-School Cook Book, USDA extension bulletins).

Reality check: these are archaic ("take a pint of sweet milk and a gill of..."). They're poor
recipe content for a modern app. But they're **excellent for bootstrapping the ingredient ontology**
— thousands of ingredient names, aliases, and historical variants, free and unrestricted.

Also free and unrestricted: **USDA FoodData Central** for nutrition. Federal government works are
public domain. Use it instead of paying for nutrition data.

### Do NOT use: academic recipe datasets

Worth stating explicitly because it's a common trap. **RecipeNLG** (2.2M recipes, all over Kaggle)
is licensed for **non-commercial research and education only**. **Recipe1M+** is MIT academic and
ships URL lists rather than the data. Most large Kaggle recipe dumps are scraped from Food.com or
Allrecipes with no clear license at all.

They're fine for a class project. Using one in a company is a licensing violation that surfaces the
moment anyone does diligence on you. Check the license on every dataset, every time.

---

## Recommended sequence

1. **Import from URL** (JSON-LD parsing) — corpus + retention feature in one.
2. **Ingredient ontology** seeded from imports + public domain sources + USDA FoodData Central.
3. **Write your own** top 200–500 recipes for the curated, fully-owned core.
4. **Index-and-link crawl** for breadth, once the parsers are proven.
5. **Migrate off Spoonacular** as owned coverage grows. Never mirror it (1-hour cache limit).

The endpoint: a corpus you own, an ontology that makes safety deterministic, and Spoonacular reduced
from dependency to optional fallback.

---

## Sources

- [Recipe Schema Markup — Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/recipe)
- [schema.org/Recipe](https://schema.org/Recipe)
- [recipe-scrapers (Python)](https://github.com/hhursev/recipe-scrapers)
- [scrape-schema-recipe (Python)](https://github.com/micahcochran/scrape-schema-recipe)
- [RecipeNLG on Kaggle](https://www.kaggle.com/datasets/paultimothymooney/recipenlg)
- [Recipe1M+ paper](https://arxiv.org/pdf/1810.06553)
- [Project Gutenberg — Cookbooks and Cooking](https://www.gutenberg.org/ebooks/bookshelf/419)
- [Spoonacular Terms of Use](https://spoonacular.com/food-api/terms)
- [Are Recipes and Cookbooks Protected by Copyright — Copyright Alliance](https://copyrightalliance.org/are-recipes-cookbooks-protected-by-copyright/)
- [Instacart Developer Platform](https://docs.instacart.com/developer_platform_api)
- [Instacart — Create shopping list page](https://docs.instacart.com/developer_platform_api/api/products/create_shopping_list_page)
- [Instacart — Recipe page concept](https://docs.instacart.com/developer_platform_api/guide/concepts/recipe)
