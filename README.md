# Tower Control — Automated Air Traffic Control System

A research and design project for replacing human air traffic controllers with a multi-agent AI architecture backed by deterministic safety nets. The system targets tower and TRACON operations at a single facility, with the goal of making the dangerous states **architecturally impossible** rather than procedurally unlikely.

## Why This Exists

The current ATC system is not sustainable. Controller staffing has been in decline for years, facilities routinely operate below minimum staffing levels, and the volume of air traffic continues to grow. The system is already under more strain than it was designed for, and that gap is widening. The result is a rising number of near-misses — over 15,000 in recent data — and life-threatening incidents that are preventable with technology that already exists.

Human controllers are good at this job. But computers would be better: they don't fatigue, don't lose situational awareness during a double shift, and can cross-check every piece of available data on every decision, every time. The goal isn't to patch the current system — it's to replace the failure-prone layer with an architecture where dangerous states are physically unreachable.

Two recent fatal incidents illustrate the kinds of failures this system is designed to prevent:

- **Potomac River Midair Collision** (DCA, Jan 29, 2025) — PSA Flight 5342 and an Army Black Hawk collided on approach to Reagan National. 67 killed. The helicopter was on a route too close to the approach path, ATC had combined two controller positions, and 15,000+ near-misses in the data had been ignored.

- **LaGuardia Runway Collision** (LGA, March 23, 2026) — Air Canada 8646 hit a fire truck on Runway 4 during landing. 2 pilots killed. A single controller handling both tower and ground frequencies cleared the truck onto an active runway while an aircraft was on final approach.

Both share root causes that this architecture eliminates: understaffing, combined positions, human attention limits, and failure to cross-check data that was already available. The simulation validates the design against both incidents.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: LLM Agents (routine operations)                        │
│  Initial contact, sequencing, monitoring, taxi clearances       │
│  Runs on: DGX Spark cluster, Linux, Python/ONNX                 │
└────────────────────┬────────────────────────────────────────────┘
                     │ Proposals (clearance requests)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: Deterministic Safety Net (safety-critical ops)         │
│  Clearance validation, runway mutual exclusion, separation      │
│  enforcement, commitment gate, collision vector monitoring      │
│  Runs on: TMR hardware, INTEGRITY-178/VxWorks, Ada/SPARK        │
│  IN THE DATA PATH — not advisory. No bypass exists.             │
└────────────────────┬────────────────────────────────────────────┘
                     │ Validated clearances only
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: Human + AI Assistants (emergencies)                    │
│  Declared emergencies escalate to human operators with          │
│  AI-powered cockpit layouts, checklists, aircraft specs         │
└─────────────────────────────────────────────────────────────────┘
```

The key insight: the deterministic safety net sits **in the data path**, not as an advisory. No clearance physically reaches a pilot without passing through invariant validation on independent hardware. Agents can be wrong — the safety net catches it.

## Safety Principles

Twelve guiding principles derived from James Reason's Swiss Cheese Model:

1. **Make the wrong thing impossible, not just unlikely** — architecture over procedure
2. **"Pay more attention" is not a defense** — every "should have noticed" becomes an automated check
3. **Ask "what was waiting to happen?"** — fix the class of failure, not the instance
4. **The deterministic layer is the floor** — safety nets have veto power, not advisory status
5. **Redundancy is not safety** — shared inputs/training/config make redundancy illusory
6. **Canary everything** — no change propagates to all instances simultaneously (max 33%)
7. **Configuration is code** — threshold changes are as dangerous as code changes
8. **Temporary is permanent unless enforced** — mandatory TTL on all non-permanent config
9. **Monitor correctness, not just health** — end-to-end synthetic validation, not just "is it running?"
10. **Automation moves the sharp end** — the maintainers become the new humans-in-the-loop
11. **Encode procedures in tooling** — if a safety procedure can be bypassed, it will be
12. **Test every defense by attacking it** — a safety net that's never triggered might be broken

Full details in [CLAUDE.md](CLAUDE.md).

## 19 Formal Invariants

The system defines 19 invariants that the deterministic safety layer makes **unreachable**, not just unlikely:

| Category | IDs | Examples |
|----------|-----|---------|
| Runway (R1-R4) | 4 | One lock per runway, no orphaned locks, TTL alerts |
| Clearance (C1-C5) | 5 | No clearance without validation, no stale surveillance data |
| Flight (F1-F6) | 6 | Commitment gate forcing function, emergency queue priority |
| Surveillance (S1-S4) | 4 | Untracked entity detection, runway occupancy cross-check |

## Simulation Environment

The `sim/` package is a discrete event-driven test harness that translates the formal state model into executable Python. It validates the design by running real-world incident scenarios.

### Running

```bash
# Run all scenarios
python -m sim.runner

# Run a specific scenario with verbose output
python -m sim.runner s02_lga --verbose

# Run unit tests
python -m pytest sim/tests/ -v
```

### Scenarios

| Scenario | What It Tests |
|----------|--------------|
| **S01: Normal IFR Cycle** | Happy path — arrival lands, departure takes off, no conflicts |
| **S02: LGA Prevention** | Fire truck crossing rejected while runway locked (R1/R2), validated after clear |
| **S03: DCA Detection** | Untracked helicopter detected by S4 invariant, CVM alerts on convergence |
| **S04: Commitment Gate** | Forced go-around at 2nm when approaching locked runway without clearance (F5) |
| **S05: CVM Escalation** | Two aircraft converging head-on — CVM escalates Advisory → Warning → Critical |
| **S06: Sequential Locks** | Vehicle crosses both runways via taxiway; each lock independent, rejected while departure holds 10R |
| **S07: VFR/IFR Mix** | VFR pattern traffic sequenced with IFR arrival on same runway, no simultaneous lock |

### Module Structure

```
sim/
├── types.py                    # Enums, dataclasses (21 clearance types, 19 invariants)
├── clock.py                    # Deterministic steppable simulation clock
├── geometry.py                 # Haversine, projection, CPA calculations
├── events.py                   # In-process pub-sub event bus
├── airport/
│   ├── layout.py               # Class C airport: parallel runways, taxiways A-E
│   └── airspace.py             # Airspace shelves, approach corridors, gate positions
├── state/
│   ├── runway.py               # Runway mutual exclusion lock (atomic check-and-lock)
│   ├── clearance.py            # 12-state clearance lifecycle with TTL enforcement
│   ├── flight.py               # IFR state machine (8 phases, 27 states)
│   ├── vfr_pattern.py          # VFR traffic pattern (9 states)
│   └── vehicle.py              # Ground vehicle state machine (LGA critical path)
├── safety/
│   ├── invariants.py           # All 19 invariant checks (R1-R4, C1-C5, F1-F6, S1-S4)
│   ├── validator.py            # Clearance validation API (atomic validate + lock)
│   ├── commitment_gate.py      # VOQ-inspired approach flow control
│   ├── cvm.py                  # 4D collision vector monitor (3-tier escalation)
│   └── negative_space.py       # Alerts when expected activity is absent
├── engine/
│   ├── simulation.py           # Tick orchestration (11-step cycle)
│   ├── surveillance.py         # Trajectory interpolation, untracked entity injection
│   └── delivery.py             # TCP-style clearance delivery (readback = ACK)
├── agents/
│   ├── base.py                 # Abstract agent interface (plug-in point for AI)
│   └── scripted.py             # Scripted scenario drivers
├── scenarios/                  # Executable test scenarios
├── tests/                      # Unit + integration tests
└── runner.py                   # CLI entry point
```

## Research Document

The primary design document is [ATC_AUTOMATION_REPORT.md](ATC_AUTOMATION_REPORT.md) — a 30-section report covering:

- **Part I (Sections 1-16)**: Research foundation — what controllers do, current technology, barriers to automation, AI approaches
- **Part II (Sections 17-29)**: System design — agent certification, multi-agent architecture, escalation model, communication protocols, physical architecture, Swiss Cheese analysis, formal state model, safety net interface
- **Section 30**: Sources

## Requirements

- Python 3.12+ (tested on 3.14)
- No external dependencies — standard library only

## Status

Research and design phase. The simulation validates the formal model. No production code, no AI agents yet — the agent interface (`sim/agents/base.py`) is the plug-in point for future implementation.

## License

Private research project.
