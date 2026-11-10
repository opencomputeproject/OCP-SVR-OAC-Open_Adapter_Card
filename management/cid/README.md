# OCP Open Adapter Card — Connector Interface Definition (CID)

**Document Status:** Draft
**Specification Revision:** 0.9
**Schema Version:** 0.9
**Normative Reference:** OCP Open Adapter Card Base Specification v0.9

---

## Overview

This directory contains the OAC Connector Interface Definition specification, its JSON template,
OCP-ratified connector profiles, reference examples, and interactive authoring and compliance
tooling.

The CID is a machine-readable JSON document stored in OAC firmware that declares everything a
baseboard needs in order to answer one question:

> **May this OAC be powered at all?**

It is purely a **compatibility** artifact. It declares connector population, per-lane pin
assignments, protocol groups, reference clocking, discrete sideband signals, and power envelopes —
and nothing about how the card should be configured once the answer is yes. Configuration is the
job of the companion [Slot Configuration Data](../scd/) specification.

The OAC Base Specification divides the two by subject:

> **CID describes the characteristics, requirements, and capabilities of the OAC to the platform,
> whereas SCD describes the platform environment and operational configuration provided to the OAC.**

So anything that describes the card lives here — connector population, lane counts, pin maps,
reference clocking, discrete signals, and the Operational Power Level menu. Anything that describes
the slot the card has been installed in lives in the SCD: which slot it is, what power that position
can supply, and how a subdividable protocol group is to be partitioned there. The link subdivision
*menu* is in the SCD Definition for that reason, and the SCD's power fields select within the
envelopes declared here and never beyond them.

### Why it exists

An OAC slot carries up to 5 kW through the BK125 connector variant and is not hot-pluggable. A
baseboard cannot discover a card by energizing it and seeing what happens. The CID is how the card
describes itself while still running on +12V_AUX alone.

---

## Transport and Timing

The CID is published by the OAC's management controller as a **FRU Data File** per DSP0257 and
retrieved over MCTP on the OAC Management USB 2.0 interface (CONN0, columns 10–11).

It is described in the OAC's PDR repository by a **File Descriptor PDR per DSP0248**, with
`EntityType` set to Device File and `FileClassification` set to `FRUDataFile`. `FileName` is
`OAC_CID.json`, fixed, and assigned to no other file.

**The controller does not find the CID by matching that name.** It retrieves the
[OAC Metadata file](../metadata/) first, resolves its `cid` role to a `FileIdentifier`, and opens
that identifier. `FileName` *names* the CID — it keeps the file identifiable in a PDR repository
dump, in a firmware image, and to diagnostic tooling, and it is what the metadata advertises
alongside the identifier so the two can be checked against each other. It is not how the CID is
opened. A controller whose metadata retrieval fails shall not fall back to name matching; doing so
would energize a slot on data obtained by a path the OAC never advertised.

The CID is **read-only**. `FcWritesPermitted` and `ExWriteOpen` are both zero, and an OAC shall not
accept a write to it.

It is a **Fixed Length File** in the DSP0242 sense, so `FileMaximumSize` carries the exact
transferred size and is updated whenever a firmware update replaces the CID. Two sensors are
mandatory: a **Device File State Sensor** (DSP0249 State Set 68) signalling content change, and a
**File Size Monitoring Sensor** reporting the exact current size.

The CID is retrievable in Operational State **O3 or later** and shall never require primary power to
serve. The controller reads it **before** reading the SCD Definition — a controller that cannot
supply the OAC's `opl_emg_w` stops there and never reads the Definition at all.

---

## Directory Structure

```
cid/
├── README.md                              ← This file
├── CHANGELOG.md                           ← Revision history
├── specification/
│   └── OAC-CID-Specification-v0.9.md      ← Normative DMTF-style specification
├── templates/
│   └── v0.9/
│       └── OAC-CID-TEMPLATE.json          ← Blank annotated authoring template
├── examples/
│   └── v0.9/                              ← Reference CID documents
├── profiles/                              ← OCP-ratified connector profiles (OAC-PROF-…)
└── tools/
    └── interactive/                       ← Self-contained browser tools, no build step
        ├── oac-cid-editor/
        ├── oac-cid-insertion-emulator/
        └── oac-cid-compliance-logic/
```

Every directory carries its own `README.md`.

Templates and examples are kept in revision-named subfolders. The companion SCD directory is
deliberately flat and single-revision instead — see [`../README.md`](../README.md).

---

## Document Structure

A CID is a JSON object with the root key `"oac_cid"` and three mandatory sections:

```json
{
  "oac_cid": {
    "metadata":   { "schema_version": "0.9", "oac_spec_revision": "0.9" },
    "power":      { "primary": { ... }, "excursion": [ ... ] },
    "connectors": [ ... ]
  }
}
```

| Section | Required | Contents |
|---------|----------|----------|
| `metadata` | Yes | `schema_version` and `oac_spec_revision`, both required; optional `description`, `iana_pen`, `platform_token` |
| `power` | Yes | `primary` object (required): input voltage, connector variant, and the Operational Power Level wattages. `excursion` array (optional): the declared transient power profile |
| `connectors` | Yes | One object per populated connector position: pin map, protocol groups, clocking, discrete signals, and — on CONN0 — the `mpesti_capable` declaration |

### Connectors

Positions `CONN0` through `CONN6`, plus an optional `CABLE`. **CONN0 is always present** — it
carries the management interface — and has **9** assignable columns; CONN1–CONN6 have **8**. Pin
rows are N, M, L, K, J, I, H, G, F, E, D, C, B, A, and **pin A1 is permanently reserved** for
`OAC_PRSNT#` / M-PESTI.

A connector object either references a ratified `connector_profile` **or** declares
`high_speed_lanes`, `clocking`, and `discrete_signals` explicitly. The two are mutually exclusive on
a given connector, though a CID may mix approaches across different connectors.

### Protocol groups

Up to **8** per connector. Each carries a `name` (snake_case, unique within that connector), a
`protocol`, a `link_direction` of `INBOUND` or `OUTBOUND`, a `total_lanes` count of 1–16, an
optional `minimum_lanes` vendor floor below which the controller blocks energization, and a 0-based
`lanes[]` array. USB 2.0 is the exception: exactly one bidirectional lane, `total_lanes` fixed at 1.

Group names are unique **within a connector**, not across the document. Two connectors may each
declare a group named `pcie_primary` and that is conformant — the SCD binding key is the pair
`(connector, group name)`. The expected implementation error here is over-enforcement.

### Power

The `power.primary` object declares `input_voltage`, the `connector_type` variant (`100A` =
4 kW BK100, compatible with all form factors; `125A` = 5 kW BK125, double-wide and double-wide
offset only), and the supported Operational Power Levels:

| Field | OPL | Required |
|-------|-----|----------|
| `opl_max_w` | OPL-MAX | Yes |
| `opl_eff_w` | OPL-EFF | Optional |
| `opl_red_w` | OPL-RED | Optional |
| `opl_emg_w` | OPL-EMG | Yes |
| `opl_set_min_w` | OPL-SET floor | Optional |

`OPL-MAX ≥ OPL-EFF ≥ OPL-RED ≥ OPL-EMG`. The SCD can only narrow this envelope; a configuration
document never raises a hardware limit. Where `opl_set_min_w` is declared, the configurable
OPL-SET range runs from it up to `opl_max_w` — there is no separately declared ceiling, because
a settable level above the OAC's maximum validated operating point would not be a valid
operating point. The presence of `opl_set_min_w` is what declares OPL-SET support.

### Power excursion

`power.excursion` is optional, and is an array of 2 to 8 `{ interval_us, ratio_max }` entries in
strictly ascending interval order. Each entry states the largest ratio of average power to
`opl_max_w` the OAC reaches over an averaging interval of that length.

Base Specification Section 10.1.4 already defines a ceiling for every OAC. It is piecewise — 3 for
T ≤ 100 µs, `4 − 0.2171 × ln(T)` for 100 < T < 1,000,000 µs, and 1 for T ≥ 1,000,000 µs — and a
validator that extrapolates the logarithm past either end gets the wrong answer. But that ceiling
describes the worst card the specification permits, not this one. A platform budgeting every slot
against it over-provisions every slot. The array is how a card says where it actually sits, and
because every declared ratio is checked against the envelope, the declaration is enforceable rather
than advisory.

Three things about it are counter-intuitive enough to be worth stating here:

- `ratio_max` is normalized to `opl_max_w` **only**. The profile does not rescale at OPL-EFF, so
  running at a lower sustained level does not buy a larger absolute excursion.
- The profile applies at OPL-MAX and OPL-EFF only. At OPL-RED, OPL-EMG, and OPL-SET the effective
  ratio is 1 regardless of what the file says — those levels exist because the platform is
  constrained, and an allowance there would defeat them.
- Interpolation is **nearest shorter declared interval**, not linear. The rule rounds toward the
  larger ratio in every direction, which is the conservative direction for a power budget.

**Absent is not zero.** An OAC that declares no `excursion` has not claimed it makes no excursions;
it has declined to characterize them, and the controller budgets it at the Section 10.1.4 ceiling.
See Section 7.3.2 of the specification.

---

## Quick Start

1. Copy `templates/v0.9/OAC-CID-TEMPLATE.json`.
2. Replace every `"<placeholder>"` with a real value, and set `schema_version` to `"0.9"`.
3. For each connector, either reference a ratified profile from [`profiles/`](profiles/) or declare
   signals explicitly — not both on the same connector.
4. Remove optional fields that do not apply.
5. Validate that the JSON is well-formed per ECMA-404. No comments: `//` and `/* */` outside a
   string literal make the document malformed.
6. **Choose an encoding.** Publish UTF-8 with no byte order mark, in expanded or minified form. Both are valid and a controller shall accept either; minified is recommended for production, purely to reduce the transferred payload.
7. Set `FileMaximumSize` in the File Descriptor PDR to the exact transferred size.

Or use the [CID Editor](tools/interactive/oac-cid-editor/) and skip steps 1 through 5 — it does
guided authoring with a visual pin map and live JSON preview, entirely in the browser.

---

## Connector Profiles

A profile is an OCP-ratified standard pinout, referenced by identifier so that a CID need not repeat
a full pin map for a configuration many cards share. Four are ratified for v0.9:

| Profile | Connector | Configuration |
|---------|-----------|---------------|
| `OAC-PROF-CONN0-PCIeGen6-x16-IN-v1` | CONN0 | PCIe Gen6 x16 inbound |
| `OAC-PROF-CONN0-PCIeGen6-x8-IN-PCIeGen6-x8-IN-v1` | CONN0 | PCIe Gen6, x8 + x8 bifurcation |
| `OAC-PROF-CONN0-PCIeGen6-x4-IN-…-v1` | CONN0 | PCIe Gen6, x4 × 4 quad bifurcation |
| `OAC-PROF-CONN-Eth200G-x16-OUT-v1` | CONN1–6 | 200G Ethernet x16 outbound |

Controllers claiming conformance carry built-in knowledge of every profile ratified at or before the
`schema_version` they support. There is no runtime fetch. See [`profiles/README.md`](profiles/README.md)
for the naming convention and submission process.

---

## Reference Examples

In [`examples/v0.9/`](examples/v0.9/):

| File | Power | Description |
|------|-------|-------------|
| `OAC-CID-0.9-2500W-PCIe-x16-(Example_using_connector_profile).json` | +50V, 125A, 2500 W OPL-MAX | Double-wide offset. CONN0 declared entirely by profile reference — the shortest conformant CID |
| `OAC-CID-0.9-SW-2500W-16L_PCIe-96L_Ethernet(Example_mixed_definition).json` | +50V, 100A, 2500 W OPL-MAX | Single-wide. CONN0 with an explicit pin map, plus six Ethernet connectors by profile reference. Shows the two approaches mixed in one document |
| `OAC-CID-0.9-ExampleA-Excursion-4800W.json` | +50V, 125A, 4800 W OPL-MAX | Declares a transient profile materially better than the Section 10.1.4 ceiling — the case `power.excursion` was added for |
| `OAC-CID-0.9-ExampleB-Excursion-600W.json` | +12V, 100A, 600 W OPL-MAX | Declares the full 3× short-interval allowance. The case the validation rules have to keep legal |
| `OAC-CID-0.9-ExampleC-Excursion-3000W.json` | +50V, 100A, 3000 W OPL-MAX | Two connectors, 2.80× at 10 µs. The implied current exceeds the BK100 derated continuous rating, which is reported and not judged |

For worked end-to-end examples that pair a CID with its SCD Definition and Assignment, see
[`../scd/examples/`](../scd/examples/) — three matched triples, which is the only place all three
documents appear side by side.

---

## Tooling

All three tools in [`tools/interactive/`](tools/interactive/) are single-file HTML with no
dependencies, no server, and no build step. Open them directly in a browser.

| Tool | Purpose |
|------|---------|
| [CID Editor](tools/interactive/oac-cid-editor/) | Guided or manual CID and profile authoring, visual pin map, live JSON preview |
| [Insertion Emulator](tools/interactive/oac-cid-insertion-emulator/) | Animated insertion simulation; load a baseboard capability file and a CID, watch the compliance checks run |
| [Compliance Logic](tools/interactive/oac-cid-compliance-logic/) | Static reference diagram of the controller's check sequence and its failure outcomes |

---

## Normative References

| Reference | Document |
|-----------|----------|
| DSP0220 | DMTF, "FRU Data Specification," Version 1.0.1 |
| DSP0236 | DMTF, "Management Component Transport Protocol (MCTP) Base Specification" |
| DSP0240 | DMTF, "PLDM Base Specification," Version 1.2 |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification," Version 1.3.1 |
| DSP0249 | DMTF, "PLDM State Set Specification," Version 1.4.0 |
| DSP0257 | DMTF, "PLDM for FRU Data Specification," Version 2.0 |
| ECMA-404 | ECMA International, "JSON Data Interchange Syntax," 2nd Edition |
| OCP OAC | OCP, "Open Adapter Card Base Specification," Version 0.9 |

The authoritative list is Section 2 of the specification itself.

---

## Revision History

See [CHANGELOG.md](CHANGELOG.md). Headline changes at v0.9: `link_subdivision` moved out to the SCD;
`link_role`, `sris_capable`, and the `ssc_capable`/`ssc_default` pair removed; a required `name`
added to every protocol group; `connector_profile` introduced; and the compression section removed
entirely — a CID is plain UTF-8 JSON and nothing else.

The v0.9 document was revised in place on **2026-10-08** following the OAC workstream review.
Connector profiles became their own Section 8, which renumbered CID Retrieval and Validation to 9,
Compliance to 10, and Annex C to Annex B. The presence-detect material, `high_speed_lanes`
presence, and the relationship between the CID and mechanical keying were rewritten, Annex A was
replaced with two complete examples, and the document standardized on "the OAC". Section
numbers cited elsewhere in this repository refer to the revised document.

It was revised again on **2026-10-09**: `opl_set_max_w` was removed in favour of bounding the
configurable OPL-SET range by `opl_max_w`, the connector profile field `is_conn0` was replaced by
the position-token array `applicable_conns` (which also extends the profile identifier grammar
to `CABLE` and to per-position segments such as `OAC-PROF-CONN6-…`), and the single-field `presence_detect` object was flattened into a `mpesti_capable`
field required on CONN0 and prohibited elsewhere. Section numbering is unchanged by that
revision. See [CHANGELOG.md](CHANGELOG.md).

A third in-place revision followed on **2026-11-09**, again without a version bump. File discovery
moved to the new [OAC Metadata file](../metadata/), lifting the WORK IN PROGRESS annotation Section
6.3 had carried since first publication; the ignore-unrecognized-keys rule of Section 7.1 was
extended to every level of nesting; and the optional `power.excursion` array was added as new
Section 7.3.2, with validation checks in Table 9.3-1 and conditional conformance rows in Sections
10.1 and 10.2. Section numbering is unchanged. See [CHANGELOG.md](CHANGELOG.md).

---

## Known Issues

Open items against the shipped v0.9 content, recorded so they are not rediscovered:

| Issue | Location |
|-------|----------|
| The two original reference examples omit `schema_version` and `oac_spec_revision`, which Table 7.2-1 marks **Required**. Their `metadata` objects carry only `description`. The three excursion examples are not affected | `examples/v0.9/OAC-CID-0.9-2500W-…` and `…-SW-2500W-…` |
| The same two example descriptions read "645W OPL-EMG" while the declared `opl_emg_w` is 625 | `examples/v0.9/OAC-CID-0.9-2500W-…` and `…-SW-2500W-…` |
| Section 7.4.3 justifies the eight-protocol-group limit by "the uint32 SCD effecter encoding … one 4-bit nibble per protocol group" — a rationale inherited from a superseded SCD draft that no longer describes how SCD works. The limit itself is correct; only the justification is stale | `specification/`, Section 7.4.3 |
| The three interactive HTML tools still say "adapter" where the specification now says "the OAC", and the compliance logic diagram labels the validation clause 8.3, which the 2026-10-08 revision renumbered to 9.3. The tool READMEs record this; the tools themselves have not been regenerated | `tools/interactive/` |

One mechanism is still annotated **WORK IN PROGRESS** inside the specification itself and is
expected to change before v0.9 is published as final: the Section 8.5 profile applicability cases.
Section 6.3's annotation was lifted in the 2026-11-09 revision when file discovery moved to the
OAC Metadata file. See [specification/README.md](specification/README.md#open-items).

Resolved in the 2026-10-08 revision and recorded here so they are not re-reported: the Section 2
reference list (MessagePack and RFC 1952 removed, DSP0236/DSP0248/DSP0249 added, DSP0242 cited
undated, the `OCP OAC v0.9` row corrected from "Version 0.8"), the Contents block numbering, and the
"adapter" / "the OAC" divergence within `specification/`. See [CHANGELOG.md](CHANGELOG.md).

---

## License

See [LICENSE](../../LICENSE) at the repository root.
