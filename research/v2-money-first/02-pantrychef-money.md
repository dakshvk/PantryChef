# PantryChef — Can It Make Money?

_Aug 2026. **WebFetch egress-blocked** — no primary document read, including Cookpad's filings.
All figures from search-result summaries._

---

## THE VERDICT UP FRONT

**Keep PantryChef as a portfolio piece. Do not commercialise it as a consumer app. If you want a
business from this work, rebuild the engine for commercial kitchens.**

The consumer path is closed by arithmetic, not by effort.

---

## 1. Do recipe apps make money? Essentially no.

### Cookpad (TSE: 2193) — the only public pure-play, and it's audited

| Metric | Figure |
|---|---|
| Revenue peak | **¥16.8B** (FY2016) |
| FY2024 | ¥5.88B (−23% YoY) |
| FY2025 | **¥5.34B** (−9.2% YoY) |
| FY2025 net income | ¥741M (−44%); margin 14%, down from 23% |
| Q1 FY2026 | Revenue ¥1.27B (−7.7%), **net loss ¥417M** |
| **Peak to now** | **−68%** |

At ~¥150/USD, FY2025 revenue is roughly **$36M** — less than a mid-sized B2B SaaS company, from the
largest recipe platform in the world outside Allrecipes, with tens of millions of MAU and ~2M paid
subscribers at its peak. Nine consecutive years of decline. First net loss since listing in 2019,
and losing money again in 2026.

**The stated cause applies directly here:** from 2016, consumption shifted from "search and read" to
"watch on video." The *interface* to recipes got disrupted. In 2026 the same thing is happening
again with LLM chat.

### Every other outcome in the category

| Company | Price | Outcome |
|---|---|---|
| **Yummly** | Free + Pro | Whirlpool paid **$100M (2017)** for ~30M users. Entire team laid off Apr 2024. **Shut down 20 Dec 2024** with no warning and no bulk export. |
| **Mealime** | Freemium | **Acquired by Albertsons, 2022.** A grocer bought it. |
| **Whisk → Samsung Food** | $6.99/mo, $59.99/yr | **Acquired by Samsung NEXT, 2019.** Now an appliance funnel, not a P&L. |
| **Crouton** | $8.99/yr | 2024 Apple Design Award winner. **Acquired by Combustion — a thermometer company.** The best-designed recipe app in the world exited to hardware. |
| **AnyList** | $9.99/yr, $14.99/yr household | **~$2M ARR, ~2 employees.** The category's best honest independent outcome. |
| **Paprika** | **One-time** $4.99 / $29.99 | Survives on zero churn and near-zero opex. |
| **Plan to Eat** | $5.95/mo, $49/yr | If all claimed 50k users paid → $2.45M/yr. Unverified they're paying. |
| **PlateJoy** | $12.99/mo, $99/yr | $8.5M revenue est., <25 staff. |

> **The pattern across every single data point: recipe apps get acquired as funnels for something
> that actually monetises — appliances, groceries, hardware. Not one built a durable standalone
> consumer business.**

### The comparison that stings

**MyFitnessPal: $310M revenue in 2025.** Nearly identical technology — roughly **9x Cookpad's entire
global revenue.**

The difference isn't technology. *"Am I getting fat"* is a problem people pay to solve continuously.
*"What's for dinner"* is a problem people solve for free in thirty seconds.

---

## 2. The CAC arithmetic that ends the conversation

Real 2025–26 benchmarks:

- **Food & Drink Day-30 retention: 3.9%** — the worst of any app category. Day-7 is ~7%.
- **Freemium D35 free-to-paid: 2.1%**
- **Median monthly subscriber churn: 13–14%** — the median subscription app replaces its entire
  paying base every 7–8 months
- **US cost per install: ~$4.06**

Therefore:

```
CAC per PAYING subscriber = $4.06 ÷ 0.021  ≈  $193
LTV = ($4.99 − 15% store cut) ÷ 0.135 churn  ≈  $31
```

### **Every paid install loses about $162.**

You'd need a ~6x improvement in conversion *or* retention just to break even on acquisition — before
COGS. And PantryChef **has** COGS: a Spoonacular call plus a Gemini call on every query, paid equally
for the 97.9% who will never pay.

This is not a marketing problem. **Paid acquisition is categorically impossible for a $4.99/mo recipe
app.** The only viable channel is organic — which a solo founder can't control or forecast.

Median subscription app MRR after 18 months: **$8.3K**. Top 5%: >$1.16M/mo. There is no middle.

---

## 3. Every non-subscription model, modelled at reachable scale

| Model | Real economics | At 10K MAU | Verdict |
|---|---|---|---|
| **Freemium subscription** | 2.1% convert, 13.5% churn | ~$890/mo, decaying | Organic only |
| **Display ads** | Food-blog RPM **$10–30** ($30–50 in Q4); Raptive dropped its floor to 25k pageviews Oct 2025 | 50K pv × $20 = **$1,000/mo** | **Most reliable model — but requires being a content site, not an app** |
| **Grocery affiliate** | **Instacart ~3%**; **Amazon groceries 1%**; **Walmart groceries 0%**; Kroger 1.6–4.8% | ~$360/mo | Structurally weak — and you must be the *last* click before checkout |
| **CPG sponsored placement** | Chicory reaches 123M shoppers across 5,200+ sites | ~$0 | Circular — you need the audience first, and Chicory owns supply-side aggregation |
| **White-label to grocers** | Northfork powers Walmart, Target, Coles, Sainsbury's | $0 | Occupied. Moat is retailer SKU mapping, not recipe scoring |
| **Data licensing** | Spoonacular $29–$149+; Edamam free–$999/mo | **$0** | **Impossible by construction — you own no data** |
| **One-time purchase** | Paprika $4.99/$29.99 | ~$1,270 once | Kills churn *and* LTV; only works at zero opex |

**Where the money actually is:** **Instacart advertising revenue hit $1.065B in FY2025** — 9,000+
brands, 1,800+ retail banners. The category's money is enormous and it accrues **entirely to whoever
owns checkout.** Not to whoever owns the recipe.

---

## 4. The structural killers specific to PantryChef

1. **No data asset.** Spoonacular's 1-hour cache limit means you can never accumulate a corpus. Every
   query is a rented API call. No compounding, no defensibility, nothing to license. **This alone
   caps enterprise value near zero.**
2. **A free incumbent with 11M recipes** doing the core job for $0.
3. **LLM chat is a free substitute.** In 2026, *"what can I make with chicken, rice and half a lemon,
   I'm dairy-free"* is a free ChatGPT query. **This is the exact disruption that took Cookpad from
   ¥16.8B to ¥5.34B** — except last time it was video and the incumbent had nine years to die.
   PantryChef would be starting *after* the disruption.
4. **A dozen near-identical AI photo-to-recipe apps** launched 2025–26 at $5–10/mo.
5. **Yummly's death proves the ceiling.** If a $100M asset with 30M users isn't worth keeping alive
   inside the company that wanted it as an appliance funnel, standalone economics are worse than
   they look.

---

## 5. THE PIVOT — point the engine at the walk-in cooler

The core of PantryChef isn't the recipe database — Spoonacular owns that and won't let you keep it.
The core is **a deterministic constraint-satisfaction engine: given an inventory, a hard restriction
set, and an objective function, rank feasible outputs and propose substitutions with an explanation.**

That engine is worth ~$5/month to a consumer and **$79–$199 per month per location** to a kitchen
with a food-cost line on its P&L.

> *"Here's what's in inventory tonight. Here's what you can put on the menu, at what plate cost, at
> what margin, without violating the allergen matrix or the 86 list."*

**Why this pivot specifically:**

1. **The technology transfers almost unchanged.** Ingredient list in → constrained ranked output +
   substitution + explanation. Swap "mood" for "target food cost %", "dietary restriction" for
   "allergen matrix + par levels." Scoring engine, substitution logic and the Gemini explanation
   layer all survive. **The Spoonacular dependency does not — and that's a feature**, because the
   recipes become the customer's own. **You finally own a data asset instead of renting one on a
   one-hour lease.**
2. **Revenue per customer goes up 20–40x.** meez sells at **$79/mo** single-location → **$199/mo**
   multi-unit; MarketMan at **$199–239 per location/month**; Craftable from $99/mo. **Thirty
   locations at $150/mo = $54K ARR** — more than 6,000 consumer subscribers at $4.99 with 14% monthly
   churn, and vastly easier to keep.
3. **Retention inverts.** Consumer food apps retain 3.9% at Day 30. A restaurant that has entered 200
   costed recipes does not churn — **the switching cost is the data entry.**
4. **The buyer is reachable by a solo founder.** meez and Craftable both publish self-serve prices.
   No RFP, no HIPAA, no procurement. **A chef can buy it on a personal card after one demo.** This is
   the only B2B segment in the whole table where that's true.
5. **Validated adjacent expansion.** Winnow built a **$26.3M revenue** business (163 staff, $45M
   raised, IKEA/Compass/Accor) on the same insight — kitchens waste inventory and don't know it — but
   with computer-vision hardware, taking 12 years. A software-only inventory-to-menu layer is the
   capital-light version of the same wedge.

### Second-best pivot: senior living dietary compliance

MealSuite starts at **$175/mo**; the sector transacts at **$3–5 per resident per month**. A 120-bed
facility = $5,760/yr; a 20-facility operator = **$115K/yr**. The incumbents are the least
sophisticated in the B2B table, and *"this resident is renal + diabetic + shellfish-allergic, what
can they eat from tonight's menu"* is **literally PantryChef's existing function with the mood
parameter deleted.** Harder sales motion, higher contract value, real compliance pressure.

### What is *not* the pivot

Grocery retailers (Northfork/Chicory/SideChef own it) · CPG (needs audience first) · health plans
(Foodsmart raised **$200M**; needs an RD network, HIPAA, 12–24 month cycles) · hospitals
(CBORD/Computrition, procurement-gated) · schools (RFPs, USDA certification) · food waste (hardware).

---

## 6. The concrete recommendation

**Ship PantryChef as-is, write it up, put it in the portfolio.** It's a strong artifact of
engineering judgment — deterministic scoring with the LLM confined to validation and explanation is
the *right* architecture, and worth saying so in interviews.

**Then spend a weekend talking to ten chefs about food cost and 86 lists before writing another line
of code.** If they don't bite, you've lost a weekend instead of two years and $193 per subscriber.

---

## Reliability notes

**Most reliable:** Cookpad financials, Instacart advertising revenue, Foodsmart funding, KFF
Medicaid/Medicare figures, RevenueCat benchmarks, and published SaaS prices (meez, MarketMan,
Craftable, MealSuite, AnyList, Plan to Eat, PlateJoy, Spoonacular, Practice Better).

**Unverified — directional only:** AnyList $2M ARR, PlateJoy $8.5M, Winnow $26.3M, Noom $296M, the
SuperCook traffic/AdSense figures, the CBORD $50K+ floor, Nutrislice per-student rates, Nutritics
pricing, and all vendor-claimed conversion lifts.
