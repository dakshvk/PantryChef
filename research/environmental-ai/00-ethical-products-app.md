# Side Question: Is there an app for "companies safe to buy from"?

_Research agent output, Aug 2026. Combined environmental + labor + health consumer scoring._
_Status: findings carry source URLs; a dedicated fact-check pass will re-verify key claims._

**Short answer: no single credible one exists — and the reason matters. Several well-funded
attempts at exactly this already died, and every survivor narrowed its scope to stay alive.**

---

## What exists today

| Name | Rates | Data source | Business model | Key limitation |
|---|---|---|---|---|
| **Yuka** | Food + cosmetics, **health only** | Crowdsourced barcode scans; score = 60% Nutri-Score, 30% additives, 10% organic bonus | Consumer subscriptions only — explicitly refuses affiliate revenue and brand payments | Additive methodology never expert-validated the way Nutri-Score was; reformulation without barcode change silently breaks scores; no corporate layer at all |
| **Good On You** | Fashion + beauty brands, scored on **People / Planet / Animals** — closest to a combined score | 500+ data points, brand *and parent company* reporting, but **publicly available info only** | Affiliate + brand partnerships + data licensing | Can only measure what's disclosed — opaque brands score low regardless of actual conduct; apparel/beauty only |
| **Ethical Consumer** (UK) | Companies across 100+ categories on Climate, Workers, Animals, Tax, Ethos | In-house human researchers | Paid subscription (~£35/yr) | UK-centric, paywalled, no barcode scanner, slow refresh |
| **Open Food Facts** | Food ingredients — a *database*, not a verdict | Volunteer crowdsourcing, open data | Nonprofit | No labor or corporate data whatsoever |
| **EWG Skin Deep** | Cosmetic ingredient hazard | Public toxicology databases | Nonprofit + "EWG Verified" licensing | Hazard-based not risk-based (ignores dose); scores demonstrably inconsistent — Sodium Coceth Sulfate scores 0 while near-identical Sodium Laureth Sulfate scores 4 |
| **Think Dirty** | Cosmetic ingredients | Ingredient lists | **Brands can pay for review**; free listings wait up to a year | Direct independence conflict |
| **Sourcemap** | B2B supply-chain traceability, forced-labor compliance | Supplier-submitted chain of custody | Enterprise SaaS, VC-backed, 250+ brand customers | Proprietary per-customer — can never become a public backbone |
| **KnowTheChain** | Forced labor benchmarking | Public disclosure | Nonprofit | **Only ~145 companies**, biennial refresh; 2025 ICT average 20/100, food & bev median 14/100 |
| **B Corp** | Whole-company certification | Self-reported + verified | Certification fees | Nespresso held certification during child-labor reporting; BrewDog lost status over workplace allegations; new standards April 2025 |
| **Buycott** | Brand → parent → boycott campaigns | Crowdsourced | Unclear | **Dead** — last update Oct 2016 |
| **GoodGuide** | Health + environment + social, 175k products / 5k companies — **the exact product proposed** | In-house scientific ratings | Acquired by UL 2012 | Dropped social/environmental 2016, **shut down 1 June 2020** |
| **DoneGood** | Ethical brand discovery | Curated list | Affiliate | Extension phased out 2022; acquired by Karma Wallet 2024 |
| **Climate Neutral Certified** | Company carbon | Self-reported + offsets | Certification fees | **Label retired** — rebuilt as The Climate Label after consumers lost faith in carbon-neutral claims |

Not yet researched (agent hit its search budget): Project Cece, Know The Origin, Bobby Approved,
Karma Wallet's current product, CDP licensing terms, GOTS/Rainforest Alliance/MSC/ASC/Leaping Bunny.

---

## The six real gaps

**1. Nothing combines environment + labor + health at product level — and the thing that did is dead.**
GoodGuide rated all three across 175,000 products. UL bought it in 2012, stripped the social and
environmental dimensions in 2016, killed it in 2020. Free2Work, Ethical Barcode, RESET: all defunct.
The union of "all three dimensions × all categories × barcode-level" exists nowhere.

**2. The parent-company problem is unsolved in live products.** Buycott was purpose-built for
brand→parent mapping and has been unmaintained since 2016. Good On You does it, but only in
fashion/beauty. Yuka scores a formula, not the firm behind it. The exact scenario — clean-looking
brand owned by a conglomerate with a bad record — has no consumer tool covering groceries,
formula, or beverages.

**3. The labor data does not exist at product resolution.** KnowTheChain, the most credible public
forced-labor benchmark, covers ~145 companies on a two-year refresh. Sourcemap has real traceability
but it's proprietary enterprise data. **There is no public dataset that could power a labor score for
a scanned barcode.** Any app claiming one is inferring, not knowing.

**4. Staleness is structural.** Manufacturers reformulate without changing barcodes. Labor data
refreshes biennially at best. Certifications lag scandals by years — Nespresso held B Corp status
while child-labor reporting was published.

**5. Coverage collapses outside the mainstream.** Roughly half of scanned products returned nothing
in one Korean grocery test of Yuka. Regional chains, private label, and specialty goods lag worst.
Good On You structurally penalizes small and non-Anglophone brands for opacity rather than conduct.

**6. Scoring transparency is partial everywhere.** Yuka publishes its weights (genuinely better than
most) but its additive risk classification was never expert-validated. EWG publishes a rubric but
scores inconsistently. Good On You publishes its framework but not per-brand evidence.

---

## The Yuka critique, reported fairly

The strongest professional criticism is **hazard vs. risk**: Yuka (like EWG and Think Dirty) flags
ingredients by intrinsic hazard classification without weighting dose, concentration, or realistic
exposure. Secondary criticisms: crowdsourced data inherits packaging errors and reformulation drift;
binary good/bad framing has drawn dietitian concern about disordered eating.

Yuka's counterargument is not unreasonable — it concedes imperfection but argues it pushes people
away from heavily processed food, which most nutritionists accept as directionally good. When the
French charcuterie lobby sued Yuka for defamation over nitrite warnings and won €20,000 at first
instance, the Paris Court of Appeal **reversed**, holding that consumer information on nitrate risk
was a matter of general interest protected by freedom of expression. Yuka is contested but has
survived legal attack on the merits.

---

## The two founder examples — what is actually documented

**Celsius:** Celsius Holdings agreed to a **$7.8M class action settlement** over labeling products
"No Preservatives" while containing citric acid; final approval 5 April 2023. That is a *labeling*
finding, not a finding that the product is unsafe. **No existing app would have surfaced this** — a
litigation/enforcement feed is not part of any scanner's data model.

**Infant formula:** Abbott's 2022 Sturgis recall followed FDA inspectors finding *Cronobacter
sakazakii* at the plant; five infants hospitalized, FDA said infections "may have contributed to
death in two patients." DOJ opened a criminal probe in Jan 2023 and closed it in 2026 after federal
labs could not genetically match plant strains to infant isolates.

**The critical counter-example:** **ByHeart** — a startup positioned as the clean challenger brand —
recalled all product in November 2025 in a 51-case infant botulism outbreak, with *C. botulinum*
type A confirmed in an opened can and in 6 of 36 finished-product samples.

**An ingredient-list scorer would have ranked ByHeart above Abbott right up until the recall.**

---

## Why this is hard

**The monetization trap has three exits, all bad:**
1. *Charge brands* → destroys independence (Think Dirty's pay-for-review model)
2. *Affiliate revenue* → you now profit from recommending (Good On You's model)
3. *Charge consumers* → the only clean path, proven exactly once. Yuka, 55M+ users, zero paid
   marketing. Public revenue figures are inconsistent across sources and unverified.

**Adjacent market just detonated.** Aspiration — the flagship "your money is sustainable" consumer
brand — filed Chapter 11 in March 2025; co-founder sentenced to 168 months for a $248M fraud.
Investor appetite for consumer ethical-consumption platforms is currently poisoned.

**The B2B fallback was legislated away.** The obvious "sell data to enterprises" pivot was
underwritten by CSRD/CSDDD. The December 2025 Omnibus deal cut CSRD scope to companies with 5,000+
employees *and* €1.5B+ turnover, restricted CSDDD to direct business partners only, and pushed
compliance to July 2029. The Green Claims Directive was withdrawn outright in June 2025.
**Supply of disclosure data and compelled demand for it shrank in the same year.**

**One genuine tailwind:** the EU Empowering Consumers Directive (2024/825) applies from
**27 September 2026** and bans generic green claims and sustainability labels not grounded in a
certification scheme.

---

## Verdict

The need is real; the product as described is not buildable. Nobody offers environment + labor +
health at barcode level across categories — because **the labor data doesn't exist at that
resolution**. GoodGuide tried the exact full-stack version with 175,000 products and was dismantled.
That's not an unserved market; it's a graveyard with a headstone.

**The defensible wedge is narrower: a corporate-accountability layer no existing scanner has.**
Yuka reads ingredients. Nothing reads *litigation, recalls, enforcement actions, and parent-company
ownership*. FDA recalls, class-action settlements, DOJ actions, CPSC notices, UFLPA entity listings
and CBP detentions are public, structured, dated, and change weekly. Mapping brand → parent → open
enforcement record would have flagged Celsius's settlement, Abbott's findings, and ByHeart's recall —
none of which any current app surfaces.

The honest AI angle is **entity resolution and ownership-graph maintenance across messy public
filings** — not "an LLM reads sustainability reports," which just launders marketing into scores.

**Strongest argument against:** ByHeart. The clean-ingredient challenger caused a botulism outbreak.
Any scoring app would have recommended it over Abbott. If the core promise is "we know which is
safer," and the honest answer in the founder's own example category is *nobody could have known*,
the promise is fraudulent at inception.
