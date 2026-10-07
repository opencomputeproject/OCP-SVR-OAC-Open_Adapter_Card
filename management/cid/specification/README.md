# OAC Connector Interface Definition (CID) Specification

**Specification Version:** 0.9
**Document Identifier:** OAC-CID-SPEC
**Document Status:** Draft
**Workstream:** Open Compute Project (OCP) — Open Adapter Card (OAC)
**Normative Reference:** OCP Open Adapter Card Base Specification v0.9

---

## Document

→ [OAC-CID-Specification-v0.9.md](OAC-CID-Specification-v0.9.md)

---

## Description

This specification defines the Connector Interface Definition — a machine-readable JSON document
stored in OAC firmware that declares the connector population, power requirements, Operational Power
Levels, high-speed signaling assignments, reference clocking, and vendor-defined discrete signals of
an OAC.

The CID is published by the OAC's management controller as a **FRU Data File** per DSP0257,
described by a **File Descriptor PDR per DSP0248**, and retrieved over MCTP on the OAC Management
USB 2.0 interface. The upstream management controller reads and evaluates it in Operational State
**O3 (Management Initialized)**, before enabling primary busbar power.

The CID answers exactly one question — may this OAC be powered at all — and the companion
[SCD specification](../../scd/specification/) answers everything after that.

---

## Specification Coverage

| Section | Content |
|---------|---------|
| 1. Scope | What the CID covers and what is out of scope |
| 2. Normative References | DSP0240, DSP0242, DSP0248, DSP0249, DSP0257, ECMA-404, OCP OAC Base Specification |
| 3. Terms and Definitions | CID, FRU Data File, FRU Bundle, OPL, Operational State, upstream management controller, expanded and minified JSON |
| 4. Symbols and Abbreviated Terms | CID, FRU, OPL, PLDM, MCTP, TX, RX |
| 5. CID Overview | Purpose and the categories of information the CID declares |
| 6. CID as a FRU File | 6.1 DSP0257 access and determinism · 6.2 UTF-8 / ECMA-404 encoding, minification · 6.3 File Descriptor PDR, `FileName` `OAC_CID.json`, `FileIdentifier`, read-only `FileCapabilities`, Fixed Length File semantics, and the two mandatory sensors |
| 7. CID JSON Document Structure | 7.1 General · 7.2 `metadata` (with `iana_pen` and `platform_token`) · 7.3 `power` · 7.4 `connectors` · 7.5 Enumerated values summary · 7.6 Field naming and ordering |
| 8. CID Retrieval and Validation | 8.1 Storage and exposure · 8.2 Retrieval sequence · 8.3 Validation requirements · 8.4 Timeout handling |
| 9. Compliance | 9.1 OAC implementation requirements · 9.2 Upstream management controller requirements |
| Annex A (informative) | Example CID JSON snippet |
| Annex C (informative) | PLDM protocol field value reference |

---

## Key Normative Points

| Topic | Requirement |
|-------|-------------|
| Access path | DSP0257 FRU Data File, located via a DSP0248 File Descriptor PDR. **No alternative access path is defined**, and an OAC shall not require one |
| File naming | `FileName` is `OAC_CID.json`. The controller matches on the name to find the record, then opens the file with the `FileIdentifier` from that same record. PDR ordering shall not be relied on |
| Read-only | `FcWritesPermitted` and `ExWriteOpen` shall both be zero. An OAC shall not accept a write to the CID |
| Fixed Length File | `FileMaximumSize` carries the exact transferred size and is updated whenever a firmware update replaces the CID |
| Mandatory sensors | Device File State Sensor (DSP0249 State Set 68) **and** File Size Monitoring Sensor. DSP0242 only recommends the latter; this specification requires it |
| Sensor association | A sensor binds to the CID by carrying the same `EntityType`, `EntityInstanceNumber`, and `ContainerID` as the CID's File Descriptor PDR |
| Encoding | UTF-8 per ECMA-404, no byte order mark, no comments. Production OACs publish **minified**; controllers shall parse minified and should tolerate expanded |
| Determinism | A CID generated on demand shall be deterministic for a given firmware configuration. The controller makes energization decisions from it, and a varying CID would undermine that |
| Availability | Retrievable in O3 or later. **Shall not require primary power** |
| Ordering | The CID is retrieved before slot energization eligibility is evaluated and before the SCD Definition is read |
| Protocol group limit | No more than 8 per connector |
| Group name scoping | Names are unique **within a connector**, not across the document |
| Profile exclusivity | `connector_profile` and explicit `high_speed_lanes` / `clocking` / `discrete_signals` are mutually exclusive on the same connector |
| Unknown profile | A controller receiving an unrecognized `connector_profile` identifier shall log a compatibility warning and **shall not** enable primary power to that slot |
| `platform_token` | Permitted only in co-designed, co-validated closed platforms. Requires `iana_pen` in the same `metadata` object. An unrecognized token shall be treated as absent, falling back to full Section 8.3 validation |
| Retrieval timeout | Implementation-defined but should be no less than 5 seconds. On timeout the controller shall not enable primary power |

---

## Version History

| Version | Status | Description |
|---------|--------|-------------|
| 0.9 | Draft | Tracks OAC Base Specification v0.9. `link_subdivision` removed from the CID and relocated to the SCD. A required `name` added to every protocol group, which is what SCD `cid_binding` resolves against. DSP0220 FRU Files Record and the Format Identifier UUID replaced by the DSP0248 File Descriptor PDR / DSP0242 access / DSP0257 FRU Data File pattern. Compression section removed — the CID is minified JSON and nothing more. `ssc_supported` replaces `ssc_capable` / `ssc_default`. `link_role` and `sris_capable` removed |
| 0.7 | Draft | DMTF-style rewrite. JSON encoding replacing YAML. Operational Power Levels introduced. Connector naming updated to CONN0–CONN6. `connector_profile` introduced. Power connector type updated to 100A/125A. Auxiliary power and `throttle_on_pwrbrk` removed. `discrete_signals` extended with `driver_type`, `default_state`, `pulldown`. `minimum_lanes` made optional. Connector profile naming convention established |
| 0.3 | Draft | Initial draft — YAML encoding, basic power, connector, and lane schema |

See [CHANGELOG.md](../CHANGELOG.md) for the full entry-by-entry history.

---

## Related Resources

- [CID Template](../templates/v0.9/) — annotated JSON template for authoring a new CID
- [CID Examples](../examples/v0.9/) — reference CID documents
- [Connector Profiles](../profiles/) — OCP-ratified standard pinouts
- [Interactive Tools](../tools/interactive/) — CID editor, insertion emulator, compliance logic viewer
- [SCD Specification](../../scd/specification/) — the configuration exchange that follows this one
- [SCD Examples](../../scd/examples/) — matched CID + Definition + Assignment triples

---

## Known Issues

Editorial defects in the shipped v0.9 document, recorded so they are not rediscovered:

- **Section 2** still lists DSP0220, MessagePack, and RFC 1952. None are used by the current
  Section 6, which replaced the DSP0220 FRU Files Record pattern and removed compression. The
  `OCP OAC v0.9` row also cites "Version 0.8" — an incomplete substitution from the 0.8 → 0.9
  renumbering.
- **The Contents block** lists Compliance as Section 10 and skips 9; the body numbers it 9. It also
  numbers the Section 7 subsections one lower than the body does.
- **Section 7.4.3** justifies the eight-protocol-group limit by "the uint32 SCD effecter encoding …
  one 4-bit nibble per protocol group." That rationale came from a superseded PLDM-effecter SCD
  draft and no longer describes how SCD works. The limit itself is still correct; only the
  justification is stale. It hides from any grep on field names.
- **Terminology.** This document says "adapter" throughout. The SCD specification standardized on
  "the OAC" at v0.9, reserving "adapter" for the proper name *Open Adapter Card*. The two
  specifications currently disagree.
