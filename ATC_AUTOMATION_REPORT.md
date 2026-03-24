# Automated Air Traffic Control System: Feasibility & Architecture Report

**Date:** March 24, 2026
**Status:** Thought Experiment / Research Phase

---

## Table of Contents

**Part I: Research Foundation**
1. [Executive Summary](#1-executive-summary)
2. [What Air Traffic Controllers Actually Do](#2-what-air-traffic-controllers-actually-do)
3. [The Three Domains of ATC](#3-the-three-domains-of-atc)
4. [Core Tasks That Would Need Automation](#4-core-tasks-that-would-need-automation)
5. [Current ATC Technology Infrastructure](#5-current-atc-technology-infrastructure)
6. [Legacy Systems: The Scale of the Problem](#6-legacy-systems-the-scale-of-the-problem)
7. [Surveillance Data: How Aircraft Are Tracked](#7-surveillance-data-how-aircraft-are-tracked)
8. [Available Data Feeds and Integration Points](#8-available-data-feeds-and-integration-points)
9. [What's Already Automated](#9-whats-already-automated)
10. [AI and Algorithmic Approaches](#10-ai-and-algorithmic-approaches)
11. [Safety, Redundancy, and Certification](#11-safety-redundancy-and-certification)
12. [Barriers to Full Automation](#12-barriers-to-full-automation)
13. [Architecture Options for a New System](#13-architecture-options-for-a-new-system)
14. [The Hobbyist Entry Point](#14-the-hobbyist-entry-point)
15. [Key Players and Active Programs](#15-key-players-and-active-programs)
16. [Conclusions and Discussion Points](#16-conclusions-and-discussion-points)

**Part II: System Design**
17. [Agent Certification: Mapping FAA Standards to Software Validation](#17-agent-certification-mapping-faa-standards-to-software-validation)
18. [Three-Tier Escalation Architecture](#18-three-tier-escalation-architecture)
19. [Multi-Agent Architecture: Full Inventory](#19-multi-agent-architecture-full-inventory)
20. [Normalcy Threshold and Compound Triggers](#20-normalcy-threshold-and-compound-triggers)
21. [Emergency AI Assistant](#21-emergency-ai-assistant)
22. [Historical Incident Analysis](#22-historical-incident-analysis)
23. [Local / Air-Gapped Model Stack](#23-local--air-gapped-model-stack)
24. [Full System Architecture Diagram](#24-full-system-architecture-diagram)
25. [Complete Pilot-ATC Communication Protocol: Gate to Gate](#25-complete-pilot-atc-communication-protocol-gate-to-gate)
26. [Physical & Software Architecture](#26-physical--software-architecture)
27. [Swiss Cheese Model: Latent Error Analysis](#27-swiss-cheese-model-latent-error-analysis)
28. [Formal State Model](#28-formal-state-model)
29. [Deterministic Safety Net Interface](#29-deterministic-safety-net-interface)
30. [Sources](#30-sources)

---

## 1. Executive Summary

Air traffic control is one of the most cognitively demanding jobs in existence. US controllers handle **44,000+ flights daily** (30.8 million in FY2024) across 20 en-route centers, 290 terminal facilities, and 600+ towers. The FAA currently employs approximately **14,264 controllers**, with over 90% of facilities reporting understaffing at various points. Controllers work rotating shifts, mandatory overtime, and 6-day weeks — fatigue and staffing shortages are the top safety concerns.

The technology infrastructure is in crisis. Of **138 FAA ATC systems, 51 (37%) are deemed unsustainable** and another 54 (39%) are potentially unsustainable. Some systems trace their code lineage to the 1960s. The FAA has just launched the **Brand New Air Traffic Control System (BNATCS)** program — a $32.5 billion effort to replace the entire stack.

Meanwhile, the building blocks for a highly automated ATC system exist today:
- **ADS-B** provides GPS-derived position, altitude, velocity, and identity for every equipped aircraft
- **SWIM** provides a service-oriented data backbone with JMS-based access
- **Deep reinforcement learning** has achieved state-of-the-art results in conflict detection and resolution
- **NLP systems** are achieving 91%+ accuracy on ATC radio communication recognition
- **UTM (drone traffic management)** is being built digital-native and highly automated from scratch

The barriers are primarily **regulatory, institutional, and human-factors-related** — not technical. No regulatory pathway exists for fully autonomous ATC. The "out-of-the-loop" problem (humans lose situational awareness when automation is too reliable) creates a paradox for gradual automation. Certifying AI/ML systems under existing safety standards (DO-178C, ED-153) remains an unsolved problem.

This report details every aspect of the problem space as a foundation for further discussion.

---

## 2. What Air Traffic Controllers Actually Do

### Minute-by-Minute Workload

At any given moment, a controller is simultaneously:

1. **Scanning** radar displays to maintain a mental picture of all aircraft positions, altitudes, speeds, and trajectories
2. **Communicating** with pilots via VHF radio — issuing clearances, instructions, and advisories
3. **Planning ahead** — mentally projecting where each aircraft will be in 2-10 minutes and identifying potential conflicts
4. **Coordinating** with adjacent sectors/facilities via landline for handoffs and point-outs
5. **Updating** flight data strips or electronic flight data
6. **Prioritizing** constantly — reprioritizing as new aircraft enter, weather changes, or emergencies arise

### Key Decisions Made Continuously

- Whether to approve altitude change requests
- Sequencing order for arriving aircraft
- Spacing intervals between departures
- Heading vectors for separation or sequencing
- Speed assignments for flow management
- When and how to hand off aircraft to the next sector
- How to reroute traffic around weather
- Emergency priority handling

### Why Computers Could Excel

Each of these tasks is fundamentally about:
- **Spatial reasoning** over 3D trajectories evolving in time
- **Constraint satisfaction** (separation minima, airspace boundaries, runway capacity)
- **Optimization** (fuel efficiency, delay minimization, throughput)
- **Pattern recognition** (conflict detection, weather impact prediction)
- **Communication** (structured, phraseology-bound exchanges)

Computers have inherent advantages in every one of these areas: perfect memory, no fatigue, no attention limits, ability to simultaneously track thousands of trajectories, and the ability to compute optimal solutions across the entire system rather than one sector at a time.

### Why Humans Are Still There

- **Edge cases and novel situations** that weren't anticipated in algorithms
- **Regulatory requirements** for human-in-the-loop
- **Trust and accountability** — who is responsible when automation fails?
- **The out-of-the-loop problem** — the better automation works, the worse humans perform when it fails
- **Communication flexibility** — understanding non-standard pilot requests, accents, emergencies

---

## 3. The Three Domains of ATC

### A. Tower (Airport Traffic Control Tower — ATCT)

Manages aircraft on the airport surface and in the immediate vicinity (3-30 miles). Three positions:

| Position | Responsibility |
|----------|---------------|
| **Clearance Delivery** | Issues IFR route clearances (route, altitude, departure frequency, squawk code) |
| **Ground Control** | All ground movement on taxiways and inactive runways; runway incursion prevention |
| **Local Control (Tower)** | Takeoff/landing clearances; runway authorization; handoff to departure |

**Automation relevance:** Ground movement is highly structured and rule-based. Surface surveillance (ASDE-X, ASSC) already provides position data. This domain is ripe for automation — digital towers are already replacing physical towers in Europe.

### B. Approach/Departure (TRACON — Terminal Radar Approach Control)

Manages terminal airspace from tower boundary out to ~20-50 NM, up to ~17,000 feet.

- Sequences arriving aircraft onto final approach
- Ensures departing aircraft are safely separated and handed off to en-route
- Uses speed control, radar vectors, altitude assignments
- Manages Standard Instrument Departures (SIDs) and Standard Terminal Arrival Routes (STARs)

**Automation relevance:** Arrival sequencing is already partially automated via AMAN. This is the highest-workload domain with the most complex traffic mixing. AI-based sequencing and conflict resolution would have the highest impact here.

### C. En-Route / Center (Air Route Traffic Control Center — ARTCC)

20 centers in the US, each covering 100,000+ square miles. Manages aircraft at higher altitudes during cruise.

- Dominated by **conflict discovery** — detecting and resolving potential separation violations
- Issues altitude changes, direct routing, weather deviations
- Handles handoffs between sectors and to adjacent centers/TRACONs

**Automation relevance:** Conflict detection and resolution is the core task. ERAM already provides substantial automation. This domain has the most structured, predictable traffic patterns and is closest to full automation.

---

## 4. Core Tasks That Would Need Automation

### 4.1 Separation Assurance

The fundamental task: ensure no two aircraft violate minimum separation standards.

| Environment | Lateral Separation | Vertical Separation |
|-------------|-------------------|---------------------|
| Terminal (within 40 NM of radar) | 3 NM | 1,000 ft (below FL410) |
| En-route (beyond 40 NM) | 5 NM | 1,000 ft (RVSM, below FL410) |
| Non-radar | 5-20 min longitudinal | 2,000 ft (above FL410) |
| Wake turbulence (behind heavy/super) | 4-6 NM additional | — |

Currently relies on controller mental projection. An automated system would need:
- Trajectory prediction algorithms (4D: lat, lon, alt, time)
- Conformance monitoring (is aircraft following its cleared trajectory?)
- Automated alerting at multiple time horizons

### 4.2 Conflict Detection and Resolution

Three time horizons:

| Horizon | Timeframe | Current System | Automation State |
|---------|-----------|----------------|-----------------|
| **Strategic** | 20+ min | TFMS flow management | Partially automated |
| **Tactical** | 2-10 min | URET Conflict Probe, MTCD | Detection automated; resolution manual |
| **Urgent** | <2 min | Conflict Alert, MSAW, STCA | Detection automated; resolution manual |

The gap: **automated conflict detection has been operational for 20+ years**, but **automated resolution has not reached operational deployment**. This is the central technical challenge.

### 4.3 Sequencing and Metering

**TBFM (Time Based Flow Management)** is already operational at all 20 en-route centers, 28 TRACONs, and 54 towers. Uses time instead of distance to sequence traffic.

Remaining automation needs:
- Optimal runway assignment considering wind, traffic mix, wake turbulence
- Dynamic slot allocation across multiple airports
- Integrated departure/arrival optimization

### 4.4 Weather Routing

Convective weather is the **largest cause of delay** in the US NAS. Current tools:

- **Dynamic Weather Routes (DWR):** Computes trajectory corrections every 12 seconds
- **RAPT (Route Availability Planning Tool):** Guidance on departure times/routes to avoid weather
- **CIWS (Corridor Integrated Weather System):** 0-2 hour weather forecasts

An automated system could continuously reroute the entire traffic picture in real-time as weather evolves, rather than having controllers handle deviations one aircraft at a time.

### 4.5 Handoffs Between Sectors

Current procedure (5 steps, requiring coordination between two humans):
1. Transferring controller initiates handoff with aircraft ID and restrictions
2. Receiving controller verifies and accepts
3. Restrictions issued before acceptance
4. Pilot instructed to contact new frequency
5. Receiving controller confirms radar identification

In an automated system, handoffs become internal data transfers — no human coordination needed. CPDLC already enables automated frequency transfer.

### 4.6 Communication

**Current state:** VHF radio voice is the primary medium. Problems include:
- Frequency congestion
- Readback/hearback errors
- Call sign confusion
- Language barriers and accent issues
- High error rates under workload

**CPDLC (Controller-Pilot Data Link Communications):** Already operational at 62 airports and all 20 en-route centers. Reduces voice channel use by up to 75%. This is the bridge to fully digital communication.

An automated system would primarily use CPDLC/DataComm for routine instructions, with voice as fallback for non-standard situations.

---

## 5. Current ATC Technology Infrastructure

### The Big Two: ERAM and STARS

| System | ERAM | STARS |
|--------|------|-------|
| **Domain** | En-route (20 ARTCCs) | Terminal (236 TRACONs, 655 towers) |
| **Contractor** | Lockheed Martin | Raytheon (RTX/Collins Aerospace) |
| **Hardware** | IBM P-series (Power) / AIX | COTS microprocessors |
| **Software** | Ada (~2 million LOC) | Ada |
| **Deployed** | Full capability March 2015 | Final site May 2021 |
| **Capacity** | 1,900 simultaneous aircraft | 900 aircraft, 16 radar feeds |
| **Displays** | — | 2048x2048 color, 20"x20" |

Both systems are written in **Ada** — a language chosen for safety-critical applications but with a shrinking developer pool.

### Communication Systems

| System | Function | Status |
|--------|----------|--------|
| **VHF Radio** | Primary voice (118-136.975 MHz) | Active; frequency band congested |
| **Legacy voice switches** | ~800 analog switches | Being replaced by VoICE (VoIP) |
| **NEXCOM** | Next-gen air/ground radios | Active modernization |
| **ACARS** | Digital datalink (text messages) | Active; being supplemented by CPDLC |
| **CPDLC/DataComm** | Digital ATC clearances | Operational at all 20 ARTCCs, 62 airports |

### The BNATCS Program (Brand New Air Traffic Control System)

Announced 2025, this is the most significant ATC modernization in decades:

- **Prime Integrator:** Peraton
- **Total estimated cost:** $32.5 billion ($12.5B initially funded)
- **Scope:** Replace the *entire* ATC technology stack
- **Initial priorities:** Copper-to-fiber infrastructure, digital command center, radar replacement
- **Radar contracts:** RTX Collins ($438M) and Indra ($342M) for 612 sites by June 2028
- **Common Automation Platform (CAP):** RFI issued for a unified platform to replace both STARS and ERAM

---

## 6. Legacy Systems: The Scale of the Problem

### GAO Assessment (2024-2025)

Of **138 FAA ATC systems**:

| Status | Count | Percentage |
|--------|-------|------------|
| Unsustainable | 51 | 37% |
| Potentially unsustainable | 54 | 39% |
| Sustainable | 33 | 24% |

**17 systems** identified as "especially concerning" — modernization not expected for **6-10+ years**. Three systems at least 30 years old have **no modernization plans at all**.

### Why Replacement Is So Hard

1. **Spare parts extinct:** Components no longer manufactured. Finding replacements is increasingly impossible.
2. **Expertise retiring:** Staff who understand analog voice switches, legacy mainframe code, and custom protocols are leaving with no replacements.
3. **Custom hardware:** Historical systems used purpose-built hardware (e.g., IBM 9020 multiprocessor from the 1960s).
4. **Certification:** ATC software is safety-critical. Existing certification criteria don't address AI/ML systems. Software can't realistically be tested in all possible states.
5. **Integration complexity:** New systems must interoperate with existing ones during multi-year transitions.
6. **Acquisition speed:** 8 of 9 applicable modernization investments took **over 4 years just to establish baselines**.

### Historical Context

The code lineage of some ATC systems stretches back to the 1960s:
- **1960s-70s:** IBM 9020 (custom multiprocessor System/360) — purpose-built for ATC
- **1986:** Replaced by IBM 3083 mainframes ("HOST" system) running essentially the same application code
- **1998:** HOST hardware upgraded via HOCSR program (~$226M)
- **2015:** ERAM replaced HOST at all 20 ARTCCs

That's 55+ years of incremental evolution. BNATCS aims to break this cycle entirely.

---

## 7. Surveillance Data: How Aircraft Are Tracked

### Primary Surveillance Radar (PSR)

- **How it works:** Rotating antenna emits high-power pulses; measures reflected energy
- **Data provided:** Range and azimuth only — no altitude, no identity
- **Range:** Up to 60 NM at large airports
- **Key advantage:** Detects aircraft with no transponder (non-cooperative)
- **Key limitation:** Cannot distinguish aircraft from birds, weather, terrain

### Secondary Surveillance Radar (SSR)

Cooperative system: ground interrogator (1030 MHz) → aircraft transponder replies (1090 MHz).

| Mode | Data Provided |
|------|--------------|
| **Mode A** | 4-digit octal squawk code (4,096 codes: 0000-7777) |
| **Mode C** | Pressure altitude in 100-ft increments |
| **Mode S** | Unique 24-bit ICAO address + selective interrogation + two-way data link |

Mode S carries: callsign, selected altitude, indicated airspeed, Mach, magnetic heading, roll angle, track angle rate, and more via BDS registers. Mode S is the foundation for ADS-B.

### ADS-B (Automatic Dependent Surveillance-Broadcast)

The game-changer for automated ATC. Every equipped aircraft continuously broadcasts:

- ICAO 24-bit address (globally unique)
- Callsign / flight identification
- GPS-derived latitude and longitude
- Barometric and geometric altitude
- Ground speed and airspeed
- Track angle / true heading
- Vertical rate (ft/min)
- Squawk code
- Emitter category (light, large, heavy, rotorcraft, etc.)
- Navigation integrity and accuracy categories
- Emergency/priority status
- Selected altitude (from autopilot/FMS)

**~49 individual parameters** per aircraft, broadcast without interrogation.

**FAA Mandate (January 1, 2020):** ADS-B Out required in Class A (above FL180), Class B/C, Class E above 10,000 ft, and within 30 NM of major airports.

**Two frequencies in the US:**
- **1090 MHz Extended Squitter (1090ES):** Required above FL180; global ICAO standard
- **978 MHz UAT:** US-only; permitted below 18,000 ft; also carries weather (FIS-B) and traffic (TIS-B)

### Multilateration (MLAT)

- Uses **Time Difference of Arrival (TDOA)** across 4+ synchronized receivers
- Works with **any** transponder on 1090 MHz — no ADS-B required
- Professional accuracy: 3-7.5 meters on airport surfaces
- **Resistant to GPS jamming/spoofing** (position computed independently by ground receivers)
- Serves as integrity check on ADS-B positions

---

## 8. Available Data Feeds and Integration Points

### For Building a System: Where to Get Data

| Source | Data | Format | Protocol | Access |
|--------|------|--------|----------|--------|
| **FAA SWIM** | Flight, weather, surveillance, aeronautical | FIXM/AIXM XML | JMS (Solace) | FAA agreement |
| **OpenSky Network** | ADS-B positions, 6,000+ global receivers | JSON / CSV | REST / Trino SQL | Free (rate-limited) |
| **FlightAware AeroAPI** | Flight status, tracking, 60+ endpoints | JSON | REST | Usage-based pricing |
| **FlightAware Firehose** | Real-time all-data stream | JSON Lines | TCP/SSL | Enterprise pricing |
| **FlightRadar24** | ADS-B + MLAT, 35,000+ receivers | JSON | REST | Commercial license |
| **ADSBexchange** | Unfiltered ADS-B (no blocking) | JSON | REST | RapidAPI / Enterprise |
| **ADSB.lol** | Open-data, unfiltered | JSON | REST | Free |
| **Direct ADS-B receiver** | Raw 1090ES/978 UAT | SBS/Beast/JSON | TCP/HTTP | Self-hosted (~$75-160) |

### SWIM Deep Dive

SWIM is the FAA's enterprise data-sharing backbone — the most important integration point for any system that needs to work with real ATC data.

- **Architecture:** Service-Oriented Architecture (SOA) on Solace messaging
- **External access:** NAS Enterprise Security Gateway (NESG) via VPN
- **Public cloud access:** SWIM Cloud Distribution Service (SCDS) via JMS 1.1
- **Key services:**
  - **SFDPS:** En-route flight data from ERAM
  - **STDDS:** Terminal/TRACON data (RVR, surface surveillance)
  - **TFMS:** Traffic flow management / demand-capacity data
  - **ITWS:** Terminal weather

### ASTERIX (EUROCONTROL Standard)

Binary protocol for surveillance data exchange. Key categories:

| Category | Data |
|----------|------|
| CAT001 | Monoradar target reports (PSR/SSR) |
| CAT021 | ADS-B target reports |
| CAT048 | Monoradar target reports (most widely used) |
| CAT062 | Fused multi-sensor system tracks |

Compact binary format, extensible, and increasingly adopted globally. Libraries and Wireshark dissectors available.

### Aviation XML Standards

- **FIXM (Flight Information Exchange Model):** Flight data interoperability
- **AIXM (Aeronautical Information Exchange Model):** Airports, runways, airspace, procedures
- **IWXXM (Weather Information Exchange Model):** Meteorological data

---

## 9. What's Already Automated

It's important to understand that ATC is not starting from zero on automation. Substantial automation already exists:

### Safety Nets (Operational Today)

| System | Function | Horizon |
|--------|----------|---------|
| **TCAS II / ACAS X** | Airborne collision avoidance (aircraft-to-aircraft) | 25-48 seconds |
| **STCA** | Short-term conflict alert (ground-based) | 2-3 minutes |
| **MSAW** | Minimum Safe Altitude Warning | Immediate |
| **Conflict Alert** | Loss-of-separation predictor | 2 minutes |
| **APW** | Area Proximity Warning (restricted airspace) | Immediate |

**ACAS X** (replacing TCAS) is notable: developed by MIT Lincoln Laboratory using **dynamic programming over Markov decision processes** — an AI technique. It reduces false advisories by ~50% compared to TCAS.

### Flow and Sequence Management (Operational Today)

| System | Function |
|--------|----------|
| **TBFM** | Time-based metering at all 20 centers, 28 TRACONs, 54 towers |
| **TFMS** | Strategic flow management across the NAS |
| **AMAN/DMAN** | Arrival and departure managers (automated sequencing) |
| **TFDM** | Terminal flight data management (deploying to 49 airports through 2029) |

### Decision Support (Operational Today)

| System | Function |
|--------|----------|
| **URET Conflict Probe** | Medium-term conflict detection (20+ years operational) |
| **DWR** | Dynamic Weather Routes — computes corrections every 12 seconds |
| **RAPT** | Route Availability Planning for weather avoidance |
| **CIWS** | 0-2 hour weather forecasts |

### What's NOT Automated

- **Conflict resolution** (the system can detect a conflict, but a human must decide how to resolve it)
- **Final clearance authority** (all clearances must be issued by a human)
- **Exception handling** (emergencies, non-standard requests, equipment failures)
- **Communication** (voice radio remains primary; CPDLC supplements but doesn't replace)

---

## 10. AI and Algorithmic Approaches

### Conflict Detection and Resolution

The state of the art has shifted dramatically toward **deep reinforcement learning**:

| Approach | Description | Status |
|----------|-------------|--------|
| **Modified Voltage Potential (MVP)** | Geometric method computing minimum deviation vectors | Validated in simulation |
| **URET Conflict Probe** | Flight plan trajectory checking | Operational 20+ years |
| **Hybrid DRL-Geometric (2025)** | Deep RL combined with MVP geometry | Research (promising results) |
| **Self-Prioritizing Multi-Agent RL (2025)** | Multi-agent RL for multi-aircraft conflicts | Research |
| **Transparent DRL (2024)** | Separated safety/efficiency Q-value modules | Research |
| **UAM Multi-Agent A3C (2024)** | Asynchronous actor-critic for 3D eVTOL | Research (resolves nearly all conflicts) |

### NLP for Radio Communications

- 2025 study: **91.73% word recognition accuracy** (ASR), **F1 score 0.9816** (NLU), ~0.6 second latency
- Dual-pipeline ML framework classifying pilot intent from both text and spectral features
- LLMs (OpenAI o3, Gemini 2.0) being investigated for AI-assisted pilot-controller communication

### Comprehensive AI Survey (2025)

The paper "AI4ATM" documents the transition from rule-based systems to ML/DL across all ATM components. AI now plays significant roles in:
- Trajectory prediction
- Flow optimization
- Surveillance enhancement
- Communication processing
- Weather impact assessment

### UTM as a Proving Ground

NASA's UTM program is designing drone traffic management with much higher automation levels:
- Digital-native, service-oriented architecture
- Automated conflict management
- Third-party Automated Data Service Providers
- FAA Part 108 BVLOS rulemaking expected **spring 2026**

UTM principles are directly informing how higher-altitude airspace management might evolve.

---

## 11. Safety, Redundancy, and Certification

### Software Certification Standards

**Airborne Systems — DO-178C:**

| DAL | Condition | Max Failure Rate | Objectives |
|-----|-----------|-----------------|------------|
| A | Catastrophic | 10⁻⁹ per flight hour | 71 |
| B | Hazardous | 10⁻⁷ | 69 |
| C | Major | 10⁻⁵ | 62 |
| D | Minor | 10⁻⁵ | 26 |
| E | No effect | — | 0 |

For context: DAL-A means no more than **one catastrophic failure per billion flight hours**.

**Ground-Based ATC Systems — ED-153:**
EUROCAE standard defining Software Assurance Levels (SWAL 1-4) for Air Navigation Service systems. Covers full lifecycle from specification through decommissioning.

### Redundancy Requirements for ATC

Any automated ATC system would need:

1. **Dual or triple redundant hardware** with automatic failover
2. **Hot standby systems** for instant switchover (ERAM already uses dual-channel architecture)
3. **Independent safety nets** running on separate processors (defense in depth)
4. **Graceful degradation** — if primary automation fails, fallback to simpler automation, then to procedural control
5. **Geographic redundancy** — distributed processing so no single facility failure brings down the system
6. **Diverse redundancy** — different software implementations for critical functions (to prevent common-mode failures)
7. **Human override capability** — ability for humans to take control at any time

### The AI Certification Problem

This is the single biggest unsolved challenge. Traditional certification requires:
- **Deterministic** behavior (same input → same output)
- **Traceable** logic (every decision explainable via code path)
- **Complete testing** (all states verified)

Neural networks and RL agents are:
- **Not deterministic** in the traditional sense
- **Not explainable** (black box problem)
- **Not testable** (astronomical state spaces)
- **Potentially brittle** in edge cases outside training distribution

**DARPA's ARCOS program** (Automated Rapid Certification Of Software), in collaboration with NASA, is researching new certification criteria specifically for autonomous and AI-based systems. This work is essential before any AI-based ATC system could be deployed.

---

## 12. Barriers to Full Automation

### The Out-of-the-Loop Problem

Research by Mica Endsley (1995, foundational) established that:
- When automation is highly reliable, human operators **lose situational awareness**
- Vigilance degrades; ability to take over during failures is **severely impaired**
- The **better** the automation works, the **worse** humans perform when it fails

This creates a fundamental paradox: you can't have a system that's "mostly automated with human backup" because the human backup deteriorates precisely when it's needed most.

### Skill Degradation

Extended reliance on automation leads to degradation of:
- Manual control skills
- Teamwork and coordination practices
- Communication proficiency
- Recovery abilities during failures

### Regulatory Framework

- **ICAO:** Requires human controllers able to intervene and assume manual control
- **FAA:** Requires "human-centered automation" — tools that complement, not replace
- **EASA:** Requires human oversight for all safety-critical ATM functions
- **No regulatory pathway currently exists for fully autonomous ATC**

### Historical Failure

The FAA's **AERA (Automated En-Route Air Traffic Control)** program in the 1980s-90s was part of a $32 billion automation plan. It failed because "the underlying science and mathematical algorithms did not exist at that time." This historical trauma has made the FAA extremely cautious about ambitious automation.

### The Implied Path

The consensus (FAA, EUROCONTROL, ICAO, research community) is **incremental**:

1. Automate routine tasks (sequencing, flow management, data handling)
2. Improve decision support (conflict detection with suggested resolutions)
3. Reduce controller workload to manage more traffic per controller
4. Maintain human authority for final decisions and exceptions
5. Develop new certification frameworks for AI/ML (DARPA ARCOS)
6. Use UTM/AAM as testbeds for higher autonomy before conventional ATC
7. Eventually — maybe — transition to autonomous operation in well-defined domains

---

## 13. Architecture Options for a New System

Based on all the research, here are the viable architectural approaches:

### Option A: Shadow System (Monitoring / Advisory)

**Concept:** Build a system that ingests live ATC data (via SWIM, ADS-B, etc.), runs its own conflict detection and resolution algorithms, and compares its decisions against what human controllers actually do. No operational authority.

**Data sources:** SWIM SCDS (JMS), OpenSky Network, direct ADS-B receivers
**Value:** Validates algorithms, builds confidence, identifies gaps
**Regulatory burden:** Minimal — it's not controlling anything
**Complexity:** Medium
**This is the obvious starting point.**

### Option B: Decision Support Tool

**Concept:** A system that provides real-time recommendations to human controllers — suggested conflict resolutions, optimal sequences, weather reroutes — that controllers can accept or override.

**Integration:** Would need to interface with STARS/ERAM or the upcoming Common Automation Platform
**Value:** Directly reduces controller workload while maintaining human authority
**Regulatory burden:** Moderate — needs safety assessment but not full DAL-A certification
**Complexity:** High (requires integration with operational systems)

### Option C: Domain-Limited Autonomy

**Concept:** Full automation for specific, well-bounded domains:
- Oceanic airspace (sparse traffic, already heavily procedural)
- Low-density en-route sectors during off-peak hours
- Ground movement at specific airports
- Drone/UTM airspace (already heading this direction)

**Value:** Proves the concept in controlled environments
**Regulatory burden:** High but bounded
**Complexity:** High

### Option D: Greenfield Full Automation

**Concept:** Build a completely autonomous ATC system from scratch, potentially for a new category of airspace (e.g., Advanced Air Mobility corridors for eVTOLs).

**Value:** Avoids legacy integration entirely; designed for automation from day one
**Regulatory burden:** Extreme — requires new certification frameworks
**Complexity:** Very high
**Timeframe:** 10-20 years

### Recommended Approach: Start with Option A

A shadow system is:
- Low risk (no operational impact)
- Immediately buildable with available data
- Provides the foundation for all other options
- Generates the performance data needed to make the case for further automation

---

## 14. The Hobbyist Entry Point

For prototyping and development, you can build a surprisingly capable surveillance picture from your laptop.

### Minimum ADS-B Receiver Setup (~$75-160)

| Component | Cost |
|-----------|------|
| Raspberry Pi Zero 2W or Pi 3/4 | $15-45 |
| FlightAware Pro Stick Plus (ADS-B-optimized RTL-SDR) | $25-35 |
| 1090 MHz antenna (commercial or DIY) | $10-40 |
| microSD card (32 GB) | $8-12 |
| Power supply + case | $10-15 |
| Short quality coax (RG-6) | $5-15 |

**Minimal build (Pi Zero 2W + generic RTL-SDR + DIY antenna): under $50**

### Software Stack

| Software | Function |
|----------|----------|
| **dump1090-fa** or **readsb** | Decode ADS-B from RTL-SDR; built-in web map |
| **tar1090** | Enhanced web map interface |
| **PiAware / fr24feed** | Feed to FlightAware/FR24 (get free premium accounts) |
| **Virtual Radar Server** | Windows-based ADS-B display and logging |

### Performance

- Stock whip antenna: ~25 miles range
- Tuned antenna + LNA: **100-150 NM (185-280 km)**
- Optimized elevated setup: up to **232 NM (430 km)** demonstrated
- Position accuracy: 10-30 meters (GPS-dependent)

### API-Based Alternative (No Hardware)

For pure software development, skip the receiver entirely:

```
# OpenSky Network - free REST API
GET https://opensky-network.org/api/states/all?lamin=33&lomin=-118&lamax=34&lomax=-117

# Returns JSON with all aircraft in bounding box:
# icao24, callsign, origin_country, longitude, latitude,
# baro_altitude, velocity, true_track, vertical_rate, squawk...
```

ADSBexchange and ADSB.lol also offer free/low-cost APIs with unfiltered data.

### Community MLAT

If you feed your ADS-B data to FlightAware, FR24, or ADSBexchange, you automatically participate in their MLAT networks — your receiver helps locate Mode S aircraft that lack ADS-B. Results are shared back to you.

---

## 15. Key Players and Active Programs

### Government Programs

| Program | Organization | Focus | Status |
|---------|-------------|-------|--------|
| **BNATCS** | FAA | $32.5B total ATC replacement | Active (Peraton as prime) |
| **NextGen** | FAA | ADS-B, DataComm, TBFM, TFDM | Completing ~2030 |
| **SESAR 3** | EUROCONTROL/EU | 42 projects, EUR 254M | Launching mid-2026 |
| **ATM-X** | NASA | Air traffic transformation for AAM | Concluded Feb 2026 |
| **UTM BVLOS** | NASA | Drone traffic management | Active |
| **ARCOS** | DARPA + NASA | AI/autonomous software certification | Active |
| **ACE** | DARPA | AI-controlled aircraft (demonstrated AI F-16 dogfight) | Demonstrated 2022 |

### Major Industry Players

| Company | Role |
|---------|------|
| **Leidos** | FAA primary systems integrator (ERAM, TFDM, ATOP); $31.5B contract |
| **Peraton** | BNATCS prime integrator; $1B+ initial tasks |
| **RTX/Collins Aerospace** | STARS; $438M next-gen radar contract |
| **Raytheon** | Historical STARS developer |
| **Lockheed Martin** | Historical ERAM developer |
| **Indra** | 4,000+ ATC installations in 160 countries; iTEC platform; $342M FAA radar contract |
| **Thales** | TopSky ATM suite; European market leader |
| **NATS** | UK ANSP; digital tower innovation (Searidge Technologies subsidiary) |
| **Frequentis** | Voice communication and ATM information management |
| **Aireon** | Space-based ADS-B via 66 Iridium satellites — global real-time surveillance |

### Research Institutions

- **MIT Lincoln Laboratory** — ACAS X development, conflict resolution algorithms
- **MITRE/CAASD** — FAA FFRDC; URET conflict probe, ATC modernization analysis
- **NASA Langley/Ames** — ATM-X, UTM, autonomous operations research
- **NLR (Netherlands)** — BlueSky open-source ATC simulator, MVP algorithms

---

## 16. Conclusions and Discussion Points

### What Makes This Feasible Now (vs. the 1980s AERA Failure)

1. **ADS-B provides the data:** Every equipped aircraft continuously broadcasts precise position, velocity, and identity. This was science fiction in the 1980s.
2. **Deep RL has cracked conflict resolution:** Multi-agent reinforcement learning can handle the combinatorial complexity of multi-aircraft conflicts that defeated classical algorithms.
3. **NLP can handle radio communications:** 91%+ accuracy on ATC speech recognition; LLMs can parse non-standard phraseology.
4. **SWIM provides the backbone:** Service-oriented architecture with JMS access to real-time flight, weather, and surveillance data.
5. **Compute is cheap:** A laptop today has more processing power than all 20 ARTCCs combined had in the 1990s.
6. **UTM is proving the concept:** Drone traffic management is being designed for automation from day one.
7. **The FAA is doing BNATCS anyway:** A $32.5B clean-slate rebuild creates a once-in-a-generation window for new architecture.

### What Remains Hard

1. **Certification of AI/ML:** No accepted framework exists. DARPA ARCOS is working on it, but this is years away.
2. **The out-of-the-loop problem:** Can't have "mostly automated with human backup" because the backup degrades.
3. **Edge cases:** Emergencies, system failures, unusual weather, birds, drones, military operations — the long tail of scenarios that algorithms haven't seen.
4. **Regulatory inertia:** ICAO/FAA/EASA all require human-in-the-loop. Changing international standards takes decades.
5. **Trust and accountability:** When an autonomous system makes a wrong decision and people die, who is responsible?
6. **Adversarial threats:** ADS-B has no authentication — positions can be spoofed. GPS can be jammed. An automated system that trusts this data is vulnerable.

### Discussion Questions

1. **Shadow system first?** Should the initial goal be a passive system that monitors live traffic and benchmarks its decisions against human controllers?

2. **Which domain first?** Oceanic (simplest), en-route (most structured), terminal (highest impact), or ground (most contained)?

3. **UTM bridge?** Should this project focus on the UTM/AAM space first, where automation is expected and the regulatory path is clearer?

4. **Open source?** Projects like BlueSky (NLR's open-source ATC simulator) provide ready-made simulation environments. Start with simulation before touching live data?

5. **ADS-B security:** Given that ADS-B has no encryption or authentication, how would an automated system verify the integrity of its surveillance data? MLAT as a cross-check?

6. **What's the actual goal?** Full autonomy (decades out)? Decision support for human controllers (nearer term)? A research platform? A commercial product? The architecture changes significantly depending on the answer.

---

## 17. Agent Certification: Mapping FAA Standards to Software Validation

### How Human Controllers Are Certified

The FAA evaluates controllers across **27 performance functions in 6 categories** (per FAA Order JO 3120.4S and the National Academies' assessment framework):

| Category | What's Evaluated |
|----------|-----------------|
| **Separation & Safety** | Maintaining aircraft separation, providing safety alerts |
| **Control Judgment** | Situational awareness, decision-making, planning |
| **Methods & Procedures** | Traffic flow management, error correction, strip accuracy |
| **Equipment Operation** | System proficiency, data entry accuracy |
| **Communication/Coordination** | Phraseology, sector coordination, professional conduct |
| **Emergency Recovery** | Relief briefings, handling abnormal situations |

The certification process: 13 training phases with exams at each stage, 40-minute observed sessions, daily instructor checklists, monthly supervisor evaluations, and a final "over-the-shoulder" check ride under real traffic. Three rating levels: exceeds standards, fully successful, unacceptable. Total time: 3-5 years. Academy washout rate: 30-50%.

### Mapping to Agent Certification

Every FAA category is directly testable for a software agent — and we can exceed the human standard:

| FAA Category | Agent Equivalent | Test Method |
|---|---|---|
| Separation & Safety | Trajectory prediction + conformance monitoring | Replay historical traffic; inject known conflicts; measure detection rate and response time |
| Control Judgment | Decision model (sequencing, routing, resolution) | Run against thousands of recorded scenarios; compare decisions to certified controller actions |
| Methods & Procedures | Rule engine + procedure library | Formal verification against FAA Order 7110.65 |
| Equipment Operation | N/A (the agent *is* the equipment) | System integration tests |
| Communication | STT + NLP + TTS pipeline | Test against recorded ATC audio; measure word accuracy, intent recognition, phraseology correctness |
| Emergency Recovery | Failure mode handling + graceful degradation | Chaos engineering — kill components, degrade inputs, inject garbage data |

The agent certification suite would also include running every NTSB incident scenario in the database and verifying the system would have prevented or mitigated each one.

---

## 18. Three-Tier Escalation Architecture

The core design principle: **match the handler to the criticality level.** LLMs handle what they're good at (flexible, conversational, pattern recognition). Deterministic systems handle what they're good at (provably correct, certifiable). Humans handle what they're good at (novel situations, accountability).

### Tier 1: LLM Agents (Routine / Flexible)

Handles early contact and low-criticality tasks:
- Initial contact and airspace confirmation ("Air Canada 8646, entering New York approach airspace")
- ATIS broadcasts and weather updates
- Preliminary sequencing ("Expect ILS Runway 4, you are number 5")
- Routine frequency changes
- Flight plan amendments
- Non-critical information requests
- **Monitoring Tier 2 output** for anomalies the deterministic system can't detect

LLMs are ideal here: flexible with accents, non-standard phraseology, and conversational exchanges. The consequence of an error at this tier is low — it's informational, not safety-critical.

### Tier 2: Deterministic Systems (Critical / Certifiable)

Handles all safety-critical operations:
- Final approach sequencing and clearances
- Landing and takeoff clearances
- Separation enforcement
- Runway assignment
- Ground movement near active runways
- All decisions where an error could cause a collision

These are **not LLMs**. They are rule engines, optimizers, and formally verified algorithms. They can be certified under existing frameworks (DO-178C / ED-153) because their behavior is deterministic, traceable, and testable.

**The LLM monitors these systems but does not control them.** The LLM's role: "The deterministic system just issued this clearance — does it make sense given everything I know about the broader traffic picture, weather, and context?"

### Tier 3: Human + AI Assistants (Emergency / Novel)

Triggered when:
- Pilot declares MAYDAY or PAN-PAN
- Any parameter exceeds the normalcy threshold (see Section 20)
- Redundant agents disagree on an action
- System detects a situation outside its training distribution

The human takes direct control but has full AI support:
- Aircraft-specific performance data and cockpit layouts
- Emergency procedure checklists
- Nearest suitable airports computed and ranked
- Other traffic already being rerouted by Tier 2
- AI recommendation with confidence level

The human's job: verify and approve (or override). They are not reconstructing the situation from scratch — the system has already done the analysis.

### Why This Solves the "Out-of-the-Loop" Problem

The traditional criticism of automation is that humans lose situational awareness when automation is too reliable. This architecture addresses it differently:

- The human overwatcher is **always active** — reviewing Tier 1 and Tier 2 decisions continuously, not just sitting idle
- The review format is designed for rapid comprehension (see Section 21)
- Emergency escalation puts the human in the loop **with full context**, not cold
- The AI assistants ensure the human has more information than a traditional controller, not less

### Escalation Triggers

| Trigger | Source | Escalation |
|---|---|---|
| Pilot declares emergency | STT pipeline | Immediate → Tier 3 |
| Squawk 7500/7600/7700 | ADS-B/transponder | Immediate → Tier 3 |
| Agent disagreement | Orchestration layer | → Tier 3 for resolution |
| Parameter exceeds normalcy threshold | Monitoring agents | Yellow → Tier 2 alert; Red → Tier 3 |
| Safety net veto | Collision/separation monitors | Immediate → halt + Tier 3 |
| System component failure | Health monitoring | → Failover + Tier 3 notification |

---

## 19. Multi-Agent Architecture: Full Inventory

### Design Principle: Redundant Consensus

Every safety-critical task has 2+ independent agents working the same problem. They don't see each other's work. The orchestration layer compares outputs — if they agree, proceed; if they disagree, escalate.

### Layer 1: Specialized Task Agents (The Workers)

| Agent | Responsibility | Type | Instances |
|---|---|---|---|
| **Approach/Landing Agent** | Sequence arrivals, assign runways, issue approach clearances | Hybrid (rules + RL + LLM) | 3 (consensus of 2, 1 standby) |
| **Departure Agent** | Sequence departures, issue clearances, SID assignment | Hybrid | 3 |
| **Ground Traffic Agent** | Taxi clearances, vehicle movement, runway crossing auth | Hybrid | 3 |
| **En-Route Agent** | Cruise-phase separation, routing, handoffs | Hybrid | 3 |
| **Weather/Routing Agent** | Monitor weather, compute reroutes, delay management | Specialized + deterministic | 2 |

### Layer 2: Safety Net Agents (The Watchers)

These **never use LLMs**. Pure algorithmic systems on independent hardware. They have **veto power** over all other tiers.

| Agent | Responsibility | Type | Instances |
|---|---|---|---|
| **Collision Vector Monitor** | Track ALL positions/trajectories; predict conflicts at multiple horizons | Deterministic (computational geometry) | 2 (independent hardware) |
| **Separation Monitor** | Verify all separations meet minimums continuously | Deterministic (rule-based) | 2 |
| **Runway Incursion Monitor** | Track all surface movement; flag unauthorized runway entry | Deterministic + sensor fusion | 2 |
| **Conformance Monitor** | Verify aircraft follow cleared routes/altitudes | Deterministic (compare actual vs. expected) | 2 |

### Layer 3: Orchestration Agent (The Referee)

| Function | Implementation |
|---|---|
| Consensus checking | Compare redundant agent outputs; flag disagreements |
| Conflict arbitration | When Layer 2 vetoes Layer 1, determine alternatives |
| Workload distribution | Assign sectors to agents, manage capacity |
| System health | Detect agent failures, trigger failover |
| Human interface | Format decisions for overwatcher display |
| **Instances** | 2 (active-passive) |

### Layer 4: Communication Pipeline

| System | Type | Instances |
|---|---|---|
| **Speech-to-Text (STT)** | Parakeet TDT (primary), Whisper Turbo (backup), Vosk (emergency) | 2 |
| **Text-to-Speech (TTS)** | Kokoro v1.0 (primary), Piper (fallback) | 2 |
| **NLP Intent Parser** | Fine-tuned 1-3B LLM for ATC phraseology | 2 |

### Layer 5: Human Interface

| Component | Function |
|---|---|
| **Overwatcher Display** | Consolidated view of all agent decisions with verification data |
| **Emergency Panel** | Aircraft-specific data, checklists, divert options (see Section 21) |
| **Override Controls** | Ability to countermand any agent decision at any time |

### Total System Inventory

**~30 independent agent/system instances.** Roughly half ML-based, half deterministic. The deterministic safety nets have veto power and are the easiest to certify.

---

## 20. Normalcy Threshold and Compound Triggers

### Individual Parameter Monitoring

| Parameter | Normal | Yellow (Alert) | Red (Escalate) |
|---|---|---|---|
| Deviation from cleared altitude | ±100 ft | ±300 ft | ±500 ft |
| Deviation from cleared heading | ±5° | ±15° | ±30° |
| Groundspeed vs. expected | ±10 kts | ±25 kts | ±50 kts |
| Unexpected vertical rate | Normal for phase | >3000 fpm | >6000 fpm |
| Proximity to other traffic | >separation min | <120% of min | <100% of min |
| Proximity to terrain | >MSAW threshold | Approaching | MSAW trigger |
| Time without position update | <5 sec | >10 sec | >30 sec |
| Transponder code change | Expected | Unexpected | 7500/7600/7700 |
| Communication gap | <30 sec | >60 sec | >120 sec |

Thresholds are **tunable per facility** (busy TRACON vs. quiet tower), **weather condition** (tighter in IMC), **traffic density** (tighter when busy), and **time of day**.

### Compound Triggers

Individual yellows may be benign. Combinations are not:

- Altitude deviation + speed deviation + no radio = probable emergency → escalate immediately
- Multiple aircraft deviating in same area = probable weather or GPS interference
- Ground vehicle approaching active runway + aircraft on final = **LaGuardia scenario** → immediate veto

The LLM monitoring layer's key value: the deterministic system sees individual parameters; the LLM sees the **pattern**. "Three slightly-off things simultaneously isn't three independent anomalies — it's one situation developing."

---

## 21. Emergency AI Assistant

### What the System Handles (FAA 7110.65 Chapter 10)

The FAA's emergency procedures cover 7 sections with 40+ specific procedures:

**Section 1 — General:** Emergency determinations, information gathering, responsibility assignment
**Section 2 — Emergency Assistance:** Hijacking (7500), NORDO (7600), VFR-into-IMC, bomb threats, volcanic ash, laser illumination, MANPADS, emergency airport recommendation, medical emergencies
**Section 3 — Overdue Aircraft:** ALNOT procedures, RCC coordination
**Section 4 — Control Actions:** Traffic restrictions, lighting, communications failure
**Section 5 — Miscellaneous:** Explosive cargo, space launch debris
**Section 6 — Oceanic Emergencies:** Phases of emergency, rescue coordination
**Section 7 — Ground Missile Emergencies:** Information relay, avoidance

### Emergency Categories and AI Assistant Roles

| Emergency | AI Assistant Provides |
|---|---|
| **Engine failure** | Aircraft type single-engine performance data, glide range circle, nearest suitable airports ranked by distance/runway length/weather |
| **Fuel emergency** | Real-time fuel burn calculation, range ring overlay, countdown timer, divert airport ranking |
| **Medical emergency** | Hospital proximity database, airport medical capability ratings, ambulance pre-staging |
| **NORDO (comms failure)** | Expected route per FAR 91.185, predicted position display, deviation alerting |
| **Hijack (7500)** | Tracking, coordination support (human handles classified procedures) |
| **Bomb threat** | Checklist automation, blast radius calculations, isolation area mapping |
| **Bird strike** | Aircraft damage assessment guides, known bird activity data |
| **VFR into IMC** | Terrain mapping, nearest VFR weather, simplified instruction generation |
| **Volcanic ash** | Ash dispersion modeling, SIGMET overlay, mass reroute computation |
| **Laser illumination** | Geolocation of source from reported position/heading |

### Aircraft Performance Database

For the ~50 most common commercial aircraft types, the system maintains:
- Cockpit layout diagrams
- All V-speeds for various configurations and weights
- Single-engine performance data
- Emergency checklist summaries
- Minimum runway requirements by condition (dry/wet/contaminated)
- Evacuation procedures and door locations
- Known system failure modes and implications
- MEL/CDL references

This database is **static and certifiable** — it's a lookup table, not an LLM inference. The LLM's job is knowing which data to pull and how to present it in context.

### Data Sources (Publicly Available)

| Source | Content |
|---|---|
| FAA type certificates | Performance data, limits, dimensions for every certified aircraft |
| POH/AFM summaries | Operating procedures, V-speeds, emergency checklists |
| ARFF index | Airport rescue/firefighting capability ratings |
| FAA NASR/CIFP | Every runway's length, width, surface, lighting, available approaches |

---

## 22. Historical Incident Analysis

Detailed case studies of how the multi-agent system would have prevented real-world incidents are maintained in a separate document:

**See: [HISTORICAL_INCIDENT_ANALYSIS.md](HISTORICAL_INCIDENT_ANALYSIS.md)**

Currently analyzed incidents:

| Incident | Date | Fatalities | Key Failure | System Prevention |
|---|---|---|---|---|
| **Potomac River Midair (DCA)** | Jan 29, 2025 | 67 | Helicopter route under approach path; combined controller positions; 15,000 near-misses ignored; visual separation at night | Collision Vector Monitor detects convergence at T-120 sec; Conformance Monitor flags altitude exceedance; automated separation instructions issued at T-60 sec |
| **LaGuardia Runway Collision (LGA)** | Mar 23, 2026 | 2 | Conflicting clearances for same runway; controller distracted by concurrent emergency; no cross-check | Runway Incursion Monitor denies crossing in <10 ms; alternative route computed instantly; Landing Agent unaffected by ground emergency |

The document also identifies 8 additional historical incidents for future analysis, including Tenerife (1977), Comair 5191 (2006), and the JFK near-miss (2023).

---

## 23. Local / Air-Gapped Model Stack

### Hard Requirement

All models run locally. No internet dependency. LAN-only core system. Possibly air-gapped to prevent external security threats. Updates delivered via signed physical media or secure transfer.

### Why Not Cloud LLMs

- Unpredictable latency (cloud inference: 500ms-3s; local: <40ms)
- WAN connection failures are unacceptable for safety-critical systems
- Unpredictable load on shared infrastructure
- No control over model updates or behavior changes
- Security surface area of internet-connected safety-critical system

### Speech-to-Text (STT) — Decode Pilot Radio

| Model | Params | Speed | Role |
|---|---|---|---|
| **Parakeet TDT 1.1B** | 1.1B | >2000x real-time | Primary — lowest latency streaming |
| **Whisper Large V3 Turbo** | 809M | 6x faster than V3 | Verification/backup — best accuracy |
| **Vosk** | ~50M | Real-time on CPU | Emergency fallback — runs on anything |

### Text-to-Speech (TTS) — Issue Verbal Clearances

| Model | Params | Role |
|---|---|---|
| **Kokoro v1.0** | 82M | Primary — best quality, Apache 2.0 |
| **Piper** | ~20M | Fallback — runs on Raspberry Pi |

ATC phraseology is highly structured. The TTS model should be fine-tuned for crisp, unambiguous, consistent ATC pronunciation — not conversational naturalness.

### NLP / Intent Classification — Parse Pilot Requests

A 1-3B parameter model fine-tuned on ATC transcripts. Pilot communications follow structured patterns:

```
"Tower, Delta 456, 10 miles out, request ILS runway 4 left"
→ {type: "approach_request", callsign: "DAL456", distance: 10,
   approach: "ILS", runway: "04L"}
```

Does not need a frontier model. Needs a narrow, reliable, fast model.

### Reasoning / Decision Agents — Core ATC Logic

Recommended: **Hybrid architecture** within each task agent:
- **Rule engine** handles 95% of routine operations (formally certifiable)
- **RL policy** handles conflict resolution optimization
- **LLM component** (7-8B, fine-tuned) handles natural-language understanding and novel situation assessment
- Each layer has clear boundaries and failure modes

### Collision / Vector Analysis — NOT an LLM

Pure deterministic math: trajectory extrapolation, closest-point-of-approach, time-to-conflict, geometric separation verification. Provably correct algorithms. Using an LLM here would be inappropriate.

### Hardware

| Unit | Role | Count |
|---|---|---|
| NVIDIA DGX Spark (or equivalent) | Primary inference cluster | 3 (hot standby) |
| Standard server | Orchestration, logging, rule engines | 2 (active-active) |
| Embedded GPU system | Safety net algorithms (independent) | 2 |
| Rack-mount NAS | Flight data recording, model weights | 2 (RAID + replication) |
| Network switches | Air-gapped LAN | Redundant pair |
| ADS-B receivers | Surveillance input | 3+ (diversity, MLAT) |
| Radio interface | VHF receive + transmit | Redundant pair |
| UPS + generator | Power resilience | Required |

Total footprint: single standard 42U rack. Estimated compute cost: $150-300K. Trivial compared to the $32.5B BNATCS program.

---

## 24. Full System Architecture Diagram

```
                    ┌─────────────────────────┐
                    │   SURVEILLANCE INPUTS    │
                    │ ADS-B | Radar | MLAT     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    DATA FUSION LAYER     │
                    │  (Deterministic — ASTERIX│
                    │   format, multi-source   │
                    │   correlation, dedup)    │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                   │
    ┌─────────▼────────┐ ┌──────▼──────┐ ┌─────────▼────────┐
    │  TIER 1: LLM     │ │  TIER 2:    │ │  SAFETY NETS     │
    │  AGENTS          │ │  DETERM.    │ │  (Independent HW) │
    │                  │ │  SYSTEMS    │ │                   │
    │ • Initial contact│ │             │ │ • Collision vector│
    │ • Sequencing est.│ │ • Approach  │ │ • Separation mon. │
    │ • Weather/ATIS   │ │ • Landing   │ │ • Runway incursion│
    │ • Monitoring     │ │ • Departure │ │ • Conformance     │
    │ • Anomaly detect │ │ • Ground    │ │ • Terrain (MSAW)  │
    │                  │ │ • Separation│ │                   │
    │  ◄── watches ──► │ │             │ │  HAS VETO POWER   │
    │  Tier 2 output   │ │             │ │  over ALL tiers   │
    └────────┬─────────┘ └──────┬──────┘ └─────────┬────────┘
             │                  │                   │
             └──────────────────┼───────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   ORCHESTRATION       │
                    │  • Consensus checking │
                    │  • Escalation logic   │
                    │  • System health      │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   HUMAN INTERFACE     │
                    │  • Overwatcher display│
                    │  • Emergency panels   │
                    │  • Override controls  │
                    └───────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                                   │
    ┌─────────▼─────────┐             ┌───────────▼──────────┐
    │    STT PIPELINE   │             │    TTS PIPELINE      │
    │ Pilot voice → text│             │ Clearance → voice    │
    │ (Parakeet/Whisper)│             │ (Kokoro/Piper)       │
    └───────────────────┘             └──────────────────────┘
```

**Normal landing flow:** LLM handles initial contact → Deterministic system takes over for approach/landing clearances → LLM monitors output → Safety nets watch everything on independent hardware → Human overwatcher reviews consolidated picture.

**Emergency flow:** Pilot says "Mayday" → STT catches keyword → Orchestrator escalates to Tier 3 → Human gets full emergency panel → AI assistants pull aircraft data, compute diverts, reroute traffic → Human approves/modifies → TTS transmits.

---

## 25. Complete Pilot-ATC Communication Protocol: Gate to Gate

This section documents **every** radio communication between pilots and ATC for a complete IFR commercial flight. This serves as the definitive specification for the NLP intent parser, STT/TTS pipeline, and the communication state machine in the automated system.

### Reference Flight: Delta 456, Atlanta (KATL) → New York JFK (KJFK)

| Element | Value |
|---|---|
| **Callsign** | Delta 456 (DAL456) |
| **Aircraft** | Boeing 737-900ER |
| **Departure Runway** | KATL Runway 8R |
| **SID** | RPTOR THREE Departure |
| **Cruise Altitude** | FL370 |
| **Route** | RPTOR3.RPTOR BEAVY J209 SBV J230 RBV LENDY6 |
| **STAR** | LENDY SIX Arrival |
| **Approach** | ILS Runway 22L |
| **Arrival Runway** | KJFK Runway 22L |
| **Squawk** | 4537 |
| **ATIS (ATL)** | Information Kilo |
| **ATIS (JFK)** | Information Papa |

### Frequency Sequence (Full Flight)

| Phase | Facility | Frequency |
|---|---|---|
| ATIS (ATL) | KATL ATIS | 125.32 |
| Clearance Delivery | ATL Clearance (or PDC/DataComm) | 121.65 |
| Ground (Departure) | ATL Ground South | 121.90 |
| Tower (Departure) | ATL Tower South | 119.10 |
| Departure | Atlanta TRACON Departure | 125.70 |
| Center | Atlanta Center (ZTL) Sector | 132.35 |
| Center | Atlanta Center (ZTL) Sector 2 (possible) | 127.95 |
| Center | Washington Center (ZDC) | 134.75 |
| Center | New York Center (ZNY) (possible) | 128.70 |
| Approach | New York TRACON (N90) — JFK Arrivals | 125.72 |
| Tower (Arrival) | JFK Tower | 119.10 |
| Ground (Arrival) | JFK Ground | 121.90 |
| ATIS (JFK) | KJFK ATIS | 128.72 |

**Total frequency changes: approximately 8-12** depending on sector splits.

---

### PHASE 1: Pre-Departure at the Gate

#### 1A. ATIS (Automatic Terminal Information Service)

**Freq: 125.32** | **One-way broadcast — no pilot transmission**

Pilot listens (or receives via ACARS D-ATIS):

> *"Atlanta Hartsfield-Jackson International Airport, information Kilo. Two one five three Zulu. Wind zero eight zero at one two. Visibility one zero. Few clouds at four thousand five hundred. Temperature two two, dewpoint one five. Altimeter two niner niner two. ILS approaches in use. Departing runways eight left and eight right. Arriving runways two six left and two seven right. NOTAM: Taxiway Mike between taxiway Alpha and taxiway Bravo closed. Advise on initial contact you have information Kilo."*

No readback. Crew sets altimeter, notes runways and NOTAMs.

#### 1B. Clearance Delivery (PDC / Voice)

**Freq: 121.65** | **Pilot initiates**

**Modern (PDC/DataComm — the norm at major airports in 2026):**

Clearance delivered digitally via ACARS or CPDLC-DCL. No voice call needed:

```
DAL456 CLRD TO KJFK VIA RPTOR3 DEPARTURE THEN AS FILED.
MAINTAIN FL370. SQUAWK 4537. DEPARTURE FREQ 125.70.
EXPECT RUNWAY 8R. INFORMATION KILO CURRENT.
PDC RECEIVED AT 2158Z. READ BACK NOT REQUIRED ON FREQ.
CONTACT GROUND 121.90 WHEN READY TO PUSH.
```

Crew loads SID into FMS, sets squawk, sends WILCO via ACARS/CPDLC.

**Voice fallback (or if PDC needs amendment):**

> **Pilot:** *"Atlanta Clearance, Delta four fifty-six, gate Bravo thirty-two, IFR to Kennedy, with information Kilo."*
>
> **Controller:** *"Delta four fifty-six, Atlanta Clearance, cleared to John F. Kennedy International Airport via the RPTOR Three departure, then as filed. Maintain flight level three seven zero. Departure frequency one two five point seven zero. Squawk four five three seven."*
>
> **Pilot (readback — MANDATORY, full CRAFT format):** *"Cleared to Kennedy via the RPTOR Three departure, then as filed. Maintain flight level three seven zero. Departure frequency one two five point seven zero. Squawk four five three seven. Delta four fifty-six."*

**CRAFT readback format:** **C**learance limit, **R**oute, **A**ltitude, **F**requency, **T**ransponder.

If readback error: Controller says *"Readback incorrect"* and restates the erroneous element. Pilot must correctly read back.

---

### PHASE 2: Ground Control — Pushback and Taxi

#### 2A. Pushback

**Freq: 121.90 (ATL Ground South)** | **Pilot initiates**

Note: At major airports (ATL, ORD, DFW), a separate **ramp control** (non-FAA, airline/airport operated) may handle pushback on a company frequency. After pushback, ramp hands off to FAA ground control. At airports without separate ramp, ground control handles pushback directly.

> **Pilot:** *"Atlanta Ground, Delta four fifty-six, gate Bravo thirty-two, request pushback, information Kilo."*
>
> **Controller:** *"Delta four fifty-six, Atlanta Ground, runway eight right, pushback approved, tail north, expect taxiway Bravo."*
>
> **Pilot:** *"Pushback approved, tail north, Delta four fifty-six."*

Readback: pushback clearance, tail direction, runway assignment.

#### 2B. Taxi Clearance

**Freq: 121.90** | **Pilot calls when pushback complete**

> **Pilot:** *"Atlanta Ground, Delta four fifty-six, pushback complete, ready to taxi."*
>
> **Controller:** *"Delta four fifty-six, runway eight right, taxi via Bravo, Bravo three, Mike."*
>
> **Pilot (readback — MANDATORY):** *"Runway eight right, taxi via Bravo, Bravo three, Mike, Delta four fifty-six."*

Must read back: runway assignment and full taxi route.

#### 2C. Runway Crossing During Taxi

Explicit clearance **always required** to cross any runway (per 7110.65 post-2007):

> **Controller:** *"Delta four fifty-six, cross runway two six left."*
>
> **Pilot:** *"Cross runway two six left, Delta four fifty-six."*

Or hold short:

> **Controller:** *"Delta four fifty-six, hold short of runway two six left, traffic a seven thirty-seven on short final."*
>
> **Pilot:** *"Hold short runway two six left, Delta four fifty-six."*

**Hold-short instructions are ALWAYS read back. Failure to read back is a serious event.** Controller must receive correct readback before considering it acknowledged.

---

### PHASE 3: Tower / Local Control — Takeoff

#### 3A. Handoff from Ground to Tower

**Ground controller initiates the frequency change:**

> **Ground:** *"Delta four fifty-six, contact tower one one niner point one."*
>
> **Pilot:** *"Tower one one niner point one, Delta four fifty-six."*

#### 3B. Check-in with Tower

**Freq: 119.10 (ATL Tower South)** | **Pilot initiates**

> **Pilot:** *"Atlanta Tower, Delta four fifty-six, runway eight right, ready for departure."*

Note: The word "takeoff" is **never used** except in the actual takeoff clearance. "Ready for departure" is the correct phrasing.

#### 3C. Line Up and Wait (if needed)

> **Controller:** *"Delta four fifty-six, runway eight right, line up and wait."*
>
> **Pilot:** *"Line up and wait, runway eight right, Delta four fifty-six."*

Aircraft taxis onto runway, aligns with centerline, holds position.

#### 3D. Takeoff Clearance

> **Controller:** *"Delta four fifty-six, wind zero niner zero at one four, runway eight right, cleared for takeoff."*
>
> **Pilot:** *"Cleared for takeoff, runway eight right, Delta four fifty-six."*

Must read back: "Cleared for takeoff" and runway. Wind is advisory — no readback required.

If includes a heading:

> **Controller:** *"Delta four fifty-six, fly heading one zero zero, runway eight right, cleared for takeoff."*
>
> **Pilot:** *"Heading one zero zero, cleared for takeoff runway eight right, Delta four fifty-six."*

#### 3E. Handoff to Departure

After liftoff (typically seconds to one minute at ATL):

> **Tower:** *"Delta four fifty-six, contact Atlanta Departure one two five point seven zero."*
>
> **Pilot:** *"Departure one two five point seven zero, Delta four fifty-six."*

---

### PHASE 4: Departure Control (TRACON)

#### 4A. Initial Check-in

**Freq: 125.70 (Atlanta TRACON Departure)** | **Pilot initiates**

> **Pilot:** *"Atlanta Departure, Delta four fifty-six, two thousand three hundred, climbing five thousand, runway heading."*
>
> **Controller:** *"Delta four fifty-six, Atlanta Departure, radar contact, climb and maintain flight level two four zero."*
>
> **Pilot:** *"Climb and maintain flight level two four zero, Delta four fifty-six."*

"Radar contact" = informational, no readback. Altitude = ALWAYS read back.

#### 4B. Step Climbs

> **Controller:** *"Delta four fifty-six, climb and maintain flight level two four zero, expect flight level three seven zero within one zero minutes."*
>
> **Pilot:** *"Climb and maintain flight level two four zero, expect flight level three seven zero within one zero minutes, Delta four fifty-six."*

The "expect" altitude is critical for lost-communications planning (14 CFR 91.185).

#### 4C. Speed Restrictions

> **Controller:** *"Delta four fifty-six, maintain two five zero knots."*
>
> **Pilot:** *"Maintain two five zero knots, Delta four fifty-six."*

Speed assignments always read back. 250-knot limit below 10,000 ft (14 CFR 91.117) applies unless ATC assigns otherwise.

#### 4D. Vectors

> **Controller:** *"Delta four fifty-six, turn right heading one two zero, vectors for traffic."*
>
> **Pilot:** *"Right heading one two zero, Delta four fifty-six."*

Heading = read back. Reason ("vectors for traffic") = advisory, no readback.

#### 4E. Handoff to Center

> **Controller:** *"Delta four fifty-six, contact Atlanta Center one three two point three five."*
>
> **Pilot:** *"Atlanta Center one three two point three five, Delta four fifty-six."*

---

### PHASE 5: Center (ARTCC) — En Route

#### 5A. Check-in with Atlanta Center (ZTL)

**Freq: 132.35 (ZTL Sector 25 High)** | **Pilot initiates**

> **Pilot:** *"Atlanta Center, Delta four fifty-six, flight level two four zero, climbing flight level three seven zero."*
>
> **Controller:** *"Delta four fifty-six, Atlanta Center, roger. Climb and maintain flight level three seven zero."*
>
> **Pilot:** *"Flight level three seven zero, Delta four fifty-six."*

#### 5B. Reaching Cruise Altitude

Under radar contact in domestic airspace, **no level-off report required** (AIM 5-3-2). Controller sees it on radar. Some crews report as courtesy:

> **Pilot:** *"Atlanta Center, Delta four fifty-six, level flight level three seven zero."*
>
> **Controller:** *"Delta four fifty-six, roger."*

#### 5C. Pilot Requests Altitude Change

> **Pilot:** *"Atlanta Center, Delta four fifty-six, request flight level three niner zero."*
>
> **Controller:** *"Delta four fifty-six, climb and maintain flight level three niner zero."*
>
> **Pilot:** *"Climb and maintain flight level three niner zero, Delta four fifty-six."*

If denied:

> **Controller:** *"Delta four fifty-six, unable flight level three niner zero due traffic. Expect higher in two zero miles."*
>
> **Pilot:** *"Roger, expect higher in two zero miles, Delta four fifty-six."*

#### 5D. Direct Routing Request

> **Pilot:** *"Atlanta Center, Delta four fifty-six, request direct BEAVY."*
>
> **Controller:** *"Delta four fifty-six, cleared direct BEAVY, rest of route unchanged."*
>
> **Pilot:** *"Cleared direct BEAVY, Delta four fifty-six."*

#### 5E. Weather Deviation

> **Pilot:** *"Atlanta Center, Delta four fifty-six, we have weather ahead on our radar. Request deviation right of course, two zero miles."*
>
> **Controller:** *"Delta four fifty-six, deviation right of course approved. Report clear of weather."*
>
> **Pilot:** *"Deviation right of course approved. We'll report clear of weather. Delta four fifty-six."*

When clear:

> **Pilot:** *"Atlanta Center, Delta four fifty-six, clear of weather, request direct BEAVY."*
>
> **Controller:** *"Delta four fifty-six, cleared direct BEAVY."*
>
> **Pilot:** *"Cleared direct BEAVY, Delta four fifty-six."*

If unable to approve the direction:

> **Controller:** *"Delta four fifty-six, unable deviation right due traffic. Deviation left of course approved, or I can offer flight level three one zero."*

#### 5F. Traffic Advisory

> **Controller:** *"Delta four fifty-six, traffic twelve o'clock, one five miles, opposite direction, a Boeing seven thirty-seven, flight level three six zero."*
>
> **Pilot:** *"Looking for traffic, Delta four fifty-six."* (or) *"Traffic in sight, Delta four fifty-six."*

Advisory — no readback required. Response is customary.

#### 5G. TCAS Resolution Advisory

If TCAS issues an RA (e.g., "CLIMB, CLIMB"):

> **Pilot:** *"Atlanta Center, Delta four fifty-six, TCAS RA, climbing."*
>
> **Controller:** *"Delta four fifty-six, roger."*

**Pilot MUST comply with TCAS RA even if it contradicts ATC** (14 CFR 91.123(b)). Controller does not countermand. When resolved:

> **Pilot:** *"Atlanta Center, Delta four fifty-six, clear of conflict, returning to flight level three seven zero."*
>
> **Controller:** *"Delta four fifty-six, roger, climb and maintain flight level three seven zero."*

#### 5H. Transponder Ident

> **Controller:** *"Delta four fifty-six, squawk ident."*
>
> **Pilot:** *"Ident, Delta four fifty-six."* (presses IDENT button)

Squawk code change:

> **Controller:** *"Delta four fifty-six, squawk five two three one."*
>
> **Pilot:** *"Squawk five two three one, Delta four fifty-six."*

Squawk codes always read back.

#### 5I. Turbulence Reports (PIREPs)

Controller solicits:

> **Controller:** *"Delta four fifty-six, say ride conditions."*
>
> **Pilot:** *"Delta four fifty-six, moderate chop at flight level three seven zero, continuous for the last fifty miles."*

Controller relays:

> **Controller:** *"JetBlue 912, pilot reports from a 737, moderate turbulence flight level 350, 20 miles ahead of your position. A 757 reported smooth at 310."*

#### 5J. CPDLC/DataComm En Route

Typical CPDLC messages (supplementing or replacing voice):

| Direction | Message | Response |
|---|---|---|
| Uplink (ATC→pilot) | CLIMB TO AND MAINTAIN FL390 | WILCO |
| Uplink | PROCEED DIRECT TO BEAVY | WILCO |
| Uplink | CONTACT WASHINGTON CENTER 134.75 | WILCO |
| Downlink (pilot→ATC) | REQUEST FL390 | Controller issues clearance or UNABLE |

When CPDLC is used, voice readback is **not required** — WILCO serves as acknowledgment. CPDLC is **never** used for time-critical instructions (TCAS, immediate turns, go-arounds).

---

### PHASE 6: Center Handoffs (En Route)

#### 6A. Atlanta Center (ZTL) → Washington Center (ZDC)

> **Controller (ZTL):** *"Delta four fifty-six, contact Washington Center one three four point seven five."*
>
> **Pilot:** *"Washington Center one three four point seven five, Delta four fifty-six. Good day."*

Pilot switches frequency:

> **Pilot:** *"Washington Center, Delta four fifty-six, flight level three seven zero."*
>
> **Controller (ZDC):** *"Delta four fifty-six, Washington Center, roger. Altimeter two niner eight six."*
>
> **Pilot:** *"Two niner eight six, Delta four fifty-six."*

Note: Above FL180, altimeter stays on 29.92. Controller provides local altimeter for awareness/anticipation of descent.

#### 6B. Subsequent Handoffs

Each follows the identical pattern: controller issues frequency → pilot reads back frequency → pilot checks in on new frequency with callsign + altitude → new controller acknowledges. May repeat 2-3 times crossing center boundaries (ZTL → ZDC → possibly ZNY → N90).

---

### PHASE 7: Approach Control (Arrival TRACON)

#### 7A. JFK ATIS

**Freq: 128.72** | Crew listens before contacting approach:

> *"John F. Kennedy International Airport, information Papa. Zero one five three Zulu. Wind two one zero at one six, gusts two two. Visibility seven. Broken clouds at three thousand five hundred. Temperature one four, dewpoint zero eight. Altimeter three zero zero five. ILS runway two two left approaches in use. Landing runway two two left and two two right. Departing runway three one left. NOTAM: Taxiway Juliet between Alpha and Bravo closed. Advise on initial contact you have information Papa."*

#### 7B. Descent from Center

Still on Center frequency:

> **Controller:** *"Delta four fifty-six, descend via the LENDY Six arrival."*
>
> **Pilot:** *"Descend via the LENDY Six arrival, Delta four fifty-six."*

"Descend via" = comply with all published altitude/speed restrictions on the STAR. Always read back.

With amendment:

> **Controller:** *"Delta four fifty-six, descend via the LENDY Six arrival except cross BOTON at and maintain one two thousand."*
>
> **Pilot:** *"Descend via the LENDY Six except cross BOTON at and maintain one two thousand, Delta four fifty-six."*

#### 7C. Handoff to New York TRACON (N90)

> **Controller:** *"Delta four fifty-six, contact New York Approach one two five point seven two."*
>
> **Pilot:** *"Approach one two five point seven two, Delta four fifty-six."*

#### 7D. Check-in with Approach

**Freq: 125.72 (N90 JFK Arrivals)** | **Pilot initiates — includes ATIS letter**

> **Pilot:** *"New York Approach, Delta four fifty-six, one three thousand, descending one one thousand on the LENDY Six, information Papa."*
>
> **Controller:** *"Delta four fifty-six, New York Approach, expect ILS runway two two left approach. Descend and maintain four thousand."*
>
> **Pilot:** *"Descend and maintain four thousand, expect ILS two two left, Delta four fifty-six."*

"Expect" approach = informational, no readback required. Altitude = MUST read back.

#### 7E. Vectors and Speed Control

> **Controller:** *"Delta four fifty-six, turn left heading one eight zero."*
>
> **Pilot:** *"Left heading one eight zero, Delta four fifty-six."*

> **Controller:** *"Delta four fifty-six, reduce speed to two one zero."*
>
> **Pilot:** *"Speed two one zero, Delta four fifty-six."*

> **Controller:** *"Delta four fifty-six, reduce speed to one seven zero."*
>
> **Pilot:** *"Speed one seven zero, Delta four fifty-six."*

All speed, heading, altitude assignments read back.

#### 7F. Approach Clearance

> **Controller:** *"Delta four fifty-six, four miles from ZALPO, turn right heading two one zero, maintain two thousand until established on the localizer, cleared ILS runway two two left approach."*
>
> **Pilot:** *"Right heading two one zero, maintain two thousand until established, cleared ILS runway two two left approach, Delta four fifty-six."*

**Critical readback:** heading, altitude restriction, "cleared ILS runway 22L approach." The distance from ZALPO is advisory.

Once established on the approach, the aircraft descends on the glideslope. No further descent clearance needed — the approach clearance authorizes it.

#### 7G. Handoff to Tower

> **Controller:** *"Delta four fifty-six, contact Kennedy Tower one one niner point one."*
>
> **Pilot:** *"Tower one one niner point one, Delta four fifty-six."*

---

### PHASE 8: Tower — Landing

#### 8A. Check-in with JFK Tower

**Freq: 119.10 (JFK Tower)** | **Pilot initiates**

> **Pilot:** *"Kennedy Tower, Delta four fifty-six, ILS two two left."*
>
> **Controller:** *"Delta four fifty-six, Kennedy Tower, wind two two zero at one five, runway two two left, cleared to land."*
>
> **Pilot:** *"Cleared to land, runway two two left, Delta four fifty-six."*

Must read back: "Cleared to land" and runway. Wind is advisory.

If runway occupied:

> **Controller:** *"Delta four fifty-six, Kennedy Tower, continue approach, runway two two left."*

Then when clear:

> **Controller:** *"Delta four fifty-six, runway two two left, cleared to land."*

#### 8B. Go-Around (if needed)

Controller-initiated:

> **Controller:** *"Delta four fifty-six, go around, fly runway heading, climb and maintain two thousand."*
>
> **Pilot:** *"Going around, runway heading, climb two thousand, Delta four fifty-six."*

Pilot-initiated:

> **Pilot:** *"Kennedy Tower, Delta four fifty-six, going around."*
>
> **Controller:** *"Delta four fifty-six, roger, fly runway heading, climb and maintain two thousand, contact Approach one two five point seven two."*

#### 8C. Runway Exit

> **Controller:** *"Delta four fifty-six, exit right on Bravo, contact Ground one two one point nine."*
>
> **Pilot:** *"Right on Bravo, Ground one two one point nine, Delta four fifty-six."*

**Pilot MUST remain on Tower frequency until explicitly told to contact Ground.**

---

### PHASE 9: Ground Control — Taxi to Gate

#### 9A. Contact JFK Ground

**Freq: 121.90 (JFK Ground)** | **Pilot initiates**

> **Pilot:** *"Kennedy Ground, Delta four fifty-six, runway two two left, off at Bravo, taxi to Terminal Four."*
>
> **Controller:** *"Delta four fifty-six, Kennedy Ground, taxi to Terminal Four gate Bravo twenty-one via Bravo, Alpha, Alpha three."*
>
> **Pilot:** *"Taxi to Terminal Four via Bravo, Alpha, Alpha three, Delta four fifty-six."*

#### 9B. Runway Crossing (if needed during taxi-in)

> **Controller:** *"Delta four fifty-six, hold short of runway three one left."*
>
> **Pilot:** *"Hold short runway three one left, Delta four fifty-six."*

When cleared:

> **Controller:** *"Delta four fifty-six, cross runway three one left."*
>
> **Pilot:** *"Cross runway three one left, Delta four fifty-six."*

#### 9C. At Gate

Aircraft guided by marshallers or VDGS. IFR flight plan closes automatically at towered airports. Optional:

> **Pilot:** *"Kennedy Ground, Delta four fifty-six is at the gate."*
>
> **Controller:** *"Delta four fifty-six, roger. Good day."*

---

### Readback Rules Summary

| Item | Readback Required? |
|---|---|
| IFR clearance (CRAFT) | **YES — full readback** |
| Runway assignment | **YES** |
| Taxi route | **YES** |
| Hold-short instructions | **YES — mandatory** |
| Runway crossing clearance | **YES** |
| Altitude assignments | **YES** |
| Heading assignments | **YES** |
| Speed assignments | **YES** |
| Approach clearance | **YES** |
| Takeoff clearance | **YES** |
| Landing clearance | **YES** |
| Squawk code | **YES** |
| Frequency changes | **YES** (frequency + callsign) |
| Altimeter setting | **YES** (per AIM 4-2-3) |
| "Descend via" / "Climb via" | **YES** |
| Traffic advisories | No — respond "looking/traffic in sight/negative contact" |
| Wind reports | No — advisory |
| "Radar contact" | No — acknowledgment only |
| ATIS information | No — one-way broadcast |
| "Expect" instructions | No (note for lost-comm planning) |

---

### Non-Standard and Edge-Case Communications

#### Holding Instructions

Full format: fix, radial/course, turn direction, leg length, EFC time.

> **Controller:** *"American 341, hold east of the DIRTY intersection on the 090 radial, right turns, expect further clearance at 1835 Zulu. Maintain flight level 350."*
>
> **Pilot:** *"Hold east of DIRTY on the 090 radial, right turns, expect further clearance 1835Z, maintain flight level 350, American 341."*

Published hold (abbreviated):

> **Controller:** *"Delta 589, hold as published at CIGEN, expect further clearance at 2015 Zulu, maintain 11,000."*

#### Amended Route Clearances

> **Controller:** *"Amendment to your route clearance. Advise when ready to copy."*
>
> **Pilot:** *"Ready to copy, Delta 1150."*
>
> **Controller:** *"Delta 1150, cleared to Chicago O'Hare via direct WATSN, J64 PLTKA, then the WATSN3 arrival. Rest of route unchanged. Read back."*
>
> **Pilot:** *"Cleared to O'Hare via direct WATSN, J64 PLTKA, WATSN3 arrival, Delta 1150."*
>
> **Controller:** *"Readback correct."*

#### Visual Approach

> **Pilot:** *"Approach, Delta 455, airport in sight, request visual approach runway 27L."*
>
> **Controller:** *"Delta 455, cleared visual approach runway 27L."*

Following traffic:

> **Controller:** *"United 302, traffic 12 o'clock, 5 miles, a 737 on final for 27L. Report that traffic in sight."*
>
> **Pilot:** *"Traffic in sight, United 302."*
>
> **Controller:** *"United 302, cleared visual approach runway 27L, follow the 737. Maintain visual separation."*

#### Missed Approach

Pilot-initiated:

> **Pilot:** *"Tower, Delta 822, going missed approach."*
>
> **Tower:** *"Delta 822, roger, fly runway heading, climb and maintain 3,000, contact departure 124.3."*

Controller-initiated:

> **Tower:** *"American 919, go around! Traffic on the runway."*
>
> **Pilot:** *"Going around, American 919."*

#### Wake Turbulence Advisory

> **Tower:** *"Cessna 12345, caution wake turbulence, preceding aircraft was a Boeing 777 heavy. Runway 25R, cleared to land."*
>
> **Pilot:** *"Cleared to land runway 25R, caution wake turbulence, Cessna 12345."*

#### LAHSO (Land and Hold Short Operations)

> **Tower:** *"Southwest 632, runway 31L, cleared to land, hold short of runway 4R. Available landing distance 7,200 feet."*
>
> **Pilot:** *"Cleared to land 31L, hold short of runway 4R, Southwest 632."*

Pilot may decline:

> **Pilot:** *"Unable LAHSO, Southwest 632."*

#### Simultaneous Parallel Approaches

> **Controller:** *"American 443, expect simultaneous ILS approach to runway 28R. Traffic will be on a parallel ILS approach to runway 28L."*

For PRM (closely spaced parallels), a monitor controller may issue breakout:

> **PRM Monitor:** *"United 812, turn left heading 200 immediately! Traffic alert!"*

#### De-icing Coordination

> **Pilot:** *"Ground, United 537, de-ice complete, Type I and Type IV applied, holdover time expires at 1435 Zulu, ready to taxi."*

#### EDCT (Expected Departure Clearance Time)

> **Controller:** *"Delta 823, your EDCT is 1742 Zulu."*
>
> **Pilot:** *"EDCT 1742Z, Delta 823."*

Must be wheels-up within 5-minute window (2 min before to 3 min after).

#### Gate Hold / Ground Stop

> **Controller:** *"JetBlue 416, a gate hold is in effect. Hold your position at the gate, expect further clearance time 1645 Zulu."*

Ground stop (more restrictive):

> **Controller:** *"Southwest 2218, a ground stop is in effect for all traffic destined Las Vegas. No departure time currently available."*

#### Progressive Taxi (Unfamiliar Airport / Low Visibility)

> **Pilot:** *"Ground, Cessna 432AB, unfamiliar with the airport, request progressive taxi."*
>
> **Controller:** *"Cessna 432AB, progressive taxi instructions: turn left on Alpha, proceed to the second intersection, that will be Bravo, turn right on Bravo. Advise when on Bravo."*

---

### Emergency Communications

#### Declaring an Emergency

**Distress (MAYDAY — immediate danger):**

> **Pilot:** *"MAYDAY, MAYDAY, MAYDAY, Center, United 585 heavy, engine fire, number 2 engine, requesting immediate return to Denver, 132 souls on board, 42,000 pounds of fuel."*
>
> **Controller:** *"United 585 heavy, roger MAYDAY. Turn left heading 270, descend and maintain flight level 240, cleared direct Denver. Say intentions and assistance required."*

**Urgency (PAN-PAN — not immediate but needs priority):**

> **Pilot:** *"PAN-PAN, PAN-PAN, PAN-PAN, Approach, American 914, we have a pressurization problem, requesting immediate descent and vectors to the nearest suitable airport."*

**ATC will ask three things:** Souls on board, fuel remaining, nature of emergency.

#### Minimum Fuel Advisory (NOT an emergency)

> **Pilot:** *"Approach, Delta 823, minimum fuel."*
>
> **Controller:** *"Delta 823, roger minimum fuel."*

Does NOT provide priority. If situation worsens:

> **Pilot:** *"Approach, Delta 823, correction, we are now declaring a fuel emergency."*

#### NORDO (Loss of Communications — Squawk 7600)

Pilot follows **A-V-E-F** rule: fly the highest of Assigned, Vectored, Expected, or Filed route/altitude.

ATC attempts:

> **Controller:** *"American 711, if you read, squawk ident."*
> (no response)
> **Controller:** *"American 711, if you read center, turn left heading 270."*
> (no turn observed)
> **Controller:** *"All aircraft, NORDO aircraft American 711, a Boeing 737, flight level 350 vicinity CIGEN intersection, heading east."*

#### Medical Emergency

> **Pilot:** *"Center, Southwest 1802, we have a medical emergency on board. Passenger experiencing chest pains and is unresponsive. We need to divert to the nearest suitable airport."*
>
> **Controller:** *"Southwest 1802, roger, medical emergency. Memphis is at your 1 o'clock, 45 miles. Turn right heading 120, descend and maintain flight level 240. Do you need equipment standing by?"*
>
> **Pilot:** *"Affirmative, request paramedics. Right heading 120, down to FL240, Southwest 1802."*

#### Pilot Incapacitation

> **Pilot (FO):** *"Center, United 447, the captain is incapacitated. I am the first officer and sole pilot. Declaring an emergency. Request immediate vectors to the nearest suitable airport. 185 souls, 4 hours fuel."*

---

### Oceanic / Non-Radar Communications

In non-radar oceanic airspace, CPDLC is primary and HF radio is backup. Position reports are mandatory.

**Position report format:** Identification, Position, Time, Altitude, Next fix + ETA, Following fix, Remarks.

> **Pilot:** *"Gander Radio, United 22 heavy, position 50 North 40 West at 1432, flight level 370, estimating 51 North 30 West at 1521, 52 North 20 West next. Mach .84, negative turbulence."*

**SELCAL** (so crews don't monitor noisy HF continuously):

> **Pilot:** *"Gander Radio, United 22 heavy, SELCAL check, code Alpha-Bravo Charlie-Delta."*
>
> **Radio:** *"United 22 heavy, SELCAL checks okay."*

---

### Automation Implications: Communication State Machine

Every communication above maps to a **state transition** in the automated system. The NLP intent parser must recognize:

| Message Category | Count of Distinct Types | Tier |
|---|---|---|
| Clearance delivery (initial) | ~5 variations | Tier 1 (LLM) |
| Ground/taxi instructions | ~10 variations | Tier 2 (Deterministic) |
| Takeoff/landing clearances | ~8 variations | Tier 2 (Deterministic) |
| En-route (altitude/heading/speed) | ~15 variations | Tier 1 or 2 depending on phase |
| Approach/sequencing | ~12 variations | Tier 2 (Deterministic) |
| Handoffs/frequency changes | ~3 variations | Tier 1 (LLM) |
| Traffic/weather advisories | ~8 variations | Tier 1 (LLM) |
| Emergency declarations | ~10 variations | Tier 3 (Human + AI) |
| Non-standard (holding, amended, LAHSO, etc.) | ~20 variations | Tier 1 or 3 |
| **Total distinct message types** | **~90** | |

The complete communication vocabulary is bounded and structured. This is not open-ended conversation — it is a **finite state protocol** with well-defined transitions, making it highly suitable for automated handling.

---

## 26. Physical & Software Architecture

This section addresses the complete implementation architecture: physical hardware, networking, geographic distribution, programming languages, database technologies, and data retention compliance.

---

### 26.1 Hardware Redundancy Patterns

Safety-critical systems use proven redundancy architectures. The two most relevant for ATC:

**Triple Modular Redundancy (TMR)** — Three independent processing channels perform the same computation in parallel; a majority voter selects the correct output (2-of-3 voting). If one channel fails, the remaining two mask the fault transparently. TMR is used in nuclear reactor protection systems, fly-by-wire flight control computers (A380, 787, F-35), and European rail signaling (CTCS-2/3).

**Dual-Channel Hot Standby** — Two functionally identical channels; one active, one hot standby. If the active channel fails, the standby takes over. This is what ERAM uses across all 20 ARTCCs, achieving **100% availability since October 2016**. STARS goes further with **quadruple redundancy** at the 11 Large TRACONs.

| Attribute | Hot Standby (ERAM) | TMR | Dual-Dual |
|---|---|---|---|
| Channels | 2 | 3 | 4 (2 pairs) |
| Fault masking | No (failover) | Yes (voting) | Partial (within pairs) |
| Failover time | Seconds | Zero (transparent) | Seconds |
| Resource utilization | ~50% | ~33% | ~50% |
| Complexity | Low | Medium | High |
| Best for | Ground ATC (proven) | Flight-critical (DAL-A) | Fail-operational |

**Recommendation**: Dual-channel hot standby for the overall system (ERAM precedent), with TMR for the deterministic safety nets (Collision Vector Monitor, Runway Incursion Monitor) where zero-interruption fault masking is required.

---

### 26.2 Geographic Separation

The 2014 Chicago Center (Aurora) fire is the definitive lesson. A deliberate arson fire caused full **ATC-Zero** at one of the busiest ARTCCs, forcing 19 adjacent facilities to absorb its airspace in an unplanned redistribution. Full restoration took **17 days**. The DOT OIG found FAA contingency plans were insufficient.

**FAA Requirements** (Order JO 1900.47F):
- Every facility must maintain an Operational Contingency Plan (OCP)
- Each facility must designate a **Primary Support Facility**
- Annual ATC-Zero exercises are mandatory

**Recommended Separation for the Automated System**:

| Tier | Location | Distance | Protects Against |
|---|---|---|---|
| **Primary** | Equipment room in/adjacent to ATCT/TRACON | — | Hardware failures |
| **Hot Standby** | Separate building, same airport campus | 300+ meters | Single-building events (fire, flood) |
| **Warm DR** | Off-airport facility | 20-50+ miles | Campus-level events, local disasters |

The primary and hot standby facilities must have **independent power feeds** (different utility transformers), independent cooling, and physically separate fiber paths. The warm DR site provides the facility-level contingency that co-located ERAM channels cannot.

Note: TRACON separation from tower is already standard FAA practice. Chicago TRACON (C90) is in Elgin, IL — 40 miles from O'Hare.

---

### 26.3 Network Architecture

**Fiber optic is mandatory** for inter-rack and inter-building links. Airport environments have significant EMI sources (radar transmitters, radio equipment, runway lighting, aircraft transponders). Fiber is immune to electromagnetic interference.

Two network technologies are relevant:

**AFDX (ARINC 664 Part 7)** — Aviation's proven deterministic network. Dual redundant physical networks (Net-A, Net-B); every end node transmits all traffic on both. Virtual Links provide guaranteed maximum bandwidth and bounded end-to-end latency. Frame relay: 123 microseconds for a 1,518-byte frame at 100 Mb/s. Deployed on A380, A350, 787. Best for interfacing with existing NAS/avionics equipment.

**TSN (IEEE 802.1 Time-Sensitive Networking)** — The emerging standard for ground-based deterministic Ethernet. Guaranteed packet transport with bounded latency, sub-microsecond time synchronization via IEEE 1588/802.1AS. Runs on standard Ethernet hardware. Joint IEC/IEEE standard for industrial automation. Better suited for new ground systems than AFDX.

**Latency Requirements** (FAA Human Factors research):
| Path | Acceptable Latency | Notes |
|---|---|---|
| Voice communications | < 280 ms | 400+ ms unsuitable; 750+ ms causes controller override issues |
| Analog voice (current) | ~70 ms | Baseline |
| Radar data processing | < 100 ms | Internal system latency |
| AI agent decision cycle | < 40 ms | For deterministic safety path |
| ML inference (advisory) | 50-200 ms | Non-safety-critical, can run async |

**Recommended Configuration**:
- Dual redundant fiber optic backbone between all racks and facilities
- TSN switches with PTP support for deterministic bounded-latency
- AFDX-compatible interfaces where NAS integration is needed
- 10 GbE minimum per node (DGX Spark provides 10 GbE + dual QSFP 200 Gbps)
- Sub-second automatic failover on network path failure

---

### 26.4 Hardware Estimate: DGX Spark Deployment

The NVIDIA DGX Spark is the target inference platform — a desktop-sized unit with 128 GB unified memory and up to 1 petaFLOP FP4.

| DGX Spark Spec | Value |
|---|---|
| Processor | GB10 Grace Blackwell (20 CPU + Blackwell GPU) |
| Memory | 128 GB unified (CPU+GPU shared) |
| Peak power | 240W (typical ~160W under load, ~35W idle) |
| Dimensions | 150mm x 150mm x 50.5mm (5.9" x 5.9" x 2") |
| Network | 10 GbE RJ-45 + 2x QSFP ConnectX-7 (200 Gbps) |

**Agent-to-Hardware Mapping**:

| Agent Type | Count | Memory/Instance | Units Needed |
|---|---|---|---|
| STT (Whisper Large V3 Turbo) | 4-6 | ~3-4 GB FP16 | 1-2 (co-locate 3-4 per unit) |
| TTS (Kokoro/Piper) | 4-6 | ~2-4 GB | 1-2 (co-locate 3-4 per unit) |
| NLP / Intent Classification | 4-6 | ~4-8 GB | 2-3 |
| Reasoning / LLM (7-8B) | 6-8 | 14-20 GB | 4-6 (1-2 per unit) |
| Safety Nets (deterministic + ML) | 4-6 | ~8-20 GB | 3-4 |
| Supervisory / Orchestrator | 2-4 | ~4-8 GB | 1-2 |
| **Total (single set)** | **~30** | | **~15-20 units** |

**Redundancy Scaling**:

| Configuration | DGX Spark Units | Server Racks (42U) |
|---|---|---|
| Single set (no redundancy) | 15-20 | 1 |
| Dual-channel (ERAM-style) | 30-40 | 2 |
| TMR (safety nets only) + dual (rest) | 40-50 | 2-3 |
| Full TMR | 45-60 | 3-4 |
| + Dev/Test/Staging | +4-6 | +0.5 |

At 2 units per 2U (conservative density with airflow), a 42U rack holds ~32-36 DGX Sparks plus switches and PDUs.

---

### 26.5 Power and Cooling

**Power Budget** (Dual-channel, ~40 units):

| Component | Power |
|---|---|
| 40 DGX Spark @ 160W typical | 6.4 kW |
| 40 DGX Spark @ 240W peak | 9.6 kW |
| Networking / switching | 0.5-1.0 kW |
| Storage servers | 0.5 kW |
| Cooling overhead | 3-5 kW |
| Lighting / misc | 0.5 kW |
| **Total typical** | **~11-14 kW** |
| **Total peak** | **~16-20 kW** |

This is a modest power footprint. For context, a single modern AI training rack can draw 50+ kW.

**Cooling**: Air cooling is sufficient at these densities (7-13 kW/rack). Rear-door heat exchangers recommended for controlled-environment reliability. **2N cooling redundancy** (fully redundant cooling plant) — at least one additional CRAC/CRAH unit beyond what full load requires. Target operating temperature: 18-22C (64-72F).

**Power Redundancy** (2N — standard for safety-critical facilities):
- Two completely independent power distribution paths (Path A, Path B)
- Each path: Utility feed → ATS → Diesel generator → UPS → PDU → Rack
- UPS: Bridge generator startup (10-15 seconds), minimum 15 minutes runtime at full load (FAA requirement)
- Diesel generators: One per path, N+1 per path
- 2N achieves **99.995% power availability** (< 26.3 minutes downtime/year)

---

### 26.6 Physical Security and Environmental

**Lightning and Grounding** (FAA-STD-019f, mandatory):
- Earth Electrode Systems with low-impedance paths
- Surge protection on all power and signal entries
- ESD control in all equipment rooms
- Any deviation requires NAS Change Proposal (NCP) approval

**EMI Shielding**:
- Shielded enclosures or EMI-filtered power/signal entry points
- All inter-building cabling must be fiber optic (EMI immune) or shielded + surge-protected
- Airport EMI sources: radar transmitters, radio equipment, runway lighting, transponders

**Seismic Requirements** (FAA Order 6480.7E):
- ATCT/TRACON facilities comply with International Building Code (IBC)
- Classified as **IBC Occupancy Category III** (Essential Facilities) — must remain operational with minor repairs post-earthquake
- All equipment racks: seismic restraints (bolted to floor, braced top and bottom)

**Fire Suppression**:
- Clean-agent systems (FM-200 or Novec 1230) in equipment rooms — no water sprinklers near electronics
- The Aurora fire destroyed cabling infrastructure — fire compartmentalization between redundant channels is critical

**Access Control**:
- Badge + biometric for safety-critical equipment spaces
- CCTV monitoring of all equipment rooms
- Compartmentalization between Channel A and Channel B equipment — the Aurora incident showed a single insider can disable an entire co-located facility

---

### 26.7 Programming Languages

The system requires a **mixed-language architecture** matching language strengths to criticality levels.

#### Ada/SPARK — Deterministic Safety Core

Ada is the language of ERAM (~2 million lines, ~half in Ada). The SPARK subset enables **mathematical proof of absence of runtime errors** — buffer overflows, integer overflows, division by zero. Under DO-178C's formal methods supplement (DO-333), SPARK proofs can **replace certain categories of tests**, reducing verification costs by 20-50%.

- GNAT Pro toolchain qualified to DO-178C DAL A
- ERAM achieved 100% availability for a decade
- Built-in tasking model for real-time concurrency
- **Weakness**: Small developer talent pool concentrated in defense/aerospace contractors

#### Rust — High-Reliability Secondary Systems

Rust's ownership model enforces memory safety at compile time without a garbage collector, eliminating ~70% of critical CVEs found in C/C++ systems. In `no_std` mode, fully deterministic memory with no hidden allocations.

- **Ferrocene certified compiler**: ISO 26262 ASIL D, IEC 61508 SIL 3 (DO-178C DAL C in progress, not yet completed)
- RTIC framework for hardware-accelerated hard real-time scheduling
- Growing aerospace adoption (ESA investigations, NSA/CISA recommendation)
- **Weakness**: No completed DO-178C certification yet

#### C (MISRA C:2025) — Hardware Interfaces

C has the most extensive DO-178C certification track record worldwide. MISRA C:2025 provides 225 guidelines covering dangerous constructs. Use for driver-level code and existing C library interfaces. Minimize new C development.

#### Python — ML Inference and Monitoring

Strictly non-safety-critical. ONNX Runtime achieves ~20-25ms inference latency. Use for model serving, monitoring dashboards, offline analytics, prototyping. Communicates with safety-critical components via IPC boundaries only, never through direct FFI.

**Language Allocation**:

| System Layer | Language | Rationale |
|---|---|---|
| Safety nets (conflict detection, separation) | Ada/SPARK | Formal verification, DO-333 test replacement, DAL A pedigree |
| Communications, data fusion, IPC | Rust | Memory safety, performance, growing ecosystem |
| Hardware drivers, legacy interfaces | C (MISRA) | Closest to hardware, broadest driver support |
| ML inference, dashboards | Python + ONNX | Ecosystem maturity, non-safety-critical |

**Sub-40ms Decision Budget**:

| Component | Latency | Language |
|---|---|---|
| Radar data ingestion + parsing | 1-2 ms | C or Rust |
| Trajectory computation | 2-5 ms | Ada/SPARK or Rust |
| Conflict detection (deterministic) | 1-3 ms | Ada/SPARK or Rust |
| IPC between partitions | 0.1-1 ms | Rust/C (iceoryx2 or shared memory) |
| Display update + alert | 1-2 ms | Any compiled language |
| **Deterministic path total** | **~5-13 ms** | |
| ML advisory inference (async) | 15-25 ms | Python/ONNX Runtime |

All compiled languages comfortably meet the sub-40ms requirement. ML inference runs asynchronously in a separate partition as advisory (not safety-critical).

---

### 26.8 Real-Time Operating Systems

The system needs a **mixed RTOS architecture** with ARINC 653-style time/space partitioning:

| Partition Type | RTOS | Certification | Runs |
|---|---|---|---|
| Safety-critical (separation, conflict) | INTEGRITY-178 or VxWorks 653 | DO-178C DAL A | Ada/SPARK deterministic code |
| High-reliability (comms, data fusion) | VxWorks or QNX | DO-178C / IEC 61508 SIL 3 | Rust components |
| Non-critical (ML inference, monitoring) | Linux PREEMPT_RT | DO-178B Level D only | Python, ONNX, Redis |

**INTEGRITY-178** (Green Hills): First commercial RTOS certified to DO-178B Level A. Deployed on F-22, F-35, B-2, A380, 787. Separation kernel with hardware-enforced memory partitioning. Strongest pedigree for safety-critical avionics.

**VxWorks 653** (Wind River): ARINC 653-conformant with robust time and space partitioning. Certified DO-178C DAL A. 360+ customers, 600+ safety programs, 100+ aircraft types. Broadest industry adoption.

**QNX** (BlackBerry): Microkernel design — drivers and network stacks run in user-space, so a fault in one component cannot crash the kernel. Certified ISO 26262 ASIL D. Excellent fault isolation but lacks DO-178C DAL A certification.

**Linux PREEMPT_RT**: Only DO-178B Level D (lowest). Dominates for HMIs, data logging, and edge computing. Appropriate for non-safety-critical partitions only.

ARINC 653 partitioning ensures a crash in the Python/ML partition **cannot affect** the Ada/SPARK safety-critical partition. Hardware-enforced memory boundaries prevent any cross-partition interference.

---

### 26.9 Database Architecture

The system uses four database tiers, each optimized for its access pattern:

#### Tier 1: Real-Time State (Sub-Microsecond)

**POSIX Shared Memory** for the innermost loop: current aircraft positions, active runway assignments, immediate separation state. Ring buffer architecture delivers ~127 nanoseconds per message — nearly two orders of magnitude faster than any networked database.

**Redis** as a structured real-time cache: active clearances, ATIS, weather, agent decision queues, pub/sub event distribution. Sub-millisecond latency. Redis 7 with enhanced I/O: 72% throughput increase, up to 71% P99 latency reduction.

#### Tier 2: Surveillance Time-Series

**TimescaleDB** (PostgreSQL extension) for ADS-B and radar track data. Ingestion rate for 500 aircraft at 1Hz: ~24,500 data points/second — trivially handled. Key advantage: unifies time-series and relational data under PostgreSQL's ACID umbrella.

- **90-97% compression** (real production: 150 GB → 15 GB)
- Hypercore engine auto-converts row-based recent data to columnar format
- Full PostgreSQL query planner, indexes, and extensions (PostGIS for geospatial)

#### Tier 3: Graph (Conflict Detection)

**Memgraph** for real-time airspace relationship queries. In-memory, C++ native, sub-millisecond latency. 114x faster than Neo4j on expansion queries in benchmarks. Models: aircraft-to-aircraft separation, route conflicts, taxiway connectivity, clearance assignments. OpenCypher query language.

#### Tier 4: Operational Records (ACID)

**PostgreSQL** for flight plans, clearances, agent decisions, audit trails. Full ACID compliance, mature synchronous replication (RPO=0), extensive certification experience in government systems.

Extensions: PostGIS (geospatial), pg_partman (automated retention), pgAudit (compliance logging).

**Replication Architecture**:

```
Primary Site (Tower/TRACON)
├── PostgreSQL Primary
│   ├── Standby #1 (synchronous, same facility, RPO=0)
│   └── Standby #2 (synchronous, same facility, RPO=0)
├── Redis Primary → Redis Replica (failover)
└── Memgraph Primary → Memgraph Replica

Remote Site (Backup Facility)
├── PostgreSQL Standby #3 (asynchronous, RPO=seconds)
└── WAL archiving to cold storage
```

Selective synchronous commit: use synchronous mode for safety-critical tables (clearances, audit logs); asynchronous for bulk surveillance data (the next ADS-B update arrives in 1 second anyway).

---

### 26.10 Data Formats

| Format | Type | Purpose | Storage Strategy |
|---|---|---|---|
| **ASTERIX** (EUROCONTROL) | Binary, variable-length | Surveillance data exchange (CAT048 radar, CAT062 tracks, CAT021 ADS-B) | Store raw binary with indexed metadata; parallel parsed columnar for analytics |
| **FIXM** 4.3.0 | XML (XSD schemas) | Flight plan exchange, FF-ICE messages | Store canonical XML for compliance; Avro binary for queries |
| **AIXM** | XML/GML | Aeronautical features (airports, runways, airspace, navaids) | Import into PostGIS; store original XML for compliance |

ASTERIX surveillance correlates with FIXM flight plans via GUFI (Globally Unique Flight Identifier). AIXM provides the static reference framework (airspace structure, runway geometry) updated on the AIRAC 28-day cycle.

---

### 26.11 Data Retention Requirements

FAA and NTSB regulations specify mandatory retention periods for all ATC operational data:

**FAA Order JO 7210.3** (Facility Operation and Administration):

| Data Type | Standard Retention | Incident/Accident | Hijacking |
|---|---|---|---|
| Voice recordings (DALR/NVR) | **45 days** | Until NTSB release | 3 years minimum |
| Radar/surveillance data (SAR/CDR/DLOG) | **45 days** | Until NTSB release | 3 years minimum |
| Data extraction recordings | **45 days** | Permanent (printouts) | 3 years minimum |
| Sign on/off data | **6 months** | Per Order 8020.16E | — |
| Tarmac delay data | **1 year** | — | — |

**FAA Order JO 8020.16E** (Accident/Incident Notification):
- Accident/incident recordings retained **until released by NTSB or FAA investigation authority**
- Printout data from accidents are **permanent records**

**NTSB 49 CFR Part 830.10**:
- **Indefinite hold** — all records pertaining to operation and maintenance must be preserved until NTSB takes custody or grants release. There is no fixed expiration.

**14 CFR 121.343/344** (Flight Data Recorders):
- FDR data: **60 days** normal retention; longer upon NTSB request

**FAA Order 1350.14B** (Records Management):
- Defines permanent vs. temporary records per NARA-approved retention schedules
- Recorder system validation must occur **daily** (not exceeding 26 hours between checks)

**Design Implications**:
1. 45-day automatic rolling retention for routine operational data
2. Immediate **litigation hold** capability — freezes all data for an incident, prevents automated deletion
3. Long-term archival storage (years to indefinite) for incident data
4. **Immutable audit trails** — append-only tables with no UPDATE/DELETE permissions
5. Data checksums (PostgreSQL `initdb --data-checksums`) to detect silent corruption

---

### 26.12 Storage Estimates

For a busy airport handling 500+ operations/day with ~200 simultaneous aircraft in the surveillance volume:

**Surveillance Data**:

| Stream | Calculation | Daily | 45-Day Retention | Yearly |
|---|---|---|---|---|
| ADS-B (200 aircraft, 1Hz, ~250B/record enriched) | 200 x 86,400 x 250B | 4.3 GB | 194 GB | 1.6 TB |
| Radar (200 targets, 0.2Hz, ~100B ASTERIX record) | 200 x 17,280 x 100B | 0.35 GB | 16 GB | 126 GB |
| **Surveillance subtotal** | | **4.7 GB** | **210 GB** | **1.7 TB** |
| **With TimescaleDB 90% compression** | | **0.47 GB** | **21 GB** | **170 GB** |

**Voice Recordings**:

| Stream | Calculation | Daily | 45-Day Retention | Yearly |
|---|---|---|---|---|
| Raw audio (25 channels, 16 KB/s, 24h) | 25 x 16KB x 86,400 | 34.6 GB | 1.6 TB | 12.6 TB |
| Codec compressed (G.711, ~8 KB/s) | 50% of raw | 17.3 GB | 779 GB | 6.3 TB |
| With VAD/silence detection (~30% active) | 30% of compressed | **5.2 GB** | **234 GB** | **1.9 TB** |

**Operational Data** (clearances, flight plans, agent decisions, audit):

| Stream | Daily | 45-Day | Yearly |
|---|---|---|---|
| All operational data combined | ~60 MB | ~2.7 GB | ~22 GB |

**Total Storage Summary**:

| | Daily | 45-Day Retention | Yearly |
|---|---|---|---|
| Surveillance (compressed) | 0.47 GB | 21 GB | 170 GB |
| Voice (VAD compressed) | 5.2 GB | 234 GB | 1.9 TB |
| Operational data | 0.06 GB | 2.7 GB | 22 GB |
| **Total** | **~5.7 GB/day** | **~258 GB** | **~2.1 TB** |

For context: the FAA's SWIM processes ~5 TB/day across the **entire U.S. NAS**. A single airport's data is well within commodity storage capacity.

**Storage Recommendation**: 10 TB NVMe RAID-10 for active storage (45-day window with headroom), with tiered archival to larger HDDs or tape for long-term incident preservation. Budget ~2.1 TB/year/facility for indefinite archival.

---

### 26.13 Complete Hardware Bill of Materials

**Dual-Channel Configuration** (recommended baseline):

| Item | Qty | Notes |
|---|---|---|
| NVIDIA DGX Spark (Channel A) | 18-20 | Primary processing |
| NVIDIA DGX Spark (Channel B) | 18-20 | Hot standby, identical |
| NVIDIA DGX Spark (Safety TMR voter) | 6-8 | Third channel for TMR safety nets only |
| NVIDIA DGX Spark (Dev/Test/Staging) | 4-6 | Offline validation |
| **Total DGX Spark** | **~50-54** | |
| Server racks (42U) | 3-4 | 2 compute, 1-2 network/storage/PDU |
| TSN Ethernet switches (managed, PTP) | 4-8 | Dual redundant |
| NAS / storage servers | 2-4 | RAID-10 NVMe + archival HDD |
| UPS units | 4 | 2N configuration |
| Diesel generators | 2 | One per power path |
| CRAC/CRAH cooling units | 3-4 | 2N cooling |
| Fiber patch panels | 4-8 | Dual path inter-rack and inter-building |

**Power**: ~16-20 kW peak (modest — well within single equipment room capacity)
**Cooling**: Air cooling sufficient at 7-13 kW/rack density
**Footprint**: 3-4 racks = approximately 10-14 square feet of rack space, plus surrounding clearance

The entire computational infrastructure for a fully automated, dual-channel ATC system fits in a **single standard equipment room** with commodity 2N power and cooling.

---

## 27. Swiss Cheese Model: Latent Error Analysis

This section applies James Reason's Swiss Cheese Model and latent error framework to the automated ATC system. The model states that accidents happen when holes in multiple defensive layers align — each layer has weaknesses, but normally they don't line up. When they do, an active error finds a path through latent conditions and reaches the hazard.

The key distinction: **Active errors** are the immediate triggers (a wrong clearance, a sensor failure). **Latent errors** are pre-existing conditions — design flaws, dormant configurations, untested interactions — that were waiting for a trigger. Fixing only the active error prevents one accident; fixing the latent error prevents an entire class.

This analysis draws on patterns documented in real-world networking outages (see `latent_errors_in_networking_outages.txt`) and maps them to ATC-specific failure modes.

---

### 27.1 The Defensive Layers (Slices of Cheese)

Our architecture has 7 defensive layers. Each must fail independently for a catastrophic outcome:

```
Layer 1: Surveillance Integrity
  ADS-B, radar, MLAT provide independent position data
  Multiple sensor types cross-check each other

Layer 2: Agent Decision Making
  2-3 independent agents per task compute clearances
  Different models, potentially different hardware

Layer 3: Consensus & Orchestration
  Orchestrator compares agent outputs
  Disagreement triggers escalation, not action

Layer 4: Deterministic Safety Nets
  Collision Vector Monitor, Separation Monitor,
  Runway Incursion Monitor — pure logic, veto power
  Independent hardware from agent layer

Layer 5: Human Overwatcher
  Reviews all agent decisions in real-time
  Can override or halt any operation

Layer 6: Pilot Cross-Check
  Pilot reads back clearances
  Pilot monitors own instruments (TCAS, GPWS)
  Pilot can refuse unsafe clearance

Layer 7: Aircraft Safety Systems
  TCAS Resolution Advisories (autonomous)
  GPWS/EGPWS terrain warnings
  Autopilot envelope protection
```

Each layer is a slice of cheese. The holes are what follows.

---

### 27.2 Known Holes in Each Layer

| Layer | Known Holes (Weaknesses) |
|---|---|
| **1. Surveillance** | ADS-B is unencrypted and spoofable. Radar has blind spots and ground clutter. MLAT degrades with poor receiver geometry. All sensors share the same RF environment — a single jammer could degrade multiple inputs simultaneously. |
| **2. Agent Decisions** | All agents may share the same training data bias. A systematic error in the training set produces identical wrong answers from "independent" agents. Agents share the same input data pipeline — corrupted input produces unanimous wrong consensus. |
| **3. Consensus** | The orchestrator is itself a single point of logic. If the consensus algorithm has a flaw, it could accept incorrect unanimous agreement or reject correct split decisions. A failure mode where all agents agree on the wrong answer is invisible to consensus checking. |
| **4. Safety Nets** | Deterministic logic only catches what it's programmed to catch. Novel conflict geometries not in the rule set pass through. Safety net parameters (separation minimums, threshold values) are configuration — configuration can be wrong. |
| **5. Human Overwatcher** | Endsley's out-of-the-loop problem: if the system is right 99.99% of the time, the human stops actually checking. Complacency is the hole in this layer. Display information overload can hide critical data in noise. |
| **6. Pilot Cross-Check** | Pilots are trained to comply with ATC. Questioning a clearance has a high social/professional cost. In high-workload phases (approach, landing), pilot attention is divided. Language barriers in international operations. |
| **7. Aircraft Systems** | TCAS cannot issue resolution advisories below ~1,000 ft AGL (the DCA collision scenario). GPWS has limited terrain database accuracy in some regions. Envelope protection can be overridden by crew. |

---

### 27.3 The Five Stacked Conflict Points Applied to ATC

These are drawn directly from Reason's framework as applied to real-world outages, mapped to our specific architecture.

#### Stack 1: The Fast Automation Paradox

**The conflict**: We automate ATC to eliminate human error. But when automation is wrong, it's wrong everywhere instantly, with no human in the loop fast enough to intervene.

**Where it applies**:
- An agent issues a clearance. The deterministic safety check passes. The instruction reaches the pilot in under 2 seconds. A human overwatcher seeing 50+ flights cannot evaluate each clearance faster than the system issues them.
- A model update propagates to all reasoning agents simultaneously. If the update introduces a subtle bias (e.g., slightly underestimates closure rates in certain wind conditions), all agents produce the same wrong answer. Consensus checking sees unanimous agreement and passes it through.
- A configuration change to normalcy thresholds takes effect immediately across all agents. If the threshold is wrong, the system either floods the human with false alerts (crying wolf until they stop responding) or suppresses real warnings.

**ATC-specific risk**: Unlike networking (where you can roll back a config in minutes), an incorrect ATC clearance may be irrecoverable within seconds. Two aircraft converging at 500+ knots close 5nm of separation in under 40 seconds.

**Defense design**:
- Model updates must use **canary deployment**: update one agent instance first, run it in shadow mode comparing its outputs to the existing model for N hours before promoting. Never update all instances simultaneously.
- Configuration changes to safety-critical parameters (thresholds, separation minimums) require **two-person authorization** enforced by tooling, not policy.
- The deterministic safety nets are **independent of the agent models** — they don't use ML and cannot be affected by model updates. They are the blast-radius firewall.

#### Stack 2: The Redundancy-Complexity Trap

**The conflict**: We add 2-3 redundant agents per task for safety. But redundancy adds interaction states between components, creating new failure modes that didn't exist in a simpler system.

**Where it applies** (paraphrasing Perrow: *"Redundant safety devices result in more complex systems, more prone to errors and accidents"*):
- Three approach sequencing agents must agree. But what happens when Agent A says "Flight 123 first," Agent B says "Flight 456 first," and Agent C says "Flight 123 first"? The 2-of-3 vote works. But what if Agent C's agreement with A is coincidental — it actually had a sensor dropout and is using stale data? The vote is correct by accident, and the stale-data condition goes undetected.
- TMR for the safety nets: three Collision Vector Monitors vote. But if they share the same input bus (the surveillance data feed), a corrupted input produces three identical wrong outputs. The redundancy is in the computation, but the input is a shared single point of failure.
- The consensus orchestrator watches agents for disagreement. But two competing failure modes exist: **false agreement** (all agents wrong the same way) and **false disagreement** (agents correct but with slightly different rounding, triggering unnecessary escalation). Tuning the orchestrator to reduce one increases the other.

**ATC-specific risk**: The AWS DynamoDB outage was caused by two DNS Enactors racing — redundancy created the race condition. In ATC, two agents simultaneously issuing different clearances to the same aircraft through different radio channels would be catastrophic.

**Defense design**:
- Redundant agents must have **independent input paths** where possible. If three agents all read from the same Redis cache, they're not truly independent. At minimum, each should independently validate its input against raw surveillance data.
- **Interaction testing**: Specifically test what happens when redundant agents disagree, when they agree but for different reasons, and when they operate at different speeds (one delayed by heavy inference load).
- **Invariant enforcement**: Regardless of how agents interact, certain states must be physically impossible — no two aircraft can be cleared for the same runway at the same time, period. This is the "DNS record cannot go to zero addresses" equivalent.

#### Stack 3: The Monitoring Layer Gap

**The conflict**: We monitor each component thoroughly — agent health, model inference latency, safety net status, network connectivity. But failures occur between layers, at boundaries the component-level monitoring can't see.

**Where it applies**:
- Each agent reports "healthy" (low latency, no errors). The safety nets report "no conflicts detected." The human display shows normal operations. But the surveillance data feeding all of them has a subtle systematic error — GPS multipath at a specific approach angle causes position reports to be offset by 200 meters. Every layer looks fine from the inside. Aircraft separation looks adequate on the display. The actual physical separation is 200 meters less than what the system believes.
- The agent correctly decides to issue a go-around instruction. The TTS system correctly synthesizes the voice command. The radio system correctly transmits it. But the frequency is congested and the pilot doesn't hear it. Every component in the chain says "I did my job." The monitoring gap is at the boundary between "system transmitted" and "pilot received."
- Memgraph shows healthy graph queries. PostgreSQL shows healthy writes. But the data pipeline between the surveillance ingest and the graph database has a 3-second lag that no component-level monitor detects. The conflict detection graph is running on stale positions.

**ATC-specific risk**: The Zoom outage happened because monitoring checked "are our DNS servers healthy?" (yes) but not "can users reach us via the TLD?" (no). In ATC, the equivalent is monitoring "are agents making decisions?" rather than "are the decisions correct and are pilots receiving and complying with them?"

**Defense design**:
- **End-to-end synthetic monitoring**: Inject synthetic flight tracks into the system periodically. These "ghost flights" follow known trajectories. If the system's output for a synthetic track deviates from the known-correct answer, something in the pipeline is wrong — even if every component reports healthy.
- **Negative-space monitoring**: Alert not only when something is wrong, but when expected activity is **absent**. If an aircraft on final approach hasn't received a landing clearance within N seconds of the expected point, that's a monitoring trigger — even if no component has reported an error.
- **Cross-layer correlation**: The human overwatcher display should show not just agent outputs but the **age of the data** feeding those outputs. If surveillance data is 3 seconds stale, that should be visually obvious, not hidden behind a "healthy" status indicator.

#### Stack 4: The Procedure Erosion Cycle

**The conflict**: Safety procedures exist for system maintenance, updates, and configuration. Under pressure (an agent is malfunctioning during peak traffic, a critical patch needs deployment), procedures get bypassed. The safety tooling that should enforce procedures has its own bugs.

**Where it applies**:
- The system requires canary deployment for model updates. But a critical vulnerability is discovered in the STT model that causes it to misinterpret a specific accent. The operations team needs to patch it NOW, during a busy arrival rush. "Just push it to all instances — we've tested it in staging." This is the AT&T case: the procedure existed, the technician didn't follow it, and nothing in the tooling enforced it.
- Safety net threshold changes require dual authorization. But the second authorizer is unavailable, and the current threshold is triggering 50 false alarms per hour. The operations team disables the threshold temporarily "until we can get the change approved." The temporary change becomes permanent. This is procedure erosion.
- "Configuration" updates to agent prompts or decision weights are treated differently from "software" updates — a less rigorous path, just like CrowdStrike treated channel file updates differently from sensor updates. But a prompt change can alter agent behavior as profoundly as a code change.

**ATC-specific risk**: The current human ATC system already suffers from this. The FCC found 58% of human-error outages stem from staff failing to follow procedures. Our automated system eliminates this for minute-to-minute ATC operations, but **transfers the risk to the maintenance and operations layer**. The humans maintaining the automation become the new "sharp end."

**Defense design**:
- **Encode procedures in tooling, not documents**. The deployment system physically refuses to update all agent instances simultaneously. The configuration system physically requires dual authorization for safety-critical parameters. If a procedure can be bypassed by a determined human, it will be, eventually.
- **Test safety tooling adversarially**: Regularly attempt the dangerous operations your safety tools should block. If the canary deployment gate can be overridden with a flag, someone will use that flag under pressure. Either remove the override entirely or audit every use.
- **Treat all agent changes as safety-critical**: Model updates, prompt changes, threshold adjustments, and configuration changes all flow through the same rigorous pipeline as core software. The CrowdStrike lesson: "just configuration" changes are often MORE dangerous than code changes because they bypass the CI/CD pipeline.

#### Stack 5: The Dormant Configuration Timebomb

**The conflict**: A configuration change enters the system and appears to work (or doesn't break anything immediately). No continuous validation checks whether the config is correct, only whether services are running. Days or months later, an unrelated change activates the dormant misconfiguration.

**Where it applies**:
- A normalcy threshold for wind shear is adjusted for winter operations. Spring arrives, the threshold is never reverted. Six months later, a summer microburst triggers a response calibrated for winter conditions — either too sensitive (false alarm flood) or too permissive (real hazard undertriggered). The person who made the winter change has rotated to a different facility.
- An airspace boundary is temporarily modified for a military exercise. The modification is entered as a permanent change instead of a time-limited one. Three months later, an aircraft following the standard approach enters what the system now considers military airspace, triggering an incorrect conflict alert — or worse, the system routes aircraft around a "restricted zone" that no longer exists, creating actual conflicts.
- A safety net rule is added to handle a specific unusual aircraft type. The rule includes an exception that slightly widens the acceptable separation for that type. The aircraft type is retired from service. The rule remains. Years later, a new aircraft type with the same type code is introduced. The legacy exception applies, and the safety net allows dangerously close separation.

**ATC-specific risk**: The Cloudflare case — a config sat dormant for 38 days until an unrelated change activated it. In ATC, dormant configs don't just cause outages; they cause the system to believe airspace is structured differently than reality. The triggering change is innocent and would be harmless in a clean system.

**Defense design**:
- **Configuration expiration (TTLs)**: Non-permanent configuration changes (temporary airspace modifications, seasonal thresholds, exercise-related rules) must have mandatory expiration dates. The system should refuse to accept a "temporary" change without a TTL.
- **Continuous configuration drift detection**: Compare the running system state against the declared intended state daily. Flag any configuration that exists but has no active traffic/usage flowing through it. Dormant config is the most dangerous config.
- **Configuration dependency graphs**: When any change is proposed, automatically surface all rules, thresholds, and agent behaviors that reference the changed object. "You're modifying runway 28L geometry. Here are the 14 safety net rules, 3 approach procedures, and 2 agent routing preferences that reference runway 28L."
- **"Dark config" scanning**: Periodically scan for configuration that exists but has never been activated in operational conditions. If a safety net rule hasn't fired in 6 months, is it because conditions never arose, or because the rule is broken and wouldn't fire if conditions did arise? This requires periodic testing of every rule, not just the frequently-triggered ones.

---

### 27.4 Mapping Networking Outages to ATC Failure Scenarios

| Networking Case | ATC Equivalent | Which Layer Fails |
|---|---|---|
| **Facebook BGP** (single command, global scope, no blast limit) | A single configuration change propagates to all agents, safety nets, or surveillance processing. No canary phase. | Layers 2-4 simultaneously |
| **AT&T Expansion** (new element, bypassed peer review) | New radar feed, agent instance, or hardware added to production without full validation. Technician under time pressure skips staging. | Layer 1 or 2 |
| **Cloudflare Dormant Config** (38-day timebomb) | Temporary airspace rule, seasonal threshold, or exercise modification sits dormant until an unrelated change activates it. | Layer 4 (safety nets with stale rules) |
| **AWS DNS Race** (redundant systems racing) | Two redundant agents simultaneously issue conflicting clearances through different channels. Consensus arrives too late. | Layer 3 (consensus timing) |
| **Zoom Domain** (third-party dependency outside monitoring) | Radar feed provider failure, GPS constellation degradation, or ADS-B ground station outage. Systems the ATC automation depends on but doesn't control. | Layer 1 (upstream of our system) |
| **Expired Certificates** (time-bound config nobody tracked) | Model calibration data expires. Airport database (AIXM) goes stale past AIRAC cycle. Agent "certification" validation token expires. | Layer 2 or 4 |
| **STP Loops** (default configs, non-deterministic election) | Default agent priority weights that were never explicitly set. Under unusual conditions, agents "elect" a non-optimal decision leader. | Layer 3 (orchestration) |
| **MTU Black Holes** (monitoring uses wrong test) | System health checks use simple test inputs. Complex real-world scenarios (non-standard aircraft, unusual approach angles, simultaneous emergencies) reveal failures that simple tests cannot. | Layer 3 (monitoring gap) |
| **CrowdStrike** (content update bypasses rigorous pipeline) | Model weight updates, prompt changes, or threshold adjustments treated as "just config" and pushed without the same rigor as core software. | Layers 2-4 |
| **Google Cloud Policy** (corrupted data, global propagation, no null check) | Invalid surveillance data (null position, impossible altitude) propagates through the pipeline. An agent attempts to compute separation against a null position — crash or undefined behavior. | Layers 1-4 (cascading) |

---

### 27.5 The Meta-Insight: Why This System Is Both the Problem and the Solution

Reason's sharp-end/blunt-end metaphor is deeply relevant here. In today's ATC system:

- **Sharp end**: The controller typing commands, issuing voice clearances, making split-second decisions while fatigued at hour 9 of a 10-hour shift
- **Blunt end**: FAA management that combined two controller positions at DCA, saving headcount while increasing cognitive load

The Potomac River collision and LaGuardia runway incursion both happened at the sharp end. The latent errors were at the blunt end — staffing decisions, procedure design, system architecture that put too much load on a single human.

**Our automated system eliminates the sharp-end failure mode**. No fatigue, no lapse in attention, no "forgot to check." But it introduces a new sharp end: **the humans who maintain, configure, and update the automation**. Every insight from the networking outage document applies directly to these maintainers:

- They will be under time pressure to push changes during operational windows
- They will skip procedures when the safety tooling is slow or inconvenient
- They will treat "just a threshold change" as less risky than a software update
- They will leave temporary configs in place because removing them is lower priority
- Their monitoring will check "is the system running?" rather than "is the system correct?"

The document's most powerful line applies without modification: **"Every 'pay more attention' in a post-mortem is a latent error waiting for its next trigger."** If our incident response for the automated system relies on "the operations team should have noticed the stale config," we've built the same trap that kills people in the current human ATC system — just moved it one layer up.

The defense is the same as Reason prescribes: **make the right thing easy and the wrong thing hard**. Encode safety in tooling that cannot be bypassed, not in procedures that erode under pressure. Test every defense adversarially. And when an incident occurs, ask not "who screwed up?" but "what was waiting to happen?"

---

### 27.6 Invariants: States That Must Be Physically Impossible

Drawing from the networking document's concept of "hard invariants" (a DNS record cannot go to zero addresses), these are states the ATC system must make **architecturally impossible**, not just procedurally unlikely:

| Invariant | Enforcement |
|---|---|
| No two aircraft may be cleared for the same runway simultaneously | Deterministic lock in shared memory — not agent logic, hardware-enforced mutual exclusion |
| No clearance can be issued if the deterministic safety net has not validated it | Safety net sits in the data path, not as an advisory. Clearance cannot physically reach the radio without safety net sign-off. |
| No surveillance data older than N seconds may be used for separation decisions | Timestamp check at the data consumer, not the producer. Stale data is silently discarded, triggering a "surveillance degraded" alert. |
| No model update may be applied to all instances simultaneously | Deployment system physically cannot target >33% of instances per deployment step. No override flag. |
| No safety-critical configuration change may be applied without dual authorization | Configuration system requires two cryptographic signatures from different authorized personnel. Single-person override is architecturally absent. |
| No temporary configuration may exist without an expiration timestamp | Schema validation rejects temporary configs with null TTL at write time |
| No agent may issue a clearance that contradicts an active clearance for the same flight | Clearance state machine enforces sequencing — a landing clearance cannot coexist with a go-around clearance for the same aircraft in the same epoch |

These are the "floors" — the states below which the system physically cannot go, regardless of what any combination of agents, humans, or configuration changes attempts. They are the innermost slices of cheese with no holes.

---

## 28. Formal State Model

This section defines the formal state machines that govern every flight, clearance, runway, and ground vehicle in the system. These state machines are the **enforceable specification** — the deterministic safety layer's job is to prevent illegal state transitions, and the agents' job is to propose legal ones. Every invariant from Section 27.6 maps to a constraint in these models.

Design decision: **V1 is deliberately conservative**. One lock per runway, no exceptions. We sacrifice some throughput to eliminate entire classes of conflict. Relaxation of specific constraints will require formal verification (Ada/SPARK, DO-333) before deployment.

---

### 28.1 Facility Reference Model (Class C)

The state machines are designed for a Class C airport with parallel runways — enough complexity to surface the conflict points (runway mutual exclusion, crossing conflicts, dependent parallel approaches) without the scale of a major hub.

```
Runways:    10L/28R, 10R/28L (parallel, ~4,300ft separation)
Taxiways:   A (parallel to 10L/28R), B (parallel to 10R/28L)
            C, D, E (cross-field, crossing both runways)
Ramp:       Terminal ramp between taxiways A and B
Airspace:   Class C — SFC to 4,000ft AGL, 5nm radius
            Outer shelf: 1,200–4,000ft AGL, 10nm radius
Frequencies: Ground (taxiing), Local/Tower (runway ops), Approach/Departure (TRACON), ATIS
```

This facility model produces the key conflict scenarios:
- **Same-runway conflicts**: Two entities competing for one runway (the core mutual exclusion problem, the LGA case)
- **Cross-runway taxi conflicts**: Taxiways C, D, E cross active runways, requiring sequential lock acquisition
- **Dependent parallel operations**: If runway separation < 4,300ft, departures on one runway constrain arrivals on the parallel
- **VFR/IFR mixed traffic**: Pattern traffic must be sequenced between IFR arrivals
- **Airspace conflicts**: VFR transits through Class C must be tracked to prevent the DCA scenario

---

### 28.2 Aircraft State Machine — IFR

#### 28.2.1 Phases and States

Hierarchical state machine. Top-level phases contain sub-states. A flight is always in exactly one state (except EMERGENCY, which overlays).

```
PHASE: PRE_DEPARTURE
    PARKED                — At gate/ramp, flight plan filed
    CLEARANCE_DELIVERED   — IFR clearance received
    PUSHBACK_APPROVED     — Cleared to push back from gate

PHASE: GROUND_OUT
    TAXIING_OUT           — Moving on taxiways toward departure runway
    HOLDING_SHORT         — Stopped at runway hold line, awaiting clearance
    LINEUP_WAIT           — On runway, not yet cleared for takeoff

PHASE: DEPARTURE (Tower)
    TAKEOFF_ROLL          — Accelerating on runway
    AIRBORNE_DEPARTURE    — Airborne, still on tower frequency

PHASE: DEPARTURE_TRACON
    DEPARTURE_CONTACT     — Aircraft contacts TRACON departure frequency
    DEPARTURE_CLIMBING    — TRACON assigns altitude, vectors as needed
    CENTER_HANDOFF        — TRACON hands off to Center for en-route

PHASE: ARRIVAL_TRACON
    ARRIVAL_INBOUND       — Center hands off to TRACON approach control
    SEQUENCED             — Assigned position in arrival flow
    VECTORING             — TRACON issuing heading/altitude/speed for spacing
    APPROACH_CLEARED      — Cleared for instrument approach (ILS, RNAV, Visual)
    ESTABLISHED           — Intercepted approach path (localizer/glideslope/RNAV)
    TOWER_HANDOFF         — "Contact tower" issued

PHASE: ARRIVAL (Tower)
    INBOUND               — On tower frequency, approaching
    FINAL_APPROACH        — Inside FAF, on final
    LANDING_CLEARED       — Landing clearance received
    LANDING_ROLL          — Wheels on runway, decelerating
    RUNWAY_EXIT           — Turning off runway onto taxiway

PHASE: GROUND_IN
    TAXIING_IN            — Moving on taxiways toward gate/ramp
    PARKED_IN             — At gate, flight complete

PHASE: GO_AROUND
    GO_AROUND_CLIMB       — Executing missed approach/go-around
    RESEQUENCED           — Back in TRACON sequence (→ SEQUENCED)

PHASE: EMERGENCY (parallel overlay — can coexist with any phase)
    EMERGENCY_DECLARED    — Squawking 7700, priority handling
    EMERGENCY_RESOLVED    — Emergency over, resuming normal ops

TERMINAL:
    FLIGHT_COMPLETE       — Out of system
```

#### 28.2.2 Departure Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| PARKED | CLEARANCE_DELIVERED | IFR clearance issued | IFR Clearance |
| PARKED | PUSHBACK_APPROVED | Pushback clearance (VFR departures skip clearance delivery) | Pushback Approval |
| CLEARANCE_DELIVERED | PUSHBACK_APPROVED | Pushback clearance | Pushback Approval |
| PUSHBACK_APPROVED | TAXIING_OUT | Taxi clearance issued | Taxi Clearance (w/ route + hold-short) |
| TAXIING_OUT | HOLDING_SHORT | Aircraft reaches hold line | Surveillance (auto-detect) |
| HOLDING_SHORT | LINEUP_WAIT | "Line up and wait" issued | LUAW Clearance |
| HOLDING_SHORT | TAKEOFF_ROLL | Takeoff clearance issued | Takeoff Clearance |
| LINEUP_WAIT | TAKEOFF_ROLL | Takeoff clearance issued | Takeoff Clearance |
| TAKEOFF_ROLL | AIRBORNE_DEPARTURE | Liftoff detected | Surveillance (auto-detect) |
| AIRBORNE_DEPARTURE | DEPARTURE_CONTACT | "Contact departure" issued | Frequency Change |

#### 28.2.3 Aborted Takeoff

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| TAKEOFF_ROLL | LINEUP_WAIT | Abort below V1 (still on runway) | Pilot-initiated (alert triggered) |
| LINEUP_WAIT | HOLDING_SHORT | "Exit runway" instruction | Exit instruction |
| LINEUP_WAIT | TAXIING_OUT | Aircraft taxis off runway | Surveillance (auto-detect) |

The DEPARTURE runway lock is retained until the aircraft exits the runway surface. An aborted takeoff does NOT release the lock — the aircraft is still physically on the runway.

---

### 28.3 TRACON State Machine

TRACON manages the airspace between tower (~5nm, SFC–3,000ft) and Center (en-route). It sequences arrivals and climbs departures.

#### 28.3.1 TRACON Departure Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| DEPARTURE_CONTACT | DEPARTURE_CLIMBING | Initial contact + climb instruction | Altitude/heading assignment |
| DEPARTURE_CLIMBING | CENTER_HANDOFF | "Contact Center" issued | Frequency Change |
| CENTER_HANDOFF | FLIGHT_COMPLETE | Aircraft exits TRACON airspace | Surveillance (auto-detect) |

#### 28.3.2 TRACON Arrival Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| [Center handoff] | ARRIVAL_INBOUND | Center transfers to TRACON | Handoff acceptance |
| ARRIVAL_INBOUND | SEQUENCED | TRACON assigns sequence number | Sequence assignment |
| SEQUENCED | VECTORING | Heading/altitude/speed issued | Vectoring clearance |
| VECTORING | APPROACH_CLEARED | "Cleared ILS/RNAV/Visual Runway XX" | Approach Clearance |
| APPROACH_CLEARED | ESTABLISHED | Aircraft intercepts approach path | Surveillance (auto-detect) |
| ESTABLISHED | TOWER_HANDOFF | "Contact tower [freq]" | Frequency Change |
| TOWER_HANDOFF | INBOUND | Aircraft checks in with tower | Handoff acceptance |

**Note**: VECTORING may loop — multiple heading/altitude/speed changes are common for spacing. A well-spaced aircraft can skip VECTORING entirely: SEQUENCED → APPROACH_CLEARED.

#### 28.3.3 Tower Arrival Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| TOWER_HANDOFF | INBOUND | Aircraft checks in with tower | Handoff acceptance |
| INBOUND | FINAL_APPROACH | Aircraft crosses FAF | Surveillance (auto-detect) |
| INBOUND | LANDING_CLEARED | Landing clearance issued early | Landing Clearance |
| FINAL_APPROACH | LANDING_CLEARED | Landing clearance issued | Landing Clearance |
| LANDING_CLEARED | LANDING_ROLL | Touchdown detected | Surveillance (auto-detect) |
| LANDING_ROLL | RUNWAY_EXIT | Speed < threshold + turning off runway | Surveillance (auto-detect) |
| RUNWAY_EXIT | TAXIING_IN | Taxi clearance issued | Taxi Clearance (w/ route) |
| TAXIING_IN | PARKED_IN | Aircraft at gate | Surveillance (auto-detect) |
| PARKED_IN | FLIGHT_COMPLETE | Systems release | None |

#### 28.3.4 Go-Around Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| FINAL_APPROACH | GO_AROUND_CLIMB | Go-around instruction issued | Go-Around Instruction |
| LANDING_CLEARED | GO_AROUND_CLIMB | Go-around instruction issued | Go-Around Instruction |
| LANDING_ROLL | GO_AROUND_CLIMB | Rejected landing (rare, pilot-initiated) | Pilot-initiated (alert) |
| GO_AROUND_CLIMB | RESEQUENCED | Aircraft on missed approach procedure | Missed approach procedure |
| RESEQUENCED | SEQUENCED | Re-entered TRACON arrival sequence | TRACON re-sequencing |

**Critical design choice**: Go-around sends the aircraft back to TRACON (SEQUENCED), not directly back to tower INBOUND. TRACON re-sequences the aircraft into the arrival flow. This is realistic — tower doesn't self-sequence a go-around; approach control does. It also means the go-around aircraft gets a fresh pass through all safety checks.

#### 28.3.5 Emergency Overlay

EMERGENCY_DECLARED can be entered from **any state**. It does not replace the current state — it overlays it, giving the flight priority access to all resources and triggering immediate escalation to Tier 3 (human + AI assistant).

Emergency is declared by:
- Pilot (squawk 7700, voice declaration "Mayday" or "Pan-Pan")
- System detection (abnormal trajectory, loss of communication beyond timeout, computed fuel state below minimums)
- Human overwatcher (manual override)

EMERGENCY_DECLARED → EMERGENCY_RESOLVED when the human overwatcher explicitly confirms resolution. There is no automatic timeout — emergencies persist until human action.

---

### 28.4 VFR Traffic Pattern State Machine

VFR traffic pattern operations (touch-and-go, stop-and-go, low approach) cycle through the pattern repeatedly without parking. This requires a dedicated state machine with its own runway lock type.

#### 28.4.1 Pattern States

```
PHASE: VFR_PATTERN
    UPWIND           — Climbing after takeoff/touch-and-go, parallel to runway
    CROSSWIND        — Turning perpendicular to runway, still climbing
    DOWNWIND         — Parallel to runway, opposite direction, level
    BASE             — Turning toward runway, descending
    PATTERN_FINAL    — Aligned with runway, descending (distinct from IFR FINAL_APPROACH)
    TOUCH_AND_GO     — Touchdown + acceleration + liftoff without stopping
    STOP_AND_GO      — Touchdown + full stop + takeoff roll
    LOW_APPROACH     — Fly over runway without touching down
    FULL_STOP        — Normal landing → transitions to LANDING_ROLL
```

#### 28.4.2 Pattern Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| AIRBORNE_DEPARTURE | UPWIND | Remaining in pattern (VFR) | Pattern Entry Clearance |
| [External entry] | DOWNWIND | VFR aircraft enters pattern | Pattern Entry Clearance |
| UPWIND | CROSSWIND | Reaching pattern altitude | None (pilot discretion) |
| CROSSWIND | DOWNWIND | Completing turn | None (pilot discretion) |
| DOWNWIND | BASE | Abeam touchdown zone | None (pilot discretion) |
| BASE | PATTERN_FINAL | Turning final | None (pilot discretion) |
| PATTERN_FINAL | TOUCH_AND_GO | "Cleared touch-and-go" | Touch-and-Go Clearance |
| PATTERN_FINAL | STOP_AND_GO | "Cleared stop-and-go" | Stop-and-Go Clearance |
| PATTERN_FINAL | LOW_APPROACH | "Cleared low approach" | Low Approach Clearance |
| PATTERN_FINAL | FULL_STOP | "Cleared to land" | Landing Clearance |
| TOUCH_AND_GO | UPWIND | Liftoff after touch | Surveillance (auto-detect) |
| STOP_AND_GO | UPWIND | Liftoff after stop+go | Surveillance (auto-detect) |
| LOW_APPROACH | UPWIND | Passing departure end of runway | Surveillance (auto-detect) |
| FULL_STOP | LANDING_ROLL | Decelerating on runway | Surveillance (auto-detect) |

Aircraft can be told to exit the pattern at any point: extend downwind, depart the area, or make a full stop.

#### 28.4.3 VFR Pattern Runway Locks

| Operation | Lock Type | Lock Duration |
|-----------|-----------|---------------|
| Touch-and-go | PATTERN | Touchdown through liftoff (~15–20 sec) |
| Stop-and-go | PATTERN | Touchdown through liftoff (~45–60 sec) |
| Low approach | PATTERN | Short final through departure end (~20–30 sec) |
| Full stop | ARRIVAL | Same as IFR arrival |

PATTERN lock is mutually exclusive with all other lock types (V1 rule: one lock per runway). The key difference from IFR: the lock window is much shorter for touch-and-go operations, so pattern traffic can cycle between IFR arrivals with tighter spacing.

#### 28.4.4 Pattern–IFR Interaction

TRACON and tower must coordinate sequencing of VFR pattern traffic with IFR arrivals. Tower "makes a hole" by extending a VFR aircraft's downwind leg to fit an IFR arrival between pattern cycles:

```
DOWNWIND → DOWNWIND (extended)    "Extend downwind, I'll call your base"
```

The DOWNWIND state persists (no state transition) but the aircraft's planned base turn point is deferred. The trigger to resume is an explicit "Turn base" instruction from tower. This is modeled as a **sequence instruction** — a clearance type that does not acquire a runway lock but constrains the aircraft's future transitions.

---

### 28.5 Runway Resource Model

The runway is the critical shared resource. Conflicts on the runway surface are the most immediately lethal failure mode in ATC — the LGA collision is the proof case.

#### 28.5.1 The Runway as a Mutual Exclusion Lock

Each runway is modeled as a shared resource with a single-holder lock:

```
RunwayLock {
    runway_id:      "10L" | "28R" | "10R" | "28L"
    lock_type:      DEPARTURE | ARRIVAL | CROSSING | LUAW | PATTERN | NONE
    holder:         flight_id | vehicle_id | null
    acquired_at:    timestamp
    ttl:            max seconds before mandatory alert
    clearance_id:   reference to the clearance that acquired this lock
}
```

#### 28.5.2 Lock Compatibility Matrix (V1)

**V1 Rule: ONE LOCK PER RUNWAY. No exceptions.**

```
                 DEPARTURE  ARRIVAL  CROSSING  LUAW  PATTERN
DEPARTURE            X         X        X       X      X
ARRIVAL              X         X        X       X      X
CROSSING             X         X        X       X      X
LUAW                 X         X        X       X      X
PATTERN              X         X        X       X      X

X = INCOMPATIBLE — cannot coexist on the same runway
```

This is more conservative than current human ATC, which routinely uses LUAW while an arrival is on approach. We deliberately sacrifice throughput to eliminate entire classes of conflict. Specific combinations (e.g., LUAW with arrival traffic at defined minimums) can be introduced later with formal verification in Ada/SPARK.

#### 28.5.3 Lock Lifecycle

```
AVAILABLE → RESERVED → OCCUPIED → RELEASED → AVAILABLE
```

| State | Meaning |
|-------|---------|
| AVAILABLE | No lock held. Runway is clear for new operations. |
| RESERVED | Clearance issued (e.g., landing clearance given). Aircraft approaching but not yet on runway surface. |
| OCCUPIED | Aircraft/vehicle physically detected on runway surface by surveillance. |
| RELEASED | Aircraft/vehicle confirmed clear of runway. Lock dropped. |

#### 28.5.4 Atomic Check-and-Lock

**The safety net validation and lock acquisition must be a single atomic operation.**

If validation and locking are separate steps, a race condition exists:

```
RACE CONDITION (must be architecturally impossible):
  T0: Agent A proposes landing clearance for Flight 123 on 10L
  T1: Safety net checks: 10L is AVAILABLE → valid
  T2: Agent B proposes crossing clearance for Vehicle 7 on 10L
  T3: Safety net checks: 10L is AVAILABLE → valid (BUG: should be RESERVED)
  T4: Both clearances issued → LGA scenario reproduced
```

This is prevented by implementing validation + lock acquisition as a single atomic operation in POSIX shared memory (mutex or hardware compare-and-swap on the deterministic safety layer's independent hardware). The safety net cannot return VALIDATED without simultaneously holding the lock.

#### 28.5.5 Lock TTL and Expiration

Every runway lock has a mandatory TTL (Time-To-Live). Expiration triggers an **alert**, not automatic release — a human must resolve the ambiguity.

| Lock Type | TTL | Rationale |
|-----------|-----|-----------|
| DEPARTURE | ~90 sec | Takeoff roll + initial climb + confirmed airborne |
| ARRIVAL | ~120 sec | Final approach segment + landing roll + runway exit |
| CROSSING | ~45 sec | Vehicle/aircraft crosses runway |
| LUAW | ~120 sec | Holding on runway + eventual takeoff |
| PATTERN | ~30 sec | Touch-and-go: touchdown through liftoff |

Expiration scenarios that trigger alerts:
- **RESERVED → not OCCUPIED** within N seconds: Expected entity didn't enter runway. Possible go-around, aborted taxi, or surveillance failure.
- **OCCUPIED → not RELEASED** within M seconds: Entity on runway longer than expected. Possible disabled aircraft, stuck vehicle, or surveillance failure.

TTL values are configurable per facility and operation type, but changes are subject to the same configuration-is-code pipeline (Principle 7).

#### 28.5.6 Approach Commitment Gate (Token-Based Flow Control)

The runway lock model prevents two entities from occupying the same runway. But it has a gap: it prevents issuing a *landing clearance* on a locked runway — it does NOT force a *go-around* for an aircraft that's already approaching. An aircraft in FINAL_APPROACH with a locked runway is a ticking clock — it will arrive at the threshold whether or not it has a clearance. Relying on the agents to "notice" this and propose a go-around violates Principle 2: "Pay more attention" is not a defense.

The fix is borrowed from Cisco's Virtual Output Queue (VOQ) credit-based flow control. In VOQ, a switch port cannot transmit a packet to a destination interface without a credit token from that interface. No token, no transmission — the packet is held in the queue, not dropped into a congested interface. This prevents head-of-line blocking by managing the queue at the *source*, before the packet reaches the point of no return.

The ATC equivalent:

| VOQ Concept | ATC Equivalent |
|-------------|----------------|
| Destination interface | Runway |
| Credit token | Runway lock (ARRIVAL, PATTERN) |
| Packet in output queue | Aircraft on approach |
| No credit → packet held | No lock → aircraft cannot proceed past commitment gate |
| Credit granted → transmit | Lock acquired → cleared to land |
| Queue management at source | Sequencing at TRACON, not at the runway threshold |

**The Approach Commitment Gate (ACG)** is the point on the approach where the deterministic safety layer enforces the token requirement. It works on two thresholds:

```
ADVISORY GATE (~5nm / FAF):
    If runway lock is held by another entity:
        → Alert agents: "Runway unavailable. Sequence accordingly."
        → Agents should delay, extend, or re-sequence approaching traffic
        → This is the "XOFF" signal — slow down the source before the buffer fills

COMMITMENT GATE (~2nm):
    If aircraft reaches this point WITHOUT a validated landing clearance:
        → Deterministic safety layer FORCES a go-around instruction
        → This is NOT an agent decision — it is a safety net action
        → The instruction is originated by the deterministic layer, bypassing agents
        → Go-around clearance follows normal state machine:
          Aircraft → GO_AROUND_CLIMB → RESEQUENCED → back to TRACON
```

The commitment gate is a **forcing function** — it converts "the agent should have noticed" into "the system physically cannot allow this." An aircraft cannot pass the commitment gate without a token (runway lock), just as a VOQ packet cannot be transmitted without a credit.

**Why two gates?**

The advisory gate gives the agents time to re-sequence traffic gracefully (extend downwind, add a vector, slow approach speed). If the agents handle it at the advisory gate, the commitment gate never fires. The commitment gate is the **backstop** — it fires only when agents have failed to manage the situation, and it fires deterministically, on independent hardware, with no agent involvement.

This same model applies to VFR pattern traffic:

```
VFR COMMITMENT GATE (~0.5nm / short final):
    If VFR aircraft in PATTERN_FINAL without a validated
    touch-and-go/stop-and-go/low-approach/landing clearance:
        → Deterministic layer FORCES a go-around (wave-off)
        → Aircraft → UPWIND → continues pattern
```

**Interaction with sequencing**: The advisory gate is where sequencing decisions are made. TRACON controls the "queue depth" — how many aircraft are vectored toward the approach at once. If the runway token is held (lock active), TRACON slows the inbound flow: extends downwind legs, adds holding patterns, increases spacing. This is queue management at the source, exactly as VOQ manages output queues at the ingress port rather than the egress. The commitment gate is the safety net that catches anything the sequencing missed.

---

### 28.6 Clearance Lifecycle

Every instruction from the system to a pilot or vehicle operator follows this lifecycle. No clearance can bypass the deterministic safety net.

#### 28.6.1 Clearance States

```
PROPOSED ──→ VALIDATED ──→ ISSUED ──→ READBACK_OK ──→ ACTIVE ──→ COMPLETED
    │            │             │            │                         │
    │            │             │            └──→ READBACK_FAIL        │
    │            │             │                   (re-issue)         │
    │            │             └──→ NO_RESPONSE                      │
    │            │                   (timeout → alert)               │
    │            └──→ REJECTED                                       │
    │                  (reason logged)                                │
    └──→ EXPIRED                                              ┌──────┘
          (TTL before validation)                             │
                                                              ├──→ CANCELLED
                                                              └──→ SUPERSEDED
```

| State | Meaning | Resource Lock |
|-------|---------|---------------|
| PROPOSED | Agent generated clearance recommendation | None |
| VALIDATED | Deterministic safety net approved; invariants satisfied | **Lock ACQUIRED** (atomic with validation) |
| REJECTED | Safety net denied — invariant violation, separation conflict | None (reason logged) |
| ISSUED | Transmitted to pilot via voice (TTS) or datalink | Lock held |
| READBACK_OK | Pilot read back correctly (STT confirmed match) | Lock held |
| READBACK_FAIL | Pilot read back incorrectly — must re-issue | Lock held (re-issue from VALIDATED) |
| NO_RESPONSE | No readback within timeout | Lock held (alert escalation) |
| ACTIVE | Clearance in effect, entity executing | Lock held |
| COMPLETED | Action finished (landed, crossed, departed) | **Lock RELEASED** |
| CANCELLED | Explicitly cancelled before completion | **Lock RELEASED** |
| SUPERSEDED | Replaced by new clearance (go-around supersedes landing) | **Lock RELEASED** (new clearance acquires its own lock) |
| EXPIRED | TTL elapsed without progression — anomaly | **Lock RELEASED** + alert |

#### 28.6.2 Clearance Types by Phase

| Type | Acquires Runway Lock | Phase |
|------|---------------------|-------|
| **Pre-Departure / Ground** | | |
| IFR Clearance | No | PRE_DEPARTURE |
| Pushback Approval | No | PRE_DEPARTURE |
| Taxi Clearance (out) | No (but reserves taxi route) | GROUND_OUT |
| Hold Short Instruction | No (prevents lock acquisition) | GROUND_OUT |
| Line Up and Wait | **Yes — LUAW lock** | GROUND_OUT |
| Hold Position | No (prevents further transitions) | Any ground |
| **Tower — Departure/Arrival** | | |
| Takeoff Clearance | **Yes — DEPARTURE lock** (or upgrades LUAW) | DEPARTURE |
| Landing Clearance | **Yes — ARRIVAL lock** | ARRIVAL |
| Go-Around Instruction | **Releases ARRIVAL lock** | GO_AROUND |
| Taxi Clearance (in) | No | GROUND_IN |
| Runway Crossing Clearance | **Yes — CROSSING lock** | GROUND (vehicles or taxiing aircraft) |
| **TRACON** | | |
| Sequence Assignment | No | ARRIVAL_TRACON |
| Vectoring Clearance (hdg/alt/spd) | No | ARRIVAL_TRACON |
| Approach Clearance (ILS/RNAV/Visual) | No | ARRIVAL_TRACON |
| Altitude/Heading Assignment (departure) | No | DEPARTURE_TRACON |
| **VFR Pattern** | | |
| Pattern Entry Clearance | No | VFR_PATTERN |
| Touch-and-Go Clearance | **Yes — PATTERN lock** | VFR_PATTERN |
| Stop-and-Go Clearance | **Yes — PATTERN lock** | VFR_PATTERN |
| Low Approach Clearance | **Yes — PATTERN lock** | VFR_PATTERN |
| Sequence Instruction ("extend downwind") | No | VFR_PATTERN |
| **Universal** | | |
| Frequency Change | No | Any |

#### 28.6.3 Clearance Mutual Exclusion (Per Flight)

A flight cannot have two active clearances of conflicting types simultaneously:

| Conflict | Resolution |
|----------|------------|
| LANDING_CLEARED + GO_AROUND | Go-around **supersedes** landing clearance |
| TAKEOFF + HOLD_POSITION | Hold **cancels** takeoff clearance |
| TAXI_OUT + TAXI_IN | Impossible — different phases of flight |
| LINEUP_WAIT + TAKEOFF | Takeoff **supersedes** LUAW (same resource, lock upgraded) |

Enforcement: A new clearance for the same flight must either be compatible with or explicitly supersede all active clearances for that flight. The clearance state machine rejects any new clearance that would create a conflicting pair.

---

### 28.7 Ground Vehicle State Machine

The LaGuardia collision (March 2026): a fire truck was cleared to cross Runway 4 while Air Canada 8646 was on final approach. The controller — handling both tower and ground frequencies due to combined positions — didn't cross-check the runway state.

This state machine ensures that ground vehicles compete for the same runway locks as aircraft. The controller's error is architecturally impossible.

#### 28.7.1 States

```
STATIONARY → TAXI_CLEARED → MOVING → HOLDING_SHORT → CROSSING_CLEARED → ON_RUNWAY → CLEAR_OF_RUNWAY → MOVING → STATIONARY
                                          ↑                                                    │
                                          └────────────────────────────────────────────────────┘
                                          (if route crosses multiple runways)
```

#### 28.7.2 Transitions

| From | To | Trigger | Clearance Required |
|------|----|---------|--------------------|
| STATIONARY | TAXI_CLEARED | Vehicle requests movement | Vehicle Taxi Clearance |
| TAXI_CLEARED | MOVING | Vehicle begins moving | Surveillance (auto-detect) |
| MOVING | HOLDING_SHORT | Vehicle reaches runway hold line | Surveillance (auto-detect) |
| HOLDING_SHORT | CROSSING_CLEARED | Crossing clearance issued | Runway Crossing Clearance |
| CROSSING_CLEARED | ON_RUNWAY | Vehicle enters runway surface | Surveillance (auto-detect) |
| ON_RUNWAY | CLEAR_OF_RUNWAY | Vehicle exits runway surface | Surveillance (auto-detect) |
| CLEAR_OF_RUNWAY | MOVING | Continuing to destination | None (automatic) |
| MOVING | STATIONARY | Vehicle reaches destination | Surveillance (auto-detect) |

#### 28.7.3 The LGA Invariant in Action

**A runway crossing clearance for a vehicle CANNOT be validated if any lock (ARRIVAL, DEPARTURE, LUAW, PATTERN) exists on that runway.**

Vehicles and aircraft are treated identically by the runway lock system. The safety net does not distinguish between "an aircraft is landing" and "a vehicle wants to cross" — it only sees "lock held, new lock request, REJECT."

```
The LGA scenario traced through this model:

  T0: Air Canada 8646 on final for Runway 4
      → Agent proposes Landing Clearance
      → Safety net: Rwy 4 AVAILABLE → VALIDATED + ARRIVAL lock acquired
      → State: AC8646 in LANDING_CLEARED, Rwy 4 locked (ARRIVAL)

  T1: Fire truck at Taxiway B requests crossing of Runway 4
      → State: Truck in HOLDING_SHORT

  T2: Agent proposes Runway Crossing Clearance for truck on Rwy 4
      → Safety net: Rwy 4 lock check → ARRIVAL lock held by AC8646 → REJECTED
      → Reason logged: "Runway 4 locked (ARRIVAL, holder: AC8646, clearance: LDG-2026-0323-1847)"

  T3: Crossing clearance NEVER ISSUED. Truck holds at HOLDING_SHORT.

  T4: AC8646 lands, decelerates, exits runway
      → State: AC8646 in RUNWAY_EXIT → ARRIVAL lock RELEASED → Rwy 4 AVAILABLE

  T5: Agent re-proposes crossing clearance for truck
      → Safety net: Rwy 4 AVAILABLE → VALIDATED + CROSSING lock acquired
      → Truck crosses safely.

The controller's error — clearing the truck onto an active runway — is architecturally impossible.
The system doesn't rely on the controller remembering who's on final.
It relies on a mutex that physically cannot be held by two entities.
```

---

### 28.8 Formal Invariants

These are the forbidden states. The deterministic safety layer must make each one **unreachable** — not just unlikely, not just alarmed, but physically impossible through the state machine and lock architecture.

#### 28.8.1 Runway Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | No runway may have more than one active lock (V1) | Atomic check-and-lock in POSIX shared memory |
| R2 | No clearance acquiring a runway lock may be VALIDATED while that runway has an existing lock | Atomic validation + lock acquisition |
| R3 | No runway lock may exist without a corresponding VALIDATED or ACTIVE clearance | Lock lifecycle bound to clearance lifecycle — lock cannot be orphaned |
| R4 | No runway lock may persist beyond its TTL without generating an alert | TTL timer with mandatory alert (expiration does NOT auto-release) |

#### 28.8.2 Clearance Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| C1 | No clearance may reach ISSUED without passing through VALIDATED | Safety net in data path, not advisory — physical impossibility |
| C2 | No flight may have two active clearances of mutually exclusive types | Per-flight clearance state machine |
| C3 | No clearance may remain in ISSUED or READBACK_FAIL beyond timeout without alert | TTL on each state transition |
| C4 | A SUPERSEDING clearance must explicitly reference and cancel the clearance it replaces | State machine enforces supersession chain with clearance IDs |
| C5 | No clearance using surveillance data older than N seconds may be VALIDATED | Consumer-side timestamp check at validation time |

#### 28.8.3 Flight Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| F1 | No flight may transition to a state requiring a clearance without that clearance being ACTIVE | State machine transition guards |
| F2 | No two flights/vehicles may hold the same runway lock simultaneously | Mutual exclusion (follows from R1) |
| F3 | Emergency aircraft gets priority in resource queue, but cannot override physical exclusion (R1) | Emergency flag moves flight to front of lock acquisition queue. If no runway available within N seconds → mandatory Tier 3 escalation + alternate runway assignment |
| F4 | Every flight in facility airspace must have a defined state at all times | State machine completeness — no "unknown" or "untracked" state permitted |
| F5 | No aircraft may pass the Commitment Gate without a validated runway clearance | Deterministic layer forces go-around at commitment gate (~2nm) if no ARRIVAL/PATTERN lock held. Safety net-originated, not agent-proposed |
| F6 | Go-around entry must immediately notify TRACON sequencing | GO_AROUND_CLIMB state entry publishes event to TRACON. TRACON adjusts vectors for all aircraft in arrival sequence to maintain separation against the climbing go-around aircraft |

#### 28.8.4 Surveillance Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| S1 | Any aircraft/vehicle detected on a runway surface without a corresponding lock triggers immediate alert | Continuous surveillance cross-check against lock state |
| S2 | Any lock held for a runway with no detected aircraft/vehicle beyond expected time triggers alert | Continuous surveillance cross-check against lock state |
| S3 | Position data older than N seconds is discarded at the consumer, not used for any decision | Consumer-side age check — stale data silently dropped, "surveillance degraded" alert raised |
| S4 | Any aircraft in Class C airspace without a tracked state triggers alert | Surveillance detection cross-referenced against state machine — no untracked entities |

Note: S4 generalizes S1 beyond the runway surface to the entire airspace. This is the invariant that addresses the DCA scenario — the helicopter must be tracked, not invisible on a different frequency.

#### 28.8.5 Mapping to Section 27.6 Hard Invariants

| Section 27.6 Invariant | Corresponding Formal Invariant(s) |
|------------------------|----------------------------------|
| No two aircraft cleared for same runway simultaneously | R1, R2, F2 |
| No clearance issued without deterministic safety net validation | C1 |
| No surveillance data older than N seconds used for separation | C5, S3 |
| No model update applied to all instances simultaneously | (Deployment system constraint — outside state machine scope) |
| No safety-critical config change without dual authorization | (Configuration system constraint — outside state machine scope) |
| No temporary config without expiration timestamp | (Configuration system constraint — outside state machine scope) |
| No agent may issue contradicting clearance for same flight | C2, C4 |

The state machine directly enforces 4 of the 7 hard invariants. The remaining 3 are deployment/configuration constraints enforced by the maintenance tooling layer (Principles 6, 7, 8).

---

### 28.9 Parallel Runway Interactions

With two parallel runways (10L/28R and 10R/28L), operations on different runways are generally independent — each runway has its own lock. But physical proximity creates dependencies.

#### 28.9.1 Wake Turbulence Constraints

A heavy aircraft departing on 10L generates wake turbulence that drifts laterally. If runway centerline separation is less than 4,300ft, this wake can affect aircraft on the parallel runway:

```
If runway_separation < 4,300ft:
    Dependent parallel operations required
    Departures on one runway constrain arrivals on the parallel
    Staggered timing enforced by a cross-runway timing constraint
    (NOT a shared lock — separate mechanism)

If runway_separation ≥ 4,300ft:
    Independent parallel operations allowed
    Each runway's lock is fully independent
    Simultaneous arrivals permitted with appropriate monitoring (PRM)
```

Our reference facility (4,300ft separation) is at the threshold — independent ops are permitted with Precision Runway Monitor (PRM) equipment, which the surveillance system provides by default.

#### 28.9.2 Intersecting Taxi Routes

Taxiways C, D, and E cross both runways. An aircraft or vehicle taxiing from the terminal ramp to Runway 10R must cross Runway 10L. This creates a **sequential lock acquisition** requirement:

```
Taxi from gate to Runway 10R (departure):

  1. PUSHBACK_APPROVED → TAXIING_OUT on Taxiway A toward Taxiway C
  2. HOLDING_SHORT at Runway 10L hold line
  3. Agent proposes CROSSING clearance for Runway 10L
  4. Safety net: check 10L lock → AVAILABLE → VALIDATED + CROSSING lock acquired
  5. Aircraft crosses Runway 10L
  6. CLEAR_OF_RUNWAY → CROSSING lock on 10L RELEASED
  7. Continue on Taxiway C to Taxiway B
  8. HOLDING_SHORT at Runway 10R hold line
  9. Agent proposes TAKEOFF clearance for Runway 10R
  10. Safety net: check 10R lock → AVAILABLE → VALIDATED + DEPARTURE lock acquired
  11. TAKEOFF_ROLL → AIRBORNE_DEPARTURE
```

This demonstrates that a single flight may acquire and release **multiple runway locks sequentially** during its lifecycle. Each acquisition is independent and atomic. The flight never holds two runway locks simultaneously (which would create deadlock potential).

---

### 28.10 DCA/LGA Validation

Every architectural decision in this project must pass two tests: "Would this have prevented DCA?" and "Would this have prevented LGA?" Here we trace both incidents through the formal state model.

#### 28.10.1 LGA Validation (Runway Collision)

**Incident**: Air Canada 8646 (CRJ-900) landed on Runway 4 and collided with a fire truck that had been cleared to cross the active runway. Two pilots killed. Root cause: controller handling both tower and ground frequencies cleared the truck onto the runway while the aircraft was on final.

**State machine trace**: See Section 28.7.3 above for the complete trace.

**Result**: The runway mutual exclusion lock (R1, R2) makes this incident **architecturally impossible**. The fire truck's crossing clearance cannot be VALIDATED while the ARRIVAL lock is held. The system doesn't rely on a human remembering who's on final — it relies on a hardware-enforced mutex.

**Which invariants prevent it**: R1 (one lock per runway), R2 (no validation while lock held), F2 (no two entities hold same lock), C1 (no clearance without validation).

#### 28.10.2 DCA Validation (Midair Collision)

**Incident**: PSA Flight 5342 (CRJ-700) on ILS approach to Runway 33 at Reagan DCA collided with an Army Black Hawk helicopter on VFR Route 4 at approximately 300ft AGL. 67 killed. Root causes: helicopter route crossed the approach corridor, controller had combined two positions (reducing cross-check capacity), TCAS could not issue resolution advisories below ~1,000ft AGL, visual separation was relied upon at night.

**State machine trace**:

```
In the automated system:

  1. PSA 5342 (CRJ-700):
     ARRIVAL_INBOUND → SEQUENCED → VECTORING → APPROACH_CLEARED (ILS Rwy 33)
     → ESTABLISHED → TOWER_HANDOFF → INBOUND → FINAL_APPROACH → LANDING_CLEARED
     State: LANDING_CLEARED. ARRIVAL lock held on Rwy 33.

  2. Army Black Hawk (helicopter):
     Operating VFR in Class C airspace. Class C REQUIRES ATC contact.
     State: Tracked in system with defined state per invariant F4.
     The helicopter has a VFR clearance through the airspace with a defined route.
     Invariant S4: Every aircraft in Class C must have a tracked state.

  3. Collision Vector Monitor (deterministic safety net, Layer 4):
     Continuously computes closure vectors between ALL tracked aircraft.
     Helicopter on Route 4, altitude ~300ft, heading crosses Rwy 33 approach path.
     CRJ-700 on ILS Rwy 33, altitude ~300ft, 3nm from threshold.

     The CVM detects: two tracks converging, closure rate > threshold,
     projected minimum separation < required minimum.

     Action sequence:
     a. ALERT raised immediately (not advisory — safety net has veto authority)
     b. Resolution computed: instruct helicopter to hold position or deviate
     c. If helicopter does not deviate within N seconds → escalate to human overwatcher
     d. Human overwatcher receives: conflict visualization, recommended resolution,
        aircraft types, emergency checklists pre-loaded

  4. The key difference from the actual incident:
     - The human controller combined two positions → attention overloaded → didn't cross-check
     - The automated system has the Collision Vector Monitor running continuously on
       independent hardware — it CANNOT be "combined with another position"
     - The CVM doesn't rely on a human noticing two converging tracks on a display
     - It computes separation mathematically, every surveillance update cycle
```

**Result**: The DCA incident is prevented by the **combination** of:
- **F4** (every aircraft tracked — helicopter cannot be invisible on a different frequency)
- **S4** (any untracked aircraft in Class C triggers alert — helicopter must be in the system)
- **Collision Vector Monitor** (continuous separation computation, independent of agent layer)
- **Invariant C1** (no clearance without safety net validation — the helicopter's VFR route clearance would have been checked against the approach path)

**What the state machine alone does NOT prevent**: The state machine doesn't enforce airspace separation — that's the Collision Vector Monitor's job. But the state machine ensures the prerequisite: **every aircraft must have a tracked state (F4, S4)**. Without this invariant, the CVM would have nothing to compute against. The state machine makes the helicopter visible; the CVM makes the conflict detectable; the safety net veto makes the collision preventable.

---

### 28.11 Stress Testing: Thought Experiment Results

The formal state model was validated by running 7 scenarios through the state machine logic — from routine parallel operations to emergency preemption edge cases. The goal was to find gaps before implementation, not after an incident.

#### 28.11.1 Scenarios Tested

| # | Scenario | Outcome |
|---|----------|---------|
| 1 | **Normal parallel operations** — arrival on 10L, departure on 10R simultaneously | Clean. Independent locks on independent runways. No interaction. |
| 2 | **Aborted takeoff with arrival on short final** — SWA 223 aborts on 10L, AAL 100 at 2nm on approach to 10L | **Gap found**: Safety net correctly rejects landing clearance (runway locked), but nothing forces a go-around. Aircraft approaches without clearance. |
| 3 | **Race condition** — two agents propose conflicting clearances for 10L simultaneously | Clean — atomic check-and-lock serializes. First proposal wins, second is rejected. Requires per-runway mutex. |
| 4 | **Go-around cascade** — AAL 100 goes around from 10L, UAL 445 being vectored for same runway behind | Clean for state machine. CVM handles airspace separation. **Found**: go-around entry must notify TRACON immediately so it adjusts vectors for sequenced traffic. |
| 5 | **VFR pattern vs IFR arrival** — N12345 on pattern final, JBU 602 on approach, timing squeeze | **Same gap as #2**: VFR in PATTERN_FINAL with locked runway needs mandatory wave-off. Also revealed pre-emptive sequencing need (extend downwind BEFORE conflict). |
| 6 | **Emergency preemption** — AAL 100 (engine fire) needs 10L, DAL 812 in takeoff roll on 10L | **Found invariant conflict**: F3 (emergency priority) vs R1 (one lock per runway). Cannot clear emergency to land on occupied runway. F3 was too broad. |
| 7 | **Sequential cross-field taxi** — multiple aircraft crossing runways to reach departure positions | Clean. No deadlock — flights never hold two runway locks simultaneously. Sequential acquisition with release between. |

#### 28.11.2 Gaps Found and Fixes Applied

**Gap 1 (Critical): No forcing function for go-around when runway is locked**

The state machine prevents issuing a landing clearance on a locked runway (correct), but doesn't force a go-around for an aircraft already approaching. This violates Principle 2: relying on agents to "notice" and propose a go-around is "pay more attention."

**Fix**: The Approach Commitment Gate (Section 28.5.6) — a token-based flow control model inspired by Cisco VOQ credit-based switching. The runway lock is the "token." An aircraft cannot pass the commitment gate (~2nm) without holding the token. If it reaches the gate without a validated landing clearance, the deterministic safety layer (not the agents) forces a go-around. An advisory gate at ~5nm gives agents time to re-sequence traffic before the commitment gate fires. Formalized as invariant **F5**.

**Gap 2 (Medium): F3 (emergency priority) conflicts with R1 (one lock per runway)**

F3 as originally written — "No flight in EMERGENCY_DECLARED may be denied priority resource access" — implies emergency could override the runway mutex. Clearing an emergency aircraft to land on an occupied runway would cause a collision.

**Fix**: F3 refined to: emergency gets **priority in the queue** (front of lock acquisition), not override of physical exclusion. If no runway is available within N seconds, mandatory Tier 3 escalation + alternate runway assignment. R1 always wins over F3 — physics is not negotiable.

**Gap 3 (Low): Go-around must notify TRACON**

When an aircraft enters GO_AROUND_CLIMB, it's climbing into TRACON's airspace on the missed approach. TRACON needs immediate notification to adjust vectors for aircraft in the arrival sequence. The CVM provides backup (continuous separation monitoring), but TRACON's sequencing agent needs the information proactively.

**Fix**: Formalized as invariant **F6** — GO_AROUND_CLIMB entry must publish an event to the TRACON sequencing agent, which immediately re-evaluates vectors for all aircraft in the arrival sequence.

**Gap 4 (Design note): Safety net must serialize per runway**

The atomic check-and-lock assumes a single mutex per runway. If multiple safety net nodes on different hardware can independently check the same runway's lock state with separate lock stores, the race condition from Scenario 3 reappears.

**Note**: The runway lock state must reside in shared memory accessible to all safety net instances, with a per-runway mutex. This is an implementation constraint on the deterministic layer's hardware architecture — the lock store is the single source of truth.

**Gap 5 (Sequencing note): Pre-emptive VFR sequencing**

Scenario 5 showed that the commitment gate is a backstop, not the primary defense. The primary defense is sequencing: extending a VFR aircraft's downwind leg BEFORE it turns base, once the system knows an IFR arrival is inbound. If the sequencing agent fails, the commitment gate catches it.

**Note**: The sequencing agent must look ahead at the runway lock timeline and pre-emptively delay VFR pattern traffic when IFR arrivals are inbound. This is an agent responsibility with the commitment gate as the deterministic backup — defense in depth.

#### 28.11.3 State Model Completeness Assessment

After fixes:
- **19 formal invariants** (R1–R4, C1–C5, F1–F6, S1–S4)
- **All 7 scenarios** resolve safely under the corrected model
- **Both case studies** (DCA, LGA) are provably prevented
- **The forcing function gap** (the most critical finding) is closed by the Approach Commitment Gate — a deterministic, agent-independent backstop that converts "the agent should notice" into "the system physically prevents"

The next validation step is formal verification in Ada/SPARK: prove that the invariants are consistent (no two invariants can conflict), complete (no reachable state violates safety), and that the state machine is deadlock-free.

---

## 29. Deterministic Safety Net Interface

The deterministic safety net is the most critical boundary in the system. It sits between agent intelligence (LLM-driven, probabilistic, potentially wrong) and real-world consequences (clearances transmitted to pilots, aircraft moving). Every clearance must pass through this interface. No bypass exists. This is Principle 4 made concrete: the deterministic layer is the floor.

The safety net runs on **separate physical hardware** from the agents — TMR on INTEGRITY-178/VxWorks 653, implemented in Ada/SPARK, connected to the agent cluster (DGX Spark, Linux) via dual-redundant fiber. The "atomic check-and-lock" from Section 28.5.4 is implemented as a synchronous RPC call to the safety net, which serializes all proposals per runway on its own hardware.

---

### 29.1 Interface Overview

The safety net has three distinct roles, each requiring a different interface:

| Role | Direction | Protocol | Purpose |
|------|-----------|----------|---------|
| **Clearance Validator** | Agent → Safety Net → Agent | Synchronous RPC | Agent proposes, safety net approves or rejects. The data path — no clearance reaches a pilot without this call succeeding. |
| **Continuous Monitor** | Safety Net → System | Autonomous (event-driven) | CVM, commitment gates, negative-space monitoring. Safety net watches for danger and originates actions independently, without any agent requesting them. |
| **State Provider** | Safety Net → Agents | Pub-sub + on-demand RPC | Publishes runway lock state, flight states, clearance states. Agents subscribe to make informed proposals. |

Design principles for this interface:

1. **The safety net is the single source of truth** for all lock state, flight state, and clearance state. Agents do not maintain independent copies — they subscribe to the safety net's published state.
2. **Validation and lock acquisition are atomic** — a single call to the safety net either validates AND acquires the lock, or rejects. No two-step process.
3. **Fail-safe on communication failure** — if agents lose contact with the safety net, no clearances can be issued (C1 enforced). The safety net continues monitoring independently.
4. **All clearances use TCP-style reliable delivery** — the readback is the ACK. No clearance operates in UDP mode.

---

### 29.2 Clearance Validation API

#### 29.2.1 Request: ClearanceProposal

The agent submits a structured proposal. The safety net validates it against all applicable invariants and, if approved, atomically acquires any required resource locks.

```
ClearanceProposal {
    // Identity
    proposal_id:        UUID            — unique, for audit trail
    proposing_agent:    AgentID         — which agent instance
    timestamp:          Timestamp       — when the agent decided

    // Target
    target_entity:      EntityID        — flight_id or vehicle_id
    target_entity_type: AIRCRAFT | VEHICLE

    // Clearance
    clearance_type:     ClearanceType   — enum of 22 types (Section 28.6.2)
    parameters: {
        runway:         RunwayID?       — required for lock-acquiring clearances
        taxi_route:     TaxiRoute?      — taxiway segments + hold-short points
        heading:        Degrees?        — vectoring clearances
        altitude:       Feet?           — altitude assignments
        speed:          Knots?          — speed assignments
        approach_type:  ILS | RNAV | VISUAL?
        frequency:      MHz?            — frequency changes
        supersedes:     ClearanceID?    — if replacing an active clearance (C4)
    }

    // Evidence — the surveillance data the agent used
    surveillance_refs: [{
        source:         ADSB | RADAR | MLAT | SURFACE
        entity:         EntityID
        position:       LatLonAlt
        velocity:       Vector3D
        timestamp:      Timestamp       — checked against C5/S3
    }]
}
```

The `surveillance_refs` field serves two purposes: the safety net checks data age (C5 — reject if any referenced position is older than N seconds), and it creates an audit trail of what the agent saw when it made the decision.

#### 29.2.2 Response: ValidationResult

```
ValidationResult {
    proposal_id:        UUID            — echoed from request
    result:             VALIDATED | REJECTED
    timestamp:          Timestamp       — when the safety net decided

    // On VALIDATED:
    clearance_id:       ClearanceID?    — system-assigned, all future references
    lock_acquired: {
        runway_id:      RunwayID?
        lock_type:      LockType?
        ttl:            Seconds
    }?

    // On REJECTED:
    rejection: {
        invariants_violated:  [InvariantID]  — e.g., ["R1", "R2"]
        reason:               String          — human-readable
        blocking_entity:      EntityID?       — who holds the conflicting lock
        blocking_clearance:   ClearanceID?    — which clearance holds it
    }?

    // Always included (saves the agent a follow-up query):
    runway_state: {
        runway_id:      RunwayID
        lock_status:    AVAILABLE | RESERVED | OCCUPIED
        holder:         EntityID?
        lock_type:      LockType?
        ttl_remaining:  Seconds?
    }?
}
```

On rejection, the response includes `blocking_entity` and `blocking_clearance` so the agent can make an informed next decision (wait for the lock to release, propose an alternate runway, or re-sequence traffic) without needing a separate state query.

#### 29.2.3 Invariants Checked Per Clearance Type

| Clearance Type | Invariants Checked | Lock Action |
|---|---|---|
| Landing Clearance | R1, R2, C1, C2, C5, F1, F2 | Acquires ARRIVAL lock |
| Takeoff Clearance | R1, R2, C1, C2, C5, F1, F2 | Acquires DEPARTURE lock (or upgrades LUAW) |
| Line Up and Wait | R1, R2, C1, C2, F1, F2 | Acquires LUAW lock |
| Runway Crossing | R1, R2, C1, C5, F2 | Acquires CROSSING lock |
| Touch-and-Go | R1, R2, C1, C2, F1, F2 | Acquires PATTERN lock |
| Stop-and-Go | R1, R2, C1, C2, F1, F2 | Acquires PATTERN lock |
| Low Approach | R1, R2, C1, C2, F1, F2 | Acquires PATTERN lock |
| Go-Around | C1, C2, C4 | **Releases** ARRIVAL lock. C4: must reference superseded clearance |
| Taxi Clearance | C1, C2, F1 | No runway lock (reserves taxi route) |
| IFR Clearance | C1, C2, F1 | No lock |
| Approach Clearance | C1, C2, C5, F1 | No lock (CVM checks approach path) |
| Vectoring Clearance | C1, C5 | No lock (CVM checks projected path) |
| Frequency Change | C1 | Minimal — housekeeping |

All clearance types additionally check C5 (surveillance data age) when position data is referenced.

Additionally, for clearances that don't acquire runway locks (vectoring, approach clearance), the CVM performs a **trajectory conflict check** — "if I give this heading/altitude to this aircraft, does the projected 4D volume intersect with any other aircraft's volume?" This is not an invariant check (it's predictive, not absolute), but a rejection reason of "CVM conflict detected" is possible.

#### 29.2.4 Serialization Model

The safety net serializes all proposals **per runway**. Proposals for different runways are processed in parallel. Proposals for the same runway pass through a per-runway mutex.

Agents fire proposals without coordinating with each other. The safety net handles contention — if two agents race for the same runway lock, the first to reach the mutex wins. The second gets REJECTED and re-evaluates. This is by design: agents are loosely coupled, the safety net is the coordination point.

For non-runway clearances (vectoring, approach, taxi), serialization is per-entity — two agents cannot propose conflicting clearances for the same flight simultaneously. The per-entity mutex prevents C2 violations.

---

### 29.3 State Query API

Agents need current state to make intelligent proposals. Blindly proposing and relying on rejections wastes cycles and loads the safety net unnecessarily.

#### 29.3.1 Pub-Sub State Feed

The safety net publishes state changes on a dual-redundant message bus. Agents subscribe to topics they need.

```
Topic: runway.{runway_id}.lock_changed
    When: Lock acquired, released, TTL warning
    Payload: RunwayLockState {
        runway_id, lock_status, lock_type, holder,
        ttl_remaining, clearance_id, timestamp
    }

Topic: flight.{flight_id}.state_changed
    When: Flight transitions to new state in the state machine
    Payload: FlightState {
        flight_id, phase, state, runway_assignment,
        active_clearances: [ClearanceID],
        emergency: bool, position, velocity, timestamp
    }

Topic: clearance.{clearance_id}.state_changed
    When: Clearance transitions (VALIDATED → ISSUED → ACTIVE, etc.)
    Payload: ClearanceState {
        clearance_id, clearance_type, target_entity,
        state, lock_held: RunwayLockState?, timestamp
    }

Topic: surveillance.{entity_id}.position_update
    When: New position fix from any source
    Payload: SurveillanceUpdate {
        entity_id, source, position, velocity, altitude,
        timestamp, age_ms
    }

Topic: alert.{alert_type}
    When: Safety net detects anomaly
    Payload: Alert {
        alert_id, alert_type, severity, affected_entities,
        description, recommended_action, timestamp
    }
```

#### 29.3.2 On-Demand Query RPC

Synchronous queries for specific state. Used for initialization, recovery after restart, or when an agent needs a consistent snapshot.

```
GetRunwayState(runway_id)         → RunwayLockState
GetFlightState(flight_id)         → FlightState
GetActiveClearances(entity_id)    → [ClearanceState]
GetAllRunwayStates()              → [RunwayLockState]
GetApproachQueue(runway_id)       → [FlightState]   — ordered arrival sequence
```

#### 29.3.3 Data Freshness

State published on the bus is **authoritative** — it reflects the safety net's internal state, the single source of truth. But agents must treat received state as potentially stale (network delay). An agent that received "10L AVAILABLE" 500ms ago should not assume it's still available — it should propose and handle rejection gracefully.

The state feed enables **informed decision-making**. Only the validation API provides **guarantees** (via atomic check-and-lock).

---

### 29.4 Safety Net Originated Actions

The safety net doesn't just validate — it independently monitors for dangerous conditions and originates actions without any agent requesting them. These actions bypass the agent proposal pipeline but follow the same clearance lifecycle from VALIDATED onward.

#### 29.4.1 TCP-Style Reliable Delivery

Every clearance — agent-proposed or safety-net-originated — uses reliable delivery modeled on TCP. The pilot readback is the ACK. No clearance operates in UDP mode.

```
VALIDATED → ISSUED (SYN — instruction transmitted via TTS/radio)
         → Wait for readback (ACK timeout: ~5 seconds)
         │
         ├─ READBACK_OK (ACK received, correct) → ACTIVE
         │
         ├─ READBACK_FAIL (ACK received, incorrect)
         │    → Re-issue from VALIDATED (correct the misunderstanding)
         │
         └─ NO_RESPONSE (ACK timeout, no readback heard)
              → Retransmit (up to 3 attempts, ~5 sec each)
              → After max retries: ESCALATE
                   • Alert: "Clearance unacknowledged after 3 attempts"
                   • Human overwatcher takes over voice communications
                   • CVM alerted: this aircraft may not comply
                   • Lock HELD — system sequences as if aircraft complying,
                     but surveillance monitors for deviation
                   • If aircraft deviates from expected behavior
                     (e.g., continues approach instead of going around):
                     → CVM computes new conflict vectors
                     → Tier 3 separation response if needed
```

| TCP Concept | ATC Clearance Equivalent |
|-------------|--------------------------|
| SYN | ISSUED — instruction transmitted |
| ACK | READBACK_OK — pilot confirms understanding |
| Retransmit on timeout | Re-issue after ~5 seconds of silence |
| RST after max retries | Escalate to human — "connection failed" |
| Data in flight | Lock held, system assumes compliance, monitors for deviation |

The safety net does not get to skip the ACK for its own originated actions. A go-around instruction that the pilot didn't hear is no better than no instruction at all.

#### 29.4.2 Commitment Gate Go-Around (F5)

```
Trigger:    Aircraft reaches commitment gate (~2nm from threshold)
            WITHOUT a validated landing clearance, AND the runway
            is locked by another entity.

Action:     Safety net generates a Go-Around Instruction.

Lifecycle:  Enters clearance lifecycle at VALIDATED (not PROPOSED —
            the safety net is the validator, it doesn't need to validate
            its own instruction). Then follows full TCP-style delivery:
            ISSUED → readback wait → retransmit if needed → ACTIVE.

Lock effect: If the approaching aircraft held a lock (shouldn't at
             commitment gate, but defensive check), it is released.

Notification: GO_AROUND event published on event bus (F6).
              TRACON sequencing agent receives immediately and
              adjusts vectors for all aircraft in the arrival sequence.

Priority:   Safety-net-originated actions take priority over
            agent-proposed actions in the TTS/radio queue.
```

#### 29.4.3 Collision Vector Monitor — 4D Trajectory Prediction

The CVM runs continuously on TMR hardware, independently of the agent layer. It does NOT use simple distance thresholds — raw proximity triggers too many false positives in a terminal environment where aircraft are routinely close together (parallel approaches at 0.7nm, pattern traffic at 1-2nm).

Instead, the CVM computes **4D conflict volumes** (3D space + time) using predictive trajectory modeling:

```
For each tracked aircraft, every surveillance update cycle:

  1. CURRENT STATE
     Position (lat/lon/alt), velocity (3D vector), acceleration

  2. AIRCRAFT PERFORMANCE MODEL
     Type-specific: climb rate, turn rate, approach speed,
     takeoff acceleration profile, descent rate
     (e.g., CRJ-700 rotating at 140kt → 250kt, climbing 2,500fpm
      vs. Cessna 172 at 90kt, climbing 500fpm)

  3. CLEARANCE INTENT
     Active clearance defines the expected trajectory:
     - Departure: runway heading → assigned heading, climb to assigned alt
     - Approach: ILS/RNAV path (3D, precisely defined)
     - Pattern: rectangular legs at pattern altitude
     - Vector: assigned heading/altitude/speed

  4. PROJECTED VOLUME
     Compute predicted position at T+10, T+20, T+30... T+120 seconds.
     Each prediction has an uncertainty cone that widens with time.
     The volume is the swept 3D space over the prediction window.

  5. CONFLICT DETECTION
     For every pair of projected volumes:
     - Do they intersect within the prediction window?
     - If yes: is the intersection EXPECTED (parallel approaches,
       sequenced arrivals) or UNEXPECTED (deviation from clearance)?
     - Only UNEXPECTED intersections generate alerts.
```

**Clearance-aware detection eliminates false positives**: Two aircraft on parallel ILS approaches, 4,300ft apart laterally, converging toward the airport? Expected — no alert. One of those aircraft drifting 500ft off the localizer toward the parallel approach? The CVM detects the deviation from the expected ILS path AND projects that the deviation creates an intersection with the other approach volume. Alert fires at 120 seconds out.

**Three-axis resolution**: When a conflict is detected, the CVM computes resolution options across all three spatial dimensions — lateral (heading change), vertical (altitude change), and speed (buys time). The computer evaluates all axes simultaneously and picks the optimal resolution. At low altitude (<1,000ft AGL), vertical options are limited (the DCA problem — TCAS can't help below 1,000ft). The CVM's advantage: it sees the conflict minutes earlier, when the aircraft are at altitudes where vertical separation is still available.

**Escalation tiers** (time-to-conflict OR distance, whichever threshold is reached first):

```
Tier 1 — ADVISORY (< 5nm OR < 90 sec to projected conflict):
    Published as: alert.separation_advisory
    Payload: conflict geometry, affected aircraft, resolution options
    Action: Notify agents. Agents should resolve (re-vector, re-sequence).
    No direct action by safety net — agents have time.
    90-second window is viable because clearance-aware detection has
    already filtered expected proximity. If this fires, it's real.

Tier 2 — WARNING (< 3nm OR < 45 sec to projected conflict):
    Published as: alert.separation_warning
    Action: Agents failed to resolve after advisory. Safety net
    originates a resolution clearance (heading, altitude, or speed
    change) for the lower-priority aircraft.
    Clearance enters lifecycle at VALIDATED. Full TCP delivery.

Tier 3 — CRITICAL (< 1nm OR < 15 sec to projected conflict):
    Published as: alert.separation_critical
    Action: Safety net issues IMMEDIATE resolution to BOTH aircraft.
    Escalates to Tier 3 (human overwatcher with AI assistant).
    All agent-proposed clearances for affected aircraft are FROZEN
    until human confirms resolution.
```

Both thresholds (distance AND time) are checked because we have continuous surveillance data providing both position and velocity. Time-to-conflict accounts for closure rate (two aircraft at 5nm closing at 500kt are far more urgent than at 100kt). Distance catches cases where velocity data is unreliable or aircraft are drifting slowly. Whichever threshold fires first triggers the tier.

#### 29.4.4 Negative-Space Monitoring

Alerts when **expected activity is absent** — the things that should be happening but aren't.

| Monitor | Trigger | Action |
|---------|---------|--------|
| NSM-1 | Aircraft in FINAL_APPROACH > N sec without LANDING_CLEARED | Alert agents (advisory gate handles before commitment gate fires) |
| NSM-2 | TOWER_HANDOFF issued > N sec ago, flight never reached INBOUND | Alert — possible comm failure, lost aircraft |
| NSM-3 | Lock held > TTL with no surveillance detection on runway | Alert per R4 (TTL expiration) |
| NSM-4 | No state transition for flight > N sec when one is expected | Alert — stuck aircraft, surveillance failure, or state machine error |
| NSM-5 | Aircraft in LANDING_CLEARED but increasing altitude | Alert — possible unreported go-around, surveillance anomaly |
| NSM-6 | Clearance in ISSUED > N sec without READBACK_OK or READBACK_FAIL | Alert — no ACK received (TCP timeout) |

#### 29.4.5 Advisory Gate Notifications

```
Trigger:    Aircraft crosses advisory gate (~5nm / FAF) AND
            the target runway is locked by another entity.

Published:  alert.runway_unavailable
Payload:    runway_id, lock_holder, estimated_time_to_available,
            approaching_flight_id, distance_to_commitment_gate

Purpose:    Gives agents ~60 seconds to re-sequence traffic
            (extend downwind, slow approach, assign alternate runway)
            before the commitment gate forces a go-around.
```

#### 29.4.6 Priority Rules

When the safety net originates an action, it takes priority over agent-proposed clearances:

| Priority | Source | Example |
|----------|--------|---------|
| 1 (highest) | CVM Tier 3 | Critical separation — immediate resolution to both aircraft |
| 2 | Commitment Gate (F5) | Forced go-around — aircraft at 2nm, no clearance, runway locked |
| 3 | CVM Tier 2 | Separation warning — safety net resolution for one aircraft |
| 4 | Agent-proposed | Normal clearances through the validation API |
| 5 (lowest) | CVM Tier 1 | Advisory — informational, agents handle |

If a safety-net-originated action and an agent proposal compete for the same runway lock, the safety net action wins. The agent proposal is REJECTED with reason "preempted by safety net action."

---

### 29.5 Event Bus Architecture

The event bus is the system's nervous system. All state changes, alerts, and notifications flow through it.

#### 29.5.1 Topology

```
                    ┌───────────────────────────┐
                    │     Event Bus             │
                    │     (dual-redundant)      │
                    └──┬───┬───┬───┬───┬───┬──┘
                       │   │   │   │   │   │
            ┌──────────┘   │   │   │   │   └──────────┐
            ▼              ▼   │   ▼   ▼              ▼
     Safety Net      TRACON  │  Tower  Ground     Human
     (pub + sub)     Agents  │  Agents Agents    Overwatcher
                             ▼                    Display
                      Surveillance
                       Ingest
```

- **Publishers**: Safety net (lock changes, alerts, originated actions), surveillance ingest (position updates), agents (proposals — for audit logging only)
- **Subscribers**: All agents, human overwatcher display, audit log, monitoring systems, data recorders (45-day retention per FAA 7210.3)
- **Dual redundant**: Two independent bus instances on separate physical networks. Every message published to both. Consumers deduplicate by message_id.

#### 29.5.2 Message Format

```
EventMessage {
    message_id:     UUID            — unique, for deduplication
    topic:          String          — hierarchical (e.g., "runway.10L.lock_changed")
    timestamp:      Timestamp       — when the event occurred (not when published)
    source:         ComponentID     — who published
    payload:        TypedPayload    — schema determined by topic
    sequence_num:   uint64          — per-topic monotonic counter
}
```

#### 29.5.3 Ordering Guarantees

Events on the **same topic** are ordered by sequence_num (monotonically increasing). Cross-topic ordering is NOT guaranteed — components use timestamps for cross-topic correlation. This matches the per-runway serialization model: events about 10L are totally ordered, events about 10R are totally ordered, their interleaving is non-deterministic.

---

### 29.6 Hardware Boundary and Communication

#### 29.6.1 Physical Architecture

```
┌──────────────────────────────────────────────────────────┐
│  SAFETY NET HARDWARE (TMR)                               │
│  RTOS: INTEGRITY-178 / VxWorks 653 (DO-178C DAL A)      │
│  Language: Ada/SPARK (formally verified)                  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Channel A │  │Channel B │  │Channel C │  ← TMR       │
│  │ CVM      │  │ CVM      │  │ CVM      │    channels  │
│  │ Locks    │  │ Locks    │  │ Locks    │              │
│  │ Invariant│  │ Invariant│  │ Invariant│              │
│  │ checks   │  │ checks   │  │ checks   │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       └──────────────┼──────────────┘                    │
│                 TMR Voter (2-of-3)                       │
│                      │                                   │
│            Validation API endpoint                       │
│            State Query endpoint                          │
│            Event Bus publisher                           │
│            TTS/Radio pipeline (direct, not via agents)   │
└──────────────────────┬───────────────────────────────────┘
                       │ Dual redundant fiber
                       │ TSN (IEEE 802.1, deterministic Ethernet)
┌──────────────────────┴───────────────────────────────────┐
│  AGENT HARDWARE (DGX Spark cluster)                      │
│  RTOS: Linux PREEMPT_RT (non-safety-critical)            │
│  Languages: Python/ONNX (inference), Rust (IPC/comms)    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Tower    │  │ TRACON   │  │ Ground   │  ← agents    │
│  │ Agents   │  │ Agents   │  │ Agents   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│         │            │            │                      │
│         Rust IPC layer                                   │
│         (proposals → fiber out, state ← fiber in)        │
└──────────────────────────────────────────────────────────┘
```

The safety net has a **direct connection to the TTS/radio pipeline** for safety-net-originated actions (commitment gate go-arounds, CVM resolutions). These do not route through agents — the safety net can speak to pilots independently.

#### 29.6.2 Communication Protocols

| Interface | Protocol | Transport | Timeout |
|-----------|----------|-----------|---------|
| Clearance Validation | Synchronous RPC | TSN (deterministic Ethernet) | 10ms — no response = REJECTED (fail-safe) |
| State Feed | Pub-sub | UDP multicast, sequence-numbered | N/A (continuous) |
| On-Demand Query | Synchronous RPC | TSN | 10ms |
| Safety Net Actions | Direct to TTS/radio + event bus publish | Dedicated fiber channel | N/A (originated locally) |

#### 29.6.3 Fail-Safe Behavior

**If agent-to-safety-net link fails:**
- Agents cannot propose any clearances → fail-safe (C1: no clearance without validation)
- Safety net continues monitoring independently (CVM, commitment gates, negative-space)
- Safety net can still originate actions via direct TTS/radio connection
- Immediate Tier 3 escalation (human overwatcher takes primary control)
- System is degraded but safe — no unauthorized clearances possible

**If one TMR channel fails:**
- Degraded to 2-of-3 voting. Remaining channels mask the fault transparently.
- Alert published on event bus: "Safety net degraded — TMR Channel [A|B|C] offline"
- Operations continue normally. Maintenance dispatched.

**If two TMR channels fail:**
- System goes to **ATC-Zero** — all automated operations halted
- Human overwatcher assumes full control
- No silent degradation — the system never operates with less than 2-of-3 agreement
- Alert: "SAFETY NET CRITICAL — ATC-Zero declared, human control required"

**No silent failure**: Safety net health is continuously published on the event bus. The human overwatcher display shows safety net status at all times (all three channels healthy, one degraded, etc.). A safety net that reports "healthy" when it's not is the most dangerous failure mode — health reporting itself runs on independent monitoring hardware.

---

### 29.7 Latency Budget

End-to-end timing from agent decision to pilot hearing the instruction:

```
Component                           Latency        Cumulative
────────────────────────────────────────────────────────────
Agent computes proposal              0 ms           T+0
Network: Agent → Safety Net          ~0.2 ms        T+0.2
Invariant checks (Ada/SPARK)         ~1-3 ms        T+1.5
Lock acquisition (local mutex)       ~0.1 ms        T+1.6
Network: Safety Net → Agent          ~0.2 ms        T+1.8
Agent receives VALIDATED             ~2 ms total    T+2.0
────────────── validation complete ──────────────
Agent submits to TTS pipeline        ~0.5 ms        T+2.5
TTS synthesis (Kokoro/Piper)         ~100-200 ms    T+150
Radio transmission                   ~50 ms         T+200
────────────── pilot hears instruction ──────────
Pilot readback                       ~2-4 sec       T+3000
STT processing (Whisper)             ~100-200 ms    T+3200
Readback verification                ~1-2 ms        T+3202
READBACK_OK → ACTIVE                 ~0.5 ms        T+3203
────────────── clearance confirmed ──────────────
```

The safety net validation is **<5ms**. The bottleneck is the human in the loop (readback takes 2-4 seconds), which is irreducible but expected. The lock is held from the moment VALIDATED returns (~2ms), so the runway is protected the instant the safety net approves — the remaining pipeline (TTS, readback) confirms the pilot received the instruction but does not affect the safety guarantee.

For safety-net-originated actions, the path is shorter — no agent round-trip:

```
Safety net detects condition          0 ms
Safety net generates clearance        ~1 ms
Direct to TTS pipeline               ~0.5 ms
TTS synthesis                         ~100-200 ms
Radio transmission                    ~50 ms
Pilot hears instruction               ~150-250 ms total
```

---

### 29.8 Data Schemas

Complete schema definitions for all structured types used across the interface.

```
// === Identifiers ===

EntityID:       String          — "UAL445", "DAL812", "TRUCK-7"
AgentID:        String          — "tower-local-1", "tracon-approach-2"
ClearanceID:    String          — "CLR-2026-0324-14523" (date + sequence)
RunwayID:       String          — "10L", "28R", "10R", "28L"
ComponentID:    String          — "safety-net-A", "cvm-voter", "tower-agent-1"

// === Enums ===

ClearanceType:  enum {
    IFR_CLEARANCE, PUSHBACK_APPROVAL, TAXI_OUT, HOLD_SHORT,
    LINEUP_WAIT, TAKEOFF, LANDING, GO_AROUND, TAXI_IN,
    RUNWAY_CROSSING, APPROACH_CLEARANCE, VECTORING,
    SEQUENCE_ASSIGNMENT, ALTITUDE_HEADING_ASSIGNMENT,
    PATTERN_ENTRY, TOUCH_AND_GO, STOP_AND_GO, LOW_APPROACH,
    SEQUENCE_INSTRUCTION, FREQUENCY_CHANGE, HOLD_POSITION
}

LockType:       enum { DEPARTURE, ARRIVAL, CROSSING, LUAW, PATTERN }
LockStatus:     enum { AVAILABLE, RESERVED, OCCUPIED }
ClearanceState: enum { PROPOSED, VALIDATED, REJECTED, ISSUED,
                       READBACK_OK, READBACK_FAIL, NO_RESPONSE,
                       ACTIVE, COMPLETED, CANCELLED, SUPERSEDED, EXPIRED }
AlertSeverity:  enum { ADVISORY, WARNING, CRITICAL }
SurveillanceSource: enum { ADSB, RADAR, MLAT, SURFACE }

// === Composite Types ===

LatLonAlt: {
    latitude:   float64         — decimal degrees
    longitude:  float64         — decimal degrees
    altitude:   int32           — feet MSL
}

Vector3D: {
    ground_speed:   float32     — knots
    heading:        float32     — degrees true
    vertical_rate:  float32     — feet per minute (+ = climb)
}

TaxiRoute: {
    segments:       [String]    — ["A", "C", "B"] (taxiway identifiers)
    hold_short:     [RunwayID]  — runways to hold short of
}

RunwayLockState: {
    runway_id:      RunwayID
    lock_status:    LockStatus
    lock_type:      LockType?
    holder:         EntityID?
    clearance_id:   ClearanceID?
    acquired_at:    Timestamp?
    ttl_remaining:  Seconds?
}

FlightState: {
    flight_id:          EntityID
    phase:              String      — "PRE_DEPARTURE", "GROUND_OUT", etc.
    state:              String      — "PARKED", "TAXIING_OUT", etc.
    runway_assignment:  RunwayID?
    active_clearances:  [ClearanceID]
    emergency:          bool
    position:           LatLonAlt
    velocity:           Vector3D
    timestamp:          Timestamp
}

Alert: {
    alert_id:           UUID
    alert_type:         String      — "separation_advisory", "runway_unavailable", etc.
    severity:           AlertSeverity
    affected_entities:  [EntityID]
    description:        String
    recommended_action: String?
    resolution_options: [ResolutionOption]?
    timestamp:          Timestamp
}

ResolutionOption: {
    target_entity:  EntityID
    action:         String          — "turn_left_30", "climb_to_4000", "reduce_speed_180"
    axis:           LATERAL | VERTICAL | SPEED
    projected_resolution_time: Seconds
}
```

---

## 30. Sources

### Pilot-ATC Communication Protocol
- [FAA AIM Chapter 4: Air Traffic Control](https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap4_section_2.html)
- [FAA AIM Chapter 5: Air Traffic Procedures](https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap5_section_2.html)
- [FAA AIM Chapter 6: Emergency Procedures](https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap6_section_3.html)
- [FAA Order 7110.65BB: Air Traffic Control](https://www.faa.gov/air_traffic/publications/atpubs/atc_html/)
- [14 CFR 91.123: Compliance with ATC Clearances](https://www.ecfr.gov/current/title-14/section-91.123)
- [14 CFR 91.185: IFR Lost Communications](https://www.ecfr.gov/current/title-14/section-91.185)
- [AC 90-117: Data Communications (CPDLC/DCL)](https://www.faa.gov/regulations_policies/advisory_circulars)

### ATC Certification and Training
- [FAA Order JO 3120.4S: Air Traffic Technical Training](https://www.faa.gov/documentLibrary/media/Order/FAA_Order_JO_3120.4S.pdf)
- [National Academies: Performance Assessment, Selection, and Training](https://www.nationalacademies.org/read/5493/chapter/5)
- [FAA: Air Traffic Controller Qualifications](https://www.faa.gov/air-traffic-controller-qualifications)

### Emergency Procedures
- [FAA 7110.65 Chapter 10: Emergencies](https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap_10.html)
- [FAA AIM Section 6-3: Distress and Urgency Procedures](https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap6_section_3.html)
- [Emergency Communications - SKYbrary](https://skybrary.aero/articles/emergency-communications)
- [Declaring an Emergency - Boldmethod](https://www.boldmethod.com/learn-to-fly/regulations/what-happens-when-you-declare-an-emergency-with-atc/)

### LaGuardia Incident (March 23, 2026)
- [LaGuardia Collision Explained - ABC7](https://abc7ny.com/post/laguardia-air-canada-plane-emergency-truck-collision-explained-how-did-cross-paths-runway/18754668/)
- [Air Canada Jet Collides with Firetruck - NPR](https://www.npr.org/2026/03/23/g-s1-114773/laguardia-air-canada-plane-collision-fire-truck)
- [LaGuardia Collision - Washington Post](https://www.washingtonpost.com/transportation/2026/03/23/us-airport-laguardia-air-canada-plane/)

### Local / Air-Gapped Model Deployment
- [Running LLMs in Air-Gapped Environments (2026)](https://dasroot.net/posts/2026/03/running-llms-air-gapped-environments/)
- [Enterprise Local LLM Deployment Guide 2026](https://www.sitepoint.com/the-2026-definitive-guide-to-running-local-llms-in-production/)
- [Best Open Source STT Models 2026 - Northflank](https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks)
- [Top Open-Source Speech-to-Text Models 2026 - Resemble AI](https://www.resemble.ai/open-source-ai-speech-to-text-models/)

### FAA Official Sources
- [FAA: NextGen](https://www.faa.gov/nextgen)
- [FAA: ERAM Overview](https://www.faa.gov/air_traffic/technology/eram)
- [FAA: STARS/TAMR](https://www.faa.gov/air_traffic/technology/tamr)
- [FAA: SWIM Overview](https://www.faa.gov/air_traffic/technology/swim/overview)
- [FAA: SWIM Cloud Distribution Service](https://www.faa.gov/air_traffic/technology/swim/products/get_connected)
- [FAA: ADS-B FAQ](https://www.faa.gov/air_traffic/technology/equipadsb/resources/faq)
- [FAA: BNATCS Fact Sheet](https://www.faa.gov/newsroom/brand-new-air-traffic-control-system-bnatcs-fact-sheet)
- [FAA: Controller Workforce Plan 2025-2028](https://www.faa.gov/about/office_org/headquarters_offices/afn/offices/finance/offices/office-financial-labor-analysis/plans/controller-workforce.pdf)
- [FAA: ATC Hiring](https://www.faa.gov/atc-hiring)
- [FAA: Separation Standards](https://www.faa.gov/air_traffic/separation_standards)

### Government Oversight
- [GAO-24-107001: FAA Aging Systems](https://www.gao.gov/products/gao-24-107001)
- [GAO-25-108162: Urgent Modernization](https://www.gao.gov/products/gao-25-108162)
- [DOT OIG: NextGen Capstone Report](https://www.oig.dot.gov/sites/default/files/library-items/NextGen%20Capstone%20Memo_9-29-25.pdf)

### EUROCONTROL / SESAR
- [EUROCONTROL: ASTERIX](https://www.eurocontrol.int/asterix)
- [SESAR Joint Undertaking: ATM Master Plan 2025](https://www.sesarju.eu/MasterPlan2025)
- [EUROCONTROL: AI and Digitalisation in ATC](https://www.eurocontrol.int/article/digitalisation-and-ai-air-traffic-control-balancing-innovation-human-element)

### Technical Standards
- [ICAO Annex 11: Air Traffic Services](https://applications.icao.int/postalhistory/annex_11_air_traffic_services.htm)
- [ICAO Doc 4444: PANS-ATM Procedures](https://store.icao.int/en/procedures-for-air-navigation-services-air-traffic-management-doc-4444)
- [DO-178C (Wikipedia)](https://en.wikipedia.org/wiki/DO-178C)
- [14 CFR 91.225: ADS-B Mandate](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-C/section-91.225)

### Surveillance Technology
- [SKYbrary: Primary Surveillance Radar](https://skybrary.aero/articles/primary-surveillance-radar-psr)
- [SKYbrary: Secondary Surveillance Radar](https://skybrary.aero/articles/secondary-surveillance-radar-ssr)
- [The 1090MHz Riddle: Mode S and ADS-B](https://mode-s.org/1090mhz/content/introduction.html)
- [Multilateration - SKYbrary](https://skybrary.aero/articles/multilateration)

### Data APIs
- [OpenSky Network REST API](https://openskynetwork.github.io/opensky-api/rest.html)
- [FlightAware AeroAPI](https://www.flightaware.com/commercial/aeroapi)
- [FlightAware Firehose](https://www.flightaware.com/commercial/firehose/)
- [ADSBexchange Data Access](https://www.adsbexchange.com/data/)
- [ADSB.lol](https://www.adsb.lol/)

### AI/ML Research
- [AI4ATM: AI Towards Autonomous ATM (2025)](https://www.sciencedirect.com/science/article/pii/S2941198X25000211)
- [Hybrid DRL-Geometric Conflict Resolution (2025)](https://www.sciencedirect.com/science/article/abs/pii/S0957417425012011)
- [NLP-Enhanced ATC Communication (2025)](https://link.springer.com/article/10.1186/s43067-025-00234-9)
- [NASA: Conflict Resolution Algorithms](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20050242942.pdf)
- [Kuchar & Yang: Conflict Detection and Resolution (MIT)](http://web.mit.edu/jkkuchar/www/ATC-102.pdf)

### Hobbyist / ADS-B Reception
- [RTL-SDR: ADS-B Aircraft Radar Tutorial](https://www.rtl-sdr.com/adsb-aircraft-radar-with-rtl-sdr/)
- [dump1090 (GitHub)](https://github.com/antirez/dump1090)
- [readsb (GitHub)](https://github.com/wiedehopf/readsb)

### Human Factors
- [Endsley: Out-of-the-Loop Performance Problem (1995)](https://journals.sagepub.com/doi/10.1518/001872095779064555)
- [National Academies: Future of ATC - Human Operators and Automation](https://nap.nationalacademies.org/read/6018/chapter/4)
- [SKYbrary: Stress in Air Traffic Control](https://skybrary.aero/articles/stress-air-traffic-control)

### Industry
- [Peraton BNATCS Announcement](https://www.peraton.com/news/faa-awards-peraton-a-modernization-contract-to-build-the-brand-new-air-traffic-control-system)
- [Leidos Air Traffic Management](https://www.leidos.com/markets/aviation/air-traffic-management)
- [Indra Air Automation](https://www.indracompany.com/en/indra-air-automation)
- [Aireon Space-Based ADS-B](https://aireon.com/)
- [DARPA ACE Program](https://www.darpa.mil/research/programs/air-combat-evolution)

### Hardware Architecture and Redundancy
- [ERAM - FAA](https://www.faa.gov/air_traffic/technology/eram)
- [ERAM - Wikipedia](https://en.wikipedia.org/wiki/ERAM)
- [FAA OIG: ERAM Outages Report (2018)](https://www.oig.dot.gov/sites/default/files/FAA%20Actions%20to%20Address%20ERAM%20Outages%20Final%20Report%5E11-07-18.pdf)
- [FAA OIG: STARS at Large TRACONs](https://www.oig.dot.gov/sites/default/files/FAA%20Terminal%20Modernization%20(STARS)%20Final%20Report.pdf)
- [STARS - Wikipedia](https://en.wikipedia.org/wiki/Standard_Terminal_Automation_Replacement_System)
- [Triple Modular Redundancy - Wikipedia](https://en.wikipedia.org/wiki/Triple_modular_redundancy)
- [2014 Chicago Center Fire - AOPA](https://www.aopa.org/news-and-media/all-news/2014/november/06/atc-zero-inside-the-chicago-center-fire)
- [2014 Chicago ARTCC Fire - Wikipedia](https://en.wikipedia.org/wiki/2014_Chicago_Air_Route_Traffic_Control_Center_fire)
- [FAA OIG: Chicago ATC Contingency Plans](https://www.oig.dot.gov/sites/default/files/FAA%20contingency%20plans%20and%20security%20protocols%20at%20Chicago%20ATC%20facilities.pdf)
- [NVIDIA DGX Spark Hardware Overview](https://docs.nvidia.com/dgx/dgx-spark/hardware.html)
- [DGX Spark Review - Tom's Hardware](https://www.tomshardware.com/pc-components/gpus/nvidia-dgx-spark-review)
- [DGX Spark Rack Mount Guide - Racknex](https://racknex.com/blog/2026/03/09/how-to-mount-an-nvidia-dgx-spark-in-a-19-inch-rack/)

### Networking
- [AFDX - Wikipedia](https://en.wikipedia.org/wiki/Avionics_Full-Duplex_Switched_Ethernet)
- [AFDX and TSN Comparison - IEEE 802.1](https://www.ieee802.org/1/files/public/docs2015/TSN-Schneele-AFDX-0515-v01.pdf)
- [Time-Sensitive Networking - Wikipedia](https://en.wikipedia.org/wiki/Time-Sensitive_Networking)
- [IEEE 802.1 TSN Task Group](https://www.ieee802.org/1/pages/tsn.html)
- [FAA Voice Latency Study](https://hf.tc.faa.gov/publications/2003-the-effect-of-voice-communications-latency/full_text.pdf)

### Facility Standards
- [FAA-STD-019f: Lightning/Grounding/Shielding](https://staticworx.com/wp-content/uploads/2018/04/FAA-STD-019f-20171018.pdf)
- [FAA Order JO 6900.25: LPGBS Policy](https://www.faa.gov/documentLibrary/media/Order/Final_Order_JO_6900.25.pdf)
- [FAA Order JO 6480.7E: ATCT/TRACON Design](https://www.faa.gov/documentLibrary/media/Order/JO_6480.7E.pdf)
- [FAA Order JO 1900.47F: ATC Operational Contingency Plans](https://www.faa.gov/documentLibrary/media/Order/JO_1900.47F_Final.pdf)

### Programming Languages and RTOS
- [Ada in ERAM - IAENG](https://www.iaeng.org/publication/IMECS2009/IMECS2009_pp1095-1099.pdf)
- [ERAM 100% Availability - ACM SIGAda](https://dl.acm.org/doi/abs/10.1145/3591335.3591345)
- [AdaCore ATM Industry](https://www.adacore.com/industries/atm)
- [SPARK Formal Verification - AdaCore](https://docs.adacore.com/spark2014-docs/html/ug/en/usage_scenarios.html)
- [Ferrocene Rust Compiler - Ferrous Systems](https://ferrous-systems.com/blog/officially-qualified-ferrocene/)
- [Rust is DO-178C Certifiable - Pictor Labs](https://blog.pictor.us/rust-is-do-178-certifiable/)
- [MISRA C and C++ Guidelines - Perforce](https://www.perforce.com/resources/qac/misra-c-cpp)
- [INTEGRITY-178 RTOS - Wikipedia](https://en.wikipedia.org/wiki/Integrity_(operating_system))
- [VxWorks Safety Platforms - Wind River](https://www.windriver.com/products/vxworks/safety-platforms)
- [VxWorks 653 - Wind River](https://www.windriver.com/resource/vxworks-653-product-overview)
- [QNX OS for Safety Certifications](https://blackberry.qnx.com/en/developers/certifications)
- [ARINC 653 - Wikipedia](https://en.wikipedia.org/wiki/ARINC_653)
- [iceoryx2 IPC Middleware](https://deepwiki.com/eclipse-iceoryx/iceoryx2)

### Databases and Data Retention
- [QuestDB vs InfluxDB vs TimescaleDB Benchmarks](https://questdb.com/blog/comparing-influxdb-timescaledb-questdb-time-series-databases/)
- [TimescaleDB Compression: 150GB to 15GB](https://dev.to/polliog/timescaledb-compression-from-150gb-to-15gb-90-reduction-real-production-data-bnj)
- [Memgraph vs Neo4j Performance Benchmark](https://memgraph.com/blog/memgraph-vs-neo4j-performance-benchmark-comparison)
- [PostgreSQL Synchronous Replication Cost - EDB](https://www.enterprisedb.com/blog/the-varying-cost-synchronous-replication)
- [FAA Order 7210.3 Section 12-2: Data Recording and Retention](https://www.faa.gov/air_traffic/publications/atpubs/foa_html/chap12_section_2.html)
- [FAA Order 8020.16E: Accident/Incident Reporting](https://www.faa.gov/documentLibrary/media/Order/FAA_Order_JO_8020.16E.pdf)
- [FAA Order 1350.14B: Records Management](https://www.faa.gov/documentLibrary/media/Order/FAA_Order_1350.14B.pdf)
- [49 CFR Part 830: NTSB Preservation Requirements](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-VIII/part-830)
- [ADS-B 1090ES Message Format](https://mode-s.org/1090mhz/content/ads-b/1-basics.html)
- [FIXM 4.3.0](https://www.fixm.aero/)
- [ASTERIX CAT048 - Cambridge Pixel](https://cambridgepixel.com/insights/introduction-to-asterix-cat048-for-embedded-software-engineers/)

### Swiss Cheese Model / Latent Error Analysis
- James Reason, *Human Error* (Cambridge University Press, 1990)
- James Reason, *Managing the Risks of Organizational Accidents* (Ashgate, 1997)
- Charles Perrow, *Normal Accidents: Living with High-Risk Technologies* (Princeton, 1999)
- [Endsley: Out-of-the-Loop Performance Problem (1995)](https://journals.sagepub.com/doi/10.1518/001872095779064555)
- [Facebook/Meta October 2021 Outage Details](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/)
- [AT&T February 2024 Outage - FCC Report](https://docs.fcc.gov/public/attachments/DOC-404150A1.pdf)
- [Cloudflare 1.1.1.1 Incident July 2025](https://blog.cloudflare.com/cloudflare-1-1-1-1-incident-on-july-14-2025/)
- [AWS DynamoDB October 2025 Outage](https://www.infoq.com/news/2025/11/aws-dynamodb-outage-postmortem/)
- [CrowdStrike Channel File 291 Root Cause Analysis](https://www.crowdstrike.com/en-us/blog/channel-file-291-rca-available/)
- [Google Cloud June 2025 Outage](https://www.theregister.com/2025/06/16/google_cloud_outage_incident_report/)
- [Uptime Institute Annual Outage Analysis 2025](https://uptimeinstitute.com/about-ui/press-releases/uptime-announces-annual-outage-analysis-report-2025)
