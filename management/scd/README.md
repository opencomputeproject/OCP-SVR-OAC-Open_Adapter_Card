# OCP Open Adapter Card — Slot Configuration Data (SCD)

**Document Status:** Draft  
**Specification Revision:** 0.9

---

## Overview

This directory contains the OAC Slot Configuration Data specification, JSON templates, paired reference examples, and a validation tool. SCD is the return path of the CID conversation: the OAC declares what it is, the platform tells it what to be.

```
   OAC  ──── CID  (compatibility characteristics) ───────►  Upstream management controller
   OAC  ──── SCDD (configurable fields and defaults) ────►  Upstream management controller
   OAC  ◄─── SCDA (assigned field values) ──────────────────┘
```

The **SCD Definition (SCDD)** is a FRU file the OAC publishes: a template of every settable field, each with its type, bounds, response class, and a **mandatory default**. The **SCD Assignment (SCDA)** is a **sparse** PLDM file the controller writes back, keyed by field identifier, carrying only the fields it wants to change.

That structure is what lets a generic controller and an unfamiliar OAC still agree. A controller that does not recognize a field simply omits it, and because every field carries a default, the OAC's behavior is still fully determined. A model in which the controller must infer the configurable surface from the CID has no way to express that — an unknown capability has to be either guessed at or ignored, and neither is safe.

### What this replaces

SCD is a replacement for hardware strapping. A strapped interface commits its width at board layout: *n* inputs distinguish at most 2^*n* states, the encoding is positional and untyped, and both ends must agree on its meaning out of band. Extending it means an additional pin, its pull network, a board revision, and re-qualification — which is why strapping in practice carries a few coarse values, slot identity and link width among them, and leaves everything else to be fixed in firmware per platform.

SCD carries the same information as typed, named, self-describing fields, bounded by the 32 KiB transferred Definition limit rather than by pin count. An added attribute costs a schema revision and a `definition_revision` increment shipped by firmware update, not an electrical respin. Because identifiers are namespaced, a vendor adds fields under its own `pen.<IANA PEN>.` prefix with no OCP registration and no risk of collision, and a controller that has never heard of them omits them and lets the declared defaults stand. The fixed handful of strapped bits becomes an extensible configuration surface that each OAC describes for itself.

### The placement rule

The line between the two OAC-published documents is a single question:

> **Does the platform need this to decide whether to power the OAC at all?**
> **Yes → CID. No → SCD.**

Power envelopes stay in the CID, because the platform must know them before `OAC_PWR_EN`. The subdivision *menu* lives in the Definition, because the platform does not need it to make the power decision.

### Transport and timing

The CID and the SCD Definition are read by the upstream management controller as **FRU Files** via PLDM for FRU Data (DSP0257). The SCD Assignment travels the other direction as a **PLDM file** via PLDM for File Transfer (DSP0242) — `DfOpen` → `DfWrite` → `DfClose` — over MCTP on the same OAC Management USB 2.0 interface. The Assignment is **not** FRU data and is never placed in the FRU Files Record.

The Assignment is written and accepted while the OAC is in Operational State **O3**, *before* `OAC_PWR_EN` is asserted. Primary power is never enabled before the OAC has validated and accepted its configuration. The configuration latches on the O3 → O4 transition. **The accepted configuration shall not be stored in non-volatile memory** — a cached assignment that survives a slot change is a misconfiguration waiting to happen.

---

## Directory Structure

```
scd/
├── README.md                                   ← This file
├── CHANGELOG.md                                ← Revision history and porting notes
├── specification/
│   └── OAC-SCD-Specification-v0.9.md
├── templates/
│   ├── OAC-SCDD-TEMPLATE.json                  ← Annotated Definition template
│   └── OAC-SCDA-TEMPLATE.json                  ← Annotated Assignment template
├── examples/                                   ← Matched CID + SCDD + SCDA triples (A, B, C)
└── tools/
    ├── validate-scd.py                         ← Validator
    └── test-validate-scd.py                    ← Self-test, positive and negative cases
```

Each of the four directories carries its own `README.md`, omitted above; those are where the authoring guidance lives.

Only the current revision is carried in the tree. Superseded revisions remain retrievable from git history; CHANGELOG.md names the commit. The companion [CID directory](../cid/) is organized differently — it keeps revision-named subfolders for templates and examples. Neither layout should be harmonized to the other without raising it with the workstream.

---

## Document Structure

An SCD Definition is a JSON object with the root key `"oac_scdd"` and two sections:

```json
{
  "oac_scdd": {
    "metadata": { "schema_version": "0.9", "definition_revision": 1, ... },
    "fields":   [ { "id": "ocp.slot_id", "type": "integer", "default": 255, ... } ]
  }
}
```

An SCD Assignment is a JSON object with the root key `"oac_scda"`, also two sections, with the assignments keyed by field identifier:

```json
{
  "oac_scda": {
    "metadata":    { "schema_version": "0.9", "definition_revision": 1 },
    "assignments": { "ocp.slot_id": 5, "ocp.max_power_w": 2000 }
  }
}
```

Field identifiers are namespaced. `ocp.` is reserved for the registry in Specification Section 10; a vendor uses `pen.<IANA PEN>.<field_name>` and needs no OCP registration to do so.

Five rules carry most of the weight:

- **Every field descriptor carries a default.** This is what makes a sparse Assignment safe, and it is not optional.
- **The Assignment is sparse.** Omission means "use the default," which is a decision, not an oversight.
- **`required` is advisory, not mandatory.** A controller that does not recognize a `required` field omits it and the OAC proceeds on the default. Without this, one unknown vendor field would brick an otherwise working pair.
- **Group names are unique within a connector, not across the document.** The binding key is the pair `(cid_connector, cid_group_name)`. Two connectors may both declare a group named `pcie_primary`, and that is conformant.
- **Conflicting power values clamp, they do not reject.** The applied cap is `min(ocp.initial_power_level_set_w, ocp.max_power_w, opl_max_w)`.

---

## Quick Start

1. Read the OAC's CID over PLDM for FRU Data. Decide whether to power it at all.
2. Read the OAC's SCD Definition, also over PLDM for FRU Data, and resolve any `connector_profile` references in the CID.
3. Copy `templates/OAC-SCDA-TEMPLATE.json` and compose an Assignment. Set only the fields you recognize and want to change; omit everything else, including `required` fields you have no opinion about.
4. Echo the Definition's `definition_revision` in your Assignment metadata. A mismatch means you composed against a stale Definition and must re-read.
5. Delete every `$comment` key — ECMA-404 permits no comments, so the annotations are an authoring convenience only.
6. Validate with `tools/validate-scd.py`.
7. Minify. The transferred size limits are 32 KiB for a Definition and 8 KiB for an Assignment.
8. Transfer with `DfOpen`/`DfWrite`/`DfClose` while the OAC is in O3, before asserting `OAC_PWR_EN`.

To author a Definition rather than an Assignment — that is, if you are building an OAC — start from `templates/OAC-SCDD-TEMPLATE.json` and read `templates/README.md`.

---

## Reference Examples

Three matched triples ship here. Full write-ups are in [examples/README.md](examples/README.md).

| Triple | Exercises |
|--------|-----------|
| **A** | The smallest legal pair. CONN0 by profile reference, no subdividable group, no OPL-SET band, so the Definition declares two fields and no `protocol_group` binding at all |
| **B** | The common case. One subdividable group, both response classes, both `cid_binding` kinds, the sentinel default, both namespaces — and a sparse Assignment whose *omissions* are the instructive half |
| **C** | **The conformance triple.** Two connectors each declare a group named `pcie_primary`. That duplicate is deliberate and conformant; a validator enforcing document-wide name uniqueness will reject this CID, which is exactly the failure this triple exists to catch |

The size asymmetry is the point. A CID carries per-lane pin maps and runs to tens of kilobytes. A Definition is dominated by prose descriptions and runs to a few kilobytes. An Assignment is a handful of scalars and stays under a kilobyte.

---

## Validation Tool

`tools/validate-scd.py` validates a Definition, optionally an Assignment against it, and optionally both against the CID:

```
python3 tools/validate-scd.py \
    --cid  examples/OAC-CID-0.9-ExampleC-MultiConnector-NameReuse.json \
    --scdd examples/OAC-SCDD-0.9-ExampleC-MultiConnector-NameReuse.json \
    --scda examples/OAC-SCDA-0.9-ExampleC-Slot1-PartialSubdivision.json
```

Exit status is `0` for accepted, `1` for rejected, `2` for a tool or input error. `tools/test-validate-scd.py` runs the shipped examples plus a suite of deliberate mutations; see [tools/README.md](tools/README.md).

---

## Revision History

See [CHANGELOG.md](CHANGELOG.md).

---

## Normative References

These are the normative references of Specification Section 2.

| Reference | Document |
|-----------|----------|
| DSP0236 | DMTF, "Management Component Transport Protocol (MCTP) Base Specification," v1.3 |
| DSP0240 | DMTF, "PLDM Base Specification," v1.2 |
| DSP0241 | DMTF, "PLDM over MCTP Binding Specification," v1.0 |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification," v1.3.1 |
| DSP0249 | DMTF, "PLDM State Set Specification," v1.4.0 |
| DSP0257 | DMTF, "PLDM for FRU Data Specification," v2.0 |
| ECMA-404 | ECMA International, "JSON Data Interchange Syntax," 2nd Ed. |
| OAC-CID-SPEC | OCP, "OAC Connector Interface Definition (CID) Specification," v0.9 |
| OCP OAC | OCP, "Open Adapter Card Base Specification," v0.9 |

DSP0247 is cited in the specification as informative precedent for the Definition/Assignment split, not as a normative reference.

---

## License

See [LICENSE](../../LICENSE) at the repository root.
