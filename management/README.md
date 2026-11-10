# Management

**OAC Base Specification Revision:** 0.9 (Draft)
**Related Base Specification sections:** 10.2.3 Connector Interface Definitions (CID) · 10.2.4 Slot Configuration Data (SCD) · 10.2.5 Management Data Model

The companion specifications that define what an OAC and its upstream management controller say to
each other before the slot is energized. Each is a normative specification in its own right, with its
own schema, templates, examples, and tooling.

---

## Contents

| Directory | Specification | Artifacts |
|-----------|---------------|-----------|
| [metadata/](metadata/) | OAC Metadata Specification, v0.9 | `OAC_METADATA.json` |
| [cid/](cid/) | OAC Connector Interface Definition (CID), v0.9 | `OAC_CID.json` |
| [scd/](scd/) | OAC Slot Configuration Data (SCD), v0.9 | `OAC_SCDD.json`, `OAC_SCDA.json` |

They are listed in the order a controller reads them. The metadata file is read first and is a
different kind of document from the other three: it declares nothing about the card, it only says
which files the card publishes and under which `FileIdentifier` each one is opened. Everything the
controller decides, it decides from the CID and the SCD.

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

## The Four Documents

| | Metadata | CID | SCD Definition (SCDD) | SCD Assignment (SCDA) |
|---|---|---|---|---|
| Root key | `oac_metadata` | `oac_cid` | `oac_scdd` | `oac_scda` |
| `FileName` | `OAC_METADATA.json` | `OAC_CID.json` | `OAC_SCDD.json` | `OAC_SCDA.json` |
| Direction | OAC → controller | OAC → controller | OAC → controller | controller → OAC |
| Transport | PLDM for FRU Data (DSP0257) | PLDM for FRU Data (DSP0257) | PLDM for FRU Data (DSP0257) | PLDM for File Transfer (DSP0242) |
| File kind | Fixed Length File | Fixed Length File | Fixed Length File | Regular File |
| Writable by controller | No | No | No | Yes — this is the only one |
| Size limit | — | — | 64 KB transferred | 64 KB transferred |
| Density | Complete | Complete | Complete | **Sparse** |
| Retention | Persistent | Persistent | Persistent | Volatile, bounded by +12V Aux |
| Required | Always | Always | Only if the OAC has an SCD | Only if the OAC has an SCD |

All four are minified UTF-8 JSON per ECMA-404, carried over MCTP on the OAC Management USB 2.0
interface on CONN0.

### How a file is found

The `FileName` row above is not the discovery mechanism, and this is the one thing in the table most
likely to be misread. A controller does not locate the CID by matching the string `OAC_CID.json`
against the OAC's File Descriptor PDRs. It retrieves the metadata file, resolves the `cid` role to a
`FileIdentifier`, and opens that identifier.

**`FileName` names a file; `FileIdentifier` opens it.** The names above remain fixed and remain
assigned to no other file, because a fixed name keeps each document identifiable in a PDR repository
dump, in a firmware image, and to diagnostic tooling — and because the metadata file advertises the
name alongside the identifier, so the two can be checked against each other. The name is descriptive
now, not functional.

The hard-coded string does not disappear; it reduces from three to one. A controller still has to
know `OAC_METADATA.json` by name in order to find the metadata file, and nothing can remove that —
discovery has to start somewhere. What changes is that the CID, the Definition, and the Assignment
are now found through a document the OAC controls, which is what makes adding a fourth or fifth file
a metadata-only change.

Falling back to name matching when metadata retrieval fails is prohibited in all three
specifications, not merely discouraged. It is the obvious compatibility shim and it is exactly wrong:
it would energize a slot on data obtained by a path the OAC never advertised.

---

## Sequence

Everything here happens in Operational State **O3 (Management Initialized)** — after +12V_AUX is
good and the MCTP session is up, but **before `OAC_PWR_EN` is asserted**.

```
  0.  Controller reads OAC_METADATA.json     (PLDM for FRU Data)
          └─ resolves the cid, scdd, and scda roles to FileIdentifiers
          └─ retrieval or validation failure?  stop here. No fallback.
  1.  Controller reads the CID               (PLDM for FRU Data)
          opened by the FileIdentifier the cid role advertises
  2.  Controller evaluates compatibility and power feasibility
          └─ incompatible?  stop here. The busbar is never energized.
  3.  Controller reads the Definition        (PLDM for FRU Data)
          └─ no scdd role in the metadata?  skip to step 6
  4.  Controller composes a sparse Assignment from the Definition
  5.  Controller writes the Assignment       (PLDM for File Transfer)
          DfOpen (write, exclusive) → DfWrite → DfClose
          └─ OAC validates: accepted whole, or rejected whole. Never partially.
          └─ replaceable while still in O3
  6.  OAC_PWR_EN asserted                     O3 → O4, configuration latches
```

Three consequences of that ordering are load-bearing.

The metadata file is read **before** anything else, and it is the only file found by name. A
controller that cannot retrieve or validate it stops at step 0 and does not proceed by guessing.

The CID is read **before** the Definition — a controller that cannot supply `opl_emg_w` stops at
step 2 and never reads the Definition at all.

The accepted configuration **shall not be stored in non-volatile memory**; a persisted Assignment
would carry the previous chassis's slot identifier and power level into a new platform while
reporting itself as latched.

The metadata file also removes an inference the controller previously had to make. `scdd` and `scda`
are declared together or not at all, so an OAC that has no SCD is now distinguishable from an OAC
that failed to publish its SCD records. Before, both looked the same from the controller's side.

---

## PLDM Data Model

Every OAC-published file is described by a **File Descriptor PDR per DSP0248 §28.30**. This is worth
stating explicitly because it is a common misreading: DSP0257 governs FRU *content*, while the PDR
that describes the file lives in DSP0248.

| | Metadata | CID | Definition | Assignment |
|---|---|---|---|---|
| `EntityType` | Device File | Device File | Device File | Device File |
| `FileClassification` | `FRUDataFile` | `FRUDataFile` | `FRUDataFile` | `OtherFile` |
| `FileName` | `OAC_METADATA.json` | `OAC_CID.json` | `OAC_SCDD.json` | `OAC_SCDA.json` |
| `FcWritesPermitted` | 0 | 0 | 0 | 1 |
| `SuperiorDirectoryFileIdentifier` | `0xFFFF` | `0xFFFF` | `0xFFFF` | `0xFFFF` |

The `FileName` row replaces an `OemFileClassificationName` row that appeared here in earlier
revisions, carrying `oac_scdd` and `oac_scda`. That mechanism was superseded by `FileName` in the
2026-10-06 revision of the SCD specification, and this table had not been updated; see
[`scd/CHANGELOG.md`](scd/CHANGELOG.md). The values above are the current ones.

All File Descriptor PDRs and sensor PDRs for one OAC share a single `ContainerID`;
`EntityInstanceNumber` is what distinguishes the files. A sensor is associated with a file by
carrying that file's `EntityType`, `EntityInstanceNumber`, and `ContainerID`.

Required sensors:

| Sensor | State Set | Applies to |
|--------|-----------|-----------|
| Device File State Sensor | DSP0249 State Set 68 (Device File) | Metadata, CID, Definition, Assignment |
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
- **`response` classifies the value, not the document.** A `required` field is one the OAC needs a
  value for in order to operate as intended; it is not a statement that the field shall appear in an
  Assignment. A controller that does not recognize a `required` field omits it and the OAC proceeds
  on the default. The consequence surfaces through the Configuration State Sensor, not by rejecting
  the document. Without this, one unknown vendor field would brick an otherwise working pair.
- **Vendor fields are namespaced, not registered.** `ocp.` is the OCP registry; a vendor uses
  `pen.<IANA PEN>.<field_name>` and needs no OCP registration to do so.
- **Protocol group names are unique within a connector, not across the document.** The binding key
  is the pair `(cid_connector, cid_group_name)`. Two connectors may each declare a group named
  `pcie_primary`, and a conformant validator must accept that. The expected implementation error
  here is over-enforcement.
- **Contradictory power values are rejected, not reconciled.** `ocp.initial_power_max_w` shall
  not exceed `ocp.max_power_w`, and `ocp.initial_power_min_w` shall not exceed
  `ocp.initial_power_max_w`. Either violation is rejection code `0x10`. A controller that has
  composed a set point above the budget it declared in the same document has made an error, and
  absorbing it silently would leave that controller believing something false.
- **Controllers carry built-in knowledge of ratified connector profiles.** A CID may reference a
  profile by identifier instead of repeating a pin map; there is no runtime fetch.
- **Unrecognized keys are ignored at every level of nesting, not just the top.** A controller that
  meets an unfamiliar member inside `"power"` or inside a connector object proceeds as though it were
  absent, and does not treat the containing object as malformed. Without this, the first additive
  extension — `power.excursion` is the one that arrived — would break every controller that predated
  it.
- **Unrecognized metadata roles are ignored, and a matching major version is enough.** The metadata
  file accepts any `schema_version` whose major component the controller implements, and skips roles
  it does not know. This is looser than the SCD's exact-version match, deliberately: the metadata
  file is the one document a controller must be able to read before it knows anything else about the
  card, so it is the one place where refusing to proceed on a minor version difference would cost
  more than it protects.
- **Metadata vendor roles use `pen.<IANA PEN>.<name>`,** the SCD's namespacing convention rather than
  the CID's `vendor_<name>_` prefix. A role names a file in a shared namespace, which is the problem
  `pen.` was introduced to solve.

---

## Where to Start

| If you are… | Start at |
|---|---|
| An OAC vendor | [cid/README.md](cid/README.md), then [scd/templates/README.md](scd/templates/README.md), then [metadata/templates/](metadata/templates/) |
| A BMC or baseboard implementer | [metadata/specification/](metadata/specification/) first — it is what you read first at runtime — then [cid/specification/](cid/specification/) and [scd/specification/](scd/specification/) |
| Looking for worked examples | [scd/examples/](scd/examples/) — matched CID + Definition + Assignment triples |
| Authoring a CID interactively | [cid/tools/interactive/](cid/tools/interactive/) |
| Validating what you wrote | [scd/tools/](scd/tools/) — `validate-scd.py` · [metadata/tools/](metadata/tools/) — `validate-metadata.py` |

The SCD examples are the fastest way in. They are the only place the CID, Definition, and Assignment
appear side by side, and a Definition only makes sense against its CID. Read the metadata examples
separately; the metadata file is small and self-contained, and pairing it with the others adds
nothing to either.

---

## A Note on Structure

The subdirectories are organized differently, deliberately:

- **CID keeps versioned subfolders** — `templates/v0.9/`, `examples/v0.9/`.
- **SCD is single-revision and flat.** Superseded revisions are retrievable from git history, and
  `scd/CHANGELOG.md` names the commit.
- **Metadata is single-revision and flat**, following the SCD, with the schema at the top of
  `metadata/` rather than in a `schema/` subdirectory — the directory holds one schema and a
  subdirectory for it would be a folder with a single file in it.

Do not harmonize these without raising it with the workstream. Each reflects a decision about how
that specification expects to be consumed.
