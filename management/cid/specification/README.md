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
| 2. Normative References | DSP0220, DSP0236, DSP0240, DSP0242, DSP0248, DSP0249, DSP0257, ECMA-404, OCP OAC Base Specification |
| 3. Terms and Definitions | CID, FRU Data File, FRU Bundle, OPL, Operational State, upstream management controller, expanded and minified JSON |
| 4. Symbols and Abbreviated Terms | CID, FRU, OPL, PLDM, MCTP, TX, RX |
| 5. CID Overview | Purpose, the categories of information the CID declares, and how the CID and mechanical keying divide the compatibility problem between them |
| 6. CID as a FRU File | 6.1 DSP0257 access and determinism · 6.2 UTF-8 / ECMA-404 encoding, minification, and profile file encoding · 6.3 File Descriptor PDR, `FileName` `OAC_CID.json`, `FileIdentifier`, read-only `FileCapabilities`, Fixed Length File semantics, and the two mandatory sensors — **annotated WORK IN PROGRESS** |
| 7. CID JSON Document Structure | 7.1 General · 7.2 `metadata` (with `iana_pen` and `platform_token`) · 7.3 `power` · 7.4 `connectors` · 7.5 Enumerated values summary · 7.6 Field naming and ordering |
| 8. Connector Profile JSON Document Structure | 8.1 General · 8.2 Referencing a profile from a CID · 8.3 Profile identifiers and the protocol abbreviation table · 8.4 Profile document structure · 8.5 Applicability to connector positions via `applicable_conns`, with the open cases annotated |
| 9. CID Retrieval and Validation | 9.1 Storage and exposure · 9.2 Retrieval sequence · 9.3 Validation requirements · 9.4 Timeout handling |
| 10. Compliance | 10.1 OAC implementation requirements · 10.2 Upstream management controller requirements |
| Annex A (informative) | Two complete example CID documents — A.1 profile-referencing, A.2 explicitly defined |
| Annex B (informative) | PLDM protocol field value reference |

---

## Key Normative Points

| Topic | Requirement |
|-------|-------------|
| Access path | DSP0257 FRU Data File, located via a DSP0248 File Descriptor PDR. **No alternative access path is defined**, and an OAC shall not require one |
| File naming | `FileName` is `OAC_CID.json`. The controller matches on the name to find the record, then opens the file with the `FileIdentifier` from that same record. PDR ordering shall not be relied on |
| Read-only | `FcWritesPermitted` and `ExWriteOpen` shall both be zero. An OAC shall not accept a write to the CID |
| Fixed Length File | `FileMaximumSize` carries the exact transferred size and is updated whenever a firmware update replaces the CID. Fixed length binds the file within a firmware revision, not across revisions — the CID's size **may** change when firmware is updated |
| Mandatory sensors | Device File State Sensor (DSP0249 State Set 68) **and** File Size Monitoring Sensor. DSP0242 only recommends the latter; this specification requires it |
| Sensor association | A sensor binds to the CID by carrying the same `EntityType`, `EntityInstanceNumber`, and `ContainerID` as the CID's File Descriptor PDR |
| Encoding | UTF-8 per ECMA-404, no byte order mark, no comments. Expanded and minified are both valid; a controller shall accept either and shall not reject a CID over its whitespace encoding. Minified is **recommended** for production as a size optimization |
| Determinism | A CID generated on demand shall be deterministic for a given firmware configuration. The controller makes energization decisions from it, and a varying CID would undermine that |
| Availability | Retrievable in O3 or later. **Shall not require primary power** |
| Ordering | The CID is retrieved before slot energization eligibility is evaluated and before the SCD Definition is read |
| Protocol group limit | No more than 8 per connector |
| Group name scoping | Names are unique **within a connector**, not across the document |
| Presence detect | Always implemented, never negotiable, and never declared. The `mpesti_capable` field exists solely to declare the M-PESTI overload on CONN0 Pin A1. It is required in the CONN0 connector object and prohibited in all others; `false` means standard GND-tied presence detect and no M-PESTI |
| `high_speed_lanes` presence | Prohibited when a `connector_profile` is declared; required when no profile is declared and the connector carries high-speed signals. Optional only in the sense that a conformant connector object may omit it |
| Profile exclusivity | `connector_profile` and explicit `high_speed_lanes` / `clocking` / `discrete_signals` are mutually exclusive on the same connector. The reference is whole or not at all — no amendment, extension, or partial override is defined |
| Profile applicability | A profile's `applicable_conns` value shall name the connector position it is applied to, and shall agree with the connector segment of its `profile_id`. `OAC-PROF-CONN0-…` is `["CONN0"]`; `OAC-PROF-CONN6-…` is `["CONN6"]`; `OAC-PROF-CONN-…` names more than one of CONN1 through CONN6, including `["CONN1-6"]`; `OAC-PROF-CABLE-…` is `["CABLE"]`. All tokens in one array shall be drawn from a single geometry class |
| Unknown profile | A controller receiving a `connector_profile` identifier it does not recognize, or recognizes but cannot support, shall log a compatibility warning and **shall not** enable primary power to that slot |
| Profile knowledge | A conformant controller carries built-in knowledge of the ratified profiles **its baseboard can support** — not of every ratified profile — and handles all others robustly rather than treating them as parse failures |
| `platform_token` | Intended for tightly coupled, pre-validated baseboard and OAC pairings. Requires `iana_pen` in the same `metadata` object. An unrecognized token shall be treated as absent, falling back to full Section 9.3 validation. A validated pairing is defined by the act of validation, not by who owns the two parts |
| Retrieval timeout | Implementation-defined but should be no less than 5 seconds. On timeout the controller shall not enable primary power |

---

## Version History

| Version | Status | Description |
|---------|--------|-------------|
| 0.9 | Draft | **Revised 2026-10-08** in response to the OAC workstream review of the published v0.9 document. Connector profiles moved out of Section 7.4.1 into their own Section 8, which pushed Retrieval and Validation to 9 and Compliance to 10. `presence_detect`, `high_speed_lanes` presence, and the mechanical-keying relationship rewritten. Section 6.3 and Section 8.5 annotated as work in progress. Annex A replaced with two complete, labelled examples. Terminology standardized on "the OAC". Tracks OAC Base Specification v0.9. `link_subdivision` removed from the CID and relocated to the SCD. A required `name` added to every protocol group, which is what SCD `cid_binding` resolves against. DSP0220 FRU Files Record and the Format Identifier UUID replaced by the DSP0248 File Descriptor PDR / DSP0242 access / DSP0257 FRU Data File pattern. Compression section removed — the CID is plain UTF-8 JSON and nothing more. `ssc_supported` replaces `ssc_capable` / `ssc_default`. `link_role` and `sris_capable` removed. **Revised again 2026-10-09**: `opl_set_max_w` removed — the configurable OPL-SET range is bounded above by `opl_max_w`; connector profile `is_conn0` replaced by the position-token array `applicable_conns`, extending the identifier grammar to `CABLE` and to per-position segments such as `OAC-PROF-CONN6-…`; the single-field `presence_detect` object flattened into a `mpesti_capable` field required on CONN0 and prohibited elsewhere. Section numbering unchanged by this revision |
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

## Open Items

Two mechanisms are marked **WORK IN PROGRESS** in the document itself and are expected to change
before v0.9 is published as final:

- **Section 6.3 in its entirety** — the hard-coded `FileName`, the match-on-name-then-open-by-
  identifier discovery sequence, and the PDR field constraints that follow from them. An alternative
  has been raised in which an OAC publishes a metadata file enumerating the files it exposes.
  Annex B is scoped by the same annotation.
- **Section 8.5** — whether a `["CONN1-6"]` profile may be applied to CONN0 (leaving CONN0's
  ninth assignable column undefined), and whether a CID may supplement or partially override a
  referenced profile at all. Section 8.2 forbids both today, which is what makes the first a
  rejection rather than a question of syntax. `applicable_conns` can express the resolution
  directly as `["CONN0", "CONN1-6"]`; the prohibition in Table 8.4-1 on mixing geometry
  classes within one array is what holds the case closed until the workstream settles it.

Remaining editorial defect, recorded so it is not rediscovered:

- **Section 7.4.3** justifies the eight-protocol-group limit by "the uint32 SCD effecter encoding …
  one 4-bit nibble per protocol group." That rationale came from a superseded PLDM-effecter SCD
  draft and no longer describes how SCD works. The limit itself is still correct; only the
  justification is stale. It hides from any grep on field names.

The Section 2 reference list, the Contents block, and the "adapter" / "the OAC" terminology
divergence were all corrected in the 2026-10-08 revision — see [CHANGELOG.md](../CHANGELOG.md).
