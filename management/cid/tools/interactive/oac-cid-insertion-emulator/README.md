# OAC CID Insertion Emulator

**File:** `OAC-CID-Insertion-Emulator.html`
**Type:** Interactive simulation — no external dependencies

## Purpose

An animated simulation of inserting an OAC into a baseboard slot and running the CID compliance evaluation sequence. Load two JSON files (baseboard capabilities and the OAC CID), then click Insert to watch the compliance checks run in real time with a sequenced event log.

## How to Use

1. Click **Baseboard JSON** to load a file describing the baseboard slot's capabilities
2. Click **Adapter CID JSON** to load the OAC's CID
3. Click **Insert Adapter** to run the simulation
4. Watch the hardware animation and event log
5. Review the verdict (BLOCKED / DEGRADED / NORMAL) and any issues listed
6. Click **Export Event Log** to save the log as a `.txt` file
7. Click **Reset** to clear and start over

## Baseboard JSON Format

The baseboard file uses the same `oac_cid` JSON structure as an OAC CID, but represents what the slot supports rather than what the OAC requires. Any undeclared field generates a WARN rather than a FAIL. See the interactive tools README for an example baseboard file.

## Compliance Checks

The emulator runs 10 compliance checks:

1. Primary input voltage match
2. Connector type (100A/125A) compatibility
3. OPL-MAX power budget
4. OPL-EMG declaration
5. Per-connector impedance match
6. High-speed lane protocol, role, direction, minimum lanes
7. Required lane pin assignments
8. Required reference clock parameters
9. Required discrete signal names and pins
10. OAC spec revision compatibility

## Verdict States

- **BLOCKED** — Any FAIL. OAC_PWR_EN remains de-asserted. The OAC does not power on.
- **DEGRADED** — No FAIL, one or more WARN. OAC_PWR_EN asserted with reduced capability.
- **NORMAL** — All checks pass. OAC_PWR_EN asserted. The OAC powers on at full capability.

## Power-Up Narrative

The simulation sequences through OAC Operational States O0→O2→O3 before running checks, then proceeds to O4→O5 if compatible, matching the initialization model defined in OCP OAC Base Specification v0.9 Section 10.1.1.

No internet connection required.
