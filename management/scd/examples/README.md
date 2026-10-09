# Examples

**OAC SCD Specification Version:** 0.9  
**OAC CID Specification Reference:** v0.9  
**OAC Base Specification Reference:** v0.9

Each example is a **matched triple**, because SCD is two documents. The CID is what the OAC presents so the platform can decide whether to power it. The **SCD Definition** is what the OAC publishes to say what it will accept. The **SCD Assignment** is what the controller writes back. Read all three side by side — a Definition makes sense only against its CID, and an Assignment only against its Definition.

## Reference Triples

### Triple A — the smallest legal pair

| Role | File |
|------|------|
| CID | [OAC-CID-0.9-ExampleA-PCIeGen6-x16-Profile.json](OAC-CID-0.9-ExampleA-PCIeGen6-x16-Profile.json) |
| Definition | [OAC-SCDD-0.9-ExampleA-Minimal-NoSubdivision.json](OAC-SCDD-0.9-ExampleA-Minimal-NoSubdivision.json) |
| Assignment | [OAC-SCDA-0.9-ExampleA-Slot0-FullBudget.json](OAC-SCDA-0.9-ExampleA-Slot0-FullBudget.json) |

CONN0 is declared entirely by `connector_profile` reference, so its group name lives in the profile and is inherited by this connector. The CID declares only the two mandatory power fields, `opl_max_w` 2500 W and `opl_emg_w` 625 W — there is no `opl_set_min_w`, so there is no settable power band.

The Definition therefore declares two fields and no `protocol_group` binding at all: nothing is subdividable, and with no `opl_set_min_w` there is neither an `ocp.initial_power_max_w` nor an `ocp.initial_power_min_w` to declare. The controller sets slot 0 and the full 2500 W budget — which is also what `ocp.max_power_w` would have defaulted to, since the budget field defaults to the OAC's own `opl_max_w`.

This triple is the one to study for what a Definition looks like when almost nothing is configurable. Note that the profile is never resolved by the SCD path here — with no `protocol_group` binding, the Definition and the profile never meet.

### Triple B — the common case, and the vendor-field demonstration

| Role | File |
|------|------|
| CID | [OAC-CID-0.9-ExampleB-PCIeGen6-x16-Bifurcatable.json](OAC-CID-0.9-ExampleB-PCIeGen6-x16-Bifurcatable.json) |
| Definition | [OAC-SCDD-0.9-ExampleB-Bifurcatable-VendorField.json](OAC-SCDD-0.9-ExampleB-Bifurcatable-VendorField.json) |
| Assignment | [OAC-SCDA-0.9-ExampleB-Slot5-x8x8-Sparse.json](OAC-SCDA-0.9-ExampleB-Slot5-x8x8-Sparse.json) |

CONN0 is defined with explicit per-lane pin mapping: PCIe Gen6, x16 inbound, named `pcie_primary`. The subdivision menu lives in the Definition as `ocp.link_subdivision.conn0.pcie_primary`. The CID declares the full OPL set plus an `opl_set_min_w` of 625 W, which puts the configurable OPL-SET range at 625 W through `opl_max_w`, 2500 W.

The Definition declares six fields — both response classes, both `cid_binding` kinds, the sentinel default, and both namespaces. The Assignment sets four of them and omits two.

**The omissions are the more instructive half.** `pen.32473.boot_source` is marked `required`, yet this controller has never heard of PEN 32473, skips it, and the OAC boots from local flash exactly as intended. An unrecognized field self-handles — which works only because `response` classifies the value rather than obliging the document *and* because every field carries a mandatory default. Remove either property and a generic controller is stuck. The OAC is not silent about it either: an accepted Assignment that omitted a `required` field is reported as State Set 15 state 4, Missing Configuration.

The power fields demonstrate the cross-field relation. The OAC is rated to 2500 W, the platform budgets 2000 W, and the Assignment sets `ocp.initial_power_max_w` to 1800 W — inside the budget, which is the relation the OAC checks. `ocp.initial_power_min_w` is omitted and falls back to the CID's own 625 W floor. Had the controller assigned 2400 W to the maximum, the OAC would have rejected the whole Assignment with code `0x10` rather than quietly reducing it: a controller that has composed a set point above the budget it declared in the same document has made an error worth reporting.

### Triple C — cross-connector name reuse

| Role | File |
|------|------|
| CID | [OAC-CID-0.9-ExampleC-MultiConnector-NameReuse.json](OAC-CID-0.9-ExampleC-MultiConnector-NameReuse.json) |
| Definition | [OAC-SCDD-0.9-ExampleC-MultiConnector-NameReuse.json](OAC-SCDD-0.9-ExampleC-MultiConnector-NameReuse.json) |
| Assignment | [OAC-SCDA-0.9-ExampleC-Slot1-PartialSubdivision.json](OAC-SCDA-0.9-ExampleC-Slot1-PartialSubdivision.json) |

**This is the conformance triple.** CONN0 carries two groups, `pcie_primary` (x8 inbound, subdividable) and `eth_sideband` (Ethernet 200G, not subdividable). CONN1 is declared by profile. CONN2 carries a group **also named `pcie_primary`** (x16 outbound, subdividable).

That duplicate name is deliberate and is conformant. Group names are unique within a connector, not across the document. A validator that enforces document-wide uniqueness will reject this CID, and that is the specific failure this triple exists to catch — under per-connector scoping the expected implementation error is over-enforcement, not under-enforcement.

The two subdivision fields differ only in their connector segment:

```
ocp.link_subdivision.conn0.pcie_primary
ocp.link_subdivision.conn2.pcie_primary
```

which is the entire reason that segment exists. Drop it and the two fields collide, and field identifiers are the Assignment's keys, so they must be unique.

The triple also exercises `applies_when`: `pen.32473.stream_image_slot` is relevant only when `pen.32473.boot_source` equals `stream`. The Assignment omits both, so the predicate is unsatisfied and a supplied value would have been ignored without error.

Note the Assignment omits `ocp.link_subdivision.conn2.pcie_primary` even though it is marked `required`. The declared `x16` default is what this platform wants, so there is nothing to say. This is normal, not a defect — see Specification Section 7.7.

Note also that `definition_revision` is `3` here rather than `1`. Where an OAC chooses to declare it, it is an opaque counter tracking the OAC's Definition content; it has no relationship to the schema version. It is informational in both documents — the OAC does not validate what an Assignment echoes back, and a controller learns that a cached Definition is stale from `OAC_MC_RDY` deassertion instead.

## Coverage Summary

| Behavior | A | B | C |
|----------|:-:|:-:|:-:|
| `connector_profile` resolution present in the CID | ● | | ● |
| Definition with no `protocol_group` binding | ● | | |
| OAC with no OPL-SET floor | ● | | |
| Sentinel default (`ocp.slot_id`) | ● | ● | ● |
| `power.primary` binding | ● | ● | ● |
| Single subdividable group | | ● | |
| Vendor (`pen.`) namespace field | | ● | ● |
| Sparse Assignment omitting a `required` field | | ● | ● |
| Unrecognized vendor field self-handling | | ● | |
| **Cross-connector group name reuse** | | | ● |
| Two subdividable groups on different connectors | | | ● |
| Subdividable and fixed groups in one connector | | | ● |
| `applies_when` predicate | | | ● |
| `definition_revision` other than 1 | | | ● |
| Assigned power set point under the assigned budget | | ● | |

## Usage

Validate any triple with the [validation tool](../tools/):

```
python3 ../tools/validate-scd.py \
    --cid  OAC-CID-0.9-ExampleC-MultiConnector-NameReuse.json \
    --scdd OAC-SCDD-0.9-ExampleC-MultiConnector-NameReuse.json \
    --scda OAC-SCDA-0.9-ExampleC-Slot1-PartialSubdivision.json
```

A Definition can be validated on its own, without a CID, for everything except binding resolution:

```
python3 ../tools/validate-scd.py --scdd OAC-SCDD-0.9-ExampleB-Bifurcatable-VendorField.json
```

Triples A and C contain CIDs that reference connector profiles, and `--profiles ../../../cid/profiles` resolves them. Neither triple needs it: no `protocol_group` binding in either Definition targets a profile-declared connector, so the SCD path and the profile never meet. The validator reports an unresolvable profile only when a field actually binds into that connector, which is why these two validate clean without it.

To author new documents, start from the [templates](../templates/).

## Notes

**The example CIDs are v0.9 CIDs.** Each protocol group carries a `name`, and no `link_subdivision` array is present — the two CID features the binding rules depend on. See CHANGELOG.md.

**IANA PEN 32473** is the number reserved for documentation and example use. A real OAC substitutes its own Private Enterprise Number. No OCP registration is required for a `pen.` field.

**On size.** Minified as they would be transferred, the CIDs here run from 755 bytes to 6.9 KB, the Definitions from 1.1 KB to 3.3 KB, and the Assignments from 384 to 822 bytes. Definitions are dominated by prose `description` text, which is what makes them several times the size of the Assignments composed against them. All of these sit well inside the 64 KB transferred limit that Section 13 sets for both documents.
