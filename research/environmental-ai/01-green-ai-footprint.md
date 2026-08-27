# Green AI / AI Footprint — Findings

_Agent 2 output, Aug 2026. 200 searches run. WebFetch was egress-blocked for most domains, so
quotes are search-surfaced page text rather than text read in the primary document. **Every quote
needs one verification pass before it goes in a deck.**_

---

## Headline verdict

**Mostly hype at the label, real underneath — but only where the environmental outcome is a
*byproduct* of a constraint someone is already paying to solve.**

Money is demonstrably real:
- **Emerald AI** raised $150M at a $1.05B valuation on 25 Aug 2026 for data-centre load flexibility
  (investors incl. NVIDIA, Siemens, GE Vernova)
- **Phaidra** raised $50M in Oct 2025 for cooling control
- **Greenpixie** hit cash-positive on ~£5M raised, ~50% YoY revenue growth, Fortune 1000 customers

Note what all three sell: **capacity, uptime, and cost.** Emerald sells a faster grid connection.
Phaidra sells reclaimed megawatts for revenue-generating compute. Greenpixie sells cloud-spend
reduction with carbon attached. **None sells virtue.**

Evidence the virtue market is dead:
- SEC proposed rescinding its climate rule outright, May 2026
- EU Omnibus cut CSRD scope ~80% (in force 18 Mar 2026)
- CARB's SB 261 deadline enjoined by a Ninth Circuit injunction
- OpenAI and Anthropic approach IPOs with no emissions disclosure and no apparent penalty
- **Electricity Maps killed its own marginal-emissions product in 2025** because the signal wasn't
  defensible — the exact signal that justifies carbon-aware scheduling

---

## The twelve findings, ranked by whether anyone pays

### Would pay — strongest theses

**6. Utilities cannot tell real data-centre load requests from phantom ones** ⭐ strongest
Load interconnection queues are flooded with speculative and duplicate requests — the same project
shopped to multiple utilities in multiple states. Unlike generator queues, **load requests carry no
standardized transparency requirement.** Utilities build capital plans and rate cases on numbers
inflated 3–5x.
- Wood Mackenzie projects only **28% of 1,066 GW** in US data centre power requests will be honored
- ERCOT reported ~226 GW of large-load interconnection requests in Dec 2025, up from ~63 GW at
  end-2024
- *"It's very difficult for utilities to tell in advance which data center interconnection requests
  will pan out… load requests are not subject to standardized transparency requirements"*
- **Angle:** cross-jurisdiction "is this project real?" scoring — LLM/agentic extraction from county
  zoning agendas, air permits, LLC/land records, utility filings and job postings, deduplicated into
  project entities with a probability-of-build score
- **Why it pays:** utilities, IPPs, transmission developers and infra investors already pay real
  money for siting intelligence. It sells as market intelligence; environmental benefit (avoided
  overbuild) is the byproduct. Confidence: high

**9. Inference/GPU efficiency — sold as cost, not carbon**
Average GPU utilization in AI clusters ~22%; advanced Kubernetes scheduling can move 13%→37%;
continuous batching can move sub-20%→70%+, cutting cost per token 3–4x. Every watt saved is a dollar
saved, which is why this is reliably funded.
- **Data access is the best in this whole report** — DCGM/NVML telemetry, scheduler logs, billing
  exports, gateway logs. No begging a utility for data.
- **Angle:** inference-layer optimizer (routing, batching, cache reuse, region selection) reporting
  dollars first, kWh/CO2e/water second, exported into the customer's Scope 3 filing
- **Caveat:** extremely crowded — every FinOps vendor, every LLM gateway, the clouds themselves.
  Greenpixie is the realistic template. Confidence: high

**4. Colocation Scope 2/3 allocation has no standard method**
When a bank runs racks in a colo, both parties need an emissions number and **3–4 incompatible
allocation methods circulate**, so the same MWh gets counted differently by two counterparties.
Handled today via per-tenant spreadsheets and bespoke contract annexes.
- **Angle:** two-sided attestation — operator uploads facility data once, each tenant gets a signed,
  method-labeled allocation with a reconciliation report
- **Why it pays:** the colo operator currently absorbs this as unbilled account-management labor.
  Most plausible "boring B2B SaaS" wedge here. Confidence: medium (thin sourcing — could not verify
  date/authorship of the 7x24 Exchange source)

**5. Water — ~half of operators still don't measure it, while water becomes the binding permit constraint**
Water data collection was 47% in the 2025 Uptime survey, 53% in 2026 (the rise led by Europe,
presumably EED-driven). Meanwhile ~two-thirds of new data centres built or in development since 2022
are in places already under high water stress.
- Regulatory patchwork: EU EED (WUE is one of 24 KPIs); Minnesota 2025 water permitting; Utah HB0076
  advance-notice requirement; Illinois SB2181 annual reporting from 1 Jan 2026; federal S.4213
  introduced 25 Mar 2026 — **not law**
- **Sell to developers in active permitting, not to sustainability teams.** Permit delay costs far
  more than software; an ESG report doesn't. Confidence: high on gap, medium on buying motion
- ⚠️ The widely-cited "264 billion gallons in 2025" figure traces to a commercial market-research
  firm — **unverified**

**7. Load flexibility is becoming mandatory — and curtailment must be measured and verified**
Texas SB 6 requires large loads to curtail within 30 minutes of an ERCOT emergency instruction
without compensation (in force after 31 Dec 2025). PJM's Interim Resource Adequacy Service, filed
with FERC 31 Jul 2026, applies to new 50 MW+ loads from 1 Jun 2027.
- **Angle:** not the orchestrator — the **M&V layer**. An independent baseline-and-settlement service
  certifying how many MW actually came off against a counterfactual.
- **Why the niche:** the orchestration slot is taken by a $1B company welded to NVIDIA's DSX Flex. A
  1–3 person team should not compete there; settlement/audit is unglamorous enough to be left alone.

### Would pay — conditionally

**1. EU EED Article 12 data-centre reporting.** Every EU data centre ≥500 kW IT power must file 24
KPIs annually by 15 May. *"first-round EED data was incomplete."* Real mandate, small tickets,
crowded field (Schneider, Socomec, DCIM incumbents). Wedge is the messy middle — European colos too
small for Schneider, too big for spreadsheets.

**10. EU AI Act per-model energy documentation.** Art. 53 + Annex XI requires GPAI providers to
document computational resources, training time, and known-or-estimated energy per model version,
retained 10 years. In force 2 Aug 2025 for new models, 2 Aug 2027 for legacy. **No prescribed
methodology** — the Commission has an open consultation on how to measure AI energy at all. Small
buyer universe (dozens of labs) but real legal exposure. Better as open-source standard + paid
attestation than seat-based SaaS.

**2. California SB 253/261** — real deadline, legally wobbly. CARB set a first-year deadline of
10 Aug 2026, delayed to 10 Nov 2026; SB 261 unenforced due to a Ninth Circuit injunction. The buyer
exists but already spends with Watershed/Persefoni/Workiva. **Sell into those platforms as a data
source, not against them.**

**3. Scope 3 buyers can't get emissions data from AI vendors.** Neither OpenAI nor Anthropic
publishes full Scope 1/2/3. Only Google has published a per-prompt methodology (0.24 Wh, 0.03 g CO2e,
0.26 mL water per median Gemini text prompt). Current practice is estimation by analogy — *"guesswork
dressed as accounting"* that won't survive limited assurance. **Weak on its own** (a line item nobody's
bonus depends on); becomes payable only bundled with the cost/routing optimization in #9.

### Do not build

**8. Carbon-aware scheduling — the clearest "don't build it" signal in the report.** Decade-old idea,
open-source tooling, cloud provider features, dozens of papers. The Green Software Foundation's own
public adopter list names a handful of firms. And the underlying signal is being deprecated by its own
vendor: *"Electricity Maps worked with marginal emissions for close to a decade, when it decided to
discontinue the marginal data offering in 2025 due to concerns about the veracity and verifiability
of such signals… recent legislations from the US government and the European Commission prohibiting
their use."* **Regulation is moving against the value case.** Reframe entirely if pursued: schedule on
price and capacity headroom, report carbon as free exhaust.
- ⚠️ The "$310M → $2,845M by 2036" market figure circulating for this comes from a paid
  market-research press release — **unverified marketing**

**11. Hardware refresh / e-waste.** Real physical problem — generative AI could produce up to 2.5 Mt
of e-waste/year by 2030 from a 2023 baseline of 2,600 t; extending server life and reusing parts
could cut that up to 86% (Nature Comp. Sci., Oct 2024). But **no software buyer.** The refresh
decision is driven by performance-per-watt economics that dwarf e-waste considerations, and the
people who care have no budget. Skip.

**12. Hyperscalers — a targeting constraint, not an opportunity.** Google's overall emissions rose 11%
YoY to 11.5 Mt (+51% vs 2019) with data-centre electricity up 27%, even while per-unit data-centre
emissions fell 12%. Microsoft's total emissions are +23.4% vs 2020, with Scope 3 (>97% of footprint)
up 26% over five years. Best-instrumented environments on earth, huge in-house teams, no data gap to
sell into. **Implication: sell to the parties constrained by hyperscaler growth** — utilities, water
districts, counties, colos, enterprise buyers.

---

## The strongest argument against building here

The buyer with the legal obligation (a corporate sustainability team) has shrinking budget and
shrinking mandate. The buyer with real budget (utilities, colos, AI infra teams) **does not want a
green product** — they want capacity, permits, and lower cost, and will buy those from a vendor with
domain credibility and no environmental branding at all.

Build "green AI software" and you land in the gap between the two: **the people who care can't pay,
and the people who can pay don't care what you call it.**

---

## Recommended plays for this founder

No hardware dependency, data actually accessible:
1. **Phantom-load / project-reality intelligence** for utilities and infra investors (#6)
2. **Colocation Scope 2/3 allocation exchange** (#4)
3. **Inference-cost optimizer emitting compliance-grade footprint data as exhaust** (#9 + #3)

Avoid: carbon-aware scheduling, e-waste, anything sold to a hyperscaler.

---

## Key sources

IEA *Energy and AI* (Apr 2025) · LBNL 2024 US Data Center Energy Usage Report · White & Case EU
outlook 2026 · Mayer Brown / Greenberg Traurig on CARB rulemaking · SEC climate rescission proposal
(May 2026) · Clifford Chance on Omnibus I · Fortune/Bloomberg "AI giants quiet on climate"
(12 Aug 2026) · Google Cloud inference impact methodology (Aug 2025) · Google 2025 Environmental
Report · Microsoft 2025 Sustainability Report · Uptime Institute 2025/2026 surveys · Bloomberg water
graphics (2025) · S.4213 (119th Congress) · Baker Botts on TX SB 6 · Utility Dive on PJM IRAS and
phantom load · Latitude Media on ERCOT queue · SiliconANGLE on Emerald AI · Tech.eu on Greenpixie ·
GSF Carbon Aware SDK adopters · Electricity Maps data page · Latham & Watkins on EU AI Act GPAI ·
EC consultation on measuring AI energy · Nature Comp. Sci. on generative AI e-waste ·
7x24 Exchange on sustainable colocation
