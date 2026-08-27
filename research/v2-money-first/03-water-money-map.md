# Water Industry — The Money Map

_Aug 2026. **WebFetch egress-blocked** — every dollar figure is the search layer's summary of a page,
not text read directly. Confirm before building._

---

## THE BOTTOM LINE

> The money in water for one person with no capital is **not** in selling software to water
> utilities — that path is an RFP, a reference customer, and a 9–18 month cycle.
>
> It is in **(a)** selling to the thousands of small contractors the utilities regulate — who pay by
> credit card, whose names and phone numbers are **published for free on utility websites**, and
> whose work is legally compelled; and **(b)** the **tester-pay clearinghouse model**, the only way
> to get a municipal "yes" without a budget line.
>
> **Backflow is where both overlap.**

---

## #1 — Backflow test software sold to the TESTERS, not the utilities ⭐

**Why it's first:** the only opportunity on the map where the buyer swipes a card the same day. No
procurement, no reference customer, no RFP — and **the complete buyer list is already public.**

Every water utility in America publishes its list of certified backflow testers as a PDF or web page.
Marin Water, CFPUA, James City County VA, Liberty Lake WA, SF.gov, Missouri DNR — thousands of such
lists. **Name, company, phone, often email — pre-qualified as licensed and actively working.**

**The market:** 19,000+ ASSE-certified backflow professionals across all 50 states. Testing runs
$100–$300 per device per year. Irvine Ranch Water District alone tracks **17,000+ assemblies**.

**Existing prices to undercut:** Syncta from **$29/mo** (Watts-owned, generic) · MyBackflow **$49/mo**
(≤500 assemblies) · BackflowNet **$149/mo** (≤250) · ServiceTrade ~$75/tech/mo.

**The concrete path:**
1. **Scrape 200–400 utility "certified tester list" pages** into a national tester database. Two
   weeks of work, and it is itself a defensible asset.
2. **Build v1:** mobile test-report capture (gauge readings, pass/fail, assembly serial, photo) →
   auto-generates *the specific PDF form that specific utility requires* → plus a **due-date engine**
   telling the tester which customers are coming up for annual re-test, with the reminder generated.
   **The re-test reminder is the actual product** — it turns a one-off job into an annuity for the
   tester. That is why he pays.
3. Charge **$39–$79/mo**. 19,000 targets × 1% at $59/mo = **~$135K ARR.**
4. Sell by phone and email to the scraped list.

**Realistic:** first paying customer in 30–60 days; $2K–$8K MRR by month 9 if he actually dials.

**Risk:** crowded (Syncta, MyBackflow, BackflowNet, C3Backflow, BackflowGo, ServiceTrade), low ACV,
SMB churn. The differentiator must be **utility-specific form output + the retest-reminder revenue
engine** — not "another inspection app."

---

## #2 — Then flip that base into a utility filing clearinghouse

Same codebase, other end of the pipe. **This is where the real money is**, and the economics are
extraordinary:

**The jurisdiction pays literally nothing.** Brycer's municipal agenda materials say "zero cost for
any aspect — setup, training, ongoing service." **The contractor pays per filed report:**

| Vendor | Per-report fee |
|---|---|
| **Brycer / The Compliance Engine** | Raleigh **$10–12** · Charleston **$15** · Forney TX **$17** · Redmond WA **$37** |
| **BSI Online** | **$12.95** (Holly Hill FL, Round Rock TX) → **$15.95** elsewhere |
| **Tokay** (Veralto) | $1.00/report + $0.50 small-batch fee |

BSI Online does an estimated **$5.2M/yr** on this model with ~43–51 staff. ⚠️ *ZoomInfo-class estimate.*

**Why a solo founder can play here:** **there is no budget line to approve.** A Cross-Connection
Control Coordinator can adopt this administratively or with a one-page policy change — not a capital
procurement. **That is the fastest path to a municipal "yes" in the entire water sector.**

**Targeting:** find utilities that publish a tester list **but still accept paper or emailed PDF test
reports** — a directly observable "no system" signal you can qualify from their own websites in a day.

**The sequencing insight:** #1 funds #2 — *and gives it its unfair advantage.* When a utility asks
"will our testers actually use this," you answer with names.

**Money:** a utility with 5,000 assemblies at $9.95/report ≈ **$50K/yr from one city.** Ten cities =
$500K/yr on a support burden one person can carry. Expect **3–9 months per city**, and expect BSI,
Brycer and SwiftComply to defend.

---

## #3 — Consumer Confidence Report as a service, timed to the 2027 rule

**A dated, unavoidable forcing event.** EPA finalised CCR Rule Revisions **15 May 2024**; first
compliance **1 Jan 2027**; reports due **1 July 2027** covering 2026; systems ≥10,000 people must
deliver **twice per year**; new translation and accessibility requirements.

**~51,000 community water systems**, >92% serving ≤10,000 people. Every one must change its template;
the >10,000 tier doubles its workload.

**The price point already exists and sits under the micro-purchase threshold.** 1water.ai publishes
**$299 / $699 / $1,499**. Municipal no-bid thresholds are typically **$5,000+** (MS and NY $5,000;
NJ $2,625 rising to $17,500–$40,000 with a Qualified Purchasing Agent; TN up to $25,000–$50,000).
**A $750 CCR is a P-card purchase, not a procurement.**

**Why it fits:** a CCR is regulated document assembly from structured, publicly downloadable state
SDWIS data. Python + LLM + templating. **The new translation requirement is an LLM-shaped cost that
consultants will charge dearly for.**

**Targeting:** pull each state's system list, target those with a recent **public notification or
monitoring violation** — they are already scared and already spending.

**Honest weakness:** seasonal (money lands Feb–June), free EPA/state templates cap the price, and a
competitor already publishes this exact pricing. Starting Aug 2026, the first real season is Q1 2027.

---

## #4 — California Cross-Connection Control Plans for small systems

Brand-new dated mandate: **CCCPH effective 1 July 2024**, plans due **1 July 2025**. Systems with
≥1,000 connections must consult a CCC specialist; ≥3,000 must employ one. That leaves a large
population of **small CA systems** who must produce a compliant written plan with no consultant and
no budget for **$209/hr** engineering time.

Productise: guided intake → compliant CCC Plan → annual report generation. **$1,500–$3,000 flat**,
still a P-card purchase. **Deadlines have already passed — which means there's a *late* cohort, the
best-converting cohort in all of compliance sales.**

---

## #5 — California Industrial General Permit annual reports, sold to private facilities

**8,035 permittees already paying $1,791/yr each just for the permit — $14.4M of proven,
non-optional annual spend in one program in one state.** And **the payer is a private business, not
a government**: no procurement, invoice, net-30.

Each needs SWPPP maintenance, quarterly sampling records, and a hard-deadline annual report through
SMARTS. An older State Board figure showed only ~2,000 of ~8,581 annual reports submitted
electronically — a paper backlog.

Price at **$1,200–$2,500/facility/yr** vs SW² at $12–18/site/mo for software that still leaves the
facility doing the work. 100 facilities = **$150K+/yr.**

---

## The enforcement teeth (why backflow buyers actually act)

- **Longmont CO:** fee added to the utility bill at day 31; **civil penalty up to $500 per assembly**
  and scheduled service interruption at day 91
- **Denver Water:** **$250 penalty** after three unanswered notices; service goes to suspension
- **San Francisco:** failure to test can mean **termination of water service, fines, or both**

Three separate parties touch one record — utility, property owner, tester — and none of them share a
system. **That is why it is still Excel.**

---

## The sleeper nobody is working

Whoever sits between the utility notice and the tester controls **$25–$150 per lead** of demand
routing. Plumbing leads run **$35–$75** via Google Ads, **$150–$200+** on competitive search terms.

The utility mails a legally-compelled notice to a property owner who **must hire a certified tester
within 30 days.** That is the highest-intent lead in the trades — and right now it converts through a
photocopied list.

---

## Who already sells to water utilities

**Tier 1 strategics (won't chase small deals):** Veralto/Aquatic Informatics (Tokay, Hach WIMS —
**$27,140 one-time + $4,885.20/yr** in one public agenda packet) · Tyler Technologies (Watertown MN
chose Incode at **$89,830 implementation + $27,490/yr**) · Trimble/Cityworks · Esri (a channel and a
data dependency, not a competitor) · Watts Water (owns Syncta).

**Tier 2 water-specific:** **SwiftComply** — the direct competitor; won Tampa RFP #41012821 scoring
78/100 against 7 bidders, reportedly **$2–$6 per assembly per year**, 700+ organisations, 400+ cities,
**acquired XC2** · HydroCorp full-service (**Royal Oak MI: $420,360 over 24 months** — the category
price ceiling) · BSI Online · Brycer · 120Water · BlueConduit · iWorQ · C3Backflow · BackflowGo
(attacking per-test pricing: "start free, pay only when you submit").

**Tier 3 — study this one:** **Current Software** raised a **$2.75M seed** (Burnt Island Ventures +
Bienville Capital) and reached **80 utilities in 16 states since Oct 2025**, targeting the **45,000
utilities under 10,000 connections**. This verifies the segment is real — *and* proves it took
venture money and a team. 80 utilities in ~10 months is not a solo pace, and billing/CIS is a
rip-and-replace sale. **Read it as validation of the customer segment, not a template for the product.**

**Consultant rates being displaced:** senior engineering **$209/hr** (Minnesota's prima-facie cap),
cross-firm average ~$170/hr, senior specialists $215–$300+/hr. A CCR, a CCC plan, an MS4 annual
report and an IGP annual report are each 8–30 hours of that rate spent on **document assembly from
structured public data.**

---

## Ideas checked and rejected

**Small-utility billing/CIS** — multi-year rip-and-replace sale, and Current Software has venture
money and a head start. **Private well testing** — 13M+ households but **no mandate**, and it needs
physical kits, lab logistics and inventory capital. **Water rights / brokerage** — data moat plus
relationships he doesn't have. **SB 555 water loss audits** — requires a CA-NV AWWA validator
certificate. **Rate studies** — the deliverable is credibility, not a spreadsheet. **811 locate
management** — incumbent-heavy at $5K–$20K/yr. **Irrigation districts** — Watervize already occupies
exactly his target segment. **Operator continuing education** — buildable, but each state must
approve the provider (6–12 month gate).

---

## What could not be verified

- **The single most load-bearing number is the least solid:** SwiftComply's **$2–$6 per assembly/yr**
  came via a competitor-adjacent blog summarising the Tampa RFP. The award itself was never seen.
- **BSI Online's $5.2M revenue / 43–51 employees** — ZoomInfo/RocketReach class, routinely wrong 2–3x
  for private companies.
- **Tokay, XC2, iWorQ, 120Water, BlueConduit, CCRiWriter, Waterlitix, Watervize, Rubicon publish no
  pricing at all.** Every "price not public" is a genuine gap.
- **Could not find anywhere:** total US backflow assemblies · total US backflow testing *companies*
  (only 19,000+ certified individuals) · water-rights broker commissions · SB 555 validator day rates
  · per-facility CA IGP consultant cost · **any rate-study award amount** (five live RFPs, zero
  awarded values).
- **Conflicting:** CA IGP permittees read as 8,035 (2023) vs 8,581 (2016). Backflow filing fees span
  **$1.00 to $37 — a 37x spread**, which suggests the fee is negotiated per jurisdiction rather than
  list-priced. **That variance is itself strategic: a new entrant can undercut without a price war.**
