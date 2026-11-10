# OAC CID Insertion Emulator

**File:** `OAC-CID-Insertion-Emulator.html`
**Type:** Interactive simulation — no external dependencies
**Schema Version:** 0.9

## Purpose

An animated simulation of inserting an OAC into a baseboard slot and running the CID compliance evaluation sequence. Load two JSON files (baseboard capabilities and the OAC CID), then click Insert to watch the compliance checks run in real time with a sequenced event log.

## How to Use

1. Click **Load Baseboard JSON (slot capabilities)** to load a file describing the baseboard slot's capabilities
2. Click **Load OAC CID (oac_cid)** to load the OAC's CID
3. Click **Insert OAC into Baseboard** to run the simulation
4. Watch the hardware animation and event log
5. Review the verdict (BLOCKED / DEGRADED / NORMAL) and any issues listed
6. Click **Export Event Log** to save the log as a `.txt` file
7. Click **Reset Simulation** to clear and start over

## Baseboard JSON Format

The baseboard file uses the same `oac_cid` JSON structure as an OAC CID, but represents what the slot supports rather than what the OAC requires. Any undeclared field generates a WARN rather than a FAIL. See the interactive tools README for an example baseboard file.

`link_role` is not part of the v0.9 schema — it was removed because link topology has no bearing on the power decision — so a baseboard file that still carries it is simply ignored, under the unrecognized-key rule of specification Section 7.1.

## Compliance Checks

The emulator runs 11 compliance checks:

1. Primary input voltage match
2. Connector type (100A/125A) compatibility
3. OPL-MAX power budget
4. OPL-EMG declaration
5. Declared power excursion profile
6. Per-connector impedance match
7. High-speed lane protocol, direction, minimum lanes
8. Required lane pin assignments
9. Required reference clock parameters
10. Required discrete signal names and pins
11. OAC spec revision compatibility

### Notes on check 5

The excursion comparison is made in **absolute watts**, not ratio against ratio. Each document's `ratio_max` values are normalized to its own `opl_max_w`, so two ratios drawn from documents with different OPL-MAX figures are not comparable quantities. The emulator converts both sides to watts at each interval before comparing.

A baseboard that declares no excursion profile is treated as supporting the full Base Specification Section 10.1.4 envelope, because the Base Specification requires a conformant slot to tolerate any conformant OAC.

A malformed OAC profile is **rejected, not budgeted against**. The intrinsic checks — entry count, ascending intervals, ratios at or above 1.0 and at or below the piecewise Section 10.1.4 envelope, monotonically non-increasing ratios — run first, and if any fails, the log records that the transient budget was not evaluated rather than reporting a PASS the declaration did not earn.

The implied peak current is reported and not judged. The connectors' rated and derated figures are *continuous* current, which is a thermal limit and is not comparable to a microsecond-scale average.

## Verdict States

- **BLOCKED** — Any FAIL. `OAC_PWR_EN` remains de-asserted. The OAC does not power on.
- **DEGRADED** — No FAIL, one or more WARN. `OAC_PWR_EN` asserted with reduced capability.
- **NORMAL** — All checks pass. `OAC_PWR_EN` asserted. The OAC powers on at full capability.

## Power-Up Narrative

The simulation sequences through OAC Operational States O0→O2→O3 before running checks, then proceeds to O4→O5 if compatible, matching the initialization model defined in OCP OAC Base Specification v0.9 Section 10.1.1.

In O3 the log shows the controller reading the **OAC Metadata file** and resolving the `cid` role to a `FileIdentifier` before retrieving the CID. That is narration, not function: the emulator is given a CID file directly and performs no discovery. The step is shown because a reader who sees the CID appear from nowhere will carry away the wrong model of how it was found. See [`../../../../metadata/`](../../../../metadata/).

No internet connection required.
