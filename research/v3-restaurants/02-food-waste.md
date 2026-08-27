# Restaurant Food Waste — The Honest Picture

_Aug 2026. **WebFetch egress-blocked** (confirmed against refed.org). All figures are search-index
summaries, not primary text._

---

## THE ONE NUMBER THAT DECIDES THIS

> **70.2% of uneaten food at restaurants is PLATE WASTE** — post-consumer, food the customer was
> served and chose not to eat.
> — ReFED Insights Engine

**Only ~30% of restaurant food surplus is back-of-house.** Of ReFED's 12.5M tons of foodservice
surplus, roughly **3.75M tons** ever passes through a walk-in, a prep station, or a purchase order.

| Bucket | Share | Can inventory software touch it? |
|---|---|---|
| **Plate waste** — portions too large, customer didn't finish | **~70%** | **No.** Portion size, menu design, buffet ops. |
| Trim / prep loss — peels, bones, fat | part of ~30% | **Barely.** Physically determined by yield. Better tracking improves *costing accuracy*, not waste volume. |
| **Spoilage from over-ordering** | part of ~30% | **Yes — the real target.** Par levels, order forecasting, purchase-vs-usage variance. |
| Spoilage from poor rotation | part of ~30% | **Partially.** Software can prompt; it cannot see the walk-in. |
| Over-prep / overproduction | part of ~30% | **Partially.** Needs forecasting tied to POS. |
| Cooking errors, comps, remakes | small | **No.** |

**Realistic software-addressable slice: 15–20% of total restaurant food surplus** — before you write
a line of code.

---

## THREE LOAD-BEARING NUMBERS THAT DON'T HOLD UP

### ❌ "$162 billion lost to restaurant food waste"

**This is a misattribution.** The $162B is **USDA ERS's 2010 estimate of total US retail + consumer
food loss** — two-thirds of it in homes and *all* away-from-home eating combined, one-third in
grocery retail. Restaurants are a fraction of a fraction.

**Anyone quoting $162B as a restaurant number is careless or selling something.**

### ❌ "4–10% of food purchased never reaches a customer"

Attributed variously to the National Restaurant Association and the Green Restaurant Association;
appears almost entirely in vendor and trade content. **No primary study, methodology, or sample was
locatable.**

**Verdict: industry folklore with a plausible magnitude.** And it is *the* load-bearing number in
almost every waste-software pitch.

### ❌ The 7:1 ROI claim (Champions 12.3, 2018)

Real study — 114 sites, 12 countries, ~7:1 benefit-cost ratio. But:

1. **Self-selection.** The sites studied were *already running waste programs*. Sites that tried and
   quit are structurally absent. Survivorship bias in its purest form.
2. **Vendor-supplied data** — assembled with data from **Winnow and Leanpath**, the two companies
   whose product the 7:1 ratio justifies buying.
3. **No control group.** A kitchen installing a waste program is usually also getting new management
   attention, new SOPs and a corporate mandate at the same time.
4. **Modeled avoided-cost, not audited P&L.** Assumes purchasing actually fell. It often doesn't —
   the food gets used elsewhere or the par stays put.
5. Measures kitchen waste only — the ~30% slice.
6. **2018 data. Eight years old.**

### ⚠️ And the cause breakdown itself comes from a vendor

ReFED's foodservice pre-consumer cause split is **derived from Leanpath's aggregated customer data**,
and the catering plate-waste rates are *"based on expert interviews"* — not measurement. Leanpath
sells waste-tracking hardware, and its customers are institutional caterers and hotels.

**The cause mix in a Sodexo cafeteria is not the cause mix in a 60-seat bistro.**

### And the two authoritative sources disagree by 2×

EPA puts foodservice at ~26.5M tons (2019); ReFED at 12.5M tons (2024). Different boundaries,
different definitions of "surplus." **If the measurement is that loose, per-restaurant derivations
from it are noise.**

Academic economists agree: University of Minnesota researchers found commonly cited food waste
estimates *"inaccurate, incomplete, overstated, or contradictory."* The famous "40% of US food is
wasted" traces to a 2009 study that **inferred waste from the gap between available and consumed
calories** — defining every unconsumed calorie as waste.

---

## THE STRUCTURAL FINDING: why it's all hardware

**Manual logging fails, and everyone in the category learned it the hard way.**

Consistent across vendor and trade sources: **staff compliance with manual waste logging degrades
within 2–3 weeks.** Entries get filled in from memory at end of shift rather than at disposal, and
logging is the first thing skipped when service gets busy — **which is exactly when overproduction
happens.** The dataset is systematically biased at precisely the moments that matter.

> **You cannot measure waste without hardware, because the measurement requires a human action
> during the busiest moment of their day, and they will not do it.** Every company that succeeded
> in this category paid for a camera to remove the human from the loop.

**Software-only waste measurement has never reached scale.** The survivors either added a camera
(Winnow, Leanpath, Orbisk, Kitro, and Phood which *pivoted* to computer vision) or added a
transaction (Spoiler Alert — B2B surplus liquidation, not restaurants, not measurement).

**Everything that survived either added a camera or added a transaction. Pure dashboards did not.**

---

## THE VENDOR LANDSCAPE — and who they don't sell to

| Vendor | Price | Customers |
|---|---|---|
| **Winnow** (UK, 2013) | ~$300–600/mo per site ⚠️ unverified | IKEA, Hilton, Marriott, Accor, Mandarin Oriental, casinos, cruise lines, contract caterers |
| **Leanpath** (US, 2004) | Quote only, no free tier | **Sodexo** (3,000-site rollout), **Aramark, Compass**, Hilton, Marriott, **Google** |
| **Orbisk** (NL) | Quote only | Hotels, hospitality groups |
| **Kitro** (CH) | **From €369/mo per kitchen**, device included | Zürich Marriott, Hyatt Regency Düsseldorf, Four Seasons Geneva |

### **Not one of them sells to independent restaurants. Zero.**

Every named customer is a hotel chain, cruise line, casino, contract caterer or corporate campus.
Why:

- **Buffets.** Over-production waste is enormous, visible and centrally controlled. A 60-seat à la
  carte restaurant doesn't have this problem in the same form.
- **ESG reporting.** Compass, Sodexo, Hilton and Accor have investor-facing disclosure obligations.
  Waste data is a *reporting deliverable*. **An independent restaurant has no one to report to.**
- **Central procurement.** One contract covers 3,000 sites; CAC amortises across an enterprise.
- **Tender advantage.** In contract catering, waste data "can be the deciding factor in winning
  client tenders." That B2B2B driver doesn't exist for independents.

### The category's ceiling

**Winnow — clear category leader, 12+ years old, $36–45M raised, camera hardware, blue-chip
customers in 94 countries — is at roughly $26M revenue.** ⚠️ *Self-reported aggregator data.*

That's the top of this market **with** hardware and **with** enterprise buyers.

---

## THE REGULATORY PICTURE: no compelled spend anywhere

**California SB 1383** requires Tier 2 generators (**restaurants with 250+ seats OR 5,000+ sq ft**)
to contract with a food recovery organisation, recover surplus edible food, and keep records.

**Penalties: $50–$100 first violation, $100–$200 second, with a mandatory 60-day cure period.**

Three reasons this creates nothing:
1. **It mandates diversion, donation and record-keeping — not measurement and not prevention.** The
   compelled spend is a hauler subscription, a food-bank agreement, and a logbook. **None requires
   software.**
2. **It exempts most independents.** 250 seats / 5,000 sq ft excludes the typical single unit.
3. **Nobody buys $200/month SaaS to avoid a $100 fine with a 60-day cure window.**

### And the peer-reviewed evidence says the bans don't work

> ***Science*, September 2024 (UC San Diego Rady School):** of the **first five US states** with food
> waste bans, **only Massachusetts** measurably reduced landfilled waste. The others showed almost no
> change against synthetic controls. **Combined effect did not exceed 3%.** The authors explicitly
> call for policymakers to reassess these laws as *"having little to no effect, contrary to
> policymakers' expectations."*

**And the flagship voluntary programme:** US Food Waste Pact signatories collectively cut **4,000
tons** — against a 12.5-million-ton sector. **That's 0.03%.**

---

## WHAT IT ACTUALLY COSTS A RESTAURANT

Bottom-up for a $1M independent at 32% food cost = **$320,000/yr in purchases**:

| | |
|---|---|
| Pre-consumer waste at the folkloric 4–10% | $12,800 – $32,000/yr |
| Strip irreducible trim (~half) | **~$6,000 – $16,000/yr** theoretically preventable |
| Realistic capture for software-only, imperfect logging (20–30%) | **~$1,500 – $5,000/yr recovered** |

**That supports a $50–150/month product. It does not support $500/month on waste reduction alone** —
and it sits below what MarketMan already charges for a much broader product.

---

## THE VERDICT

### As a "food waste" product: don't build it.

Four reasons, any one close to disqualifying:

1. **~70% of the problem is post-consumer plate waste** — structurally outside what inventory
   software can touch.
2. **Measurement requires hardware.** Manual logging collapses in 2–3 weeks and fails hardest during
   rush. A software-only product inherits a data-quality problem no UX solves.
3. **The buyers who pay are not restaurants.** They're hotels, cruise lines and contract caterers,
   for reasons independents structurally lack. **A solo founder has no path to Sodexo.**
4. **Nothing compels the spend**, and *Science* says the mandates that exist mostly don't work.

### But the described product isn't a waste product — and that changes everything

*"Helps commercial kitchens use inventory before it spoils and cost their menus accurately"* is an
**inventory and COGS product.** Reframed, the evidence is meaningfully favourable:

- Food cost is **28–35% of revenue, up 34% vs pre-pandemic**, named by **9 in 10 operators** as a
  significant challenge
- **42% of operators were unprofitable last year**
- **Inventory management is the 3rd-ranked area for future tech investment**; 36% prioritise tech
  that reduces food costs
- Restaurant inventory/purchasing software: **$4.55B (2025) → $9.18B (2030), 15% CAGR**
- Theoretical-vs-actual variance is a number operators already understand and already track badly

Tech spending priorities 2026: digital guest experience 57% · POS 53% · driving traffic 52% ·
**reducing food costs 36%.** **Waste tracking does not chart as a category at all.**

---

## THE STRATEGIC RECOMMENDATION

> **Sell the food cost line. Never the waste line.**

- **Don't pitch** *"reduce your food waste."* Nobody has it on their list, and you can't measure it
  credibly without hardware.
- **Do pitch** *"your theoretical food cost is 29% and your actual is 34% — here are the five points,
  itemised."* Waste reduction is the **mechanism**. Margin is the **pitch**.
- ⭐ **Build from data that already exists and requires no staff action during service: invoices, POS
  sales, and recipes.** Purchase-vs-theoretical-usage variance is computable **without anyone
  weighing anything.** That is the one honest path to waste insight that survives the compliance
  problem.
- **Never cite 7:1, "$162B", or "4–10%" in a deck.** All three are unverifiable or misattributed, and
  any operator or investor who checks will discount everything else you said.

### The real risk isn't the problem — it's bundling

Toast, Restaurant365, MarketMan and Craftable already occupy this. **Toast bundles inventory *and*
waste tracking into a POS that ~70%-single-unit independents already have installed.**
Restaurant365 ships waste categorisation *by cause* plus AvT variance reporting.

> **For a solo founder the binding constraint is not the product and not the problem — it's why a
> restaurant would buy a standalone tool instead of switching on a module they already pay for.
> That question needs an answer before any code is written.**

---

## Confidence

**High:** the 70% plate-waste split · vendor customer profiles (enterprise only) · manual-logging
compliance failure · SB 1383 scope and penalties · the *Science* 2024 finding · NRA operator priorities.

**Unverified:** the "4–10%" figure · all per-restaurant dollar and poundage figures · Winnow's
pricing · all Latka revenue figures (self-reported aggregator data).

**Could not obtain:** a clean FSR/QSR/institutional tonnage split · Winnow's or Leanpath's filed
financials · **any independent third-party audit of vendor 50%-reduction claims** — searched for
critical coverage and found none, which is itself notable.
