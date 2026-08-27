# Underwater Messaging & Universal Air Integration — Does It Exist, and Can You Build It?

_Aug 2026. Answering two direct questions: (1) can anything transmit messages underwater via sonar or
another wave frequency, and (2) could an app link all dive computers together as a messaging medium
and connect to any tank transmitter. **WebFetch egress-blocked** — all figures are search-index
summaries._

---

## FIRST: THREE CORRECTIONS TO THE BRIEF YOU PASTED IN

The summary you brought was mostly accurate, but three claims are wrong or overstated, and two of
them would change what you build.

### ❌ "Premium dive computers display local reef maps underwater on your wrist"

**Garmin DiveView maps are real — bathymetry plus 4,000+ dive sites — but they are a surface and
planning feature.** GPS does not penetrate water, so the watch has no live fix while you are down.
There is no live map with a "you are here" dot underwater on any consumer device.

### ❌ "Real-time diver tracking showing your distance from the entry point or boat"

Not from GPS. Anything of this kind is **dead reckoning** — compass heading plus estimated speed —
which accumulates error continuously and has no way to correct itself. The watch tags your entry and
exit coordinates at the surface, and interpolates nothing reliable in between.

### ❌ "If you buy Garmin you must buy Garmin; if you use Shearwater you need a different one"

**Half right, and the half that's wrong is the interesting half.** See the transmitter section below —
a de facto cross-brand standard already exists, it just doesn't include Garmin or Suunto.

### ✅ "Garmin's SubWave network" — this one is correct, and it settles your first question

---

## QUESTION 1: CAN YOU SEND MESSAGES UNDERWATER?

**Yes. It ships today, and Garmin owns it.**

### Garmin SubWave — Descent Mk3i + Descent T2 transceiver

| Capability | Spec |
|---|---|
| Diver-to-diver preset messages | **Up to 30 m, line of sight** |
| Message latency | **Up to 45 seconds to send** |
| Network size | **Up to 8 divers** |
| Buddy tank pressure, air consumption rate, remaining dive time | **Within 10 m** |
| Message set | Preset only — *"Are You OK?"* and its response, *"Come to Me"*, *"Safely End Dive"* |
| Diver Assistance Mode | Alerts divers within 30 m, who can then monitor the distressed diver's **depth and distance** |

**Not free text. Not fast. But real, shipping, and in the hands of the largest wearable company on
earth.**

### The other systems that exist

- **Buddy Phone D2** — digital DSP ultrasonic transceiver, diver-to-diver and diver-to-surface voice.
- **L3Harris CUUUWi** — bridges above-water mobile and SATCOM users to submerged users and platforms
  without them surfacing. Military/industrial.
- Research systems that transmit prestored codes and even sketches, *"if directional connectivity can
  be maintained."*
- **Nautilus Lifeline nexGen, $249** — GPS to 1.5 m, AIS/DSC broadcast to vessels up to 34 miles.
  **Surface only.** It solves lost-at-sea, not lost-underwater.

---

## WHY IT'S SLOW — the physics, because this decides everything

Radio does not work. GPS at 1.5 GHz and Bluetooth at 2.4 GHz are both attenuated within centimetres
of seawater. **Acoustic is the only channel, and acoustics have hard limits:**

| Constraint | Consequence |
|---|---|
| **Sound travels at ~1,500 m/s** | Propagation delay is inherent. Not an engineering flaw — the speed of sound. |
| **Low frequency = long range, tiny bandwidth** | Commercial modems reach **beyond 10 km at under 400 bps**. Under 1,000 bps for ranges to 100 km. |
| **High frequency = high bandwidth, heavy attenuation** | Range collapses. This is the central tradeoff. |
| **Multipath and Doppler** | Only **1–2 bits per symbol** survive, and error-control coding cuts the effective rate further. |

### ⭐ But here is the number that matters for you

> **Wide-bandwidth acoustics can reach ~1 Mbps at distances up to 100 m.**

**At diver ranges — 30 m — the physics does *not* force a 45-second preset message.** Garmin is
trading throughput for robustness, battery life and the size of a wrist device, not hitting a wall
imposed by nature.

**There is genuine engineering headroom between "45 seconds for a canned phrase at 30 m" and "1 Mbps
at 100 m."** That gap is the real opportunity in underwater messaging — *and it is a DSP, transducer
and power-budget problem, not an app.*

---

## QUESTION 2: COULD AN APP LINK ALL DIVE COMPUTERS AS A MESSAGING MEDIUM?

**No. And the reason is worth internalising because it kills a whole class of ideas.**

> **Your phone is on the boat.**

A dive computer underwater has no link to a phone. Bluetooth is 2.4 GHz radio — it dies in
centimetres of water, the same as GPS. **Every dive computer syncs to a phone only after you surface,
and that is a hardware constraint, not a software gap.**

So:

- **Underwater, the medium must be acoustic and hardware-to-hardware.** An app cannot sit in the
  middle, because there is no path between the wrist and the phone while you are wet.
- **On the surface, an app absolutely can be the medium** — but at that point it is a sync-and-share
  product, and that market is occupied. **Subsurface** already reads **100+ dive-computer models**,
  free and open source. **Deepblu** built the social layer on top of exactly this, ran it for ten
  years with its own dive computer, and **shut its servers down in December 2023 citing "lack of paid
  users."**

**The app-as-medium idea is blocked underwater by radio physics and blocked at the surface by a free
incumbent and a dead competitor.**

---

## QUESTION 3: COULD IT CONNECT TO ANY TANK TRANSMITTER?

**Partially — and a cross-brand standard already quietly exists.**

### The part everyone gets wrong

**Oceanic, Aqualung, Sherwood and Shearwater transmitters are the same hardware**, manufactured by
**Pelagic Pressure Systems**. Shearwater's own guidance: **any transmitter marked `FCC ID MH8A` on the
body will work with a Shearwater computer, regardless of brand.**

That is a functioning four-brand de facto standard, and it is already in the field.

### The holdouts

**Garmin and Suunto are genuinely proprietary.** Their transmitters even require unique air spools
with flow restrictors that differ from standard spools — a mechanical lock-in on top of the protocol
one.

### Why you cannot fix this with software

The pairing lives in **the radio protocol inside the transmitter and the receiver chip** — sub-GHz RF
between a tank-mounted sender and a wrist unit, at close range, in water. **There is no software
layer to insert yourself into.** Making Garmin talk to a Shearwater would require either building
your own transmitter and reverse-engineering two proprietary protocols, or getting two competitors to
license theirs to a student.

> **This is a business problem wearing a technical costume. The reason there is no universal standard
> is not that nobody thought of it — it's that transmitters are a $200–350 accessory that locks a
> customer into a $700–1,600 computer, and lock-in is the point.**

---

## SO WHAT'S ACTUALLY LEFT IN THIS AREA

### ❌ Dead on arrival

- **An underwater messaging app.** No path from wrist to phone underwater. Physics.
- **A universal transmitter bridge in software.** The protocol is in the radio, and the lock-in is
  deliberate.
- **A cross-brand dive log with social features.** Subsurface is free and reads 100+ computers;
  Deepblu died running exactly this with its own hardware.

### ⚠️ Real but not yours yet

- **Higher-bandwidth short-range acoustic diver comms.** The gap between Garmin's 45-second preset at
  30 m and the ~1 Mbps-at-100 m the research literature reaches is genuine engineering headroom. It is
  also transducer design, DSP and power budgeting — a hardware company, and Garmin has a several-year
  head start with distribution attached.
- **Cross-brand tank telemetry.** Only reachable by manufacturing your own transmitter. Capital,
  certification, FCC.

### ✅ The one thing here that is software-shaped

**Garmin just created a networked-diver data stream that didn't exist before** — up to eight divers,
sharing depth, distance, tank pressure, air-consumption rate and remaining dive time. That is a
genuinely new dataset about how groups of divers behave together.

**Dive operators and instructors are the plausible buyer** — someone responsible for eight people at
once who currently has no telemetry on any of them. Whether Garmin exposes that stream to third
parties is the entire question, and it is the first thing to check before spending an hour on the
idea.

⚠️ **I could not verify whether Garmin offers third-party access to SubWave data.** Egress is blocked,
so I could not open the developer documentation. **Check that before anything else** — if the answer
is no, this closes too.

---

## Confidence

**High:** SubWave's specs (30 m, 45 s, 8 divers, 10 m for tank data, preset messages only) · the
acoustic bandwidth and range figures · Pelagic Pressure Systems making transmitters for four brands
and the `FCC ID MH8A` interoperability rule · Garmin and Suunto being proprietary · DiveView being a
surface planning feature · Bluetooth and GPS being unusable underwater.

**My inference, not a sourced finding:** that Garmin's 45-second latency is a design tradeoff rather
than a physical limit. It follows from the ~1 Mbps-at-100 m research figure, but no source states it
directly.

**Could not obtain:** Garmin's developer documentation or any third-party SubWave API terms ·
transmitter unit economics · whether anyone has reverse-engineered the Garmin transmitter protocol.
