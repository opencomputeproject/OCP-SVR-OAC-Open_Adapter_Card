# Management

**OAC Base Specification Revision:** 0.9 (Draft)
**Related Base Specification sections:** 10.2.3 Connector Interface Definitions (CID) · 10.2.4 Slot Configuration Data (SCD) · 10.2.5 Management Data Model

The two companion specifications that define what an OAC and its upstream management controller say
to each other before the slot is energized. Each is a normative specification in its own right, with
its own schema, templates, examples, and tooling.

---

## Contents

| Directory | Specification | Artifacts |
|-----------|---------------|-----------|
| [cid/](cid/) | OAC Connector Interface Definition (CID), v0.9 | `OAC_CID.json` |
| [scd/](scd/) | OAC Slot Configuration Data (SCD), v0.9 | `OAC_SCDD.json`, `OAC_SCDA.json` |

---

## Why There Are Two

An OAC slot carries up to 5 kW and is not hot-pluggable. A baseboard therefore cannot discover a
card by energizing it and observing the result — it has to find out what the card is, and decide
whether it can host it, while the card is still running on +12V_AUX alone.

That produces two separate conversations, and they are separate because they have different failure
modes.

**The CID answers one question: may this OAC be powered at all?** It is a declaration, read-only,
flowing one way. The OAC states its connector population, pin maps, protocol groups, clocking
requirements, and power envelopes. The controller compares that against what the slot can supply. If
the answer is no, nothing further happens and the busbar is never energized.

**The SCD answers everything after that.** It is an exchange. The OAC publishes a **Definition**
listing every field it will accept — with type, bounds, and a mandatory default — and the controller
writes back a sparse **Assignment** setting only the fields it recognizes and has an opinion about.
This replaces hardware strapping: typed, named, self-describing fields instead of a fixed handful of
pulled-up pins.

The division is a single question:

> **Does the platform need this to decide whether to power the OAC at all?**
> **Yes → CID. No → SCD.**

Power envelopes stay in the CID, because the platform weighs them before `OAC_PWR_EN`. The link
subdivision *menu* lives in the SCD Definition, because the platform does not need it to make the
power decision.

A consequence worth stating plainly: **the SCD can only narrow what the CID declared.** The platform
states the budget it is willing to supply, bounded by the OPL range the CID already published. A
configuration document never raises a hardware limit.

---

## The Three Documents

| | CID | SCD Definition (SCDD) | SCD Assignment (SCDA) |
|---|---|---|---|
| Root key | `oac_cid` | `oac_scdd` | `oac_scda` |
| `FileName` | `OAC_CID.json` | `OAC_SCDD.json` | `OAC_SCDA.json` |
| Direction | OAC → controller | OAC → controller | controller → OAC |
| Transport | PLDM for FRU Data (DSP0257) | PLDM for FRU Data (DSP0257) | PLDM for File Transfer (DSP0242) |
| File kind | Fixed Length File | Fixed Length File | Regular File |
| Writable by controller | No | No | Yes — this is the only one |
| Size limit | — | 32 KiB transferred | 8 KiB transferred |
| Density | Complete | Complete | **Sparse** |
| Retention | Persistent | Persistent | Volatile, bounded by +12V Aux |

All three are minified UTF-8 JSON per ECMA-404, carried over MCTP on the OAC Management USB 2.0
interface on CONN0.

---

## Sequence

Everything here happens in Operational State **O3 (Management Initialized)** — after +12V_AUX is
good and the MCTP session is up, but **before `OAC_PWR_EN` is asserted**.

```
  1.  Controller reads OAC_CID.json          (PLDM for FRU Data)
  2.  Controller evaluates compatibility and power feasibility
          └─ incompatible?  stop here. The busbar is never energized.
  3.  Controller reads OAC_SCDD.json         (PLDM for FRU Data)
  4.  Controller composes a sparse Assignment, echoing definition_revision
  5.  Controller writes OAC_SCDA.json        (PLDM for File Transfer)
          DfOpen (write, exclusive) → DfWrite → DfClose
  6.  OAC validates: accepted whole, or rejected whole. Never partially.
          └─ replaceable while still in O3
  7.  OAC_PWR_EN asserted                     O3 → O4, configuration latches
```

Two consequences of that ordering are load-bearing. The CID is read **before** the Definition — a
controller that cannot supply `opl_emg_w` stops at step 2 and never reads the Definition at all. And
the accepted configuration **shall not be stored in non-volatile memory**; a persisted Assignment
would carry the previous chassis's slot identifier and power level into a new platform while
reporting itself as latched.

---

## PLDM Data Model

Both OAC-published files are described by **File Descriptor PDRs per DSP0248 §28.30**. This is worth
stating explicitly because it is a common misreading: DSP0257 governs FRU *content*, while the PDR
that describes the file lives in DSP0248.

| | CID | Definition | Assignment |
|---|---|---|---|
| `EntityType` | Device File | Device File | Device File |
| `FileClassification` | `FRUDataFile` | `FRUDataFile` | `OtherFile` |
| `OemFileClassificationName` | — | `oac_scdd` | `oac_scda` |
| `FcWritesPermitted` | 0 | 0 | 1 |

All File Descriptor PDRs and sensor PDRs for one OAC share a single `ContainerID`;
`EntityInstanceNumber` is what distinguishes the files. A sensor is associated with a file by
carrying that file's `EntityType`, `EntityInstanceNumber`, and `ContainerID`.

Required sensors:

| Sensor | State Set | Applies to |
|--------|-----------|-----------|
| Device File State Sensor | DSP0249 State Set 68 (Device File) | CID, Definition, Assignment |
| File Size Monitoring Sensor | Numeric or Compact, BaseUnit Bytes | CID, Definition |
| Configuration State Sensor | DSP0249 State Set 15 (Configuration) | Assignment |

The Configuration State Sensor is how an Assignment's outcome is reported — 1 Valid, 2 Invalid,
3 Not Configured, 4 Missing Configuration. It is the reason there is no digest or acknowledgement
document in the SCD exchange.

---

## Interoperability Rules

These are the properties that let a generic controller and an unfamiliar OAC still reach a working
configuration. Each exists because removing it breaks that case.

- **Every SCD field descriptor carries a mandatory default.** This is what makes a sparse Assignment
  safe. Without it, an omitted field would have undefined behavior.
- **The Assignment is sparse, and omission is a decision.** Omitting a field means "use the
  default," which is a complete and valid outcome, not an oversight.
- **`required` is advisory, not a hard gate.** A controller that does not recognize a `required`
  field omits it and the OAC proceeds on the default. The consequence surfaces through the
  Configuration State Sensor, not by rejecting the document. Without this, one unknown vendor field
  would brick an otherwise working pair.
- **Vendor fields are namespaced, not registered.** `ocp.` is the OCP registry; a vendor uses
  `pen.<IANA PEN>.<field_name>` and needs no OCP registration to do so.
- **Protocol group names are unique within a connector, not across the document.** The binding key
  is the pair `(cid_connector, cid_group_name)`. Two connectors may each declare a group named
  `pcie_primary`, and a conformant validator must accept that. The expected implementation error
  here is over-enforcement.
- **Conflicting power values clamp, they do not reject.**
  `applied_cap = min(initial_power_level_set_w, max_power_w, opl_max_w)`.
- **Controllers carry built-in knowledge of ratified connector profiles.** A CID may reference a
  profile by identifier instead of repeating a pin map; there is no runtime fetch.

---

## Where to Start

| If you are… | Start at |
|---|---|
| An OAC vendor | [cid/README.md](cid/README.md), then [scd/templates/README.md](scd/templates/README.md) |
| A BMC or baseboard implementer | [cid/specification/](cid/specification/) and [scd/specification/](scd/specification/) |
| Looking for worked examples | [scd/examples/](scd/examples/) — matched CID + Definition + Assignment triples |
| Authoring a CID interactively | [cid/tools/interactive/](cid/tools/interactive/) |
| Validating what you wrote | [scd/tools/](scd/tools/) — `validate-scd.py` |

The SCD examples are the fastest way in. They are the only place all three documents appear side by
side, and a Definition only makes sense against its CID.

---

## A Note on Structure

The two subdirectories are organized differently, deliberately:

- **CID keeps versioned subfolders** — `templates/v0.9/`, `examples/v0.9/`.
- **SCD is single-revision and flat.** Superseded revisions are retrievable from git history, and
  `scd/CHANGELOG.md` names the commit.

Do not harmonize these without raising it with the workstream. Each reflects a decision about how
that specification expects to be consumed.
