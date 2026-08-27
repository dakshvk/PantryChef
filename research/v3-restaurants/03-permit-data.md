# Permit Data — The Arbitrage Was Already Arbitraged

_Aug 2026. **WebFetch egress-blocked** (confirmed against shovels.ai/pricing). All figures are
search-result snippets. ⚠️ Note that many "comparison" and "pricing" pages ranking for these queries
are **written by the competitors themselves** — their numbers about rivals are self-interested._

---

## THE FINDING THAT REFRAMES EVERYTHING

> **A building permit is a LAGGING indicator of a homeowner's purchase decision, not a leading one.**
>
> By the time a re-roof permit is issued, the homeowner has already signed with a roofer — and the
> roofer usually pulled the permit. **Permit records are near-worthless as leads for the trade named
> on the permit.**

They only have value as: (a) leads for **adjacent** trades, (b) leads for people selling **to the
contractor**, or (c) **evidence of a completed event** (roof age, addition, panel upgrade) for
underwriting.

Shovels' own marketing confirms it — their solar use case is *"identify homeowners with active
roofing permits for installation opportunities."* Adjacent trade, not same trade.

---

## THE MARKET HAS ALREADY PRICED THIS

| Signal | Timing | Market price |
|---|---|---|
| Form-fill *"I need a new roof"* | **Before** hiring | **$71–$162** (roofing LSA) |
| Phone call from Local Services Ads | **During** decision | Highest close rates |
| **Permit issued** | **After** hiring, often after work started | **$0.001 – $0.10 per record** |

**The market priced permit records at roughly 1/1000th of a real lead. That gap is not an arbitrage
waiting to be captured — it is the market correctly discounting a lagging indicator.**

---

## ⚠️ THE LOW END IS ALREADY FULL

The earlier research called this "the clearest arbitrage found." That assessment looked only at
Shovels and missed that **the niche is already densely populated by exactly the business proposed:**

| Player | Pricing | Coverage |
|---|---|---|
| **PermitStack** | **Free (100 req/day), $19 / $29 / $49 per month**, self-serve Stripe | **67M+ permits, 7,000+ cities, all 50 states.** Ships a Python SDK *and an MCP server* |
| **Permit Ledger** | Free weekly reports; **$39/mo**, no contract, no sales call | 338 US cities |
| **PermitDrop** | **$299/mo for 100 exclusive contractor leads** with verified phones | — |
| **permits.llc** | **$0.01/record raw → $0.10/record with homeowner contacts**; **exclusivity: one business per niche per county** | MA, NH, CT, NJ, NY, PA, FL, TX |
| **HomeLogs.io** | Free API key | Washington State |
| PermitCore, Permitlify, PermitMint, Open Permit Data, Construction Lead Pro | mostly $0–89/mo | metro/territory |

**And below even that, the floor has collapsed to nothing.** Apify hosts **a dozen-plus** building
permit scraper actors at **$0.001 per result — $1 per 1,000 records.** One national aggregator prices
a **500,000-permit national pull at ~$500**.

> **The market price for a normalised permit record from open data is one-tenth of one cent.**
> Shovels' $599/month is not the price of the data. It is the price of **coverage of the closed
> jurisdictions**, plus enrichment, contractor entity resolution, and an enterprise SLA.

---

## Why the $599 exists — the part you cannot arbitrage

**Shovels** (founded 2022, Ryan Buckley & Luka Kacil): **$5M seed led by Base10 Partners, June 2025**,
~$6.5M total, **39–44 staff**. Covers **2,770+ jurisdictions ≈ 85% of US population, 180M permits
across 30M addresses**, plus standardised contractor license files for **37 states**. Has **acquired
ReZone** — consolidation has started.

**But here is the number from Shovels' own blog: ~10,000 of the ~20,000 US permitting jurisdictions
publish nothing online at all.** Their "Project Storm" exists to onboard those offline jurisdictions
one at a time.

**And HBW — in business since 1992 — employs 10 editorial staff plus 40+ human reporters in the
field** collecting permit data. **That is the market's revealed answer to "can this be automated
everywhere?"** No.

Even the open-data cities are rough: one competitor reports **LA's portal running 12–24 months
behind**; NYC stores `issuance_date` as unsortable text; every portal has a different schema across
Socrata, CKAN, ArcGIS, CARTO, Accela, Tyler EnerGov, OpenGov, CityView, Clariti, and PDF-only
bulletins.

---

## The churn problem — Angi is the cautionary tale

Best public evidence on contractor lead-gen retention:

- **Q3 2025 revenue $265.6M, down 10% YoY.** Network Service Requests **−67%**, Leads **−81%**
- **131,000 monthly active pros, down 17% YoY**
- **Average monthly churn 5.9% ≈ 52% annually — and that is their *improved* number**
- **Q2 2026: loss widened, stock fell 31% in a day**

**Why the reputation collapsed, precisely:** the **FTC's January 2023 order required HomeAdvisor to
pay up to $7.2M** for deceptively marketing leads — misrepresenting that leads matched providers'
services and geography, and **overstating lead-to-job conversion rates it could not substantiate.**
The FTC mailed **>$3M in refunds to >110,000 home-service businesses.**

> **5.9% monthly churn is the industry-leading number in contractor lead-gen. A solo founder selling
> $39–99/month subscriptions would spend every hour replacing customers.** And overstating conversion
> rates in your marketing is a documented FTC enforcement trigger *in this exact vertical.*

---

## The legal position — precise

**CFAA risk is low. Contract, state-records, and telemarketing risk are what will actually hurt you.**

**Scraping public pages is defensible.** *Van Buren v. United States* (2021) held "exceeds authorized
access" reaches only areas **off limits** to the user — it does not criminalise accessing information
you're entitled to see for an improper purpose. *hiQ v. LinkedIn* (9th Cir., 2022) applied the
**"gates-up-or-down" test**: scraping publicly accessible pages requiring no account is not access
"without authorization." **Municipal permit portals are the paradigm case** — no login, public records
by statute.

**But hiQ won the CFAA point and then lost on breach of contract** — a **$500,000 stipulated judgment**
in Dec 2022. The counterweight: ***Meta v. Bright Data*** (N.D. Cal., Jan 2024) — **Meta's ToS do not
bind a scraper who is logged out**, because the terms govern account holders. Meta dropped the case.

> ### The operational rule this dictates
> **Never register an account on a permit portal. Never click through an "I agree." Never log in.**
> The moment you accept a click-wrap you convert low-risk activity into a contract claim.
> **Bright Data won *because* it was logged out.**

**State anti-solicitation statutes — the sleeper risk, and specific to the homeowner-lead model:**
- **South Carolina:** a person "shall not knowingly obtain or use personal information obtained from
  a state agency... **for commercial solicitation.**" Misdemeanor, fine and/or up to a year.
- **Washington:** the Public Records Act **prohibits disclosure of "lists of individuals" for
  commercial purposes** — and this applies to electronic records sortable into such lists.
- **Kansas:** requires written certification that records won't be used for commercial solicitation.

**These bite the homeowner-solicitation product, state by state. They do *not* meaningfully restrict
selling contractor-activity intelligence to B2B buyers.**

**TCPA is what actually kills the homeowner-lead product:** statutory damages **$500–$1,500 per
call/text**, private right of action, routine class actions. **Permit records give you an address —
not consent.**

---

## ✅ THE ANGLE THAT SURVIVES: sell TO contractors, not FOR them

The permit record names an **active, licensed, currently-working contractor with an address, a trade,
a volume, and a trajectory.** That's a B2B prospect list with a behavioural signal attached.

**The market agrees:**
- **Shovels' named case studies are Beam and Haven — companies doing cold outreach *to contractors*,**
  reporting 20–30% higher engagement
- Shovels has dedicated pages for **building materials suppliers and manufacturers**
- **PermitCore's entire pitch** is "which contractors just pulled commercial permits in your
  territory — ranked by volume, value and momentum"
- PermitDrop sells **"exclusive contractor leads" at $2.99 each**

**Why it's structurally better:** B2B buyers churn slower, pay annually, tolerate **$500–$5,000/mo**,
have no TCPA-on-consumers problem, and **are not covered by state anti-solicitation statutes aimed at
soliciting individuals.** It sidesteps four of the five things that kill the homeowner version.

**Who has budget:** building-product manufacturers and distributors (territory reps), contractor
fintech and lending, contractor insurance and surety, contractor SaaS, staffing, PE roll-ups hunting
acquisition targets.

---

## ⚠️ CORRECTION to the earlier research

The prior pass claimed contractor license data is unsold — "only free state lookup portals and nobody
selling it." **That is wrong.**

- **CSLB (California)** publishes a free master list; bulk file orders cost **$235 per file**
- **Dietrich Direct** sells contractor mailing lists **from $69**
- **BizInfor** sells a **650K+ contractor contact** database with emails and direct dials
- **National Contractor Index** indexes **1,025,495+ verified records across 28 states**
- **Shovels already ships standardised license files for 37 states**

**Why nobody built a big business on it:** the file is free, static, decays slowly (no recurring
value), and a license alone tells you nothing about whether the contractor is *active*. **The value
is only in joining licenses to permit activity** — which is exactly what Shovels sells.

---

## Other angles checked

**Vertical permit data (solar / EV / heat pump)** — real, but occupied. **Ohm Analytics** has owned it
since 2018, serves 700+ companies, free tier for installers as a data-barter, enterprise reports, and
is **listed on Neudata for hedge funds.** Shovels calls energy/electrification customers "some of our
largest and most engaged."

**Permit expediting software** — structurally a *better* business, wrong one for you. **PermitFlow
($54M Series B, Accel)** and **GreenLite ($49.5M Series B, Insight, Sept 2025; ~$86M total)** sell
workflow to builders. Requires enterprise sales, jurisdiction filing expertise, licensed plan
reviewers. **The capital race is decided — Pulley raised $4.4M and lost it.**

**Insurance / unpermitted-work detection** — the deepest pocket (BuildFax found **two-thirds of
owner-reported roof ages understated by >5 years**; Verisk acquired them in 2019). But it's
Verisk/Moody's/CAPE territory: nationwide coverage, SOC 2, E&O, 9–18 month procurement. **Closed.**

**Alt-data funds** — hedge funds spent **$2.8B on alt data in 2025 (+17%)**, average fund $1.6M/yr.
But they buy national coverage, 10-year history, and compliance memos. **A one-metro dataset is
unsellable here.**

**Municipalities and researchers** — no budget, and the Census Building Permits Survey is free.

---

## VERDICT

**The "clearest arbitrage" was real in 2022 and has since been arbitraged.**

1. **The gap is already filled by people exactly like you** — you'd be entrant #12 into a niche whose
   commodity floor is one-tenth of a cent.
2. **The $599 isn't priced on the open data** — it's priced on the ~10,000 jurisdictions that publish
   nothing. You can't arbitrage the part that's free, because it's free to your competitors too.
3. **Permit leads are a lagging indicator** — the core homeowner pitch is economically broken.
4. **~52% annual churn at the best-run scale player**, plus FTC enforcement history for overstating
   lead quality.

**Could a solo undergrad build a metro version in 90 days? Yes, easily — that's the problem.** For
open-data cities this is a two-weekend project: a Socrata/ArcGIS/CKAN ingester, address normaliser,
dedupe, Postgres, FastAPI. **The 90-day question was never "can you build it." It's "can you sell
it," and that has nothing to do with your Python skills.**

### What kills it

Commodity pricing with no floor · the lagging-indicator problem (you'll discover it on sales call #3
when a roofer says *"I pulled that permit"*) · churn · **scraper rot** (2,770 heterogeneous portals
means constant breakage — Shovels built self-healing AI scrapers *and still* needed Project Storm;
you'd spend 80% of your time on maintenance, not sales) · TCPA and state statutes · enterprise buyers
who won't buy from you without SOC 2 · **and Shovels is now acquiring competitors.**

---

## If you do it anyway — the plan worth defending

**Do not build a permit data API. Do not sell homeowner leads to contractors. Both are taken and both
are commodities.**

Build **one vertical, one geography, sold to people who sell TO contractors.**

**Days 1–14 — sell before you build.** Pick ONE metro with clean open data (Austin, Seattle, Phoenix,
Chicago — **avoid LA**, its portal reportedly runs 12–24 months behind) and ONE vertical
(electrification/heat-pump/panel-upgrade is highest-value and least covered outside Ohm). Pull twelve
months of permits **by hand in a weekend.** Build the **contractor** table, not the homeowner table:
name, license, trade, permit count trailing 90 days and 12 months, growth rate, valuation sum, ZIP
concentration. Manually email **30 people who sell to those contractors** — regional distributors,
manufacturer reps, contractor fintech, contractor insurance brokers. **Ask for $500 for the list.**

> **If zero of 30 pay, stop. You have saved 76 days.**

**Days 15–45 — only if someone paid.** Automate that one metro. Add the free state license join.
Weekly delivery. Price at **$300–800/month for exclusive access within a territory + vertical** — copy
permits.llc's exclusivity model, **the only structure in this market with pricing power.** Target 3
customers.

**Days 46–90 — expand along the customer, not the map.** Don't add cities to look impressive. Add the
*second* metro your existing customer's territory covers. Target **10 customers at $500/mo = $60K ARR.**

**First-10 path:** manufacturer rep associations (AIM/AIMR chapters), regional building-products
distributor branch managers on LinkedIn, solar/HVAC equipment distributors, contractor insurance
brokers and surety agents, contractor fintech on YC's directory, and the trade shows those people
attend. All findable, all reachable by one person, **all with budget authority under $1K/month that
doesn't need procurement.**

**What would change this verdict:** if in Days 1–14 someone hands over $500 for a hand-built
spreadsheet. **That is the only evidence that matters, and it costs two weeks to obtain.**

---

## Unverified

Shovels total funding $8.3M vs $6.5M · BuildZoom $23.7M vs $37.4M · Construction Monitor $200–800/mo,
Dodge $100–150/mo, ConstructConnect $1,000/mo, ATTOM ~$500/mo, BatchData $500/mo — **all from
competitor-authored comparison pages** · LA's 12–24 month lag (from an Apify listing) · PermitCore
$89/mo (single snippet) · statute numbers S.C. §30-2-50, RCW 42.56.070(8), K.S.A. 45-220(c)(2) ·
**TCPA 1-to-1 consent rule status — snippets say effective 27 Jan 2025, but it was likely vacated by
the 11th Circuit before taking effect. Verify with counsel.** · all 2026 cost-per-lead figures come
from marketing agencies with an incentive to make paid channels look good.
