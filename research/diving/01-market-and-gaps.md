# The Diving Market — What Each Group Uses, What They All Miss, and Where the Money Actually Is

_Aug 2026. **WebFetch egress-blocked** — every figure is a search-index summary, not primary text.
No PDF, no filed financial, no Devpost or App Store page was opened directly._

---

## ⚠️ READ THIS BEFORE ANY NUMBER BELOW

Three paid market-research firms give the **scuba equipment market for the same year** as
**$5.18B**, **$1.10B** and **$1.87B**. That is a **5× disagreement**, and it is not a rounding
difference — it means they are measuring different things and none of them says which.

Diving market sizing is dominated by report-selling firms whose business model is publishing
confident numbers. **Treat every dollar figure on this page as an order of magnitude, not a
measurement.** The population and participation numbers are far more trustworthy than the revenue
numbers, because certification agencies actually count certificates.

---

## THE SEGMENTS, BY SIZE

| Segment | 2026 size | Growth | Note |
|---|---|---|---|
| **Unmanned underwater vehicles (ROV/AUV)** | **$6.91B** → $19.22B by 2031 | **22.7% CAGR** | Fastest-growing thing in the water by a wide margin |
| AUV/ROV for offshore inspection, maintenance, repair | $7.39B → $13.50B by 2034 | 7.8% | Offshore wind is the driver |
| **Dive tourism** | **$5.52–6.25B** → $10.8–15.3B | **~11.5–11.9%** | Biggest consumer-facing pool |
| Scuba equipment | $5.4B ⚠️ *(or $1.1B, or $1.87B)* | 4.4% | See warning above |
| Commercial diving services | $3.2B (2025) → $4.8B by 2033 | 5.2% | 25,000 divers globally |
| Spearfishing gear | $1.2B (2024) → $1.8B by 2033 | ~4.6% | |
| **Dive computers** | **~$250M (2025)** → $400M by 2034 | 5.5% | **The entire hardware category is a quarter-billion.** Software on top of it is a fraction. |

> ⭐ **The inversion that organises everything: the money gets bigger the deeper you go, while the
> people get fewer.** Six million recreational divers support a $250M dive-computer category.
> Twenty-five thousand commercial divers support $3.2B. Zero humans support a $19B robot market.

---

## THE POPULATION — and the asymmetry that decides which segment to pick

### Scuba

- ~**6 million** certified divers worldwide; **fewer than half (41.67%) are "active"** — dived at
  least once in the past year. ⚠️ *Other sources claim 6–9M **active**, which contradicts this
  outright. The industry does not know its own population.*
- PADI issued a record **1,317,383 certifications in 2024**, +43% on 2019.
- **But in the US, entry-level open-water certifications fell from 198,000 (2001) to 128,000 (2023)**
  — a **35% decline over 22 years**, with a COVID floor of 87,000 in 2020.

**Worldwide growth is real and it is happening somewhere other than the United States.**

### Freediving

- **7 million+ active participants in 2025 — up 52% since 2021.**
- **Certifications up 25% in 2024 alone.** 4,000+ centres in 62 countries.
- AIDA alone: ~4,000 active instructors, ~180,000 certified students.

### Commercial

- **25,000+ certified commercial divers** globally, **47% on offshore energy**.
- **26% of the workforce is over 45**; ~4,000 new certifications needed annually just to replace
  retirements; **31% of operators report shortages** during peak offshore season.
- Offshore wind: 75GW+ installed capacity, 12,000+ turbines, **~28% of foundations need
  diver-supported cable routing and inspection**, and a **50% rise** in subsea cable inspection work.

> ⭐ **The single most important comparison on this page: US scuba shrank ~35% over two decades while
> freediving grew 52% in four years.** If you are picking a segment on trajectory rather than on
> romance, it is not scuba.

---

## WHAT EACH GROUP USES — AND WHAT THEY MISS

### 1. Scuba divers

**Use:** a dive computer (Shearwater, Garmin Descent, Suunto, Oceanic, Mares) and a logging app —
**Subsurface** (free, open source, imports from **100+ dive-computer models**, cloud sync),
**MacDive** (Apple-native, 3D profile visualisation), **Shearwater Cloud**, **Divelogs**,
**DiverLog+** (Pelagic/Oceanic), and increasingly **Oceanic+ on Apple Watch Ultra**.

**Miss:**

- **Sync is chronically broken and the complaints are specific.** Documented on ScubaBoard and in App
  Store reviews: DiverLog+ WiFi sync failing outright, the app crashing on export and on the calendar
  view, a user unable to connect an i300c at all *(who solved it by abandoning the vendor app for
  MacDive)*, and the Oceans app returning **wrong dates and times even when synced directly from the
  computer** — a bug the reviewer worked around by entering the following day.
- **Shearwater Cloud is web-only** — no native mobile app, no offline access, on a device people use
  on boats with no signal.
- **The data is trapped per-vendor.** Subsurface supports 100+ computer models *because* no
  interchange standard actually works end to end. UDDF exists; adoption is partial.

### 2. Freedivers

**Use:** breath-hold timers running CO₂ and O₂ tables — **STAmina Apnea Trainer**, **Apnea
Assistant**, **Static Apnea Trainer**, **Freedive & Apnea Trainer** (180k+ downloads). Plus
freediving-mode watches.

**Miss — and this is the most serious unsolved problem in the water:**

> **Approximately 59–61 freedivers die each year** (DAN, analysing 2006–2011).
> **~73% of analysed freediving accidents were fatal** — if something goes wrong, you have less than
> a one-in-three chance.
> **The majority of recreational freediving fatalities involved divers who were alone or had
> separated from their buddy.**

Shallow-water blackout **has no warning signal**. Hyperventilation removes the body's CO₂-driven urge
to breathe, so consciousness goes without any subjective cue. The standard mitigation is entirely
social — one up, one down, and the safety diver watches for **thirty seconds after surfacing**,
because that is when blackout is most likely.

**What exists:** research prototypes only.
- A wearable concept for underwater SpO₂ monitoring with an acoustic "latest point of return"
  warning — *Proceedings of the Augmented Humans International Conference*, 2020.
- A student-built MAX30100 pulse-oximetry experiment asking whether the approach can work at all.
- **US Patent 7,988,511** — a freediving safety apparatus that auto-inflates a flotation device if
  the diver exceeds a personal time or depth limit.

**No mainstream commercial blackout-detection product was found.**

⚠️ **Why it's unsolved — my inference, flag it and verify before building anything:** the mammalian
dive reflex causes **peripheral vasoconstriction**, shunting blood away from the extremities. Wrist
and finger pulse oximetry depends on peripheral perfusion. **The physiological response that makes
breath-hold diving possible is the same one that breaks the obvious sensor.** If that holds, this is
a sensor-physics problem, not a software problem — which explains a decade of prototypes and no
product.

### 3. Spearfishers

**Use:** navigation/GPS, species ID, weather and logbook apps. Emerging hardware trend: **smart
spearguns with tracking systems**, plus buoyancy aids and visibility aids as safety features.

**Miss:**

- **Regulatory compliance is genuinely broken.** Market research names it directly: rules are
  **highly fragmented across countries and regional jurisdictions** — licensing, gear limitations,
  protected-species lists, size and bag limits — and that fragmentation "adds compliance complexity."
  There is no single answer to *"can I legally take this fish, at this size, here, today?"*
- **The solo-risk profile is the worst of any group.** DAN found **spearfishing/game collecting among
  the most common activities at the time of fatal breath-hold accidents**, and notes that spearfishing
  is often solitary and that **many spearos are self-taught** and under-informed about the risks. Of
  six US spearfishing deaths with an established cause: three drowning, one drowning with barotrauma,
  one air embolism, one cardiovascular.

### 4. Commercial, technical and subsea

**Use:** for tec — **V-Planner** (VPM-B, handles OC/SCR/CCR, trimix, heliox, bailout, lost-deco and
turn pressures), **AP Diving Projection**, **DiveBlendr**, Divesoft's planning tooling. For subsea —
ROVs, AUVs, NDT inspection rigs, and inspection-compliance platforms of the **LAUTEC Q** type.

**Miss:** CCR trimix planning past 50m is acknowledged as genuinely hard — the diluent on the bottle
isn't what you breathe, bailout volumes balloon, deco mixes multiply and the scrubber budget tightens
— but **the tooling exists and is mature.** No obvious software gap was located here. The gap in this
segment is **labour, not software**: an ageing workforce, a 4,000-diver annual replacement need, and a
50% rise in offshore-wind inspection demand.

---

## WHAT ALL FOUR GROUPS MISS, TOGETHER

**1. You cannot be located or communicate underwater. GPS does not penetrate water.**

Everything available is a workaround:
- **Ultrasonic** — Buddy Phone D2 (digital DSP transceiver, diver-to-diver and diver-to-surface);
  L3Harris **CUUUWi**, which bridges above-water mobile/SATCOM users to submerged ones; research
  systems that send prestored codes ("I need to surface", "come over here") and even sketches, *if
  directional connectivity holds.*
- **Surface relay** — **Nautilus Lifeline nexGen, $249** (£195). Rated to 425ft, GPS accurate to
  1.5m, broadcasts to AIS/DSC-equipped vessels **up to 34 miles**. But it only helps **once you have
  already surfaced.**
- **Analogue** — the DSMB. A brightly coloured inflatable tube.

**2. Buddy separation is the shared failure mode.** It is the leading circumstance in freediving
fatalities, it is what the DSMB and the Lifeline exist to mitigate, and it is what ultrasonic
diver-to-diver systems are built for. **Four different sports, four different equipment sets, one
common way people die.**

**3. Everybody's data sits in a vendor silo**, which is why the most-used logging tool in the world
is an open-source project that reverse-engineered a hundred proprietary formats.

---

## WHAT HAS ALREADY BEEN TRIED AND DIED

### Deepblu — the definitive case

A social network for divers. **"The Strava of diving."** Ten years. It went as far as **launching its
own dive computer, the Cosmiq+, purely to push the app.**

**In December 2023 it took its servers offline, citing "lack of paid users."** Too few would pay the
subscription; server costs became unaffordable. Users had to export their own data.

> **A consumer dive social/logging app was run as a real business, with its own hardware, for a
> decade, and it died of the exact thing that kills consumer subscription apps: people who dive six
> days a year will not pay every month.** Do not re-run this experiment.

---

## THE GAPS THAT CLOSED WHILE NOBODY WAS LOOKING

Both of the obvious ideas are now crowded, as of 2026.

**AI fish identification — at least six live products:**
Seabook (AI fish ID + dive log), FINS (5,000+ fish and invertebrates), ReefDex, FishID, **Fishial.ai**
(open-source, public-domain code, crowdsourcing photos from divers), plus **iNaturalist** as the
free general-purpose incumbent with millions of geo-referenced observations, and **Reef Check**
(17,000+ surveys, 102 countries) owning the structured citizen-science channel.

**Visibility and condition forecasting — at least five live products, all recent:**
**DiveSight** (28,000+ dive sites, two daily forecasts out to seven days, modelling sunlight, cloud,
wind, rainfall, runoff, wave and swell energy, currents, tides, chlorophyll and suspended matter),
**DiveViz**, **Marla Blue** (satellite + weather + diver reports, UK/Ireland/Australia/California),
**VizFinder**, **Viz-app** (crowdsourced).

**The critique those companies make of the prior art is worth stealing regardless of what you build:**
most condition apps either *repackage shallow surface weather, blind to what's happening underwater*,
or *lean on user-submitted reports, which are inherently sparse — only a handful of sites, only on
days someone happened to dive them.*

---

## THE PLATFORM THREAT — and the best pricing idea in the industry

**Oceanic+**, built by **Huish Outdoors with Apple**, turns an Apple Watch Ultra into a dive computer
to 40m. Free to download with depth, timers and basic logging. Subscription unlocks decompression
tracking, tissue loading, the location planner and unlimited logbook.

| Plan | Price |
|---|---|
| **Day pass** | **$4.99** |
| Month | $9.99 |
| Year | $79.99 |
| Year, family of 5 | $129 |

> ⭐ **The day pass is the smartest thing in diving software, and it is the direct answer to what
> killed Deepblu.** Recreational divers dive a handful of days a year, on holiday. An annual
> subscription asks someone who dives six days a year to pay for 365. **A day pass charges them on
> the days they are actually in the water.** Any consumer dive product you build should price this
> way — and note that Apple and a major manufacturer got there first, which tells you how the
> economics really work.

---

## THE B2B LAYER IS ALSO FULL

Dive-centre management software already exists and is competitive: **Dive Shop 360** (all-in-one POS
built by industry people), **EVE Diving** (PADI-endorsed, package pricing), **Bloowatch** (watersports
schools, PADI and SSI integration, **startup plan $199/month**), **Divery**, **Dive Admin**,
**Diversdesk**.

**Same shape as the restaurant research: an established category, mid-hundreds monthly pricing, and
agency endorsement as the distribution moat.**

---

## RANKED OPPORTUNITIES — honest

### 1. ⭐ Spearfishing regulation compliance — *best fit for you specifically*

*"Can I legally take this fish, at this size, in this water, today?"*

- **The problem is named in the market research itself** as a genuine compliance burden, not inferred.
- The data is **public record** — state and national fisheries regulations — which means the hard
  part is structured-data work: ingesting, normalising and versioning hundreds of fragmented
  jurisdictions. **That is a statistics-and-data-science problem, not an ML problem.**
- **Low liability if framed as reference, not advice**, and no safety-critical failure mode.
- Segment is growing, and spearos are the least served by existing apps.

**Against it:** the market is small, spearfishers are famously unwilling to pay, and regulation data
requires perpetual maintenance — which is simultaneously the moat and the cost. **Run the interviews
first.**

### 2. Freediver blackout / buddy-loss detection — *best problem, worst fit*

The highest human stakes in the file, in the fastest-growing segment, with **only research prototypes
in the field.** But: hardware, a safety-critical device where a false negative kills someone,
probable regulatory and liability exposure, and a likely sensor-physics blocker. **This is a PhD
group or a funded hardware startup, not a solo undergraduate project this academic year.**

### 3. Commercial dive and inspection compliance — *real money, no access*

Mandated record-keeping, real budgets, an ageing workforce and offshore wind driving a 50% rise in
inspection demand. **But you cannot sell to offshore contractors without industry access**, and that
takes years to acquire.

### 4. Dive travel — *where the money is, hardest to enter*

$5.5–6.25B growing 11.5%. Average trip spend **$1,950** overall, rising to **$2,680 (age 51–65)** and
**$2,840 (65+)**. **Liveaboards take ~18% of dive-travel revenue on just 6.3% of trips** at $250–450
a day standard and $500–1,200 luxury. It is the richest pool on the page — and it is a marketplace
business with a brutal cold-start problem, competing with established operators.

### 5. ❌ Consumer dive log, social network, fish ID, or visibility forecast

**Deepblu ran the first for ten years with its own hardware and died. Six companies ship the third.
Five ship the fourth.** Do not enter any of these.

---

## Confidence

**High:** the DAN freediving fatality figures and the alone/separated finding · US certification
decline · freediving participation growth · Deepblu's shutdown and its stated reason · Oceanic+
pricing · the fish-ID and visibility-forecast competitor lists · Nautilus Lifeline specs and price ·
commercial diver workforce demographics.

**⚠️ Low — treat as order-of-magnitude only:** every market-size dollar figure, and especially the
scuba equipment market, where three firms disagree by 5×. Also the active-diver population, where
sources contradict each other outright.

**My inference, not a sourced finding:** the peripheral-vasoconstriction explanation for why
underwater pulse oximetry has never shipped. Verify with a diving-medicine source before relying on
it.

**Could not obtain:** DAN Annual Diving Report primary PDFs · App Store review corpora · dive-computer
brand market shares · what share of divers pay for any dive app at all — **the single most important
missing number, and Deepblu's death suggests the answer is "very few."**
