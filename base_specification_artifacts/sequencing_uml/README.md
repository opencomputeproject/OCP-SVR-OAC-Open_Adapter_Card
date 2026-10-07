# Sequencing UML

**OAC Base Specification Revision:** 0.9 (Draft)
**Format:** PlantUML (`.puml`)
**Related Base Specification sections:** 10.1.1 Operational States · 10.1.2 Operational Power Levels · 10.1.3 Power Brake Response and Timing · 10.2.7 Initialization and Sequencing

PlantUML sequence diagrams of the OAC operational-state transitions, from physical insertion through
power throttling. Two participants appear throughout: **Baseboard** and **OAC**.

---

## Contents

| File | Covers | Description |
|------|--------|-------------|
| [OAC_IntializationSequence_Full_v0.9.puml](OAC_IntializationSequence_Full_v0.9.puml) | O0 → O7 | The complete sequence in one diagram, divided into four labelled segments. This is the master; the three segment files below are extracts of it |
| [OAC_IntializationSequence_O0-O3_v0.9.puml](OAC_IntializationSequence_O0-O3_v0.9.puml) | O0 → O3 | Insertion, presence detection, auxiliary power, and management bring-up |
| [OAC_IntializationSequence_O3-O5_v0.9.puml](OAC_IntializationSequence_O3-O5_v0.9.puml) | O3 → O5 | Primary power enable, reset release, and device enumeration |
| [OAC_IntializationSequence_O5-O7_v0.9.puml](OAC_IntializationSequence_O5-O7_v0.9.puml) | O5 → O6 → O7 | Power throttling, both the managed path and the power brake path |

The segment files exist because the full sequence does not fit legibly on a specification page. They
are extracts, not independent diagrams — **a change to the full diagram must be mirrored into the
affected segment file, and vice versa.**

---

## What Each Diagram Shows

### O0 → O3 — Insertion to Management Initialized

The OAC is seated, which grounds `OAC_PRSNT[0:6]#` (or is discovered via M-PESTI) and takes the slot
from **O0** to **O1**. The baseboard enables +12V_AUX, reaching **O2**. The OAC's management
controller boots, asserts `OAC_MC_RDY`, and an MCTP session is established over the OAC Management
USB 2.0 interface on CONN0, reaching **O3**.

Everything the platform needs in order to decide whether to energize the slot happens in O3, on
auxiliary power alone. OAC slots are not hot-pluggable and carry up to 5 kW, so the baseboard cannot
discover a card by powering it and observing the result.

### O3 → O5 — Primary Power to Operational

Only after the CID has been evaluated and the SCD Assignment accepted does the baseboard energize
the primary busbar and assert `OAC_PWR_EN`. The OAC brings up its voltage regulators and clocks and
answers with `OAC_PWR_GD`, reaching **O4**. The accepted configuration latches on this transition.
`OAC_PLT_RST#` is then deasserted, the OAC initializes its primary-domain devices, the baseboard
enumerates them, and the slot reaches **O5**.

The diagram carries an explicit note that when several OACs share a platform, primary power may be
applied sequentially, so the interval between one card's `OAC_PWR_GD` and the next power-up event is
platform-dependent and must not be assumed.

### O5 → O6 → O7 — Throttling and Power Brake

Two distinct mechanisms, deliberately drawn together:

**Managed throttling (O5 → O6).** Either the baseboard writes a new Operational Power Limit, or the
OAC reduces power on its own initiative. Either way the OAC emits an OPL PLDM transition event and
the slot is **Power Constrained**.

**Power brake (O5 or O6 → O7).** The baseboard asserts `OAC_PWRBRK#`. The OAC reduces to **OPL-EMG**
and emits a transition event, reaching **Emergency Power Constrained**. This path takes precedence
over every software- and firmware-configured limit, and its timing is a compliance requirement — see
[`../timing_json/`](../timing_json/). The managed path has no comparable deadline, which is the
reason the two are separate mechanisms rather than one.

---

## Rendering

```
plantuml OAC_IntializationSequence_Full_v0.9.puml          # requires Java + Graphviz
plantuml -tsvg OAC_IntializationSequence_Full_v0.9.puml    # SVG, preferred for spec builds
```

Or paste the file contents into [plantuml.com/plantuml](https://www.plantuml.com/plantuml). No local
installation is needed for review.

---

## Editing Conventions

- Operational state labels are PlantUML `note left of Baseboard` blocks containing only the state
  identifier (`O0`, `O3`, `O5/O6`). Keep them that way — they read as a state gutter down the left
  edge of the diagram, which is the point.
- Segment boundaries are `== ... ==` separators whose text names the state range covered.
- Use exact Base Specification signal names, including the active-low `#` suffix.
- Explanatory prose goes in `note right of Baseboard` blocks, so that notes and state labels do not
  compete for the same column.
- The card is the **OAC**, never "the adapter".

---

## Known Issues

Carried here so they are not rediscovered. All are cosmetic in the source and none change the
modelled behavior, but each will appear verbatim in a rendered specification figure.

| Issue | Where |
|-------|-------|
| `Intialization` is misspelled in all four filenames | Filenames |
| `@startuml OAC power up to S5` — should read `O5`; `S5` is an ACPI system state and does not exist in the OAC model | All four files, line 1 |
| `Intialize devices in primary power domain` | `O3-O5`, and the corresponding line in `Full` |
| `Check OAC Adapter Presence` — should be `Check OAC Presence` | `Full` and `O0-O3` |
| `else adapter initialized` — should be `else OAC initialized` | `O5-O7`, and the corresponding line in `Full` |
| `Assert PWRBRK#` — should be `Assert OAC_PWRBRK#` | `O5-O7`, and the corresponding line in `Full` |
| Segment title reads `O5 to O7` but the segment ends at O6; the `Full` diagram labels the same segment `O5 to O6` correctly | `O5-O7`, first `==` separator |

Renaming the files is a breaking change for anything linking to them, so it is deferred to a
coordinated revision rather than done piecemeal.
