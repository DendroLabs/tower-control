# Tower Control — Automated ATC System

## Project Context

This is a research and design project for an automated air traffic control system using multi-agent AI architecture. The system replaces human controllers with redundant AI agents, deterministic safety nets, and human overwatchers — targeting tower/TRACON operations at a single facility as the initial scope.

The primary research document is `ATC_AUTOMATION_REPORT.md`. All design decisions should be validated against two case studies: the Potomac River midair collision (DCA, Jan 2025) and the LaGuardia runway collision (LGA, March 2026).

---

## Guiding Safety Principles

These principles are derived from James Reason's Swiss Cheese Model, latent error analysis of real-world outages, and the two fatal incidents above. They govern every design, implementation, and maintenance decision in this project. No contributor — human or AI — makes a choice that makes it easy to fail.

### 1. Make the Wrong Thing Impossible, Not Just Unlikely

If a state is dangerous, the architecture must make it physically unreachable — not procedurally discouraged. Procedures erode under pressure; architecture does not. Every safety-critical constraint must be enforced by tooling, hardware, or schema validation, never by policy alone.

The 7 hard invariants (Section 27.6 of the report) define the floor below which the system cannot go:
- No two aircraft cleared for the same runway simultaneously (hardware-enforced mutual exclusion)
- No clearance issued without deterministic safety net validation (safety net in the data path, not advisory)
- No surveillance data older than N seconds used for separation decisions (consumer-side timestamp check)
- No model update applied to all instances simultaneously (deployment system caps at 33% per step, no override)
- No safety-critical config change without dual cryptographic authorization (single-person override architecturally absent)
- No temporary config without an expiration timestamp (schema rejects null TTL at write time)
- No agent may issue a clearance contradicting an active clearance for the same flight (state machine enforcement)

These 7 are expanded into 19 formal invariants in the state model (Section 28.8: R1–R4, C1–C5, F1–F6, S1–S4), including the Approach Commitment Gate (Section 28.5.6) — a forcing function that prevents aircraft from approaching a locked runway without a clearance, inspired by VOQ credit-based flow control.

When designing any new component, ask: "What states must be impossible?" Define them as invariants before writing logic.

### 2. "Pay More Attention" Is Not a Defense

If a post-mortem for this system would recommend "the operator should have noticed X," that is a latent error in the design, not a gap in human performance. Every "should have noticed" must be converted into an automated check, an invariant, or a forcing function. Attention is a finite, unreliable resource — never treat it as a safety layer.

### 3. Ask "What Was Waiting to Happen?"

When something goes wrong, the question is never "who screwed up?" but "what latent condition made this possible, and how many other triggers could have activated it?" Active errors are symptoms. Latent errors are the disease. Fix the class of failure, not the instance.

### 4. The Deterministic Layer Is the Floor

Safety nets (Collision Vector Monitor, Separation Monitor, Runway Incursion Monitor) are not advisories. They sit in the data path with veto power. No clearance physically reaches a pilot without deterministic validation, regardless of what agents decide. The deterministic layer runs on independent hardware from the agent layer and does not use ML. It is the blast-radius firewall between agent errors and real-world consequences.

### 5. Redundancy Is Not Safety

Redundant components that share inputs, training data, configurations, or failure modes are not truly independent. Adding redundancy adds interaction states between components, creating new failure modes that didn't exist in a simpler system (Perrow). Three agents reading from the same Redis cache are one agent with extra steps.

Before claiming any component is "redundant," verify:
- Independent input paths (not just independent computation)
- Independent failure modes (no shared single points of failure)
- Tested interaction behavior (what happens when they disagree, agree for different reasons, or run at different speeds)

### 6. Canary Everything

No change — model update, configuration change, threshold adjustment, prompt modification, safety net rule — may propagate to all instances simultaneously. The deployment system must enforce staged rollout (max 33% per step) with mandatory observation windows. This is enforced by architecture, not policy. There is no override flag.

This applies equally to changes that feel minor. The CrowdStrike lesson: "just a config change" can be more dangerous than a code change because it bypasses the CI/CD pipeline.

### 7. Configuration Is Code

Threshold changes, prompt edits, airspace modifications, model weight updates, and safety net rule changes are as dangerous as source code changes. They flow through the same rigorous pipeline: version control, peer review, staged deployment, rollback capability. There is no "fast path" for configuration. If a change can alter agent behavior, it is a software change.

### 8. Temporary Is Permanent Unless Enforced

Every non-permanent change (seasonal thresholds, temporary airspace modifications, exercise-related rules, maintenance overrides) requires a mandatory expiration timestamp. The system refuses to accept a "temporary" change without a TTL at the schema level. Dormant configuration is the most dangerous configuration — it sits unnoticed until an unrelated change activates it weeks or months later.

Run continuous configuration drift detection: compare running state against declared intended state. Flag any config that exists but has no active traffic flowing through it.

### 9. Monitor Correctness, Not Just Health

Component health checks ("is it running?") miss systemic failures. A system where every component reports "healthy" can still be catastrophically wrong if the data flowing between components is stale, offset, or corrupted.

Required monitoring approaches:
- **End-to-end synthetic validation**: Inject ghost flights with known-correct trajectories. If system output deviates from the known answer, something in the pipeline is broken — even if every component reports healthy.
- **Negative-space monitoring**: Alert when expected activity is absent. An aircraft on final with no landing clearance within N seconds is a trigger, even if no component has errored.
- **Data age visibility**: Every decision-making display must show the age of the data feeding it. 3-second-stale surveillance data must be visually obvious, not hidden behind a "healthy" status.

### 10. Automation Moves the Sharp End — It Doesn't Eliminate It

This system eliminates the controller as the sharp end (no fatigue, no attention lapses, no "forgot to check"). But the humans who maintain, configure, and update the automation become the new sharp end. They will:
- Be under time pressure to push changes during operational windows
- Skip procedures when safety tooling is slow or inconvenient
- Treat threshold changes as less risky than software updates
- Leave temporary configs in place because removal is lower priority
- Check "is the system running?" rather than "is the system correct?"

Every design decision about maintenance tooling, deployment pipelines, and operational procedures must account for this reality. The maintainer is subject to the same Reason framework as the controller they replaced.

### 11. Encode Procedures in Tooling That Cannot Be Bypassed

A procedure documented in a runbook will be skipped under pressure. A procedure enforced by tooling cannot be. The deployment system physically refuses simultaneous updates. The config system physically requires dual authorization. If a safety procedure can be bypassed by a determined human with root access, it will be — eventually, at the worst possible time.

Test safety tooling adversarially: regularly attempt the dangerous operations your tools should block. If an override exists, someone will use it. Either remove the override or audit every invocation.

### 12. Test Every Defense by Attacking It

A safety system that has never been triggered might be broken. Every invariant, every safety net rule, every escalation path must be periodically tested by attempting to violate it. If a safety net rule hasn't fired in 6 months, determine whether conditions never arose or whether the rule is broken. "Dark config" scanning — finding rules that exist but have never activated — is a continuous requirement, not a one-time audit.

---

## Three-Tier Escalation Model

All design decisions must identify which tier handles the task and what triggers escalation:

1. **LLM Agents** — routine operations: initial contact, airspace confirmation, low-priority sequencing, monitoring
2. **Deterministic Systems** — safety-critical operations: final approach, landing clearance, separation enforcement, ground movement near active runways
3. **Human + AI Assistants** — emergencies: declared emergencies immediately escalate to a human operator with AI-powered assistants (cockpit layouts, checklists, aircraft specs)

Handoff is based on criticality, not proximity. The normalcy threshold (configurable per facility, weather, traffic density) triggers escalation when readings exceed normal bounds.

---

## Architecture Constraints

- **Air-gapped / LAN-only**: No internet dependency. All models run locally.
- **Sub-40ms latency**: Real-time decisions cannot tolerate WAN round-trips.
- **No single point of failure**: Every subsystem independently deployable and testable.
- **Independent safety layer**: Deterministic safety nets on separate hardware from agent compute.
- **Formal verification**: Safety-critical core in Ada/SPARK (DO-333). High-reliability middleware in Rust. ML inference in Python (non-safety-critical partition).

---

## Design Validation Test

For every architectural decision, ask:

1. **Would this have prevented DCA?** (Combined controller positions, no cross-check of helicopter route vs. approach path, TCAS ineffective below 1,000ft)
2. **Would this have prevented LGA?** (Single controller handling tower + ground, cleared truck onto active runway during final approach)
3. **What latent error does this introduce?** (What could sit dormant and be activated by an unrelated change?)
4. **Where is the sharp end?** (Who is the human most likely to make a mistake with this component, and have we made the wrong thing impossible for them?)
5. **How do we know it's working correctly, not just running?** (What's the end-to-end correctness check, not just the health check?)
