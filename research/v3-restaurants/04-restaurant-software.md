# How Restaurants Actually Buy Software — And Why That Kills The Standalone Play

_Aug 2026. **WebFetch egress-blocked.** All figures are search-index summaries; no primary documents
were opened. Pricing and revenue figures marked ⚠️ are vendor-stated or aggregator self-report._

---

## THE EVENT THAT CHANGED THE MARKET — 2 April 2026

> **Square launched "Square Restaurant Inventory **by MarketMan**."**
> MarketMan's engine, running inside Square. Single sign-on, unified billing, native POS feed.
> **$99/month per location.**

Toast has bundled **xtraCHEF** since acquiring it in 2021. As of April 2026, **both dominant POS
platforms ship a first-party food-costing and inventory answer that is one toggle away** for a
restaurant that already has the POS installed.

**This is the single most important fact in the restaurant research.** It is not "there are
competitors." It is: *the distribution channel you would have to go through has already shipped the
product you were going to sell through it.*

---

## THE PRICE CEILING — from Toast's own investor math

**Toast's investor-day model assumes roughly $4,000 in annual software spend per restaurant. That is
~$333/month, across every vendor a restaurant uses.**

POS alone typically eats $69–165/mo of it. Scheduling, payroll, accounting, reservations, online
ordering and delivery middleware take more.

| | |
|---|---|
| Total realistic monthly software wallet | **~$333** |
| Already committed to POS + payments | roughly half |
| What is genuinely contestable by a new category | **~$100–150/mo, and it is crowded** |

Cross-check with the economics doc: at a **$48,000 annual profit**, $4,000/yr of software is already
**8.3% of net profit.** There is no headroom. Every dollar you win is a dollar taken from a vendor
already installed.

---

## THE PLATFORM TAX — what it costs to sell through a POS marketplace

Reaching restaurants through Toast or Square looks like the obvious answer to distribution. The
terms are brutal.

### Toast

| Term | Value | ⚠️ |
|---|---|---|
| Revenue share to Toast | **30%, in perpetuity** | ⚠️ Reported, not from a published contract |
| Restaurant must also pay Toast | **$50/mo** for the Restaurant Management Suite that any API integration requires | |
| Partner onboarding | **Eight-stage process** — compliance, privacy, security and legal sign-off *before* development begins | |

**Run the numbers at $99/month:**

```
Restaurant pays you                  $99
Toast takes 30%                     −$30
Your payment processing (~2.9%+30¢)  −$3
                                    ─────
You keep                             $66
Restaurant's true cost               $149/mo  ($99 to you + $50 to Toast)
```

**You keep two-thirds. The restaurant pays half again as much as your sticker price.** And you are
selling against a bundled module the same restaurant can switch on with no integration fee at all.

### Square

- **You must have five live, paying Square sellers before Square will list you** in its marketplace.
  Classic chicken-and-egg: the channel that would get you customers requires customers.
- Square now competes with its own marketplace in this exact category, as of April 2026.

---

## WHY INTEGRATION IS NOT OPTIONAL

> **26% of operators name POS integration as the #1 barrier** to adopting inventory software.

Without a POS sales feed you cannot compute **theoretical usage**. Without theoretical usage there is
no **variance** — no "you should have used $9,100 of protein and you used $10,400." And variance is
the entire product.

**A costing tool with no POS feed is a spreadsheet with a login.**

So the integration is mandatory, the integration is gated by an eight-stage approval, and the gate is
operated by a company that sells the competing product.

---

## THE CONSOLIDATION HEADWIND

- **64% of restaurants name technology consolidation as a priority.** Operators describe "vendor
  fatigue" from managing as many as 20 providers.
- Buying preference is running *toward* suites and *away* from best-of-breed point tools.
- **~70% of US restaurant locations are single-unit independents** — the segment with the least
  patience for another login, another bill, another integration to maintain.

**You would be selling a 21st vendor into a market actively trying to get to five.**

---

## THE ONE DOCUMENTED SOLO SUCCESS — and why it doesn't transfer

**Recipe Cost Calculator — Daniel Wintschel, solo founder.**

- **10,000+ food businesses**, pricing from **$29/month** ⚠️ *self-reported*
- No sales team, no funding, self-serve checkout, no demo call

It's the proof that one person *can* build a profitable food-costing business. Read the details and
almost none of it is repeatable from a standing start:

1. **He owned a wholesale bakery for a decade first.** Domain credibility was pre-existing, not
   acquired through customer interviews.
2. **He was his own first customer for a year** before selling to anyone.
3. **He does not sell to restaurants.** Customers are bakeries, caterers, meal-prep companies, CPG
   producers and food manufacturers.
4. **Therefore he needs no POS integration.** A bakery costing a product SKU has no covers, no
   tickets, no Toast. **The single hardest technical and political dependency simply isn't in his
   product.**
5. **It took 13+ years.**

> The lesson isn't "a solo founder can win here." It's **"the solo founder who won did it in the
> adjacent market that has the same math and none of the gatekeepers."**

---

## THE COMPETITIVE FLOOR AND CEILING

| Product | Price/location/mo | Note |
|---|---|---|
| **Square Restaurant Inventory by MarketMan** | **$99** | Native to the POS, launched Apr 2026 |
| MarketMan standalone | ~$179+ ⚠️ | Already ships **AI recipe creation from a photographed ingredient list** |
| xtraCHEF by Toast | bundled / add-on | Free-ish inside the Toast stack |
| MarginEdge | **$350** | Invoice capture, plate cost, AvT |
| Restaurant365 Essential | **$469–499** | Full back-office + accounting |

**The AI-differentiation angle is already gone.** MarketMan ships AI recipe creation from an
ingredient-list screenshot today. "We use an LLM to parse your invoices/recipes" is table stakes, not
a wedge.

**And the floor is $99 from inside the POS.** You cannot undercut a bundled module, and you cannot
out-integrate the company that owns the integration.

---

## VERDICT

> **Don't build inventory software for restaurants.**

Five stacked reasons:

1. **Both dominant POS platforms shipped the answer** — Toast/xtraCHEF since 2021, Square/MarketMan
   since April 2026, at $99.
2. **The wallet is ~$333/mo total and mostly spent**, against a $48K annual profit.
3. **Distribution costs 30% in perpetuity plus a $50/mo tax on your own customer**, gated behind an
   eight-stage legal review run by your competitor.
4. **The mandatory POS feed is the #1 adoption barrier** and is controlled by that same competitor.
5. **The market wants fewer vendors, not a better 21st one.**

### If the pull toward this problem is real

Three things the evidence actually supports:

- ⭐ **Sell costing to food businesses that aren't restaurants** — bakeries, caterers, meal-prep,
  ghost kitchens, CPG producers, food trucks. Same math, same pain, **no POS dependency, no
  marketplace gatekeeper, no bundled incumbent.** This is the only path with a documented solo
  success.
- **Price so nobody has to talk to you.** $29–79/mo, self-serve, no demo. Recipe Cost Calculator's
  entire go-to-market.
- **Go get a kitchen job first.** Every durable player in this category was founded by someone who
  had already run the operation. Wintschel had a bakery. That is the actual prerequisite, and it is
  cheaper to acquire than a year of building the wrong thing.

---

## Confidence

**High:** the Square/MarketMan April 2026 launch and $99 price · Toast's xtraCHEF bundle · the 26%
POS-integration barrier · the 64% consolidation priority · MarketMan shipping AI recipe creation ·
competitor list pricing for MarginEdge and R365.

**⚠️ Reported but unverified from primary sources:** Toast's 30% perpetual revenue share · the
$50/mo Restaurant Management Suite requirement · Toast's $4,000/restaurant investor assumption ·
Recipe Cost Calculator's 10,000-customer figure · MarketMan standalone pricing.

**Could not obtain:** Toast's or Square's actual published partner agreements · any partner's stated
economics from inside either marketplace · churn data for standalone inventory tools.
