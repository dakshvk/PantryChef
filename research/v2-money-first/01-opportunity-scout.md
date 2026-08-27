# Money-First Opportunity Scout — Any Discipline

_Aug 2026. Ranked on speed to first dollar and solo executability. Environmental impact is not a
criterion. **WebFetch confirmed egress-blocked** — every figure is from search-result snippets, not
a vendor pricing page loaded directly. Load the real page before acting on any price._

---

## THE HEURISTIC WORTH REMEMBERING

> **Any vertical where the incumbent refuses to publish a price is a market where a self-serve
> competitor with a public price wins on friction alone.**

Sales-gated in this dataset: PestPac, Briostack, ServiceTitan, Passare, storEDGE, Vantaca, Highway,
Carrier Assure, GovWin, BidPrime, Brightwheel, Procare, Vanta, Drata. **The list of "no AI-native
player exists here" verticals correlates almost perfectly with the list of "vendor won't publish a
price."**

---

## #1 — DOT/FMCSA compliance for 1–10 truck carriers ⭐ fastest path found

**Buyer:** owner-operator or safety manager at a carrier with 1–10 trucks.

**What they pay today:**
| Service | Price |
|---|---|
| Managed driver-qualification files | **$30/driver/mo** (DotFleet) → **$49/driver/mo** (My Safety Manager) |
| Full-service DOT compliance | $100–$250/driver/mo |
| DIY software | $5–$20/driver/mo |
| Drug & alcohol consortium | $49–$595/yr per driver ($295/yr unlimited fleet common) |
| IFTA quarterly filing | $14.90–$80 per truck per quarter |
| FMCSA Clearinghouse queries | **$1.25 each**, federally mandated annually per driver |

**Why it wins on every criterion:**

- **The lead list is free, public, phone-verified, and refills itself.** FMCSA's census file gives
  name, phone, email, address and authority grant date. **~3,200 new operating authorities granted
  per week.** 2,204,341 active USDOT registrants; ~580,000 authorized interstate carriers.
- **The purchase is legally mandatory and time-boxed.** A new authority must have consortium
  enrollment before operating and faces a New Entrant Safety Audit. You arrive the week they are
  *required* to act — you are not persuading anyone to want software.
- **Credibility is not the gate.** A one-truck owner-operator cares that his file is right and his
  renewal doesn't lapse. He does not check your degree. (Contrast HACCP below.)
- **Nobody sells the bundle.** DQ files from one vendor, consortium from another, IFTA from a third,
  Clearinghouse from the government's own portal. The $30–$49/driver/mo "managed" tier is people
  doing filing by hand.

**The 60-day plan:**
- *Days 1–7:* pull the FMCSA census, build the new-authority filter, get a phone number. **Partner
  with an existing consortium as a reseller — do not try to become one** (licensing problem;
  wholesale is $49–$60/driver/yr against $295 retail).
- *Days 8–21:* call 30 new authorities a day. Offer: *"$499 for your first year — consortium
  enrollment, DQ file built and kept audit-ready, Clearinghouse queries run, IFTA filed quarterly."*
  Do the first ones by hand in Google Drive. **Target first dollar by day 14.**
- *Days 22–60:* with 10–20 paying carriers, build the software you were faking. Customers dictate
  the spec.

**Realistic 60-day number: ~15 carriers × $499 = ~$7,500 collected**, converting to ~$500–$700/mo
recurring as renewals cycle. Not life-changing — but real revenue from a real market with a
repeatable channel, and the fastest honest path found.

---

## #2 — HACCP food-safety plan generation → logbook subscription

**The gap is enormous:** consultant-written plans run **$3,250 (10 hrs) to $5,000–$8,000, up to
~$17,000**; consultants bill $50–$300/hr (senior specialists $150–$1,000/hr). The cheapest software
is **$59.99/location/mo** (Zip HACCP), with FoodDocs $84–$250/mo and QTRACA $199–$349/mo.

**Nothing serves a food truck or a five-person co-packer well.**

Proof the middle monetises: **FoodReady.ai — an AI HACCP builder — estimated ~$3.5M annual revenue,
~40,000 users**, customers reportedly including Kraft-Heinz and Conagra. ⚠️ *Third-party estimate
site, not a disclosure.*

**Price:** $750 flat for the generated plan (vs a $3,250 floor), then $89/mo for the daily logs the
plan requires.

**The honest risk:** buyers ask *"are you a certified food safety professional?"* A 20-year-old
statistics undergraduate is a hard sell. Mitigate by positioning as software plus a contracted
reviewer — never as the expert.

---

## #3 — Permit / contractor-license data sold as sales leads

**The clearest arbitrage in the dataset.** Shovels.ai charges **from $599/mo, sales-gated**, for
normalised building-permit data across 2,770+ jurisdictions — data that is free and public at source.

**Price:** $149–$299/mo for one metro, one trade. Undercut by 4x on a narrow slice.

**90-day v1:** scrape 20–40 county permit portals, normalise, geocode, score by job value, deliver a
daily CSV and a simple dashboard. Pure API orchestration and scoring — the closest fit to what
already exists in PantryChef.

**First 10 customers:** email the contractors who *appear in your own permit data*. You already have
their name, address, and proof they are actively working.

**Comparable lead economics:** roofing leads $40–$120, HVAC install $30–$80, plumbing emergency
$15–$50; Google LSA exclusive $25–$75; Angi $15–$150/shared lead with real cost per booked job
$250–$500. Personal-injury legal leads average **$284 CPL in 2026**.

---

## #4 — New-authority carrier lead feed (sell separately from #1)

**Buyer:** trucking insurance agent, freight factoring rep, ELD/dispatch service.

~3,200 new authorities/week from free FMCSA data. A new authority **must** buy insurance
($750K–$1M auto liability required before authority activates) — so intent is near-certain.

**Price:** $299/mo state-exclusive daily feed, or $15/lead exclusive.

**Could produce a first dollar in two weeks.** ⚠️ Apify already hosts FMCSA new-authority scrapers —
competition exists, which is also proof of demand. Build against USDOT number, not MC (being retired).

---

## #5–#10, briefly

**5. Vertical AI receptionist, one trade.** Human answering service Ruby is **$235/mo for 50 minutes**
rising to $1,725/mo with $4.35–$5.40/min overage. AI: Rosie $49/$149/$299, Goodcall $79/mo.
**But your cost is $0.13–$0.33/min all-in** — at 1,000 minutes that's $200 against Rosie's $149 list.
**Price at $349/mo, not $99.** Ranked only fifth because it's an agency not a product, Vapi and
Retell ship no native white-label, and **Avoca — voice AI for HVAC and plumbing dispatch — hit a $1B
valuation in April 2026.** The vertical now has a unicorn defending it.

**6. Janitorial bid assembly.** A bid is production-rate math plus boilerplate — ideal for LLM +
scoring. But the going rate is $24.95–$159/mo, so the ceiling is low.

**7. Fire/life-safety inspection reporting.** Price dispersion from **$40/user/mo to $1,299/mo** for
functionally the same NFPA form output. That much dispersion means buyers can't compare and nobody
owns the category. Annual, mandatory, recurring.

**8. Childcare licensing compliance.** 82,200 establishments, $74.3B industry. ChildCareComp charges
$99/mo. Rules are state-by-state — that's both the moat and the build cost.

**9. Productized AI-visibility (GEO) audits.** Fastest cash of anything here — agencies charge
$1,500–$5,000 for one-off audits, $2,000–$8,000/mo retainers. But it's services, not recurring, and
it's a bubble.

**10. Micro-acquisition — don't.** Sub-$50K deals trade at a **median ~1.7x profit multiple**;
Acquire.com's overall SaaS median is **3.9x profit**. He has no capital. Listed for completeness only.

---

## Verticals where the software is genuinely bad

1. **Pest control — strongest evidence.** PestPac sits at **3.9/5 across 233 Capterra reviews**, with
   verified reviewers calling the interface *"extremely dated,"* *"clunky,"* support *"slow for
   smaller accounts,"* and add-ons *"poorly integrated."* Yet it remains the mid-market default. A
   disliked leader in a market that can't leave.
2. **Anything sales-gated** — see the heuristic at the top.
3. **Trucking compliance** — four unrelated vendors for one owner-operator's obligations.
4. **Small-scale food safety** — a gap from $3,250 to $59.99/mo with nothing in between.
5. **Fire inspection** — 32x price dispersion for the same output.
6. **Funeral homes** — 15,401 buyers; the transparent leader charges **$135/mo and counts *computers***.
   Pricing by seat-installs in 2026 is a tell.

⚠️ **Critical caveat:** the search tool cannot reach Reddit at all. There is **no primary owner-voice
evidence** for any "software is bad here" claim — only vendor pages and review aggregators. Treat
these as hypotheses to validate by phone, not findings.

---

## Solo founders who actually did it — the relevant comparison set

- **Pieter Levels: $3M+ ARR, zero employees.** PhotoAI at $138K MRR (Nov 2025).
- **Base44: solo founder, $3.5M ARR at six months, sold to Wix for $80M** — built on $10–20K of his
  own money.
- **Ben Broca / Polsia: $1M ARR solo**, 1,100 client companies.
- **Leadmore AI: $30K+ MRR solo.**

Venture-scale, relevant only as proof the vertical pays: Harvey (legal) $300M ARR by May 2026;
Legora $100M ARR in 18 months; Sierra $150M ARR at $15.8B; Arena $100M ARR nine months post-launch.

⚠️ Most "AI agency" revenue claims found ($20K–$50K MRR by day 90, etc.) appeared **only on the
websites of companies selling AI agency tooling**, with no named customer. Treat as marketing fiction.

---

## What could not be verified

- **Every figure here.** No vendor pricing page was loaded directly.
- **Reddit inaccessible** — no owner-voice evidence anywhere.
- **No published price exists** for PestPac, Briostack, Passare, storEDGE, Vantaca, ServiceTitan,
  Highway, Carrier Assure, GovWin, BidPrime, Brightwheel, Procare.
- **FoodReady's $3.5M / 40,000 users** — third-party estimate.
- **BoredHumans at ~$8.8M ARR** — single Medium post, implausible, discount heavily.
- **No published price per new-authority lead** — the volume and buyers are established, the price
  is a gap. One call to an insurance agency settles it.
- **Business counts conflict badly** (pest control 13,600 vs 64,575; funeral homes 15,401 vs 19,000
  vs 28,816; motor carriers 2.2M vs 580K). Use the lower, definition-tight figure in any model.
- **Contractor license data as a commercial product** — searches returned only free state lookup
  portals. Either an opportunity or evidence nobody pays.
