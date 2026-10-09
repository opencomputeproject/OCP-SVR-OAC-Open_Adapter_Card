# OAC CID Editor

**File:** `OAC-CID-Editor.html`
**Type:** Self-contained browser application — no server, no installation, no internet connection required

---

## Overview

The OAC CID Editor is a browser-based authoring tool for creating and editing OAC Connector Interface Definition (CID) documents. A CID is a machine-readable JSON file stored in OAC firmware that declares everything an upstream management controller needs to know about an OAC before energizing its slot: power requirements, connector configuration, high-speed signaling assignments, reference clocking, and discrete sideband signals.

Authoring a well-formed CID from scratch — especially for multi-connector OACs with complex lane assignments — is time-consuming and error-prone when done by hand. The CID Editor provides a structured, validated environment that guides the user through every field of the schema, enforces constraints at entry time, and produces standards-compliant JSON output ready for integration into OAC firmware.

---

## Why It Exists

The CID schema is rich and carries many interdependencies. For example:

- A connector that declares a `connector_profile` reference must not also define `high_speed_lanes`, `clocking`, or `discrete_signals` — these are mutually exclusive.
- `link_subdivision` only applies to PCIe and CXL protocols, and only when `total_lanes` is a power of 2.
- OPL power fields must satisfy an ordering constraint: `opl_max_w ≥ opl_eff_w ≥ opl_red_w ≥ opl_emg_w`.
- Pin A1 on every connector is permanently reserved for `OAC_PRSNT#`/M-PESTI and cannot be assigned to any other signal.
- Clock and lane assignments must be mapped to physically valid pin positions for the connector type (CONN0 has 9 assignable columns; CONN1–6 have 8).

Tracking these rules manually while editing raw JSON is impractical. The editor enforces them continuously, surfacing errors and warnings in a live validation panel before the user exports.

---

## Key Features

### Two Authoring Modes — CID and Connector Profile

The editor operates in two distinct modes selectable from the header:

**CID Mode** — for authoring a complete OAC CID. Covers the full schema: metadata, power (input voltage, connector type, all OPL levels), and per-connector signal definitions for up to seven connectors (CONN0–CONN6). Each connector can reference an OCP-ratified Connector Profile by identifier, or define its signals explicitly — but not both.

**Connector Profile Mode** — for authoring a reusable, OCP-ratified connector profile. A profile defines standard `high_speed_lanes`, `clocking`, and `discrete_signals` assignments for one or more connector positions and a protocol configuration. The `applicable_conns` control is a row of checkboxes, one per position: `CONN0`, `CONN1` through `CONN6`, and `CABLE`. Select every position the profile is ratified for. The editor enforces the rule that one array may not mix geometry classes, so checking `CONN0` or `CABLE` clears the others and checking any of `CONN1` through `CONN6` clears `CONN0` and `CABLE`; the selection can never be emptied. Selecting all six of `CONN1` through `CONN6` emits the `"CONN1-6"` shorthand, and any other selection emits the positions it names. The selection drives the pin map column count — nine columns for `CONN0`, eight otherwise — and the connector segment of the suggested identifier, which is the position itself when exactly one of `CONN1` through `CONN6` is selected and `CONN` when more than one is. Once ratified by the OCP OAC workstream, OACs can reference a profile by its identifier rather than repeating full pin-level declarations in every CID. This keeps CIDs compact and consistent across vendors.

### Guided and Manual Editing — Live Two-Way Sync

Within each mode, the user can switch between:

**Guided mode** — a structured form broken into labelled sections accessible from the left navigation panel. Every field has appropriate input controls (dropdowns for enumerated values, number fields with step and min constraints, checkboxes). Optional fields are clearly marked. Hover tooltips (the `?` icons) on key fields provide concise descriptions and constraint reminders without leaving the page. The form enforces schema rules as fields are populated.

**Manual mode** — a raw JSON textarea with syntax highlighting that lets experienced users type or paste JSON directly. A live two-way sync keeps the form and the JSON consistent: edits in the guided form immediately update the JSON, and valid JSON entered manually populates the form. Validation runs continuously in both modes.

Switching between modes at any point is safe — the current document state is preserved.

### Visual Pin Map

Each connector panel includes an expandable Visual Pin Map showing the full CONN0 or CONN1–6 pin grid (rows A–N, columns 1–9 or 1–8). Clicking any available cell opens an assignment picker for that pin. The picker lists all unassigned signals — HS lanes grouped by protocol group and lane index, clock signals, and discrete signals — with their group index and polarity clearly labeled to avoid ambiguity in multi-group configurations.

Assigned pins are color-coded by signal type (RX+, RX−, TX+, TX−, clock, discrete) and labeled with the protocol group and lane index. Reserved positions (Pin A1, clock/discrete-only rows, and fully blocked positions per the OAC connector specification) are visually distinct and cannot be assigned.

### Real-Time Validation

A validation panel below the JSON preview shows errors and warnings as the document is built. Errors represent schema violations that would cause the BMC to reject the CID or block slot energization. Warnings represent conditions that are technically permitted but may indicate an incomplete or unusual configuration. The header badge shows a count of errors and warnings at a glance.

Validation covers:

- Required field presence (metadata, power, connector ID)
- Power field ordering constraints (OPL hierarchy)
- connector_profile mutual exclusivity with explicit signal sections
- `mpesti_capable` present on CONN0 and absent everywhere else
- `applicable_conns` present and non-empty, free of duplicate and unrecognized tokens, not mixing geometry classes, not combining `"CONN1-6"` with an individual `"CONN1"` through `"CONN6"` token, and in agreement with the `profile_id` connector segment
- A referenced `connector_profile` identifier parses as an OCP-ratified identifier, and its connector segment names the position it is applied to — `OAC-PROF-CONN6-…` only on CONN6, `OAC-PROF-CONN-…` on any of CONN1 through CONN6, `OAC-PROF-CONN0-…` only on CONN0, `OAC-PROF-CABLE-…` only on CABLE
- High-speed lane protocol compatibility, lane count limits, link_subdivision applicability
- Clock count maximum (16 per connector), required clock fields, ssc_supported presence
- Pin assignment validity and conflict detection
- Connector Profile naming convention compliance

### Import and Export

**Import JSON** loads any existing CID or Connector Profile JSON file, auto-detects the document type, switches to the correct mode, and populates the form immediately — including in manual mode.

**Export JSON** offers two formats:

- **Formatted JSON** — human-readable with indentation, suitable for documentation and review
- **Minified JSON** — all optional whitespace removed, suitable for direct firmware storage. Minification is the only size reduction the CID defines; compression was removed from the specification at v0.9, and a CID shall be served as UTF-8 JSON per Section 6.2.

### Connector Profile Naming Assistance

The Connector Profile panel includes a **✦ Suggest ID** button that auto-generates a standards-compliant profile identifier from the currently defined protocol groups, lane counts, and signal direction. The generated identifier follows the OCP-ratified naming convention:

```
OAC-PROF-<CONN0|CONN1..CONN6|CONN|CABLE>-<proto1>-x<lanes1>-<dir1>[-<proto2>-x<lanes2>-<dir2>]-v<n>
```

### Help System

A `?` button in the header opens a help modal with four tabs:

- **Getting Started** — a six-step walkthrough from mode selection through firmware export
- **Field Reference** — a searchable table of every CID and profile field with type, required/optional status, and description

Documents written against the pre-2026-10-09 schema still load. `is_conn0` and the `presence_detect` wrapper object are read on input and reported as superseded, and re-saving the document emits `applicable_conns` and a flat `mpesti_capable` field in their place.
- **Keyboard Shortcuts** — `?` (open help), `Esc` (close), `Alt+G`/`Alt+M` (mode switch), `Alt+I` (import), `Alt+E` (export)
- **About** — schema version, spec revision, repository link, normative references, and last-modified date

---

## Usage

1. Open `OAC-CID-Editor.html` in any modern browser (Chrome, Edge, Firefox, Safari)
2. Select **CID** or **Connector Profile** mode from the header toggle
3. Use the left navigation panel to move between sections, or scroll through the guided form
4. Fill in fields — hover `?` icons for field descriptions and constraint reminders
5. Expand the **Visual Pin Map** on any connector to assign physical pins graphically
6. Monitor the validation badge and error panel in the JSON preview
7. When the badge shows **✓ Valid**, click **Export JSON** to save the completed document

To edit an existing document: click **Import JSON** and select the file. The editor auto-populates and validates immediately.

---

## Normative Basis

This tool implements the OAC CID Specification v0.9, which is normatively grounded in:

| Reference | Document |
|-----------|----------|
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification" |
| DSP0249 | DMTF, "PLDM State Set Specification" |
| DSP0257 | DMTF, "PLDM for FRU Data Specification" |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| OCP OAC | OCP, "Open Adapter Card Base Specification," v0.9 |

The editor does not replace the normative specification. When in doubt, the specification document is authoritative.
