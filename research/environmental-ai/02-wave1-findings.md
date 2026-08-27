# Wave 1 Consolidated Findings

_Problem Scout · Research Gap Hunter · Ocean & Diving · Land & Terrestrial. Aug 2026._

> **⚠️ VERIFICATION DEBT — READ FIRST.** WebFetch/curl were egress-blocked for essentially every
> external domain in this session (nature.com, arxiv.org, epa.gov, noaa.gov, sciencedirect, pmc,
> gao.gov — all 403 policy denials). **No agent opened a single primary PDF.** Every quote below is
> text as reproduced by the search index against the cited URL. Nothing was invented, but everything
> needs one verification pass before it goes anywhere external. This is precisely what the
> fact-check wave exists to clear.

---

## THE CONVERGENT SIGNAL

Five themes were named independently by multiple unrelated literatures. Repetition across
non-overlapping fields is the strongest evidence in this whole program.

### 1. Annotation labor is the universal bottleneck — six independent literatures

Coral, camera traps, aerial wildlife surveys, bioacoustics, terrestrial ecology ML, and marine AI
all separately name manual annotation or labeled-data scarcity as *the* binding constraint.

The most citable number found: **"it would take a single trained expert around 200 full-time working
days to annotate one million images"** (Science of the Total Environment, 2026).

Others: NOAA benthic stereo-video reviewers spend **30–60 min per 4.5-minute transect** (~7–13 hours
of analyst time per hour of footage). MBARI holds ~28,000 hours of deep-sea video. Reef Check
California reports **1–2 hours of data processing per survey**, against 681 dives in one 2024 season
for one region.

*"When the rate of data production exceeds analytical capacity… important data are frequently cast
aside as bycatch, left unanalyzed on decaying hard drives."* (arXiv:2411.14219)

### 2. Data fragmentation across incompatible systems — four+ independent literatures

- **Water quality:** ~25M records in the EPA/USGS Water Quality Portal; **~14.5M have missing or
  ambiguous metadata**. 130 unique parameter names represent nitrate-plus-nitrite alone.
- **Biodiversity (PNAS 2026):** *"Current biodiversity data are fragmented, uneven in quality, and
  seldom comparable across space or time"*; Darwin Core and FAIR/CARE *"do not connect the full
  chain from field observation to policy reporting."*
- **Federal fuel treatments (Scientific Data 2025):** *"Information regarding when, where, and what
  types of treatments have occurred is scattered across multiple systems of record."*
- **Ocean FAIR (WorldFAIR):** *"entirely valid, but local/regional, FAIR implementations will still
  lack global interoperability."*
- **Microplastics:** studies use incompatible size fractions, *"offering no reliable way to combine
  the available data."*
- **Kelp forests:** four programs (SBC LTER, PISCO, Channel Islands NP KFM, Reef Check CA) survey
  the same Santa Barbara reefs with incompatible protocols. Crosswalks are rebuilt by hand per project.

### 3. Models don't survive moving to a new site — four literatures

Camera traps (*"limiting the models' applicability in new locations"*), marine AI (*"subject to
domain shifts… poorly benchmarked across operational contexts"*), terrestrial ecology
(*"difficulties with model generalization"*), coral. **Nobody sells operational benchmarking for
environmental ML.**

Concrete: MegaDetector hits ≥94.6% accuracy on motion-triggered images but **≤61.6% on time-lapse
images**. BirdNET predictive power ranges 0.16–0.23 in North America/Oceania/Europe but **0.03–0.04
in Africa and Asia**.

### 4. Cost, not capability, gates adoption

A 2022 practitioner survey: *"high cost was the main barrier to technology use across occupations."*
Coral monitoring is *"limited in scale due to requiring expensive equipment or substantial expert
time."* Soil carbon is *"prohibitively expensive."*

**Commercial implication: sell the removal of an expert salary or a capex line. Never sell an addition.**

### 5. The gap between what is reported and what is real

MPAs report protection that isn't implemented (*"only 2.6% of the ocean was implemented and highly
or fully protected"*). NEPA produces no structured record of its own output. Fuel treatments can't be
evaluated. Every one is a **document-processing problem hiding inside a policy problem.**

---

## THE META-THESIS

From the Ocean agent, and the single best strategic sentence produced by Wave 1:

> The *technical* bottlenecks in conservation are increasingly solved by open-source tools and open
> models. The *deployment* bottleneck — a small organization with no ML staff, no GPU, and no budget
> getting an answer this week — is not.
>
> **Don't build the model. Build the operational layer that makes existing open models usable by
> people who will never install VIAME.**

---

## TOP OPPORTUNITIES (pre-scoring)

### Tier 1 — legally compelled, real buyers, public data

**Phase I ESA historical records automation** *(Land #7)*
CERCLA §101(35)(B) / 40 CFR Part 312 "All Appropriate Inquiries" — a Phase I meeting ASTM E1527-21
is the **only** way to get the innocent-landowner liability defense. Lenders require it. $2,200–4,000
per report, 2–3 weeks each. The most time-consuming input — historical aerials, USGS topo, Sanborn
maps, city directories — is **public, free and digitized** (Library of Congress has ~35,000 Sanborn
maps; USGS topoView; NAIP/EarthExplorer), while incumbent EDR/LightBox sells it back as an expensive
proprietary report. Buyer is a consulting firm with a cost-per-report line item, not a grant-funded
agency. Vision + document extraction + LLM drafting — exact founder stack.
⚠️ National annual volume unverified.

**CEQAnet corpus + CEQA exemption screener + MMRP tracker** *(Land #6)*
Everyone chased federal NEPA; **PNNL's PermitAI got there first** with NEPATEC (28,000 docs, 4.6M
pages, >3.6B tokens, expanding past 100,000). **Nobody built the state analogue.** CEQAnet holds 35
years of full-text California environmental documents, public and free, with no LLM tooling on it.
Meanwhile AB 130/SB 131 (June 2025) created a brand-new multi-condition housing exemption test that
hundreds of planning departments now apply **by hand**, and §21081.6 MMRP tracking is a decades-old
spreadsheet problem. Clearest "rich public dataset going underused" finding in the program.

**Parcel-level wildfire mitigation verification for insurance** *(Land #10)*
Strongest regulatory driver found. **CA Ins. Code §2644.9** requires insurers using wildfire risk in
pricing to discount for *documented* mitigation. The FAIR Plan stood up **12 discrete discounts
effective 15 Nov 2025** (up to 16.4% savings). Policyholders have a statutory **right to appeal their
risk score** — creating a second buyer. Inputs are free and now essentially complete: USGS 3DEP lidar
>98% national coverage with baseline finishing 2026, NAIP, county parcels, 2025 FHSZ maps. Lidar
returns within 5 ft of a structure footprint answer Zone 0 compliance directly.
⚠️ Validate whether Zesty.ai / Delos / Faura already do *mitigation verification* vs. just risk scoring.

**Landfill methane: GHGRP self-report vs. satellite discrepancy** *(Land #12)*
The mandated method demonstrably fails: *"SEM was effective for closed sites, achieving on-average
67% rate coverage, however, SEM missed relevant emission sources at open landfill sites, most notably
from the active face, reducing its rate coverage to 17%."* (Waste Management vol. 207, 2025). EPA has
issued an enforcement alert on landfill gas calculation violations. **Pure public-data product:**
cross-reference EPA GHGRP Subpart HH self-reported emissions against public satellite plumes
(Carbon Mapper, EMIT, TROPOMI) and rank facilities by discrepancy.

### Tier 2 — strong fit, softer buyers

**Temperate reef / kelp forest CV + four-program crosswalk** *(Ocean #1 + #4)*
Every dollar in benthic CV went to tropical coral. CoralNet's two documented failure modes are
*exactly* the temperate condition: *"Class imbalance remains a major bottleneck—performance is strong
on frequent genera but drops markedly for rare genera"* and *"CoralNet's user-generated labels are
heavily source-dependent and lack a unified taxonomic standard like WoRMS."*
**This is the one opportunity where the founder's location is a genuine, non-transferable advantage** —
SBC LTER, PISCO, Channel Islands KFM, Reef Check CA, CINMS and NCEAS are all within a few miles of
UCSB, with 40+ years of overlapping public data.
⚠️ Verify CoralNet doesn't already have substantial California sources.

**Validation-first triage for passive acoustic archives** *(Ocean #5)*
Everyone builds better *detectors*. The community says detection isn't the constraint: *"our ability
to collect data using acoustic recorders is no longer the bottleneck"* — the scarce resource is
*"highly specialized person-hours"* for **validation**. Nobody builds for that step. Pure
interface + active-learning. **No vessel, no sensor, no permits** — SanctSound data is free on Google
Cloud via the NOAA Big Data Program (30 sites, 7 sanctuaries, 2018–2022). Buildable and evaluable in
weeks with zero fieldwork.
⚠️ The "200 TB NOAA archive" figure is medium-confidence; re-verify against NCEI.

**NOAA Coral Reef Watch ground-truth intake** *(Scout #3)*
NOAA's own blunt admission: *"NOAA Coral Reef Watch does not have the resources to conduct in-water
coral bleaching surveys, and instead relies on reports… from partners, collaborators, and users
around the world to ground-truth their bleaching heat stress products."* Ground truth arrives by
**email and a Google Form**. NOAA further states *"a different methodology is needed for analyzing
and quality-controlling such reports."* During an event where heat stress hit 84% of global reef area.

**Live fuel-treatment effectiveness layer on TWIG** *(Gap #14)*
TWIG is published as a static geodatabase; the hard curation is done. Missing: continuous ingestion,
a treatment→fire-outcome join API, and the dashboard answering "did this treatment change outcomes."

**Bioacoustic validation-as-a-service** *(Land #2)*
*"advances in automated detection and deep-learning bioacoustic models have not been matched by
equivalent progress in the broader software ecosystems required to manage, analyse, and interpret
large PAM datasets."* Per-species thresholds retain **70 ± 37%** of detections vs **17 ± 14%** for a
universal threshold — but must be re-derived per site and season. Boring middleware nobody built.

**Scientific diving compliance co-pilot** *(Ocean #13)*
Small market (~130 AAUS orgs, unverified) but **UCSB Marine Operations runs a scientific diving
program on the founder's own campus.** Easiest customer-discovery conversation on the entire list —
validates or kills in one meeting.

### Tier 3 — software-only, real gaps, unproven buyers

eDNA reference-gap diagnostic (public DB integration + set logic, no wet lab) · museum specimen →
barcode gap matching · coral dataset registry + benchmark harness · Darwin Core Data Package
validator · ocean FAIR semantic-alignment broker · MPA regulation parsing against The MPA Guide ·
microplastics method harmonization · marine regulatory obligation crosswalk · soil carbon sampling-
design optimizer · urban canopy from free lidar/NAIP/thermal · conservation easement deed-parsing +
change detection.

---

## DO NOT BUILD — the negative findings

These are as valuable as the positives.

| Area | Why not |
|---|---|
| **Carbon-aware scheduling** | Decade of free tooling → adopter list you can count on two hands. Electricity Maps **killed its own marginal-emissions product in 2025** on veracity grounds; US and EU legislation now prohibits its use in reporting. Regulation moved *against* the value case. |
| **Voluntary carbon market / offset MRV** | Total 2024 transaction value **$535M** — smaller than a single Series C — with volume down 25%. 2025 retirements down another ~4.5–7%; issuances lowest since 2020. **Nori shut down in Sept after raising $17M.** Crowded and consolidating (Pachama acquired by Carbon Direct Nov 2025). |
| **Camera trap species classification** | Microsoft MegaDetector (MIT license) + Google SpeciesNet (~2,000 species) + Wildlife Insights (>200M images). Free, open, good. |
| **Federal NEPA document AI** | PNNL PermitAI + NEPATEC — national-lab funded, owns the corpus. Go to the states instead. |
| **Utility vegetation management** | AiDash, Overstory, SharperShape funded; Pano AI raised $89M total with 15 utility customers. **Line geometry is confidential** — no data access without a utility contract. PG&E alone plans ~$18B over the 2023–25 WMP cycle, which tells you who the incumbents are courting. |
| **Tropical coral image classification** | CoralNet, ReefCloud, TagLab, Allen Coral Atlas, DeepReefMap, ReefNet. Solved to ~80–90% for morphofunctional categories. |
| **Fisheries EM video review** | Painful but claimed — funded startups, NOAA SBIR winners, vessel relationships a solo founder can't replicate. |
| **IUU detection, photo-ID, deep-sea annotation infra, kelp *canopy* remote sensing** | Global Fishing Watch / Wildbook / FathomNet / Kelpwatch own these. *(Note: the kelp **subsurface** is the opening — canopy signal is a poor proxy for what's underneath.)* |
| **Pollinator/insect ID** | ~85% of bee monitoring cost is physical specimen handling; bottleneck is a scarce human with a microscope and a genuinely hard fine-grained vision problem. Poor software fit. |
| **Generic ESG dashboards, e-waste, selling to hyperscalers** | Saturated / no buyer / in-house teams. |

---

## OPEN LEADS AND UNRESOLVED ITEMS

1. **The 2026 ocean-AI practitioner survey was NOT found as described.** What exists: an **OCTO
   survey, November 2025, 173 submissions, 97 describing current AI use** — spanning illegal-fishing
   detection, marine debris classification, proposal development, and paper summarization. Referenced
   only via a Google Groups thread that was egress-blocked. **Chase OCTO/OpenChannels directly.**
   Practitioners are already using raw ChatGPT against regulatory corpora with no citation grounding.
2. Whether CoralNet already has substantial California/temperate sources.
3. Whether the 200 TB NOAA acoustic archive figure is current.
4. Whether CINMS was one of the seven SanctSound sanctuaries.
5. Whether GAO-14-369's NEPA data gap persists, or CEQ's 2025 EIS release closed it. **Verify first —
   it weakens or strengthens a Tier-1 candidate.**
6. Whether Zesty.ai/Delos/Faura already do wildfire *mitigation verification*.
7. Coverage gaps from exhausted search budgets: agriculture, waste, harmful algal blooms,
   environmental justice / air quality, climate adaptation planning, corporate reporting burden.
   *(Water/Waste and Climate agents were launched to cover several of these and are still running.)*

---

## STALE OR WEAK — flagged honestly by the agents themselves

- **Restoration/mitigation monitoring:** the hardest number (Corps received only 21 of 89 required
  monitoring reports) is **GAO-05-898, from 2005**. RIBITS was built partly in response. Treat as
  hypothesis, not finding.
- **Deforestation enforcement:** the 1.3% and ~98% non-enforcement figures are **2022, Brazil, under
  a different administration**. Shape of the problem is probably durable; the numbers likely are not.
- **eDNA reference gaps:** real and well-evidenced, but fails founder-fit — the binding constraint is
  wet-lab sequencing of museum vouchers. No identified buyer for the software slice.
- **Lead service lines:** the central 24M-unknowns figure comes from an **advocacy page**
  characterizing EPA's estimate, and BlueConduit et al. are already funded here.
- **Conservation tech cost-barrier survey:** 2022, outside the 2024–26 window.
