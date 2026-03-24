# Historical Incident Analysis: How the Multi-Agent ATC System Would Have Responded

**Date:** March 24, 2026
**Purpose:** Demonstrate how the proposed multi-agent architecture would have prevented or mitigated real-world aviation incidents. Each case study maps the chain of human failures to specific system components that eliminate them.

---

## Table of Contents

1. [The Common Pattern](#the-common-pattern)
2. [Incident 1: Potomac River Midair Collision (January 29, 2025)](#incident-1-potomac-river-midair-collision-january-29-2025)
3. [Incident 2: LaGuardia Runway Collision (March 23, 2026)](#incident-2-laguardia-runway-collision-march-23-2026)
4. [Structural Comparison](#structural-comparison)
5. [The Argument These Cases Make](#the-argument-these-cases-make)
6. [Future Cases to Analyze](#future-cases-to-analyze)
7. [Sources](#sources)

---

## The Common Pattern

Every incident in this document shares the same structural failures. The specifics differ — different airports, different aircraft, different weather — but the root causes are human limitations that the multi-agent architecture eliminates by design:

| Human Limitation | System Property |
|---|---|
| Humans can only track ~7 things at once | Agents track everything simultaneously |
| Combining positions saves money but kills people | Agents cost electricity, not salary — never combined |
| Humans get distracted by concurrent emergencies | Each agent has one job; emergencies are a separate agent |
| "I have traffic in sight" can mean the wrong aircraft | Position data is unambiguous — transponder/ADS-B, not eyeballs |
| Verbal instructions can be blocked or misheard | Data link + voice redundancy; safety nets don't depend on communication |
| Cross-checking requires active human effort | Cross-checking is automatic, continuous, microsecond |
| Fatigue degrades performance over a shift | Agents perform identically at hour 1 and hour 1,000 |
| Safety data sits in databases unanalyzed | Every alert is trended, analyzed, and surfaced automatically |

---

## Incident 1: Potomac River Midair Collision (January 29, 2025)

**Location:** Reagan National Airport (DCA), Washington, D.C.
**Aircraft:** American Airlines Flight 5342 (CRJ-700, operated by PSA Airlines) and U.S. Army Black Hawk helicopter (PAT25)
**Fatalities:** 67 (all aboard both aircraft — 64 on the CRJ, 3 on the helicopter)
**NTSB Report:** AIR-26-02, released January 27, 2026

### What Happened

At 8:47 PM EST, Flight 5342 was on visual approach to Runway 33 at Reagan National. Army Black Hawk PAT25 was flying Helicopter Route 4 along the Potomac River on a night training mission with night vision goggles. They collided at approximately 300 feet altitude, half a mile from the runway threshold. Both aircraft crashed into the Potomac River. There were no survivors.

This was the deadliest U.S. air disaster since American Airlines Flight 587 in 2001, and the first major commercial passenger crash since Colgan Air 3407 in 2009.

### The Chain of Failures (NTSB Findings)

The NTSB identified **not a single error but a stack of 11 systemic failures** with 74 findings and 50 recommendations:

| # | Failure | Detail |
|---|---------|--------|
| 1 | **Helicopter route design** | Helicopter Route 4 passed directly beneath the Runway 33 approach path. At the route ceiling of 200 ft, there was only **75 feet of vertical separation** from a landing aircraft. The FAA placed this route here and never adequately reviewed it. |
| 2 | **15,000 near-misses ignored** | FAA had data showing **over 15,000 close encounters** between helicopters and airplanes near DCA from 2021 to 2024. This data was neither shared nor acted upon — a systemic failure in safety culture and risk management. |
| 3 | **Combined controller positions** | At 3:40 PM, the supervisor merged helicopter control and local control into one position so a controller could leave early. These positions would normally remain split until 9:30 PM when traffic decreases. This was nearly 6 hours before the standard combination time. |
| 4 | **Overreliance on visual separation** | ATC relied on the "see and avoid" principle. This was a night operation, with a dark helicopter over dark water. The NTSB called this an overreliance on visual separation "without consideration for the limitations of the see-and-avoid concept." |
| 5 | **Altimeter error** | The Black Hawk's barometric altimeter had a known tolerance issue that the Army never warned pilots about. The helicopter's radar altimeter recorded **278 feet** — 78 feet above its Route 4 ceiling of 200 feet. The crew likely believed they were lower than they actually were. |
| 6 | **Misidentification of traffic** | The Black Hawk crew reported the CRJ "in sight" twice and said they'd maintain visual separation. The NTSB believes they may have been looking at the **wrong aircraft**. |
| 7 | **Blocked radio transmission** | A critical instruction from the controller to the helicopter to "pass behind" the CRJ may have been **partially blocked** by a simultaneous mic press from the helicopter crew. |
| 8 | **Separate frequencies** | Helicopter control and tower local operated on **different radio frequencies**. The CRJ crew and Black Hawk crew could not hear each other's transmissions. They could hear the controller, but not each other. |
| 9 | **TCAS altitude limitation** | The CRJ-700's TCAS (Traffic Collision Avoidance System) functioned as designed, but at that altitude (~300 ft on approach), the system **could not issue a Resolution Advisory** — existing altitude limits prevented it. Only a Traffic Advisory (information, no maneuver) was possible. |
| 10 | **No ADS-B In** | Had the CRJ been equipped with ADS-B In, the cockpit display would have shown the helicopter's position. The NTSB estimated this could have provided approximately **59 seconds of advance warning**. |
| 11 | **Incomplete charts** | Fixed-wing pilots' approach charts for Runway 33 did **not show** the nearby helicopter routes, creating a situational awareness gap for the CRJ crew. |

### How Each System Component Responds

#### Collision Vector Monitor (Deterministic — Independent Hardware)

This is the primary defense. It tracks ALL aircraft and helicopter positions via ADS-B, radar, and MLAT. It continuously computes:

- Projected trajectory for every tracked object
- Closest Point of Approach (CPA) between every pair of objects
- Time to CPA

**What it sees at T-120 seconds:**

PAT25 is at approximately 278 ft, tracking northeast along Route 4. Flight 5342 is on approach to Runway 33, descending through approximately 600 ft. Their trajectories converge.

```
COLLISION VECTOR MONITOR — ALERT
═══════════════════════════════════════════════════════════
YELLOW ALERT: Converging traffic detected

  Aircraft A: PAT25 (UH-60L Black Hawk)
  Position:   38.8521°N, 77.0402°W
  Altitude:   278 ft (radar alt)
  Track:      045° at 120 kts

  Aircraft B: AA5342 (CRJ-700)
  Position:   38.8380°N, 77.0510°W
  Altitude:   580 ft descending
  Track:      330° at 140 kts (on Rwy 33 approach)

  Closest Point of Approach: 0.08 NM lateral, ~20 ft vertical
  Time to CPA: 118 seconds

  STATUS: CONVERGING — MONITORING
═══════════════════════════════════════════════════════════
```

#### Conformance Monitor (Deterministic)

Simultaneously and independently:

```
CONFORMANCE MONITOR — ALERT
═══════════════════════════════════════════════════════════
YELLOW ALERT: Altitude exceedance

  Aircraft:   PAT25 (UH-60L Black Hawk)
  Route:      Helicopter Route 4
  Max Altitude: 200 ft
  Actual:     278 ft (78 ft above ceiling)
  Duration:   Continuous for 2+ minutes

  ACTION: Alert issued to PAT25
═══════════════════════════════════════════════════════════
```

#### Escalation at T-60 seconds

The CPA computation updates. The situation has not resolved.

```
COLLISION VECTOR MONITOR — CRITICAL
═══════════════════════════════════════════════════════════
RED ALERT: COLLISION RISK — VETO AUTHORITY ENGAGED

  CPA: <100 ft lateral, <50 ft vertical
  Time to CPA: 58 seconds

  IMMEDIATE ACTIONS (AUTOMATED):

  1. PAT25: "PAT25, DESCEND IMMEDIATELY TO 100 FEET AND
     HOLD POSITION. TRAFFIC CRJ-700 ON SHORT FINAL
     RUNWAY 33, YOUR 2 O'CLOCK, HALF MILE."
     [Issued via voice AND data link simultaneously]

  2. IF PAT25 does not alter trajectory within 15 seconds:
     AA5342: "FLIGHT 5342, GO AROUND. FLY RUNWAY HEADING,
     CLIMB AND MAINTAIN 2,000. TRAFFIC CONFLICT, HELICOPTER
     AT YOUR 10 O'CLOCK, QUARTER MILE, 300 FEET."

  3. All other Runway 33 approach traffic: HOLD/REROUTE

  HUMAN OVERWATCHER: NOTIFIED — EMERGENCY PANEL ACTIVE
═══════════════════════════════════════════════════════════
```

#### What the Human Overwatcher Sees

```
╔══════════════════════════════════════════════════════════════╗
║  ⚠  COLLISION RISK — AUTOMATED RESPONSE IN PROGRESS        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  PAT25 (Black Hawk) converging with AA5342 (CRJ-700)       ║
║  Time to impact: 58 sec → 43 sec → [updating]              ║
║                                                              ║
║  [MAP: Shows both aircraft, projected paths, conflict       ║
║   point marked in red, Route 4 boundaries highlighted]      ║
║                                                              ║
║  ACTIONS TAKEN:                                              ║
║  ✓ PAT25 issued immediate descent/hold (T-58 sec)          ║
║  ○ Monitoring PAT25 compliance... AWAITING                   ║
║  ○ Go-around for AA5342 queued if PAT25 non-compliant       ║
║  ✓ Approach traffic holding                                  ║
║                                                              ║
║  [APPROVE ACTIONS]  [MODIFY]  [TAKE MANUAL CONTROL]        ║
╚══════════════════════════════════════════════════════════════╝
```

#### Why Every Failure is Eliminated

| Original Failure | System Response |
|---|---|
| Route 4 too close to approach | Collision Vector Monitor enforces separation regardless of route design — the geometry is computed, not assumed |
| 15,000 near-misses ignored | Every proximity alert is logged and trended automatically. System generates reports: "Route 4: 847 alerts in 30 days, 12 within 50 ft of minimums." Cannot be ignored. |
| Combined controller positions | Landing Agent and helicopter/ground agents are separate compute. Cannot be "combined to let someone leave early." |
| Visual separation at night | System never relies on visual. Position data is from transponder/ADS-B/radar — works identically day or night, clear or fog. |
| Altimeter error (278 ft vs. 200 ft limit) | Conformance Monitor detects exceedance from radar/ADS-B data. Flags it regardless of what the cockpit altimeter reads. |
| Wrong aircraft identified as "in sight" | System doesn't depend on pilot visual identification. Separation computed from unambiguous position data — transponder ICAO address, not eyeballs. |
| Blocked radio transmission | Safety nets don't depend on communication being received. Collision Vector Monitor acts independently. Voice + data link redundancy for instructions. |
| Separate frequencies hiding traffic | All aircraft in single unified data picture. Frequency is irrelevant to the tracking and alerting system. |
| TCAS can't issue RA at low altitude | Collision Vector Monitor has no altitude floor. Computes separation and issues alerts at all altitudes, including 300 ft. |
| No ADS-B In on CRJ | System provides equivalent of ADS-B In for all aircraft through ground-based tracking and alerting. |
| Charts don't show helicopter routes | All route data in the system. Collision Vector Monitor knows every route boundary, approach path, and restriction. |

### Outcome in the Automated System

**No collision.** The Collision Vector Monitor detects the convergence at T-120 seconds. The Conformance Monitor independently flags the altitude exceedance. By T-60 seconds, automated instructions are issued. Even if the helicopter fails to comply, a go-around is issued to Flight 5342 by T-45 seconds — 45 seconds before the point of impact. All 67 people survive.

---

## Incident 2: LaGuardia Runway Collision (March 23, 2026)

**Location:** LaGuardia Airport (LGA), New York
**Aircraft:** Air Canada Express Flight 8646 (CRJ-900, operated by Jazz Aviation)
**Vehicle:** Port Authority Fire Truck (Truck 1)
**Fatalities:** 2 (both pilots of the CRJ-900)
**Injuries:** Dozens, at least 9 hospitalized
**Status:** Under investigation (NTSB)

### What Happened

At approximately 11:38 PM EST, Flight 8646 (CRJ-900 arriving from Montreal with 72 passengers and 4 crew) was landing on Runway 4 at LaGuardia. Minutes earlier, United Flight 2384 had aborted takeoff on Runway 13 and reported a cabin odor that sickened flight attendants. A Port Authority fire truck (Truck 1) was dispatched to respond.

To reach the United aircraft on Runway 13, Truck 1 needed to cross Runway 4. The controller cleared Truck 1 to cross Runway 4 at taxiway Delta. But Flight 8646 had already been cleared to land on Runway 4. Only **3 minutes** elapsed between the landing clearance and the collision.

ATC recordings captured the controller urgently calling **"Stop, Truck 1. Stop."** — too late. The CRJ was traveling 93-105 mph at impact. Both pilots were killed.

Approximately 20 minutes after the collision, the controller said on the recording: *"We were dealing with an emergency earlier... I messed up."*

A former FAA VP noted that "one person could have been doing the work of two people" — the same controller was handling both tower (landing clearances) and ground (vehicle movement) responsibilities.

### The Chain of Failures

| # | Failure | Detail |
|---|---------|--------|
| 1 | **Dual responsibilities** | The same controller was handling both tower operations (landing clearances for Runway 4) and ground operations (vehicle movement and runway crossings). These are normally separate positions. |
| 2 | **Conflicting clearances issued** | The controller cleared AC8646 to land on Runway 4 AND cleared Truck 1 to cross Runway 4. Two clearances that cannot safely coexist were both active simultaneously. |
| 3 | **Distraction from concurrent emergency** | The controller was simultaneously managing the United 2384 emergency (cabin odor, aborted takeoff, fire response coordination). Cognitive load exceeded capacity. |
| 4 | **Late recognition** | By the time the controller recognized the conflict, the truck was on the runway and the CRJ was seconds from touchdown. The instruction to stop came too late. |
| 5 | **No automated cross-check** | No system in the tower flagged that a landing clearance and a runway crossing clearance for the same runway were both active at the same time. |
| 6 | **No alternative route computed** | Under time pressure, the controller chose the most direct route for the truck (across Runway 4) without considering whether an alternative route existed that would avoid the active runway. |

### How Each System Component Responds

#### The Request

Truck 1 requests permission to cross Runway 4 to reach United 2384 on Runway 13.

#### Runway Incursion Monitor (Deterministic — Independent Hardware)

This is instantaneous:

```
RUNWAY INCURSION MONITOR — QUERY
═══════════════════════════════════════════════════════════
REQUEST: Truck 1 requests crossing Runway 04 at Taxiway Delta

CHECK: Runway 04 status
  → ACTIVE: AC8646 cleared to land
  → AC8646 position: 8.2 NM on final approach
  → Estimated threshold arrival: 3 min 12 sec

RESULT: ██ DENIED ██
  Runway 04 is active with traffic on final approach.
  Crossing clearance cannot be issued.

  ALTERNATIVE ROUTES COMPUTED:
  1. Taxiway Kilo → Taxiway Echo → Runway 13
     (avoids Runway 04 entirely, +90 sec travel time)
  2. Hold short Runway 04, cross after AC8646 clears
     (est. wait: 4 min 30 sec)
═══════════════════════════════════════════════════════════
```

**Total computation time: <10 milliseconds.**

#### Ground Traffic Agent

Receives the denial from the Runway Incursion Monitor and issues the instruction:

```
GROUND TRAFFIC AGENT → TRUCK 1:
"Truck 1, hold short of Runway 4. Traffic on final.
 Proceed to Runway 13 via Kilo, Echo. Acknowledge."
```

#### What Does NOT Happen

- The Landing Agent is not involved. It is managing the approach for AC8646 and is unaware of the truck request because it doesn't need to be.
- The emergency response for United 2384 is being handled by a separate agent (or Tier 3 human, depending on severity). It does not affect the Ground Traffic Agent's ability to evaluate a runway crossing request.
- No agent is "distracted." Each has a single concern.

#### What the Human Overwatcher Sees

The overwatcher sees a routine denial:

```
GROUND OPS — Truck 1
══════════════════════════════════════════
Request: Cross Runway 04 at Delta
Status:  DENIED — traffic on final (AC8646, 8.2 NM)
Action:  Routed via Kilo-Echo to Runway 13
         Truck 1 acknowledged. En route.

LANDING OPS — Runway 04
══════════════════════════════════════════
AC8646: 8.2 NM final, ILS Rwy 04, normal
        Cleared to land [AUTO-ISSUED]
        Agents agree: 3/3
        Safety nets: ALL GREEN
```

No alert. No emergency panel. No escalation needed. The conflict was prevented before it existed.

#### Why Every Failure is Eliminated

| Original Failure | System Response |
|---|---|
| Same controller doing tower + ground | Landing Agent and Ground Traffic Agent are separate. Cannot be combined. |
| Conflicting clearances on same runway | Runway Incursion Monitor makes this **impossible**. A landing clearance and crossing clearance for the same runway cannot coexist. The check is deterministic and takes microseconds. |
| Distraction from concurrent emergency | Each agent has one job. The emergency is a separate concern handled by separate agents. Workload on one task never degrades another. |
| Late recognition of conflict | There is no "recognition" delay. The conflict is evaluated at the moment of the request, before any clearance is issued. |
| No automated cross-check | The entire architecture IS the cross-check. Every clearance is validated against every other active clearance automatically. |
| No alternative route computed | The Ground Traffic Agent computes alternative routes in milliseconds and offers the best option immediately. |

### Outcome in the Automated System

**No collision.** Truck 1's crossing request is denied instantly. It is routed via an alternative path that avoids Runway 4 entirely, adding ~90 seconds of travel time. AC8646 lands normally. The United 2384 emergency is handled without interference. Both pilots of AC8646 survive. The truck reaches United 2384 approximately 90 seconds later than the direct route.

---

## Structural Comparison

| Dimension | Potomac River (DCA) | LaGuardia (LGA) |
|---|---|---|
| **Date** | January 29, 2025 | March 23, 2026 |
| **Type** | Midair collision | Ground-to-air collision |
| **Fatalities** | 67 | 2 |
| **Time of day** | Night (8:47 PM) | Night (11:38 PM) |
| **Core failure** | Converging traffic not detected in time | Conflicting clearances not cross-checked |
| **Staffing issue** | Helicopter + local control combined 6 hours early | Tower + ground handled by one person |
| **Distraction** | High traffic volume, multiple aircraft | Concurrent emergency (United 2384) |
| **Data available?** | Yes — 15,000 prior near-misses | Yes — both clearances in the system |
| **Data used?** | No | No |
| **Primary system that prevents it** | Collision Vector Monitor | Runway Incursion Monitor |
| **Time available for intervention** | ~120 seconds | ~180 seconds |
| **Difficulty of the solution** | Medium (trajectory computation) | Trivial (boolean check: is runway active?) |

### The Key Insight

Neither incident involved a situation that was *hard to solve*. A computer checking "are these two things going to hit each other?" is trivial computation. A computer checking "did I just issue two conflicting clearances for the same runway?" is a single boolean operation.

These incidents involved situations that were **hard for a human to notice in time** while juggling multiple other tasks. That is exactly the problem computers are best at solving.

---

## The Argument These Cases Make

### 69 People Died From Checkable Errors

Across these two incidents, 69 people died. In both cases:

1. The data needed to prevent the incident **existed in the system** at the time
2. A simple automated check would have caught the conflict **minutes before impact**
3. No advanced AI or machine learning was needed — deterministic logic suffices
4. The human failures were not incompetence — they were **fundamental limitations of human cognition** under workload

### What the System Needs to Be

The system doesn't need to be perfect. It doesn't need to pass the Turing test. It doesn't need artificial general intelligence. For these two incidents, it needs:

1. **Independent agents that cannot be combined** — separate compute, separate concerns, no "let someone leave early"
2. **Deterministic safety nets with veto power** — pure math, formally verified, running on independent hardware, microsecond response
3. **Automatic cross-checking of every clearance against every other active clearance** — before issuance, not after
4. **A system that doesn't get distracted, fatigued, or confused** about which aircraft is which
5. **Trend analysis that surfaces patterns automatically** — 15,000 near-misses don't sit in a database; they generate alerts

### The Cost Comparison

| Metric | Human System (Status Quo) | Automated System |
|---|---|---|
| DCA incident cost | 67 lives, $500M+ in lawsuits, investigations, fleet grounding | Prevented |
| LGA incident cost | 2 lives, airport closure, hundreds of canceled flights, lawsuits | Prevented |
| Annual controller staffing cost | ~$2.5B (14,264 controllers × avg $175K) | Fraction — compute hardware |
| System modernization (BNATCS) | $32.5 billion | Could be part of BNATCS architecture |
| Marginal cost of one more "agent" | N/A — can't hire fast enough | Electricity + compute allocation |

---

## Future Cases to Analyze

The following historical incidents should be analyzed against the multi-agent architecture in future iterations of this document:

| Incident | Date | Type | Key Failure | Primary System Component |
|---|---|---|---|---|
| **Tenerife (KLM/Pan Am)** | March 27, 1977 | Runway collision | Miscommunication, fog, unauthorized takeoff | Runway Incursion Monitor + STT |
| **Comair 5191 (Lexington)** | August 27, 2006 | Wrong runway takeoff | Crew lined up on wrong runway, single controller | Conformance Monitor + Ground Agent |
| **Colgan 3407 (Buffalo)** | February 12, 2009 | Loss of control on approach | Crew fatigue, improper stall recovery | Conformance Monitor (approach path) |
| **Asiana 214 (SFO)** | July 6, 2013 | Short landing | Crew mismanaged approach speed/glidepath | Conformance Monitor + Landing Agent |
| **Air France 447** | June 1, 2009 | Loss of control (oceanic) | Pitot tube failure, crew confusion | Anomaly detection, emergency escalation |
| **Hudson River midair** | August 8, 2009 | Midair collision (VFR) | ATC distracted, "see and avoid" failure | Collision Vector Monitor |
| **Runway incursion near-miss (JFK)** | January 13, 2023 | Near-collision on runway | Delta crossed runway while American departing | Runway Incursion Monitor |
| **Austin near-miss (AUS)** | February 4, 2023 | Near-collision on approach | FedEx landing while Southwest on same runway | Landing Agent + Runway Incursion Monitor |

Each of these would further validate that the core architecture — independent agents, deterministic safety nets with veto power, automatic cross-checking — addresses the recurring patterns in aviation accidents.

---

## Sources

### Potomac River Collision (DCA, January 29, 2025)
- [2025 Potomac River Mid-Air Collision — Wikipedia](https://en.wikipedia.org/wiki/2025_Potomac_River_mid-air_collision)
- [NTSB: Systemic Failures Led to Midair Collision Over Potomac River](https://www.ntsb.gov/news/press-releases/Pages/NR20260127.aspx)
- [NTSB Final Report AIR-26-02 (PDF)](https://www.ntsb.gov/investigations/AccidentReports/Reports/AIR2602.pdf)
- [NTSB Investigation Docket DCA25MA108](https://www.ntsb.gov/investigations/Pages/DCA25MA108.aspx)
- [NTSB Cites Multiple Factors — Flying Magazine](https://www.flyingmag.com/ntsb-cites-multiple-factors-behind-washington-midair-collision/)
- [$400 GPS Device Could Have Prevented Crash — ABC News](https://abcnews.com/US/causes-years-deadly-mid-air-collision-dc-announced/story?id=129586770)
- [US Admits Failures in Deadly Crash — ABC News](https://abcnews.com/US/army-faa-admit-failures-deadly-mid-air-crash/story?id=128502535)
- [NTSB Blames Deep Systemic Failures — NPR](https://www.npr.org/2026/01/27/nx-s1-5689091/ntsb-dca-midair-collision-black-hawk-helicopter)
- [US Government Admits Negligence — PBS](https://www.pbs.org/newshour/nation/u-s-government-admits-negligence-in-dc-midair-collision-that-killed-67-people)
- [ATC Recordings — WUSA9](https://www.wusa9.com/article/news/special-reports/dc-plane-crash/dca-midair-collision-black-box-air-traffic-control-tower-recordings-transcripts/65-b0398224-f3db-46c8-ae2f-2ee21349e938)
- [Less Than a Second Before Impact — CNN](https://www.cnn.com/2025/07/30/us/ntsb-hearing-dc-crash)
- [NTSB Hearing Details — NPR](https://www.npr.org/2025/07/30/nx-s1-5481820/ntsb-dca-army-black-hawk-midair-collision-hearings)

### LaGuardia Runway Collision (LGA, March 23, 2026)
- [Air Canada Jet Collides with Firetruck — NPR](https://www.npr.org/2026/03/23/g-s1-114773/laguardia-air-canada-plane-collision-fire-truck)
- [LaGuardia Collision Explained — ABC7 New York](https://abc7ny.com/post/laguardia-air-canada-plane-emergency-truck-collision-explained-how-did-cross-paths-runway/18754668/)
- [LaGuardia Collision, 2 Dead — Washington Post](https://www.washingtonpost.com/transportation/2026/03/23/us-airport-laguardia-air-canada-plane/)
- [Plane Traveling 93-105 mph at Impact — ABC News](https://abcnews.com/US/laguardia-airport-closed-collision-air-canada-plane-airport/story?id=131315551)
- [What Happened, Who Were the Victims — Al Jazeera](https://www.aljazeera.com/news/2026/3/23/air-canada-crash-at-laguardia-airport-what-happened-who-were-the-victims)
- [LaGuardia Airport Reopens — CNN](https://www.cnn.com/us/live-news/laguardia-collision-ice-airports-tsa-03-23-26)
- [2 Pilots Killed — CBS News](https://www.cbsnews.com/news/laguardia-airport-closed-arrving-air-canada-plane-ground-vehicle-collide/)
