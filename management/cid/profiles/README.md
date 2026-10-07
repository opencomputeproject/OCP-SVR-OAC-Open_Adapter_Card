# OAC Connector Profiles

This directory contains OCP-ratified OAC Connector Interface Definition (CID) profiles. A connector profile defines standard `high_speed_lanes`, `clocking`, and `discrete_signals` assignments for a given connector position and protocol configuration, allowing a CID to reference the profile by identifier rather than repeating the full pin-level declarations for every adapter that uses the same pinout.

The use of `connector_profile` in a CID is **mutually exclusive** with explicit signal definitions. When a connector object declares `connector_profile`, the `high_speed_lanes`, `clocking`, and `discrete_signals` sections shall not be present in that connector object. Only OCP-ratified profiles may be referenced.

---

## Naming Convention

All profile identifiers use the prefix `OAC-PROF-` and follow this pattern:

```
OAC-PROF-<CONN0|CONN>-<proto1>-x<lanes1>-<dir1>[-<proto2>-x<lanes2>-<dir2>]-v<n>[-minified]
```

| Token | Values | Description |
|-------|--------|-------------|
| `CONN0` \| `CONN` | `CONN0` or `CONN` | `CONN0` = targets CONN0 only (9 assignable columns); `CONN` = targets CONN1–CONN6 (8 assignable columns) |
| `<proto>` | e.g. `PCIeGen6`, `Eth200G` | Protocol abbreviation per Table 7.4.1.2-1 of the specification |
| `x<lanes>` | e.g. `x16`, `x4` | Total high-speed lane count for this protocol segment |
| `<dir>` | `IN` or `OUT` | Signal direction: `IN` = INBOUND (host→OAC), `OUT` = OUTBOUND (OAC→host) |
| `-v<n>` | e.g. `-v1`, `-v2` | Profile revision (incremented when pin assignments change) |
| `-minified` | optional | File contains minified JSON (no optional whitespace); functionally equivalent to the expanded form |

The `profile_id` field inside the JSON file shall always use the base identifier **without** the `-minified` suffix, regardless of whether the file itself is minified. The suffix applies only to the filename.

---

## Available Profiles

| Profile ID | Connector | Protocol | Lanes | Direction | Files |
|------------|-----------|----------|-------|-----------|-------|
| `OAC-PROF-CONN0-PCIeGen6-x16-IN-v1` | CONN0 | PCIe Gen6 | x16 | INBOUND | [expanded](OAC-PROF-CONN0-PCIeGen6-x16-IN-v1.json) · [minified](OAC-PROF-CONN0-PCIeGen6-x16-IN-v1-minified.json) |
| `OAC-PROF-CONN0-PCIeGen6-x8-IN-PCIeGen6-x8-IN-v1` | CONN0 | PCIe Gen6 (x8+x8 bifurcation) | x8+x8 | INBOUND | [expanded](OAC-PROF-CONN0-PCIeGen6-x8-IN-PCIeGen6-x8-IN-v1.json) · [minified](OAC-PROF-CONN0-PCIeGen6-x8-IN-PCIeGen6-x8-IN-v1-minified.json) |
| `OAC-PROF-CONN0-PCIeGen6-x4-IN-PCIeGen6-x4-IN-PCIeGen6-x4-IN-PCIeGen6-x4-IN-v1` | CONN0 | PCIe Gen6 (x4+x4+x4+x4 quad bifurcation) | x4×4 | INBOUND | [expanded](OAC-PROF-CONN0-PCIeGen6-x4-IN-PCIeGen6-x4-IN-PCIeGen6-x4-IN-PCIeGen6-x4-IN-v1.json) · [minified](OAC-PROF-CONN0-PCIeGen6-x4-IN-PCIeGen6-x4-IN-PCIeGen6-x4-IN-PCIeGen6-x4-IN-v1-minified.json) |
| `OAC-PROF-CONN-Eth200G-x16-OUT-v1` | CONN1–6 | Ethernet 200G | x16 | OUTBOUND | [expanded](OAC-PROF-CONN-Eth200G-x16-OUT-v1.json) · [minified](OAC-PROF-CONN-Eth200G-x16-OUT-v1-minified.json) |

---

## BMC Support Requirement

Baseboard management controllers that claim conformance with the OAC CID Specification shall have built-in knowledge of all OCP-ratified profiles published at or before the declared `schema_version`. No runtime fetch is required.

If an adapter's connector configuration does not match any available OCP-ratified profile, the adapter shall define its `high_speed_lanes`, `clocking`, and `discrete_signals` explicitly in the CID — `connector_profile` shall not be used in that case.

---

## Profile File Format

```json
{
  "oac_connector_profile": {
    "profile_id":     "OAC-PROF-...",
    "schema_version": "0.9",
    "is_conn0":       true,
    "description":    "...",
    "high_speed_lanes": { ... },
    "clocking":       [ ... ],
    "discrete_signals": [ ... ]
  }
}
```

`is_conn0` is `true` for CONN0 profiles (9 assignable columns, col 1–9) and `false` for CONN1–CONN6 profiles (8 assignable columns, col 1–8). A profile is not required to define all three sections.

---

## Proposing New Profiles

To propose a new OCP-ratified profile, open a pull request against this repository with the proposed profile JSON file and a description of the adapter configuration it targets. The OCP OAC workstream will review and ratify the profile before it is merged.
