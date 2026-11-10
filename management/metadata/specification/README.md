# Specification

**OAC Metadata Specification Version:** 0.9  
**OAC Base Specification Reference:** v0.9  
**Document Status:** Draft

## Contents

| File | Description |
|------|-------------|
| [OAC-Metadata-Specification-v0.9.md](OAC-Metadata-Specification-v0.9.md) | The normative specification of the OAC Metadata file |

Only the current revision is carried here. Superseded revisions remain in git history; [CHANGELOG.md](../CHANGELOG.md) names the commit.

## What the document covers

The metadata file is the entry point to the OAC management model — the first file an upstream management controller reads, and the file that tells it where the others are. The specification defines its structure, its encoding, the one reserved `FileName` by which it is itself located, and the retrieval sequence.

| Section | Subject |
|---------|---------|
| 1 | Scope, and what the metadata file replaces |
| 2 | Normative references |
| 3–4 | Terms, symbols, abbreviations |
| 5 | Purpose, and schema version compatibility |
| 6 | The metadata file as a FRU file — encoding, classification, and the reserved `OAC_METADATA.json` |
| 7 | JSON document structure — the `oac_metadata` object, the `files` object, the file descriptor object, and vendor roles |
| 8 | Retrieval sequence, validation requirements, failure handling |
| 9 | Compliance requirements, split between the OAC and the controller |
| Annex A | Example documents (informative) |
| Annex B | PLDM field value reference (informative) |

## The sections that get misread

**Section 6.3 — the reserved name.** The metadata file does not eliminate the hard-coded `FileName`; it reduces the count from three to one. Something has to be known in advance or discovery cannot begin. `OAC_METADATA.json` is that one thing, and it is the only reserved file name in the OAC management model.

**Section 6.3 again — name versus identifier.** `FileName` is how a controller *recognizes* the record. `FileIdentifier`, a `uint16` in that same record, is what `DfOpen` *takes*. A controller matches the name, then opens with the identifier from the record it just matched. This specification fixes the name and deliberately fixes no identifier — a name is a property of a specification, an identifier is a property of a particular OAC's PDR repository, and no OAC can guarantee a fixed value against its other device files.

**Section 7.4 and Table 7.4-2 — why the names are still fixed.** The three OCP-defined roles still carry fixed `file_name` values, which looks like the exercise undoing itself. It is not. Those names were the discovery mechanism and are now merely descriptive, retained so the files stay identifiable in a PDR dump and to diagnostic tooling. A vendor-defined role carries no such constraint.

**Section 5.2 — why version handling is looser than the SCD's.** The SCD accepts exactly `0.9` and nothing else. Metadata accepts any document whose major component the controller implements. The asymmetry is deliberate: an unrecognized SCD field can produce a configuration both sides believe is valid and that is not, whereas an unrecognized file role is a file the controller does not open — the same outcome as the role being absent.

**Section 8.3 — why there is no fallback.** A controller whose metadata retrieval fails shall not drop back to matching `OAC_CID.json`. That shim is the obvious compatibility move and it is exactly wrong: it energizes a slot on data obtained by a path the OAC never advertised.

## Related documents

- [OAC CID Specification](../../cid/specification/) — the artifact the `cid` role points at
- [OAC SCD Specification](../../scd/specification/) — the artifacts the `scdd` and `scda` roles point at
- [management/README.md](../../README.md) — how the four documents fit together
