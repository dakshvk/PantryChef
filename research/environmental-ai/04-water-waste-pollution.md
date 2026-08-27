# Water, Waste & Pollution — Findings

_Agent 8 output, Aug 2026. Egress gateway blocked **all** direct page fetches (epa.gov,
federalregister.gov, ecfr.gov, journals, even Wikipedia — all 403). Only search worked.
**Every quote is the search tool's rendering of the source page.** URLs and dates accurate;
wording needs primary-source verification._

---

## ⚠️ CONFLICT WITH WAVE 1 — Phase I ESA is more crowded than the Land agent found

The Land agent named **Phase I ESA historical-records automation** a Tier-1 opportunity. This agent
found the AI-drafting layer **already contested**: **CaseMark, V7 Go, Nomic, Quire**, plus in-house
efforts at consultancies like EKI — and documented industry anxiety about liability for
AI-generated reports.

The *historical records* sub-task (Sanborn maps, aerials, city directories) may still be open, but
"nobody is doing Phase I ESA AI" is **false**. Downgrade accordingly.

---

## The strongest new findings

### 1. LCRI school & childcare roster — the list does not exist anywhere ⭐

By **1 Nov 2027** every community water system must submit a list of all elementary/secondary schools
and licensed childcare facilities it serves, then sample ≥20% of non-waived facilities per year
(5 samples per school, 2 per childcare). Non-responders require **two documented outreach attempts**,
logged, annually.

**No utility holds an authoritative roster of licensed childcare facilities in its service territory.**
The three inputs live in three unrelated places: state social-services licensing registries, NCES
school directories, and water-system service-area boundaries. Nobody has joined them.

All three are **free and public**. EPA released **v2 of its Community Water System Service Area
dataset in September 2025**; the EPIC/SimpleLab open dataset covers **45,973 CWSs serving 307.7M
people, MIT-licensed** on GitHub and HydroShare.

Pure geospatial entity resolution. No hardware. **No vendor found doing it** — though the agent flags
this negative finding as its own biggest risk.

### 2. Industrial stormwater citizen-suit risk scoring ⭐

California's **SMARTS** database is public and contains every permitted facility's exceedance
history — and it is *literally the mechanism plaintiffs use to select targets* for Clean Water Act
citizen suits. The CWA imposes strict liability, and §505 requires a 60-day Notice of Intent before
filing.

A facility with a rolling Numeric Action Level exceedance pattern **is visible to plaintiff groups
before it is visible to its own management.** A small, identifiable set of repeat filers (LA
Waterkeeper, Eden Environmental Citizens Group, Waterkeeper affiliates) drives most California
filings — so filer behavior is *learnable*.

**Sell risk alerts to facilities and tap litigation-avoidance budgets, which are far larger than
compliance-software budgets.** Data is free, model is tractable, no analytics layer exists over SMARTS.
⚠️ 2025–26 filing volumes unverified — this materially affects market sizing.

### 3. EPR supplier-document extraction — packaging and California textiles ⭐

Packaging EPR is **in force in seven states** (OR, CO, CA, MN, MD, WA, ME); six had reports due
**31 May 2026**. California, Colorado and Oregon require **SKU-level and component-level** data;
MN/MD/WA accepted simplified aggregated weights for 2026 as an **explicitly temporary accommodation
that will tighten.**

The reporting portals are built (Ecoveritas, Circular Action Alliance, Brightest, Z2Data). **The
bottleneck moved upstream:** suppliers do not have component-level weight data in structured form —
it lives in spec sheets, drawings, PDFs and tribal knowledge. This is a document-extraction problem
wearing a reporting problem's clothes.

**California textile EPR (SB 707) is the cleanest opening** — the market is genuinely pre-formed:
CalRecycle named **Landbell USA as PRO on 1 March 2026**, covered producers had to join by
**1 July 2026**, and regulations don't take effect until **1 July 2028**. Coverage spans clothing,
shoes, swimwear, uniforms, blankets, curtains, towels, linens, pillows — determining coverage and
fiber composition across tens of thousands of SKUs from product listings, care labels (legally
required, therefore extractable) and supplier declarations is **unbuilt work**. Buyers are
well-capitalized apparel brands with a hard date.

### 4. Small water utilities — yes underserved, but they are not the buyer

The money flows through **technical-assistance intermediaries**, not the systems. EPA announced
**$30.7M on 24 July 2026** for small/rural system training and TA, with **NRWA receiving $9.1M**;
USDA RUS awarded NRWA a five-year Circuit Rider contract in **May 2026**.

**Sell a compliance copilot to circuit-rider organizations as a force multiplier across their
portfolio**, not to utilities one at a time.

Why they need it: LCRI baseline inventory (Nov 2027), school/childcare rosters (Nov 2027), revised
CCR (Jan 2027) and PFAS MCL compliance (2029, possibly 2031) all land in the same window, on staffs
of one to three people.

### 5. Consumer Confidence Report rule — doubles frequency, adds translation

Finalized 15 May 2024, **in force**. First compliance **1 Jan 2027**; first affected reports due
**1 July 2027**. Systems serving >10,000 must distribute **twice per year**, with plain-language and
translation obligations most systems have no workflow for. State primacy adoption was due 25 May 2026;
EPA issued primacy support documents Jan 2026 — evidence it is proceeding, not stalled.

Source data (state SDWIS compliance monitoring) is already structured. **This is a document-generation
problem sitting on top of a database.** No dominant incumbent found.

### 6. UCMR 5 — a near-complete national PFAS dataset nobody has fully mined

**~1.9 million sample results across 10,299 public water systems**, ~95% of expected results,
Q1 2023–Q3 2025. Eleventh release Feb 2026; final release expected early fall 2026. Fully public.

It tells you *where* PFAS is, not *why*. **Source attribution** — joining detections to upstream
industrial dischargers, airports, military AFFF sites and land-applied biosolids via TRI, NPDES/ICIS
and hydrology — is unshipped. Buyer: litigation support, state agencies, utilities building
cost-recovery cases against polluters.

### 7. EJScreen's removal created a durable gap

**EPA removed EJScreen entirely on 5 Feb 2025** — the tool, landing pages, data downloads, and the
ArcGIS server serving the spatial data. CEJST also removed. Volunteer reconstructions exist but are
frozen v2.3 snapshots with no official standing.

Meanwhile the *requirement* persists at state level: **New Jersey's EJ Law is in force** — applicants
for covered permits in overburdened communities must prepare an EJ Impact Statement addressing
cumulative stressors, hold a hearing, and respond in writing to comments; NJDEP may impose conditions
or deny.

**Permit applicants have budget** and pay consultants today. Community groups do not.
⚠️ A startup (Avow) is already publishing on rebuilding EJ screening from source data.

---

## PFAS regulatory whiplash — the "don't assume" item

**PFOA/PFOS MCLs remain in force** (final April 2024). As of 27 Aug 2026 there are **two PROPOSED,
NOT FINAL rules**: extending PFOA/PFOS compliance from **26 Apr 2029 to 26 Apr 2031**, and
**rescinding** the MCLs for PFHxS, PFNA, HFPO-DA (GenX) and the Hazard Index. Proposed 18–20 May 2026,
comment closed 20 July 2026, **neither finalized**.

A treatment plant is a 20-year capital decision being made against a rule that changed twice in
24 months.

---

## Also notable

- **TRI PFAS de minimis removal** (in force since reports due 1 July 2025) means PFAS must be counted
  at **any concentration** in mixtures. **205 TRI-applicable PFAS for RY2025, rising to 206** with
  PFHxS-Na effective 1 Jan 2026. SDSs frequently don't disclose trace constituents. LLM over a
  facility's SDS library is a clean fit; EHS incumbents (Trinity, ERA) are entrenched though.
- **NPDES eRule Phase 2 went live 21 Dec 2025** — a genuinely new standardized national dataset on
  sewer spills and biosolids now exists and is essentially unanalyzed. ⚠️ Data flow unconfirmed.
- **Air sensor calibration is a real technical problem with no paying buyer.** A study of **1,013
  PurpleAir sensors on six continents** found raw readings overestimate PM2.5 and **US-based
  calibrations show limited transferability outside North America** — and they fail worst during
  wildfire smoke, when decisions matter most. But **no regulation forces sensor data quality**, and
  community groups are chronically unfunded. Air districts under CA AB 617 are the only real buyer.
- **PFAS in biosolids: regulatory vacuum.** EPA's Jan 2025 draft risk assessment found risk at
  concentrations as low as 1 ppb; the **1 July 2026 draft guidance took a notably less stringent
  approach**. Nothing final, nothing in force. Too speculative to build on.
- **Waste characterization is still hand-sorting** — crews dump samples on a floor and sort into
  15–70 material categories (~33 for single-stream). Episodic (every 5–10 years), so composition data
  is stale exactly as EPR programs start needing it current. ⚠️ No cost figures found at all.

---

## Already crowded

Lead service line **material prediction** (BlueConduit + 120Water, partnered since June 2023) ·
**MRF sorting robotics** (AMP raised $91M Series D, plus Glacier, Greyparrot, Recycleye, Waste
Robotics — capital-intensive hardware) · **Phase I ESA AI drafting** (CaseMark, V7 Go, Nomic, Quire,
in-house) · **EPR reporting portals** (the submission layer is covered) · consumer tap-water lookups ·
general EHS/TRI suites.

---

## Could not verify

- All direct quotation — egress blocked every fetch.
- The **24 million unknown service lines** figure sits awkwardly beside EPA's 2025 DWINSA estimate of
  4M LSLs (3M reported + 1M unknowns predicted lead). These may measure different things.
- LCRI unknowns-identification deadline of 31 Dec 2037 — one search summary only.
- Outcome of *American Water Works Association v. EPA* — briefing through April 2026, **no decision found**.
- **CWA 60-day notice filing volumes for CA 2025–26** — search returned none. Materially affects the
  stormwater market sizing.
- Waste characterization study cost — no pricing found anywhere.
- MS4 annual report hours/cost — only vendor marketing copy.
- National counts of schools/childcare facilities subject to LCRI sampling.
- Current AB 617 funding level — only figure found ($245M) is from FY2018-19 and almost certainly stale.
- Whether the revised CCR rule faces reconsideration — searched specifically, found none.
- Whether Phase 2 sewer-spill data is actually flowing into ECHO.
- **That no vendor builds LCRI school/childcare rosters** — a negative finding from search absence,
  the weakest kind. **This is the biggest single risk to the agent's top recommendation.**
