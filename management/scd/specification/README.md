# OAC Slot Configuration Data (SCD) Specification

**Version:** 0.9 (Draft)  
**Workstream:** Open Compute Project (OCP) — Open Adapter Card (OAC)  
**Normative References:** OCP Open Adapter Card Base Specification v0.9; OAC Connector Interface Definition v0.9

---

## Document

[OAC-SCD-Specification-v0.9.md](OAC-SCD-Specification-v0.9.md)

---

## Description

This specification defines the Slot Configuration Data exchanged between an OAC and its upstream management controller: what slot the OAC occupies, how each subdividable protocol group should be partitioned, and what power envelope the OAC should operate within.

The SCD is the counterpart to the CID. The CID answers a single question — may this OAC be powered at all — and the SCD answers everything after that.

SCD is two documents. The **SCD Definition** is published by the OAC as a FRU file and declares every field the OAC will accept, complete with type, bounds, response class, and a mandatory default. The **SCD Assignment** is written back by the controller as a sparse PLDM file keyed by field identifier. The OAC describes its own configurable surface rather than leaving the controller to infer it from the CID, which is what makes a generic controller and an unfamiliar OAC able to interoperate: an unrecognized field is omitted, and its default still fully determines behavior.

The Assignment is transferred using PLDM for File Transfer (DSP0242) over MCTP on the OAC Management USB 2.0 interface. It is not FRU data and is never placed in a FRU Files Record. The controller writes and the OAC validates while the OAC is in Operational State O3 (Management Initialized), before `OAC_PWR_EN` is asserted; the accepted configuration latches on the O3 → O4 transition and shall not be stored in non-volatile memory.

## Specification Coverage

| Section | Content |
|---------|---------|
| 1. Scope | What the SCD covers and what is deliberately excluded |
| 2. Normative References | DSP0236, DSP0240, DSP0241, DSP0242, DSP0248, DSP0249, DSP0257, ECMA-404, OAC-CID-SPEC v0.9, OCP OAC v0.9 |
| 3. Terms and Definitions | Definition, Assignment, field descriptor, response class, sentinel default, protocol group, link subdivision mode, OPL, latch |
| 4. Symbols and Abbreviated Terms | SCD, SCDD, SCDA, CID, OPL, PLDM, MCTP, PEN |
| 5. SCD Overview | The two artifacts, why the Definition is a separate document, and the placement rule that divides CID from SCD |
| 6. SCD Definition as a FRU File | DSP0257 FRU Data File access, `FileName` `OAC_SCDD.json`, persistent storage, the File Descriptor PDR and its two mandatory sensors |
| 7. SCD Definition Document Structure | `metadata` and `fields`; the field descriptor in full — type, response class, defaults, sentinel semantics, `cid_binding`, `applies_when` |
| 8. SCD Assignment as a PLDM File | DSP0242 alignment, `FileName` `OAC_SCDA.json`, volatile-only retention bounded by +12V Aux, `DfOpen` / `DfWrite` / `DfClose` sequence, one write session delimiting one complete Assignment |
| 9. SCD Assignment Document Structure | `metadata` and `assignments`; sparseness, definition revision echo, prohibition on nulls and sentinels |
| 10. OCP-Defined Field Registry | The `ocp.` namespace, the `pen.` vendor namespace, registry field definitions, subdivision identifier construction, reserved identifiers |
| 11. Delivery, Validation, and Acceptance | Transfer sequence, OAC validation checks, the rejection code table, atomic application, latch and replacement, re-apply versus re-negotiate, cache survival |
| 12. Runtime Power Control | Post-latch power changes via PLDM effecters per DSP0248 |
| 13. Size Limits | 32 KiB Definition and 8 KiB Assignment, measured on the minified form as transferred |
| 14. Compliance | OAC and controller compliance requirement tables |
| Annex A | Informative paired CID + Definition + Assignment walkthrough |
| Annex B | Informative algorithm — how a controller composes an Assignment from a Definition |
| Annex C | PLDM protocol field value reference |
| Annex D | Items open for workstream resolution |

## Key Normative Points

| Topic | Requirement |
|-------|-------------|
| Mandatory defaults | Every field descriptor shall carry a `default`. This is what makes a sparse Assignment safe, and there is no exemption |
| Sparse assignment | The Assignment carries only the fields the controller wishes to change. Omission means the default applies and is a valid, complete outcome |
| Response classes | `required` is **advisory**. A controller that does not recognize a `required` field shall omit it, and the OAC shall proceed on the default. `optional` is the only other class |
| Field namespacing | `ocp.` is reserved for the registry in Section 10. A vendor uses `pen.<IANA PEN>.<field_name>` and needs no OCP registration |
| Group name scoping | Protocol group names are unique **within a connector**, not across the document. The binding key is the pair `(cid_connector, cid_group_name)`. Cross-connector reuse is conformant, and Section 14.2 makes accepting it a mandatory controller requirement |
| Subdivision identifiers | `ocp.link_subdivision.<connector lowercased>.<group name>`. Both segments are required; drop the connector segment and two reused group names collide, and field identifiers are the Assignment's keys |
| Sentinel defaults | A default deliberately outside `[min, max]` shall be flagged `sentinel_default`. A controller shall not assign the sentinel value; it is a state the OAC may hold, not a value the controller may choose |
| Power clamping | Conflicting power values clamp rather than reject: `applied_cap = min(ocp.initial_power_level_set_w, ocp.max_power_w, opl_max_w)` |
| Definition revision | The Assignment shall echo the Definition's `definition_revision`. A mismatch means the controller composed against a stale Definition and shall re-read and recompose |
| Duplicate keys | Rejected rather than resolved. ECMA-404 leaves duplicate-key resolution undefined, so first-wins and last-wins are both wrong answers |
| Nulls | Rejected. Absence and `null` are not equivalent |
| Application | Validation and application are atomic — accepted whole or rejected whole, never partially |
| Timing | Written and accepted in O3, before `OAC_PWR_EN`. Replaceable while still in O3; latched on O3 → O4 |
| Cache persistence | The accepted configuration **shall not** be stored in non-volatile memory |
| Size | 32 KiB for the Definition and 8 KiB for the Assignment, measured as transferred |
| Runtime changes | Post-latch power changes use PLDM effecters per DSP0248, not an Assignment rewrite |

## Related Resources

- [CHANGELOG.md](../CHANGELOG.md) — revision history and porting notes
- [Templates](../templates/) — annotated Definition and Assignment templates
- [Examples](../examples/) — matched CID + Definition + Assignment triples
- [Validation Tool](../tools/) — `validate-scd.py`
- [OAC CID Specification](../../cid/specification/) — the capability declaration this specification works alongside
- [Connector Profiles](../../cid/profiles/) — OCP-ratified pinouts that a `cid_binding` may have to resolve through
