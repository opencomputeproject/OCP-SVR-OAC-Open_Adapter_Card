# OAC CID Compliance Logic

**File:** `OAC-CID-Compliance-Logic.html`
**Type:** Static reference diagram — no interactivity, no dependencies

## Purpose

A visual reference card showing the complete sequence of CID compliance checks that the upstream
management controller performs after retrieving an OAC's JSON-encoded Connector Interface
Definition. Covers all 12 validation steps defined in
[OAC-CID-Specification-v0.9.md](../../../specification/OAC-CID-Specification-v0.9.md) Section 8.3.

## Checks Shown

| # | Check | Fields Evaluated |
|---|-------|-----------------|
| 1 | Schema Validation | `metadata.schema_version` |
| 2 | Input Voltage | `power.primary.input_voltage` |
| 3 | Connector Type | `power.primary.connector_type` |
| 4 | OPL-MAX Power Budget | `power.primary.opl_max_w` |
| 5 | OPL-EMG Declared | `power.primary.opl_emg_w` |
| 6 | Connector Impedance | `connectors[].impedance_ohm` |
| 7 | connector_profile Resolution | `connectors[].connector_profile` |
| 8 | HS Lane Parameters | `high_speed_lanes.*`, `minimum_lanes` |
| 9 | Lane Pin Assignments | `lanes[required=true].*` |
| 10 | Reference Clocking | `clocking[required=true].*` |
| 11 | Required Discrete Signals | `discrete_signals[required=true].*` |
| 12 | Spec Revision | `metadata.oac_spec_revision` |

## Verdicts

- **BLOCKED** — Any FAIL result. OAC_PWR_EN remains de-asserted.
- **DEGRADED** — No FAIL, one or more WARN. OAC_PWR_EN asserted with reduced capability.
- **NORMAL** — All PASS. OAC_PWR_EN asserted at full capability.

## Usage

Open `OAC-CID-Compliance-Logic.html` in any modern browser. No internet connection required.
