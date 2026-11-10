# OAC CID Compliance Logic

**File:** `OAC-CID-Compliance-Logic.html`
**Type:** Static reference diagram — no interactivity, no dependencies
**Schema Version:** 0.9

## Purpose

A visual reference card showing the complete sequence of CID compliance checks that the upstream
management controller performs after retrieving an OAC's JSON-encoded Connector Interface
Definition. The 13 checks shown expand on the minimum validation requirements of
[OAC-CID-Specification-v0.9.md](../../../specification/OAC-CID-Specification-v0.9.md) Section 9.3.

The diagram starts where the specification does: the CID is not located by name. The upstream
management controller retrieves the **OAC Metadata file** first — the one file located by its fixed
`FileName` — and resolves the `cid` role to the `FileIdentifier` it then opens. A controller that
cannot retrieve or validate the metadata file stops there, and falling back to matching `FileName`
is prohibited. See [`../../../../metadata/`](../../../../metadata/).

## Checks Shown

| # | Check | Fields Evaluated |
|---|-------|-----------------|
| 1 | Schema Validation | `metadata.schema_version` |
| 2 | Input Voltage | `power.primary.input_voltage` |
| 3 | Connector Type | `power.primary.connector_type` |
| 4 | OPL-MAX Power Budget | `power.primary.opl_max_w` |
| 5 | OPL-EMG Declared | `power.primary.opl_emg_w` |
| 6 | Declared Power Excursion Profile | `power.excursion[].interval_us`, `.ratio_max` |
| 7 | Connector Impedance | `connectors[].impedance_ohm` |
| 8 | connector_profile Resolution | `connectors[].connector_profile` |
| 9 | HS Lane Parameters | `high_speed_lanes.*`, `minimum_lanes` |
| 10 | Lane Pin Assignments | `lanes[required=true].*` |
| 11 | Reference Clocking | `clocking[required=true].*` |
| 12 | Required Discrete Signals | `discrete_signals[required=true].*` |
| 13 | Spec Revision | `metadata.oac_spec_revision` |

## Notes on Individual Checks

**Check 6 — power excursion.** The field is optional, and its absence is a WARN rather than a PASS,
because an OAC that declares nothing is uncharacterized, not quiet: the platform has to budget the
slot at the full Base Specification Section 10.1.4 ceiling. That ceiling is **piecewise** — 3 for
T ≤ 100 µs, `4 − 0.2171 × ln(T)` between, and 1 for T ≥ 1,000,000 µs — and a validator that
extrapolates the logarithm past either end gets the wrong answer in the permissive direction at
short intervals. The budget comparison against the slot is made in **absolute watts**, never ratio
against ratio, because each document's ratios are normalized to its own `opl_max_w`.

**Check 8 — profile resolution.** A `connector_profile` and an explicit `high_speed_lanes` /
`clocking` / `discrete_signals` declaration are mutually exclusive on the same connector
(Specification Section 8.2); a profile is not a set of defaults to be partially overridden. A
connector carrying high-speed signals must declare one or the other.

**Check 9 — high-speed lanes.** There is no `link_role` comparison. The field is not part of the
v0.9 schema — link topology has no bearing on the power decision.

## Verdicts

- **BLOCKED** — Any FAIL result. `OAC_PWR_EN` remains de-asserted.
- **DEGRADED** — No FAIL, one or more WARN. `OAC_PWR_EN` asserted with reduced capability.
- **NORMAL** — All PASS. `OAC_PWR_EN` asserted at full capability.

## Usage

Open `OAC-CID-Compliance-Logic.html` in any modern browser. No internet connection required.
