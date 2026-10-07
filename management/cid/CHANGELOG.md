# OAC CID Specification — Changelog

All notable changes to the OAC Connector Interface Definition (CID) specification and associated tooling are documented here.

---

## [0.8] — Current

### Added

- **Protocol group `name` field** — Optional string field on each `high_speed_lanes` protocol group. Allows upstream management controllers, diagnostic tools, and CID authoring software to reference specific protocol groups by a stable, human-readable label (e.g. `"pcie_primary"`, `"eth_fabric"`). Convention: lowercase letters with underscores for word separation.
- **`ssc_supported` field on clocks** — Required boolean on each clock entry indicating whether the clock supports Spread Spectrum Clocking. Applies to both `INPUT` and `OUTPUT` clocks.
- **`connector_profile` mutual exclusivity enforcement** — Normative language clarified: when `connector_profile` is declared, `high_speed_lanes`, `clocking`, and `discrete_signals` shall not be present in the same connector object.
- **`minimum_lanes` field** — Optional vendor-imposed operational floor on protocol groups. The upstream management controller should block slot energization if fewer lanes than this value are electrically routed from the baseboard to the connector.
- **Clocking maximum** — A connector shall not declare more than 16 clock signals. Implementations that encounter a `clocking` array with more than 16 elements shall treat the connector as malformed.
- **`is_conn0` field on Connector Profiles** — Boolean field distinguishing CONN0 profiles (9 assignable columns) from CONN1–6 profiles (8 assignable columns).
- **Connector Profile `profile_version` field** — Semantic version of the specific profile definition, distinct from `schema_version`.
- **Profile naming convention** — OCP-ratified profiles use the pattern `OAC-PROF-<CONN0|CONN>-<proto>-x<lanes>-<dir>-v<n>[-minified]`.
- **`-minified` file suffix** — Minified JSON profile variants (functionally equivalent to expanded form, whitespace removed for firmware storage).
- **Protocol group numbering** — Protocol groups are now numbered starting at index 0 throughout all tooling and documentation.

### Changed

- **`link_subdivision` removed from CID** — Lane bifurcation mode selection has been moved to the Slot Configuration Data (SCD) mechanism. The `link_subdivision` field is no longer part of the CID schema. Adapters that previously declared `link_subdivision` shall omit it; the upstream management controller shall use SCD to communicate the selected bifurcation mode to the adapter.
- **`ssc_capable` and `ssc_default` removed** — Replaced by the simpler `ssc_supported` boolean. SSC capability and default state are no longer part of the clock schema; `ssc_supported` indicates only whether SSC is supported on the clock.
- **`link_role` removed** — The `link_role` field (ENDPOINT/ROOT/SWITCH) has been removed from the protocol group schema. Link role is an architectural property of the system topology and is not required for BMC compliance evaluation.
- **`minimum_lanes` is Optional** (was Required) — Vendors should declare `minimum_lanes` only when a specific minimum bandwidth is required for correct adapter operation. When absent, the adapter accepts any lane count the host negotiates.
- **`sris_capable` removed** — SRIS (Separate Reference Clock with Independent Spread Spectrum) is a PCIe link-training concern handled autonomously by the PCIe hardware and is not required in the CID.
- **Protocol group `link_direction`** — Restored as a direct field on the protocol group (previously considered under `link_role`). Values: `"INBOUND"` or `"OUTBOUND"`.

### Tooling (CID Editor)

- Added Connector Profile authoring mode
- Added Visual Pin Map with per-pin assignment picker
- Added real-time validation with error/warning panel
- Added syntax-highlighted Manual JSON editing mode
- Added live two-way sync between Guided and Manual modes
- Added Export JSON dropdown (Formatted / Minified)
- Added Import JSON with auto-detection of CID vs. Connector Profile
- Added `✦ Suggest ID` button for Connector Profile identifiers
- Added help modal with Getting Started, Field Reference, Keyboard Shortcuts, and About tabs
- Added `?` hover tooltip icons on key fields
- Added keyboard shortcuts (Alt+G, Alt+M, Alt+I, Alt+E, ?, Esc)
- Pin A1 blocked in Visual Pin Map (reserved for OAC_PRSNT#/M-PESTI)
- Protocol group numbering changed to 0-based

---

## [0.7] — Previous

Initial DMTF-style specification. JSON encoding replacing YAML. FRU File alignment per DSP0220. Operational Power Levels (OPL-MAX, OPL-EFF, OPL-RED, OPL-EMG, OPL-SET). Connector naming updated to CONN0–CONN6. `connector_profile` field for standard pinout references. Updated power connector types (100A/125A). Discrete signals updated with `driver_type`, `default_state`, `pulldown` fields.

---

## [0.3-draft]

Initial draft. YAML encoding. Basic power, connector, and lane schema.
