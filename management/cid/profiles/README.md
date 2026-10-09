# OAC Connector Profiles

This directory contains OCP-ratified OAC Connector Interface Definition (CID) profiles. A connector profile defines standard `high_speed_lanes`, `clocking`, and `discrete_signals` assignments for a given connector position and protocol configuration, allowing a CID to reference the profile by identifier rather than repeating the full pin-level declarations for every OAC that uses the same pinout.

The use of `connector_profile` in a CID is **mutually exclusive** with explicit signal definitions. When a connector object declares `connector_profile`, the `high_speed_lanes`, `clocking`, and `discrete_signals` sections shall not be present in that connector object. Only OCP-ratified profiles may be referenced.

---

## Naming Convention

All profile identifiers use the prefix `OAC-PROF-` and follow this pattern:

```
OAC-PROF-<CONN0|CONN|CABLE>-<proto1>-x<lanes1>-<dir1>[-<proto2>-x<lanes2>-<dir2>]-v<n>[-minified]
```

| Token | Values | Description |
|-------|--------|-------------|
| `CONN0` \| `CONN` \| `CABLE` | `CONN0`, `CONN`, or `CABLE` | The connector position class the profile is ratified against. `CONN0` = CONN0 only (9 assignable columns); `CONN` = any of CONN1–CONN6 (8 assignable columns); `CABLE` = the CABLE position. Shall agree with the profile's `applicable_conns` field |
| `<proto>` | e.g. `PCIeGen6`, `Eth200G` | Protocol abbreviation per Table 8.3-1 of the specification |
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

## Controller Support Requirement

An upstream management controller that claims conformance with the OAC CID Specification shall have built-in knowledge of the OCP-ratified profiles that the baseboard supports, published at or before the declared `schema_version`. No runtime fetch is required. A controller that encounters a `connector_profile` it does not recognize shall handle the reference robustly and shall not energize the slot on the strength of an unresolved profile. See [OAC-CID-Specification-v0.9.md](../specification/OAC-CID-Specification-v0.9.md) Section 8.3.

If an OAC's connector configuration does not match any available OCP-ratified profile, the OAC shall define its `high_speed_lanes`, `clocking`, and `discrete_signals` explicitly in the CID — `connector_profile` shall not be used in that case.

---

## Profile File Format

```json
{
  "oac_connector_profile": {
    "profile_id":     "OAC-PROF-...",
    "schema_version": "0.9",
    "applicable_conns": ["CONN0"],
    "description":    "...",
    "high_speed_lanes": { ... },
    "clocking":       [ ... ],
    "discrete_signals": [ ... ]
  }
}
```

`applicable_conns` declares the connector position class or classes the profile was ratified against. It is a non-empty array drawn from `"CONN0"` (9 assignable columns, col 1–9), `"CONN1-6"` (8 assignable columns, col 1–8, interchangeable for profile purposes), and `"CABLE"`, with each token appearing at most once. In this revision the array shall contain exactly one token, and it shall agree with the connector segment of `profile_id`: `CONN0` corresponds to `["CONN0"]`, `CONN` to `["CONN1-6"]`, and `CABLE` to `["CABLE"]`. A profile is not required to define all three signal sections.

---

## Proposing New Profiles

To propose a new OCP-ratified profile, open a pull request against this repository with the proposed profile JSON file and a description of the OAC configuration it targets. The OCP OAC workstream will review and ratify the profile before it is merged.
