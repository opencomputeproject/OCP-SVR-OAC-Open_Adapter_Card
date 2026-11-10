# OCP Open Adapter Card — OAC Metadata

**Document Status:** Draft  
**Specification Revision:** 0.9

---

## Overview

This directory contains the OAC Metadata specification, its JSON Schema, an annotated template, three reference examples, and a validation tool. The metadata file is the entry point to the OAC management model: the upstream management controller reads it first, and uses it to locate everything else.

```
   OAC  ──── Metadata (where the management files are) ──►  Upstream management controller
                                                                      │
                   ┌──────────────────────────────────────────────────┘
                   ▼
   OAC  ──── CID  (compatibility characteristics) ───────►  Upstream management controller
   OAC  ──── SCDD (configurable fields and defaults) ────►  Upstream management controller
   OAC  ◄─── SCDA (assigned field values) ──────────────────┘
```

The file carries one thing: a mapping from file role to the `FileIdentifier` and `FileName` of the DSP0248 File Descriptor PDR that describes that file. It carries no connector data, no power data, and no configuration data.

```json
{
  "oac_metadata": {
    "schema_version": "0.9",
    "files": {
      "cid":  { "file_identifier": 1608, "file_name": "OAC_CID.json"  },
      "scdd": { "file_identifier": 1601, "file_name": "OAC_SCDD.json" },
      "scda": { "file_identifier": 1604, "file_name": "OAC_SCDA.json" }
    }
  }
}
```

### What this replaces

Previously the CID and SCD specifications each fixed a `FileName` string, and a controller located the files by matching those strings against the File Descriptor PDRs the OAC published. The arrangement worked, but it put the file catalogue in the specifications rather than on the card: every new management file required a new reserved name in a published document, and a controller could find only the files whose names were compiled into it.

The metadata file moves the catalogue onto the card. A new file role is added by extending a JSON document, and a controller that has never heard of that role ignores it and carries on — which is precisely the behavior that makes the extension safe to ship.

### The name does not disappear

It reduces from three reserved strings to one. The metadata file is itself a file in the PDR repository, so something has to be known in advance to find it. That something is:

```
OAC_METADATA.json
```

This is the only reserved `FileName` in the OAC management model, and an OAC shall not assign it to any other file. Specification Section 6.3 fixes it.

### Name identifies, identifier opens

Worth stating once, because it is the detail implementations get wrong. `FileName` is a `strASCII` string carried in the File Descriptor PDR; `FileIdentifier` is a `uint16` in that same record, unique relative to the PLDM Terminus ID, and it is what `DfOpen` takes. A controller therefore **matches on the name to find the record, then opens with the identifier from that record**. The metadata file carries both for every role so that a controller never has to perform the first step again after the bootstrap.

The `file_name` values for the three OCP-defined roles remain fixed by specification, which looks at first like a contradiction of the whole exercise. It is not. Those names are no longer the discovery mechanism — they are retained so the files stay identifiable in a PDR dump, a firmware image, and diagnostic tooling. A vendor-defined role carries no such constraint.

### Transport and timing

The metadata file is published as a **FRU Data File** and read via PLDM for FRU Data (DSP0257) over MCTP on the OAC Management USB 2.0 interface — the same path the CID and the SCD Definition use. It is read-only; an OAC rejects writes to it.

It is retrieved in Operational State **O3**, before `OAC_PWR_EN` is asserted, and before the CID. If it cannot be read or fails validation, the slot is **not** energized, and a controller shall **not** fall back to matching `OAC_CID.json` directly. That fallback would reintroduce the assumption this file exists to remove, and would energize a slot on data obtained by a path the OAC never advertised.

---

## Directory Structure

```
metadata/
├── README.md                                   ← This file
├── CHANGELOG.md                                ← Revision history and porting notes
├── OAC-Metadata-v0.9.schema.json               ← JSON Schema, Draft 2020-12
├── specification/
│   └── OAC-Metadata-Specification-v0.9.md
├── templates/
│   └── OAC-METADATA-TEMPLATE.json              ← Annotated authoring template
├── examples/                                   ← Three reference documents (A, B, C)
└── tools/
    ├── validate-metadata.py                    ← Validator
    └── test-validate-metadata.py               ← Self-test, positive and negative cases
```

Each of the four directories carries its own `README.md`, omitted above; those are where the authoring guidance lives.

The schema sits at the top of this directory rather than in a `schema/` subfolder, so that its `$id` — a raw GitHub URL pointing at this path — stays short and stable. Only the current revision is carried in the tree, following the [SCD layout](../scd/) rather than the revision-named subfolders of the [CID](../cid/).

---

## Rules That Carry the Weight

- **`cid` is mandatory.** The CID is what the energization decision is made on. An OAC that publishes no CID cannot be evaluated.
- **`scdd` and `scda` are declared together or not at all.** They are halves of one exchange. An OAC that implements no Slot Configuration Data declares neither, and the controller proceeds to energization on the CID alone.
- **`file_identifier` values are distinct across roles.** This is the defect the artifact exists to prevent, and the reason the validator has a semantic layer at all — JSON Schema cannot express it. Two roles sharing an identifier send the controller to the wrong file, which it then opens successfully and parses successfully. No error is raised anywhere in the transport.
- **`OAC_METADATA.json` never appears as an entry.** An entry carrying it would describe a file that is already open.
- **Unrecognized keys are ignored at every level of nesting**, not just at the root. A rule written only for the root object would leave undefined exactly the case this document's extensibility depends on.

### Vendor-defined roles

A vendor adds files under `pen.<IANA PEN>.<name>`, with no OCP registration required:

```json
"pen.32473.telemetry_map": { "file_identifier": 1712, "file_name": "VENDOR_TELEMETRY_MAP.json" }
```

This follows the SCD's namespacing convention rather than the CID's `vendor_<name>_` prefix. A role key identifies a file in the same sense an SCD field identifier identifies a field, and an IANA PEN is globally unique where a vendor name string is not. (PEN 32473 is the value IANA reserves for documentation and is what the published examples use.)

### Version compatibility

`schema_version` is `major.minor`, both components permitting multiple digits. A controller accepts a document whose **major** component it implements and ignores roles it does not recognize; it rejects a document whose major component it does not implement.

This is deliberately looser than the SCD, where `SCHEMA_VERSIONS` is the exact set `{"0.9"}`. The reason is what each document is. A partially understood SCD Definition can produce a configuration both sides believe is valid and that is not. A role a controller does not recognize is simply a file it will not open — indistinguishable from the role being absent, and safe. Minor-version tolerance costs nothing here and is the mechanism by which the extensibility is actually realized.

---

## Quick Start

1. Locate the File Descriptor PDR whose `FileName` is `OAC_METADATA.json`.
2. Open it with the `FileIdentifier` from that same PDR and retrieve the file over DSP0257.
3. Validate per Specification Section 8.2 — including that each declared `file_identifier` corresponds to a PDR that actually exists. A role naming an identifier the repository does not contain is a malformed document, not a missing file.
4. Resolve the `cid` role and retrieve the CID using its identifier. Decide whether to power the OAC at all.
5. If `scdd` and `scda` are present, resolve and retrieve the Definition, compose an Assignment, and write it. If absent, proceed.
6. Assert `OAC_PWR_EN`.

To author a metadata file — that is, if you are building an OAC — start from `templates/OAC-METADATA-TEMPLATE.json` and read [templates/README.md](templates/README.md). Delete every `$comment` key before shipping and minify the result.

---

## Reference Examples

Three documents ship here. Full write-ups are in [examples/README.md](examples/README.md).

| Example | Exercises |
|---------|-----------|
| **A** | The ordinary case. All three OCP-defined roles, distinct identifiers, the fixed names |
| **B** | A vendor-defined role under `pen.32473.telemetry_map` alongside the three defined roles |
| **C** | **The conformance case.** `cid` alone, with `scdd` and `scda` both absent. A validator that treats SCD as mandatory will reject this document, which is exactly the failure it exists to catch |

---

## Validation Tool

`tools/validate-metadata.py` validates a metadata document against the schema and then applies the semantic rules the schema cannot express:

```
python3 tools/validate-metadata.py examples/OAC-METADATA-0.9-ExampleA-Minimal.json
```

The schema defaults to the sibling `OAC-Metadata-v0.9.schema.json`, so `--schema` is rarely needed. `--resolve DIR` additionally checks that every advertised `file_name` exists in `DIR`; that is useful against a staged firmware image and meaningless against this repository, where the artifacts carry repository names rather than `FileName` values.

Exit status is `0` for valid, `1` for a failed instance, `2` for a schema or input error, `3` for a missing `jsonschema` dependency. `tools/test-validate-metadata.py` runs the shipped examples and template plus a suite of deliberate mutations; see [tools/README.md](tools/README.md).

---

## Revision History

See [CHANGELOG.md](CHANGELOG.md).

---

## Normative References

These are the normative references of Specification Section 2.

| Reference | Document |
|-----------|----------|
| DSP0236 | DMTF, "Management Component Transport Protocol (MCTP) Base Specification" |
| DSP0240 | DMTF, "PLDM Base Specification," v1.2 |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification," v1.3.1 |
| DSP0249 | DMTF, "PLDM State Set Specification," v1.4.0 |
| DSP0257 | DMTF, "PLDM for FRU Data Specification," v2.0 |
| ECMA-404 | ECMA International, "JSON Data Interchange Syntax," 2nd Ed. |
| OAC-CID-SPEC | OCP, "OAC Connector Interface Definition (CID) Specification," v0.9 |
| OAC-SCD-SPEC | OCP, "OAC Slot Configuration Data (SCD) Specification," v0.9 |
| OCP OAC | OCP, "Open Adapter Card Base Specification," v0.9 |

---

## License

See [LICENSE](../../LICENSE) at the repository root.
