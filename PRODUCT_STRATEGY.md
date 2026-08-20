# PantryChef — Product Strategy & Feature Gap Analysis

_August 2026. Companion to `COMPETITIVE_ANALYSIS.md`. Covers the owned-corpus plan,
deterministic safety, meal prep, grocery pricing, and the conversational chef._

---

## 0. Two blockers to resolve before building

### 0.1 You cannot legally store Spoonacular's recipes

Spoonacular's Terms of Use permit caching user-requested data **for a maximum of 1 hour**, after
which you must delete the cache and refresh from the API. Building a persistent database of their
recipes is a direct violation, and it would be the kind of violation that is trivially discoverable
(they can see your call patterns) and that kills an acquisition or a funding round during diligence.

Their terms also require you to display disclaimers about the accuracy of allergy, cost, and
nutrition data — relevant given the safety positioning.

**This does not kill the owned-corpus plan. It changes where the data comes from.**

### 0.2 What you *can* legally own

US copyright law is unusually favorable here:

- **Ingredient lists are not copyrightable.** They are factual statements
  (Copyright Office Compendium; _Tomaydo-Tomahdo v. Vozary_, 6th Cir.).
- **Simple sets of directions are not copyrightable** — functional instructions are statutorily excluded.
- **Substantial literary expression IS copyrightable** — headnotes, creative descriptions, the
  narrative voice of a cookbook, personal stories, styled photography.

So the legal path to an owned corpus is:

| Can own | Cannot take |
|---|---|
| Normalized ingredient lists and quantities | Verbatim instruction prose from a source |
| Structured facts: times, yields, techniques, cuisine tags | Cookbook headnotes and creative descriptions |
| Nutrition computed from a public source (USDA FoodData Central) | Source photography |
| **Your own written instructions** for a dish | Bulk copies of a licensed API's records |

**Do not scrape cookbooks.** Their expressive content is exactly the protected part, publishers
actively enforce, and it is the highest-risk, lowest-reward data source available. If you want
cookbook content, license it — that is a business development conversation, not an engineering task.

**Recommended architecture:** Spoonacular stays as the live discovery layer (respecting the 1-hour
cache) while you bootstrap a legally clean owned corpus from public-domain and openly-licensed
sources plus your own written instructions. Migrate traffic to the owned corpus as coverage grows.
Never mirror Spoonacular into it.

---

## 1. Why the owned database matters more than you think

The stated reason is cost and independence. Those are real. But the **more important** reason is
that it is the only way to make deterministic dietary safety actually work.

Right now safety is keyword matching over free-text ingredient strings, with Gemini as the
tiebreaker. That is fundamentally capped — you are doing string matching on human-written text
forever, and no amount of keyword tuning fixes it.

What you actually want is an **ingredient ontology**: canonical ingredient IDs, each carrying
structured allergen and diet tags, with an alias table mapping the thousands of ways people write
the same thing.

```
ingredient_id: 4412
canonical:     "coconut cream"
aliases:       ["coconut cream", "creamed coconut", "thick coconut milk", ...]
allergens:     {tree_nut: contested, dairy: false, gluten: false, soy: false}
diets:         {vegan: true, vegetarian: true, dairy_free: true}
```

With this, "coconut cream is dairy-free" is a **database lookup, not a judgment call**. It is
correct 100% of the time, costs nothing, returns in microseconds, and is auditable — you can point
at a row and explain a decision. That is what a safety claim needs.

This is the real payoff of owning your data, and it should drive the schema design.

---

## 2. Deterministic safety: your instinct is right, one correction

You said dietary restrictions should be deterministic and not rely on the LLM. Correct. Make it an
architectural invariant:

> **An LLM may never move an ingredient from unsafe to safe. It may only narrow the safe set,
> never widen it.**

The current design violates this. Per the README, the Gemini Safety Jury *approves* flagged
ingredients — "coconut cream in a dairy-free context gets approved." That means a model
hallucination becomes an allergic reaction. It is the one failure mode that ends the company.

Restructure to three tiers:

| Tier | Mechanism | Can it approve? |
|---|---|---|
| **Known safe** | Ingredient in ontology, tags clear | Yes — deterministic |
| **Known unsafe** | Ingredient in ontology, allergen tagged | Hard reject, no appeal, no LLM |
| **Unknown** | Not in ontology, or ambiguous | **Reject and queue for human review** — never LLM-approved |

Unknown ingredients get excluded from results *and* logged. That queue is your ontology backlog and
it shrinks over time. Coverage becomes a metric you can report: "94% of ingredients encountered
resolve deterministically."

Gemini keeps the jobs it is actually good at: writing the pitch, explaining substitutions,
parsing messy ingredient strings into candidate canonical IDs (a *suggestion* a human confirms),
and conversational Q&A. None of those are safety decisions.

**Marketing consequence:** you can then say "our allergen filtering is deterministic — it does not
ask an AI whether your kid's food is safe." Not one competitor can say that. That is the entire
positioning in one sentence.

---

## 3. Feature gap: them vs. you

### What competitors have that you don't

| Feature | Who has it | Priority | Notes |
|---|---|---|---|
| **Photo ingredient input** | Every 2025–26 AI app | **P0** | Table stakes for onboarding. Typing 15 ingredients is the main drop-off. |
| **Persistent pantry inventory** | SuperCook (session), most planners | **P0** | You have none. No retention without it. |
| **Accounts / saved data** | All | **P0** | Two stateless endpoints today. |
| **Mobile app** | All | **P1** | Cooking is a phone activity. |
| **Cook mode** (step-by-step, screen-on) | Mealime, Samsung Food, Paprika | **P1** | A known SuperCook complaint you also have. |
| **Portion scaling** | Mealime, Eat This Much, Paprika | **P1** | Cheap to build, constantly requested. |
| **Grocery list generation** | Mealime, Prepear, Plan to Eat, Samsung Food | **P1** | Prerequisite for cart-attach revenue. |
| **Meal planning calendar** | Mealime, Eat This Much, Prepear, Plan to Eat | **P2** | Your planned feature. See §4. |
| **Macros / calorie targets** | Eat This Much, Mealime Pro | **P2** | Eat This Much owns the macro-first niche. |
| **Recipe import from web/social** | Paprika, Samsung Food, FoodiePrep | **P2** | Strong retention feature, well-liked. |
| **Expiry / freshness tracking** | NoWaste, Kitche, some planners | **P1** | See §6 — this is underrated. |
| **Cart / delivery integration** | Samsung Food, Instacart-partnered apps | **P1** | This is the revenue mechanism. |
| **Breadth of corpus** | SuperCook (~11M recipes) | — | Don't chase. You lose. |

### What you have that they don't

| Advantage | Defensibility | Notes |
|---|---|---|
| **Retrieved, real recipes** (not LLM-invented) | Medium | Tier-3 AI apps hallucinate timings and nutrition. You don't. Strongest marketing claim. |
| **Deterministic multi-layer allergen safety** | **High** | Especially once the ontology exists. Nobody else treats safety as architecture. |
| **Transparent scoring** (explainable ranking) | Medium | Users see *why* a recipe ranked. Competitors are black boxes. |
| **Never-zero-results semantic fallback** | Low | Good UX, copyable in a sprint. |
| **Pantry-aware substitutions** | Low–Medium | Grounded in what you actually have, not a generic swap table. Becoming table stakes. |
| **Mood / profile weighting** | Low | Nice product thinking, not a moat. |

**The honest read:** exactly one item on the right-hand side is genuinely defensible. Concentrate
there and treat the rest as supporting features.

---

## 4. Meal prep: build it, but differently

Mealime, Eat This Much, Prepear, and Plan to Eat all own this space, and they are good. Do not build
a generic meal planner — you will be the 12th-best one.

**Every one of them plans forward from zero.** They assume an empty kitchen and generate a shopping
list. That is the opposite of your premise.

Three genuinely differentiated angles:

1. **Inventory-depleting plans.** Generate a week that consumes what you already have, in the right
   order, then lists only the gap. Nobody does this because nobody tracks inventory properly.
2. **Ingredient overlap optimization.** Buy one bunch of cilantro, use it across three meals so it
   doesn't rot. This is your Pantry Cleaner profile extended to a week, it is a real optimization
   problem, and it maps directly to a dollar figure users feel. USDA figures put avoidable household
   food waste around $1,500/year — a plan that demonstrably cuts it is a concrete pitch.
3. **Perishability sequencing.** Cook the spinach Tuesday and the potatoes Sunday, because that is
   the order they die in. This is a scheduling constraint no competitor models.

Calories and macros: include them, but as a **display and filter** layer, not the pitch. Eat This
Much owns macro-first planning and beating them there is not your fight.

---

## 5. Cheapest place to buy produce: don't build this yet

This is the hardest item on your list by a wide margin, and the payoff is the smallest.

**Why it's hard:**
- No clean legal cross-retailer pricing API exists. Kroger offers one for its own banners; that's
  roughly it for first-party access.
- Prices are **zip-code and store specific**, so a national price database is meaningless — you need
  per-store, per-zip resolution.
- Instacart renders prices client-side and varies them by delivery zone, so extracting them means
  browser automation against anti-bot defenses.
- Scraping retailers is legally grey, breaks constantly, and is a permanent maintenance tax on a
  team of one.

**Do this instead — same user value, 10% of the work, and it's your revenue line:**

Use the **Instacart Developer Platform** to build "you're missing 2 ingredients → add to cart."
It's legal, supported, one integration, and it converts at the highest-intent moment in your funnel.
Affiliate/partner economics on grocery are where the money actually is.

If you still want price signal afterward, add **one** retailer via the Kroger API and show a single
honest estimate rather than a fake cross-retailer comparison. Ship price comparison in v3, if ever.

---

## 6. The retention mechanic — no longer unclaimed

> **Correction (Aug 2026):** an earlier version of this section said no competitor had built this
> loop. That is wrong. **Eatvora** has built essentially all of it — receipt scanning, expiry
> tracking with color-coded urgency, a "Rescue Mode" that flags what to use first, and household
> sharing for up to five people. The loop below is still the right architecture, and it is still
> the reason to build inventory, but it is no longer a first-mover advantage. See §6.5.

SuperCook makes you re-enter your pantry every single visit. Most competitors are a **search box** —
you show up when you already have the intent. That's why most of this category has poor retention.

The loop that turns this into a company:

1. User stocks their pantry once (photo or receipt scan — that's what photo input is *for*).
2. Cooking a recipe **decrements** the inventory.
3. The system knows what's about to expire.
4. **Push: "Your spinach dies in 2 days. Here are 3 things you can make tonight."**

That flips the product from pull to push. You generate the intent instead of waiting for it. It is
the single highest-leverage feature on this entire list, it's the reason to build the inventory
system, and it compounds: the longer someone uses it, the better it knows their kitchen and the
harder it is to leave.

It also produces the data asset — real consumption patterns per household — that few others in
this space have.

---

## 6.5 Eatvora — the closest competitor found so far

Eatvora (iOS, Android; developer Zekeria Abdi) is materially closer to PantryChef's roadmap than
SuperCook is, and closer than any Tier-3 photo app. Assume it is the benchmark.

**What it already has that PantryChef doesn't:**

- Receipt scanning, barcode scanning, and expiry-date OCR for inventory capture
- Color-coded urgency (red expired → orange 1–2 days → yellow 3–7 days → green safe)
- "Pantry Health Score" and "Rescue Mode" — use-this-first surfacing
- Household sharing for up to 5 people on one pantry
- Shopping Planner drawing from five sources at once (low stock, lists, planned meals, chores, occasions)
- Meal planning across breakfast/lunch/dinner/snacks, with calorie targets and macro splits
- Chore and occasion scheduling
- Shipping on mobile, with a real pricing model

**Pricing:** Free tier caps at 25 pantry items and 3 AI recipes/day. Premium $4.99/mo (unlimited
items, better receipt reading, meal planning). Plus $9.99/mo (household sharing, chores, occasions).

**Where PantryChef can still be genuinely different:**

| Dimension | Eatvora | PantryChef |
|---|---|---|
| **Recipe source** | **AI-generated** (metered — 3/day free) | **Retrieved, real recipes** with tested instructions and true nutrition |
| **Allergen handling** | Restrictions as preferences fed into generation | Deterministic ontology lookup; LLM can never approve |
| **Product scope** | Household management — pantry, meals, shopping, **chores, occasions** | Focused on the cooking decision |
| **Core job** | Inventory-first: track everything, then suggest | Decision-first: what do I cook right now |
| **Maturity** | Newer, smaller, tight free tier | Earlier, but unconstrained |

**The strategic read:**

1. Their existence **validates the thesis**. Someone else concluded the inventory-expiry loop is the
   right architecture. That's good news about the market, bad news about the head start.
2. **Generated recipes + prompt-level dietary restrictions is the least safe combination possible.**
   If restrictions are a preference string in a generation prompt, there is no safety guarantee at
   all — the model can invent a dish containing anything. The deterministic-safety wedge cuts
   *harder* against Eatvora than against SuperCook, not softer.
3. **Their breadth is an opening.** Bundling chores and occasion planning means they are becoming a
   household organizer, not a cooking app. Nobody is going deep on the quality of the cooking
   decision itself. That is the lane.
4. **Their paywall is tight.** 3 AI recipes/day free, with the best features behind $4.99–9.99.
   Reviewers already note this. A more generous free core on the thing users actually came for is
   a viable wedge.

**Action:** download it, use it for two weeks, and log every point of friction. Do this before
writing any more inventory code — they have already made the mistakes you are about to make.

---

## 7. Conversational AI chef: last, not first

Build it, but understand it is the **least differentiated** thing on your list. Every Tier-3 app
already ships a chat interface and none of them retain users because of it.

A chatbot over a generic model is a commodity. A chatbot grounded in *your* pantry inventory, *your*
recipe corpus, and *your* deterministic safety layer is a genuine interface advantage — it can say
"you have that already, it's in the back of the fridge" and "no, that substitution breaks your
dairy restriction."

So it's valuable **only after** §1, §2, and §6 exist. Built before them, it's a demo. Built after,
it's the natural interface to everything else. Sequence accordingly.

Non-negotiable: route every dietary question through the deterministic layer. The chat surface must
never become the back door that lets an LLM approve an allergen.

---

## 8. Features worth taking from competitors

Ordered by value-to-effort:

1. **Portion scaling** — trivial, constantly requested (Mealime, Paprika).
2. **Cook mode** — step-by-step, screen stays awake, timers inline (Mealime, Samsung Food).
3. **Photo → ingredients** — table-stakes onboarding (every Tier-3 app).
4. **Receipt scanning** — better inventory capture than photographing a fridge; a receipt is
   structured text and tells you quantities.
5. **Grocery list grouped by store aisle** — small touch, disproportionately loved (Prepear).
6. **Recipe import from URL / social** — high retention, and it grows your corpus with
   user-supplied content you have a license to via your ToS (Paprika, Samsung Food, FoodiePrep).
7. **Leftover handling** — "you made 4 servings, ate 2" → leftovers become pantry inventory.
   Nobody closes this loop and it's a direct extension of what you already do.
8. **Household sharing** — shared pantry across roommates or family. Retention multiplier, and it's
   free virality. Very relevant to an Isla Vista house of five.

---

## 9. Recommended sequence

**Phase 1 — Foundation (nothing works without this)**
1. Accounts + persistent pantry inventory
2. Ingredient ontology with allergen/diet tags + alias table
3. Refactor safety so the LLM can never approve (§2)
4. Own-corpus schema, seeded legally (§0.2), Spoonacular stays live-only

**Phase 2 — The loop**
5. Photo and receipt ingredient capture
6. Cooking decrements inventory; leftovers return to it
7. Expiry tracking + push notifications (§6)
8. Cook mode + portion scaling

**Phase 3 — Planning and money**
9. Inventory-depleting weekly plans with overlap optimization (§4)
10. Grocery list generation
11. Instacart cart-attach (§5) — first revenue
12. Mobile app

**Phase 4 — Interface**
13. Conversational chef grounded in all of the above (§7)
14. Price signal, single retailer, if it still matters

---

## 10. Positioning, restated

> **PantryChef tells you what to cook with what you already have — with real tested recipes, not
> AI-invented ones, and allergen filtering that's deterministic code, not a language model's guess.**

Everything in this document serves that sentence. The meal planner, the cart integration, and the
chef are features. The inventory loop is the business. The deterministic safety layer is the moat.

---

## Sources

- [Spoonacular Terms of Use](https://spoonacular.com/food-api/terms)
- [Are Recipes and Cookbooks Protected by Copyright — Copyright Alliance](https://copyrightalliance.org/are-recipes-cookbooks-protected-by-copyright/)
- [Circular 33: Works Not Protected by Copyright — US Copyright Office](https://www.copyright.gov/circs/circ33.pdf)
- [Secret Ingredients: How to Protect Recipes — NYC Bar Association](https://www.nycbar.org/reports/secret-ingredients-how-to-protect-recipes/)
- [Instacart Developer Platform docs](https://docs.instacart.com/developer_platform_api)
- [How to Build a Grocery Price Comparison Tool — Scrapfly](https://scrapfly.io/blog/posts/how-to-build-a-grocery-price-comparison-tool-with-python)
- [Mealime](https://www.mealime.com/)
- [10 Best Meal Planning Apps in 2026 — FoodiePrep](https://www.foodieprep.ai/blog/meal-planning-apps-in-2026-which-tools-actually-simplify-your-kitchen)
- [Best Meal Planning Apps 2026 — My Subscription Addiction](https://www.mysubscriptionaddiction.com/meal-planning-service-apps)
