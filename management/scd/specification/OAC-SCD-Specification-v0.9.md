# OAC Slot Configuration Data (SCD) Specification
## Version: 0.9
### Document Identifier: OAC-SCD-SPEC
### Document Status: Draft
### Document Language: en-US
### Normative Reference: OCP Open Adapter Card Base Specification v0.9

---

## Foreword

This specification is authored by the OCP Open Adapter Card (OAC) workstream under the Open Compute Project Foundation. It defines Slot Configuration Data (SCD), the mechanism by which an OAC declares the configuration it will accept from its platform, and by which an upstream management controller supplies that configuration during initialization. The OCP OAC workstream retains editorial authority over this document. Contributions, errata reports, and change proposals shall be submitted through the OCP OAC project repository.

SCD is the counterpart to the Connector Interface Definition (CID) defined in OAC-CID-SPEC. The CID travels from the OAC to the platform and declares what the platform must know in order to decide whether the OAC may be powered. SCD carries the configuration that follows from that decision. The two documents are designed to be read together, and this specification uses the CID field names and conventions without redefining them.

This document is a Draft specification. Contents are subject to revision by the OCP OAC workstream prior to final publication.

> **This revision is a breaking change against its predecessor.** The revision history, and the porting notes for implementors coming from an earlier draft, are maintained in CHANGELOG.md in the repository root rather than in this document.

---

## Contents

1. Scope
2. Normative References
3. Terms and Definitions
4. Symbols and Abbreviated Terms
5. SCD Overview
   - 5.1 The Two Artifacts
   - 5.2 Why the Definition Is a Separate Document
   - 5.3 The Placement Rule
6. SCD Definition as a FRU File
7. SCD Definition Document Structure
   - 7.1 General
   - 7.2 metadata Object
   - 7.3 fields Array
   - 7.4 Field Identifiers and Namespacing
   - 7.5 Types and Constraints
   - 7.6 Defaults and Sentinel Defaults
   - 7.7 Response Classes
   - 7.8 cid_binding Object
   - 7.9 applies_when Object
   - 7.10 Field Naming and Ordering Conventions
8. SCD Assignment as a PLDM File
9. SCD Assignment Document Structure
10. OCP-Defined Field Registry
11. Delivery, Validation, and Acceptance
12. Runtime Power Control
13. Size Limits
14. Compliance

Annex A (informative) -- Paired CID, Definition, and Assignment Example
Annex B (informative) -- Composing an Assignment from a Definition
Annex C (informative) -- PLDM Protocol Field Value Reference
Annex D (informative) -- Items Open for Workstream Resolution

---

## 1. Scope

This specification defines Slot Configuration Data (SCD), a two-part machine-readable mechanism by which an OAC and its platform negotiate the OAC's slot-specific configuration during initialization.

SCD comprises two JSON documents travelling in opposite directions. The **SCD Definition (SCDD)** is published by the OAC and read by the upstream management controller; it enumerates every configuration field the OAC will accept, together with each field's type, constraints, and declared default. The **SCD Assignment (SCDA)** is composed by the upstream management controller and written to the OAC; it supplies values for those fields the platform wishes to set.

SCD replaces the hardware strapping mechanisms that earlier add-in card form factors used to communicate slot-specific configuration. A strapped interface encodes configuration in a fixed number of discrete inputs whose count and pull network are committed at board layout: its information capacity is bounded by pin count, and the set of representable values is fixed at the same time. Extending it is an electrical change — an additional pin, its termination, a board revision, and re-qualification of the assembly — which is why strapped interfaces in practice carry a small number of coarse, universally applicable values and nothing else. SCD carries that same class of information as a typed, self-describing document whose capacity is bounded by the maximum transferred Definition size of Section 13 rather than by pin count, and whose fields are named rather than positional. Adding an attribute is therefore a schema revision and an increment of `definition_revision`, propagated by firmware update rather than by an electrical respin, and the `pen.` namespace of Section 7.4 admits vendor-defined attributes without OCP registration and without risk of collision. SCD is exchanged while the OAC is in Operational State O3 and shall be validated and accepted by the OAC before the baseboard asserts OAC_PWR_EN.

The following are within the scope of this specification:

- The structure and encoding of the SCD Definition and SCD Assignment documents
- The field descriptor schema, including types, constraints, defaults, and response classes
- The namespacing rules that permit OAC vendors to define fields without collision
- The binding rules that associate an SCD field with the CID object it constrains
- The retrieval mechanism for the Definition via DSP0257 and the delivery mechanism for the Assignment via DSP0242
- The OAC-side validation, acceptance, and rejection reporting model
- The latching, re-application, and re-negotiation model, including cache retention requirements
- Maximum transferred size of each document
- Compliance requirements for OAC implementations and upstream management controller implementations

The following are outside the scope of this specification:

- The content and structure of the CID (governed by OAC-CID-SPEC)
- The algorithm by which an upstream management controller chooses values (implementation-defined; see Annex B for informative guidance)
- The platform's determination of whether it can power the OAC at all, which is made from the CID alone before any SCD exchange occurs (governed by OAC-CID-SPEC)
- Runtime power management after the OAC reaches Operational State O5, which is performed using the PLDM effecters described in Section 12
- OAC telemetry, sensor definitions, and reporting, other than the SCD reporting defined in Sections 11.4 and 11.5 and the file sensors of Sections 6.3 and 8.1
- Physical connector mechanical design (governed by OCP Open Adapter Card Base Specification)

---

## 2. Normative References

The following documents are normative references for this specification. For dated references, only the edition cited applies. For undated references, the latest edition of the referenced document applies.

| Reference | Document |
|-----------|----------|
| DSP0236 | DMTF, "Management Component Transport Protocol (MCTP) Base Specification," Version 1.3 |
| DSP0240 | DMTF, "PLDM Base Specification," Version 1.2 |
| DSP0241 | DMTF, "PLDM over MCTP Binding Specification," Version 1.0 |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification," Version 1.3.1 |
| DSP0249 | DMTF, "PLDM State Set Specification," Version 1.4.0 |
| DSP0257 | DMTF, "PLDM for FRU Data Specification," Version 2.0 |
| ECMA-404 | ECMA International, "JSON Data Interchange Syntax," 2nd Edition |
| OAC-CID-SPEC | OCP, "OAC Connector Interface Definition (CID) Specification," Version 0.9 |
| OCP OAC | OCP, "Open Adapter Card Base Specification," Version 0.9 |

> NOTE: DSP0242 is cited undated. Section 8.2 depends on the file write direction of that specification, and an implementer should work from the latest published edition.

---

## 3. Terms and Definitions

For the purposes of this specification, the following terms and definitions apply. Terms not defined here shall have the meaning ascribed to them in OAC-CID-SPEC, DSP0242, or the OCP Open Adapter Card Base Specification.

**3.1 SCD (Slot Configuration Data)**
The collective name for the two-document configuration mechanism defined by this specification, comprising the SCD Definition and the SCD Assignment. The unqualified term "SCD" shall not be used in normative text where either document is meant specifically.

**3.2 SCD Definition (SCDD)**
A machine-readable JSON document published by an OAC as FRU data, enumerating every configuration field the OAC will accept, together with each field's type, constraints, response class, and declared default. The SCDD is the template against which an Assignment is composed.

**3.3 SCD Assignment (SCDA)**
A machine-readable JSON document composed by an upstream management controller and written to an OAC, supplying values for a subset of the fields the OAC declared in its SCD Definition.

**3.4 CID (Connector Interface Definition)**
As defined in OAC-CID-SPEC: a machine-readable JSON document stored in OAC firmware that declares the OAC's connector population, power requirements, Operational Power Levels, high-speed signaling assignments, reference clocking, and vendor-defined discrete signals.

**3.5 upstream management controller**
The management processor that communicates with the management controller of each OAC over the OAC Management USB 2.0 interface. The upstream management controller is responsible for retrieving and evaluating the CID, retrieving the SCD Definition, composing the SCD Assignment, and delivering it before enabling primary busbar power.

The term denotes a role, not a location. Per OCP OAC Base Specification Section 10.2.1, the OAC Management USB 2.0 interface may be routed either to a management controller resident on the baseboard or carrier assembly into which the OAC is installed, or directly to a system-level management controller on the primary system board, typically the platform BMC. In the first topology the baseboard or carrier controller aggregates one or more OACs and is the upstream management controller for them, whether or not it in turn reports to a system-level controller. In the second the system-level controller provides the management functions otherwise required of the upstream controller and is itself the upstream management controller. Where a baseboard or carrier controller proxies or translates between the OAC and a system-level controller, the requirements this specification places on the upstream management controller apply to whichever device terminates the PLDM exchange with the OAC's management controller. Placement is otherwise outside the scope of this specification.

**3.6 field descriptor**
A single element of the SCDD `fields` array, describing one configurable field. Its schema is defined in Section 7.3.

**3.7 field identifier**
The value of a field descriptor's `id` key. The field identifier is the stable machine key for the field and is also the key under which a value for that field appears in an Assignment. Field identifiers are namespaced per Section 7.4.

**3.8 response class**
The value of a field descriptor's `response` key, indicating the strength of the OAC's expectation that the controller will supply a value. Response classes are defined in Section 7.7.

**3.9 declared default**
The value of a field descriptor's `default` key: the value the OAC applies when the field is absent from an Assignment. Every field descriptor carries a declared default.

**3.10 sentinel default**
A declared default that lies outside the field's own assignable range and denotes "not assigned" rather than a usable value. A sentinel default is marked by the `sentinel_default` key. See Section 7.6.

**3.11 sparse assignment**
The property that an SCD Assignment contains entries only for those fields the controller wishes to set. A field absent from an Assignment takes its declared default. There is no requirement that an Assignment enumerate every declared field.

**3.12 protocol group**
As defined in OAC-CID-SPEC: a self-contained element of a connector's `high_speed_lanes` value, comprising a single `protocol`, `link_direction`, and lane allocation. A connector object declares between one and eight protocol groups.

**3.13 protocol group name**
The value of a protocol group's `name` key in the CID, introduced in OAC-CID-SPEC v0.8. A protocol group name is unique within its containing connector and is not required to be unique across the CID document. See Section 11.2.3.

**3.14 link subdivision mode**
A string describing how the lanes of a protocol group are partitioned into independent links. Each mode string consists of power-of-2 segment counts prefixed with `"x"` and summing to the group's `total_lanes` (for example `"x8x8"` or `"x8x4x4"`). Segment order is positional over ascending lane indices. Subdivision applies to PCIe and CXL protocol groups only.

**3.15 Operational Power Level (OPL)**
As defined in OCP OAC Base Specification Section 10.1.2 and declared in the CID `power.primary` object: a discrete operating profile specifying a sustained power limit and associated performance characteristics.

**3.16 Assignment acceptance**
The condition in which an OAC has parsed an SCD Assignment, validated it per Section 11.3, and committed the contained configuration. Assignment acceptance is a precondition for the baseboard asserting OAC_PWR_EN.

**3.17 Assignment latch**
The point at which an accepted Assignment becomes immutable for the remainder of the OAC's power cycle. The Assignment latches when the OAC transitions from Operational State O3 to O4.

**3.18 re-apply**
The act of an OAC pushing a retained Assignment back into hardware without any upstream involvement. Contrast **re-negotiate**.

**3.19 re-negotiate**
The condition in which a retained Assignment has been lost and the upstream management controller shall compose and deliver a fresh Assignment before the OAC may be powered.

**3.20 Expanded Format JSON**
A JSON encoding that includes optional whitespace characters to improve human readability. Expanded format JSON is appropriate for authoring, documentation, and debugging purposes.

**3.21 Minified Format JSON**
A JSON encoding with all optional whitespace removed. Minified format JSON shall be used for transfer of both documents.

---

## 4. Symbols and Abbreviated Terms

| Symbol / Abbreviation | Meaning |
|-----------------------|---------|
| BMC | Baseboard Management Controller |
| CID | Connector Interface Definition |
| FRU | Field Replaceable Unit |
| JSON | JavaScript Object Notation |
| MCTP | Management Component Transport Protocol |
| OAC | Open Adapter Card |
| OPL | Operational Power Level |
| PEN | Private Enterprise Number (IANA) |
| PLDM | Platform Level Data Model |
| SCD | Slot Configuration Data |
| SCDA | SCD Assignment |
| SCDD | SCD Definition |
| UUID | Universally Unique Identifier |

---

## 5. SCD Overview

### 5.1 The Two Artifacts

An OAC is designed to operate in more than one platform context. The same physical OAC may be installed in slot 0 of one chassis and slot 6 of another; a subdividable protocol group it presents may serve a single host as one wide link in one platform and two hosts as a pair of independent narrower links in another, as a sixteen-lane PCIe group might be presented as one x16 or as two x8 links; and the power the platform can provision for it varies with chassis class, cooling capability, and concurrent OAC population. None of this is knowable from the OAC's own hardware, and historically it was communicated by discrete pins and resistor straps.

That mechanism constrains what can be communicated. *n* strapped inputs distinguish at most 2^*n* states, the encoding is positional and untyped, and both endpoints must agree on its meaning out of band because the wires carry no description of themselves. There is no room for a value the baseboard designer did not anticipate, no way for a card to decline a combination it cannot support, and no way to add an attribute without changing the board. The result is an interface that conveys a handful of bits of slot identity and link width and leaves every other slot-dependent parameter to be fixed in firmware per platform.

SCD is the replacement for those straps. It is defined as two documents because the information travels in both directions and neither endpoint can author the whole exchange.

**Table 5.1-1: The Two SCD Artifacts**

| Document | Direction | Transport | Role |
|----------|-----------|-----------|------|
| **SCD Definition (SCDD)** | OAC to upstream management controller | FRU Data File, retrieved per DSP0257 | Declares every field the OAC will accept, with type, constraints, and default |
| **SCD Assignment (SCDA)** | Upstream management controller to OAC | PLDM file (written per DSP0242) | Supplies values for the fields the platform wishes to set |

The OAC is the authority on what is configurable about itself, so the OAC publishes the template. The platform is the authority on the values, so the platform composes the response. The split follows the precedent of the BIOS Attribute Table and BIOS Attribute Value Table in DSP0247, where the same template-and-response structure solves the same problem.

Three properties follow from this arrangement and are load-bearing throughout this specification.

First, **every field carries a mandatory default and the Assignment is sparse**. A field absent from an Assignment is not an error; it takes the value the OAC declared. These two rules reinforce each other and together produce the property that makes vendor extension safe: a controller that encounters a field it does not recognize simply omits it, and the OAC applies its declared default. Unknown fields self-handle.

Second, **the exchange completes before primary power**. Both documents move while the OAC is in Operational State O3, after CID retrieval and validation but before the baseboard asserts OAC_PWR_EN. An OAC that has not accepted an Assignment shall not be energized. This ordering means the OAC applies configuration during its own power-on sequence rather than reconfiguring a running link.

Third, **SCD is not the admission decision**. Whether the platform can power the OAC at all is determined from the CID, before any SCD exchange begins. SCD presumes that decision has already been made in the affirmative. Section 5.3 states the rule that allocates content between the two documents.

### 5.2 Why the Definition Is a Separate Document

SCD could in principle be modeled as a strict *selection over CID*: the controller reads the CID, picks from the menus the CID advertises, and sends the selections back. That model is rejected here, because it mis-states what SCD is for.

SCD is a strap replacement, and a strap does not select from a menu the OAC published — it tells the OAC something the OAC could not otherwise know. Modeling SCD as a selection would force every such value through the CID, inflating a compatibility artifact with configuration content, and it would mean that adding a vendor-specific configuration field required a change to the CID schema. That would reintroduce, at the schema layer, the property that made strapping expensive: a centrally governed, fixed-width interface that every new attribute must be admitted into before it can be carried. Keeping the Definition separate and namespaced confines the cost of a new attribute to the parties that use it.

This specification therefore separates the two concerns. The CID is a compatibility artifact answering one question: *can this platform physically and electrically accept this OAC, and should it turn the power on?* SCD is a configuration artifact answering a different question: *given that the OAC is going to be powered, how should it be set up?* The Definition exists because the second question is the OAC's to frame — it states its own configurable surface rather than leaving the controller to infer one.

### 5.3 The Placement Rule

Content is allocated between the CID and SCD by a single test:

> **Does the platform need this value to decide whether to power the OAC at all?**
> **Yes → it belongs in the CID. No → it belongs in SCD.**

Two consequences of this rule are worth stating explicitly, because both were contested during drafting and both were resolved against the intuitive answer.

**Power stays in the CID.** The Operational Power Level menu — `opl_max_w`, `opl_eff_w`, `opl_red_w`, `opl_emg_w`, and the `opl_set_min_w` floor on the configurable level — remains in the CID. Those wattages are precisely what a platform weighs when deciding whether it can supply the OAC, and a platform that cannot supply `opl_emg_w` shall not power the OAC at all. Moving them into SCD would mean the admission decision could no longer be made from the CID alone. The `opl_max_w` value is additionally a hardware safety bound, and a configuration document shall never be able to raise a hardware limit.

**SCD states the platform's budget instead.** What SCD contributes is a quantity the CID cannot express, because it describes the platform rather than the OAC: the wattage this particular slot can supply. This flows from the controller to the OAC and is the mirror image of the CID's declaration. It does not restate anything the CID says. Section 10.2 defines it.

Applying the same test elsewhere: link subdivision is invisible to the powering decision, so the subdivision menu is an SCD field rather than CID content (Section 10.4). Slot identity was never a powering input, so it is an SCD field (Section 10.1). Connector population, lane counts, impedance, and pin maps all bear on physical compatibility, so they remain in the CID and are not restated here.

---

## 6. SCD Definition as a FRU File

### 6.1 General

The SCD Definition shall be published by the OAC's management controller as PLDM FRU data and retrieved by the upstream management controller using PLDM for FRU Data (DSP0257), over the same MCTP session that carries the CID.

DSP0257 provides that aggregated FRU data is identified and formatted in the context of a FRU Data File, and that this context, together with the format of DMTF-specified FRU data files, is defined in FRU Data File. The SCD Definition shall be accessed by that method and by no other. The OAC shall expose the Definition as a FRU Data File described by the File Descriptor PDR of Section 6.3, and an upstream management controller shall locate and retrieve it through that record. This specification defines no alternative access path to the Definition, and an OAC shall not require one.

The SCD Definition shall be read-only from the perspective of the upstream management controller. An OAC shall not accept a write to the SCD Definition.

The SCD Definition should be stored in persistent, non-volatile storage on the OAC, so that it is available to be served as soon as the OAC's management controller is ready and does not have to be reconstructed on every retrieval. An OAC may instead generate the Definition on demand from its own firmware configuration.

A Definition generated on demand shall be deterministic for a given firmware configuration. An OAC shall not return differing Definition content under one value of `metadata.definition_revision`, because Section 6.4 makes that value the sole staleness check and a Definition that varied beneath it would defeat the check.

Because the Definition may be held in non-volatile storage, a copy written before a firmware update can outlive the firmware it describes. Section 6.4 is what keeps that from going unnoticed: the OAC shall increment `metadata.definition_revision` whenever Definition content changes, a firmware update included, and a controller holding a stale copy is caught when it echoes the superseded value. An OAC that updates its firmware without updating a stored Definition and its revision is non-conformant. This specification defines no per-field removal or deprecation semantics; a Definition is replaced whole, and its revision is what identifies it.

### 6.2 Encoding

The SCD Definition shall be encoded in UTF-8 per ECMA-404. No byte order mark shall be present. The JSON document shall be syntactically valid per ECMA-404. Comments are not permitted; ECMA-404 defines no comment syntax, and a document containing `//` or `/* */` sequences outside a string literal is malformed.

The OAC shall publish the Definition in minified format JSON. An upstream management controller shall parse minified format and should tolerate expanded format.

### 6.3 File Classification and Access

The SCD Definition shall be represented in the OAC's PDR repository by a File Descriptor PDR as defined in DSP0248, with `EntityType` set to Device File and `FileClassification` set to `FRUDataFile`. The file so described is a FRU Data File per DSP0257 and is retrieved as required by Section 6.1.

The OAC shall set the `FileName` field of that File Descriptor PDR, which is a `strASCII` string, to:

```
OAC_SCDD.json
```

An upstream management controller shall use that name to distinguish the Definition from every other FRU Data File the OAC publishes, the CID among them, and shall not rely on PDR ordering to make that distinction.

`FileName` is how the Definition is *recognised*; it is not how it is *opened*. The same File Descriptor PDR carries a `FileIdentifier`, a `uint16` that DSP0248 defines as unique relative to the PLDM Terminus ID, and DSP0242 requires that value, rather than the name string, as the parameter to `DfOpen`, `DfGetFileAttribute`, and `DfSetFileAttribute`. An upstream management controller shall therefore match on `FileName` to find the record and then use the `FileIdentifier` from that same record to open the file. The OAC assigns the `FileIdentifier`; this specification fixes no value for it, and a controller shall not assume one.

The OAC shall set the `FileCapabilities` bitfield16 so that no write and no modification of the Definition is permitted: `FcWritesPermitted` and `ExWriteOpen` shall both be zero. The OAC shall set `FileMaximumSize` no greater than the Definition size limit of Section 13.1.

The SCD Definition is a **Fixed Length File** in the sense of DSP0242 — read and modify after creation but never appended to, its size unchanged between modifications — and an OAC shall treat it as one. The modification contemplated is a firmware update that replaces the Definition, per Section 6.1; nothing else modifies it. Because DSP0242 equates a fixed-length file's size to the `FileMaximumSize` field of its File Descriptor PDR, the OAC shall set `FileMaximumSize` to the exact transferred size of the Definition it is serving rather than to a padded upper bound, and shall update that field whenever the Definition is replaced.

DSP0242 sets the sensor requirements for a file by its file characteristic, not by its classification. For a Fixed Length File it makes the Device File State Sensor mandatory and the File Size Monitoring Sensor recommended, the latter because a controller that finds no size sensor may fall back to `FileMaximumSize`, which for a fixed-length file is exact. This specification tightens the second requirement: an OAC shall publish both sensors for the SCD Definition. The reason is that the fallback costs a controller a second PDR lookup and a correctness assumption at precisely the moment it is deciding whether its cached Definition is still good, and the SCD negotiation is short enough that the cost of one more sensor PDR is not worth that ambiguity.

| Sensor | Kind | DSP0242 | This specification |
|--------|------|---------|--------------------|
| Device File State Sensor | State sensor implementing DSP0249 State Set 68 (Device File) | Shall, for a Fixed Length File | Shall. Reports the state of the file and signals that its content has been modified. |
| File Size Monitoring Sensor | Compact or Numeric sensor per DSP0242 | Should, for a Fixed Length File | Shall. Reports the current size of the Definition in bytes, as transferred, and permits the upstream management controller to detect a change in size. |

DSP0242 advises against supporting the *File is at Maximum Size* state on a fixed-length file, which is always at its maximum size and for which the state therefore carries no information. Table 6.3-1 reflects that: the OAC shall not report it.

A File Size Monitoring Sensor published for the Definition shall set `BaseUnit` to Bytes and `UnitModifier` to zero. If it is a Numeric sensor, `RateUnit` shall be None, `Offset` shall be zero, and `Resolution` shall be 1.00; if it is a Compact Numeric sensor, `OccurrenceRate` shall be No Occurrence Rate. DSP0242 advises against size thresholds on a fixed-length file, and an OAC should not set them on the Definition.

A sensor is associated with the file it reports on by carrying the same entity identification as that file's File Descriptor PDR: the same `EntityType`, the same `EntityInstanceNumber`, and the same `ContainerID`. The OAC shall set all three accordingly on both sensor PDRs.

`ContainerID` identifies the containing entity, which is the OAC and not the file. The OAC shall carry one `ContainerID` value across every File Descriptor PDR and every associated sensor PDR this specification requires of it — the Definition's records and the Assignment's records alike, the Configuration State Sensor of Section 11.5 included.

`EntityInstanceNumber` is what separates the two files. The OAC shall assign the Definition and the Assignment distinct values, and shall repeat each file's value on that file's sensor PDRs. DSP0248 requires this independently: every file within a `ContainerID` shall have a unique `EntityInstanceNumber`.

This specification requires no directory. The SCD files form a flat set, and an OAC shall set `SuperiorDirectoryFileIdentifier` to `0xFFFF` on both File Descriptor PDRs to declare them outside any hierarchy. An OAC that does place its files in a directory shall do so as DSP0242 requires — a Device File Directory PDR and an Entity Association Record, with the directory's identifier as the `ContainerID` — and the one-`ContainerID` rule above then names that directory rather than the OAC. Either arrangement satisfies this specification; what it requires is that the value be common to all SCD records, so that a controller which has found one SCD record can find the rest.

The Definition's size is not a constant of the OAC design, since it changes whenever firmware changes, and an upstream management controller shall read it from the File Size Monitoring Sensor rather than assume it. A modification reported by the Device File State Sensor indicates that the controller's copy of the Definition may be stale; the authoritative staleness check remains `metadata.definition_revision` per Section 6.4, and an upstream management controller shall not treat the sensor as a substitute for it.

The Device File State Sensor shall report the states of DSP0249 State Set 68 with the meanings that set assigns them. For the Definition only two of the five are reachable, and an OAC shall not report the remaining three.

**Table 6.3-1: State Set 68 Applied to the SCD Definition**

| State | Name | Meaning for the Definition |
|-------|------|----------------------------|
| 1 | File has Not Changed | The Definition has not changed since the last status check. A controller holding a previously retrieved copy need not retrieve it again. |
| 2 | File is Updated | The Definition has changed since the last status check. The upstream management controller shall re-retrieve it and re-read `metadata.definition_revision` before composing an Assignment. |
| 3 | File is at Maximum Size | An OAC shall not report this state. A fixed-length file is always at its maximum size, so the state distinguishes nothing; DSP0242 advises against supporting it for this file characteristic. A Definition that would exceed `FileMaximumSize` is a conformance failure of Section 13.1, not a reportable file state. |
| 4 | File Data has Wrapped | Not applicable. The Definition is published whole and is never appended to. |
| 5 | File Data has Truncated | Not applicable, for the same reason. |

> NOTE: The Device File State Sensor reports the state of the *file*. It is not the Configuration State Sensor of Section 11.5, which reports whether a valid Assignment is in force. The two are unrelated.

The SCD Definition shall be retrievable whenever the OAC is in Operational State O3 or later. An OAC shall not require primary power to serve its Definition.

The upstream management controller shall retrieve the Definition after the CID and before composing an Assignment. Retrieving the Definition has no side effects and may be repeated.

### 6.4 Definition Revision

The SCDD `metadata.definition_revision` field is a monotonically increasing integer that the OAC shall increment whenever the content of its Definition changes, including across firmware updates. The upstream management controller shall echo the value into the Assignment, and the OAC shall reject an Assignment whose echoed value does not match its current Definition. This is the mechanism by which a stale controller — one holding a Definition read before a firmware update — is detected. See Section 11.3.

---

## 7. SCD Definition Document Structure

### 7.1 General

The SCD Definition is a single JSON object. The root key shall be `"oac_scdd"`. Its value shall be a JSON object containing two sections, `"metadata"` and `"fields"`, both of which shall be present and shall appear in that order.

```json
{
  "oac_scdd": {
    "metadata": { ... },
    "fields":   [ ... ]
  }
}
```

Additional top-level keys within `"oac_scdd"` are permitted for vendor extensions but shall use a `pen.<IANA PEN>.` prefix per Section 7.4. Upstream management controllers shall ignore unrecognized keys.

### 7.2 metadata Object

**Table 7.2-1: SCDD metadata Object Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `schema_version` | string | Required | e.g. `"0.9"` | Version of the SCDD schema this document conforms to. Shall match a published or draft version identifier of this specification. |
| `oac_spec_revision` | string | Required | e.g. `"0.9"` | OAC Base Specification revision the OAC was implemented against. |
| `definition_revision` | integer | Required | >= 1 | Monotonically increasing revision of this Definition's content. See Section 6.4. |
| `description` | string | Optional | Free text | Human-readable summary. Shall not be relied upon for any configuration decision. |
| `iana_pen` | integer | Optional | > 0 | IANA Private Enterprise Number of the OAC vendor. Informational provenance only; shall not be used as an authorization mechanism. |

### 7.3 fields Array

The value of `"fields"` shall be a JSON array of field descriptors. The array shall contain at least one element. Each element describes exactly one configurable field.

**Table 7.3-1: Field Descriptor Schema**

| Key | Applies To | Required | Description |
|-----|-----------|----------|-------------|
| `id` | All | Required | Stable machine key and Assignment key. Namespaced per Section 7.4. Shall be unique within the document. |
| `display_name` | All | Required | Short human-facing label. 1 to 64 characters. |
| `description` | All | Required | Human-facing explanation. No OAC behavior shall derive from it. |
| `type` | All | Required | One of `"integer"`, `"string"`, `"boolean"`, `"enumeration"`. |
| `response` | All | Required | One of `"required"`, `"optional"`. See Section 7.7. |
| `default` | All | Required | The value applied when the field is absent from an Assignment. See Section 7.6. |
| `sentinel_default` | All | Optional | Boolean. When `true`, marks `default` as a reserved not-assigned marker lying outside the assignable range. See Section 7.6. |
| `min`, `max` | `integer` | Optional | Inclusive bounds on assignable values. Shall be supplied together. |
| `units` | `integer` | Optional | Unit of measure. Omitted when the value is unitless. |
| `max_length` | `string` | Optional | Maximum character count. |
| `values` | `enumeration` | Required for `enumeration` | Array of permissible values. See Table 7.3-2. |
| `cid_binding` | All | Optional | Associates the field with the CID object it constrains or applies to. See Section 7.8. |
| `applies_when` | All | Optional | Single-field equality predicate gating relevance. See Section 7.9. |

**Table 7.3-2: values Array Element Fields**

| Field Name | JSON Type | Required | Description |
|------------|-----------|----------|-------------|
| `value` | string | Required | The literal value that may appear in an Assignment. Shall be unique within the array. |
| `description` | string | Required | Human-facing explanation of what selecting this value does. |

Machine-readable constraints shall not be restated in `description` text. A descriptor whose prose contradicts its own `min`, `max`, or `values` is defective, and this rule removes the possibility.

### 7.4 Field Identifiers and Namespacing

Every field identifier shall begin with one of the following prefixes:

| Prefix | Owner |
|--------|-------|
| `ocp.` | Reserved for fields defined by this specification. See Section 10. |
| `pen.<IANA PEN>.` | Vendor-defined, where `<IANA PEN>` is the vendor's IANA Private Enterprise Number in decimal. |

Any other prefix is non-conformant. An upstream management controller shall reject a Definition containing a field identifier with an unrecognized prefix.

This scheme lets OAC vendors define configuration fields freely, without collision risk and without an OCP registration round-trip. A vendor field is as much a first-class SCD field as an OCP-defined one; the prefix records who defined it, not how it is treated.

Field identifiers shall use snake_case within each dot-separated segment, shall consist only of lowercase letters, digits, underscores, and the dot separator, and shall not exceed 128 characters.

> NOTE: Certain OCP-defined identifiers embed a CID connector identifier as a segment — for example `ocp.link_subdivision.conn0.pcie_primary`. The connector segment is the CID connector identifier lowercased, so `CONN0` becomes `conn0`, while the `cid_binding` carries the canonical uppercase form. The two casings are deliberate: the field identifier follows the snake_case convention that governs all identifiers, and the binding quotes the CID verbatim. Section 10.4 explains why both the connector and the group name are required.

### 7.5 Types and Constraints

An Assignment value shall match the JSON type its descriptor declares. Type coercion is not permitted: the string `"5"` is not a valid value for an `integer` field, and the integer `1` is not a valid value for a `boolean` field.

For `integer` fields, when `min` and `max` are declared, an assigned value shall satisfy `min <= value <= max` inclusive. A descriptor declaring one bound without the other is malformed.

For `string` fields, when `max_length` is declared, an assigned value shall not exceed it. String values are opaque to this specification; an OAC shall not derive configuration from the content of a `string` field except as Section 10 specifies.

For `enumeration` fields, an assigned value shall exactly match, as a case-sensitive comparison, one of the `value` entries in the descriptor's `values` array. Matching shall be by value and never by array position.

A JSON `null` is not a valid value for any field and shall not appear in either document. Absence and `null` are not equivalent; `null` is malformed.

### 7.6 Defaults and Sentinel Defaults

Every field descriptor shall carry a `default`. There is no such thing as a field without one, and this is what makes sparse assignment safe: omission is always well-defined.

A declared default shall satisfy its own descriptor's constraints — it shall be of the declared type, shall lie within `min` and `max` where declared, and shall appear in `values` where the type is `enumeration` — except in the sentinel case below.

**Sentinel defaults.** Some fields have no value the OAC could correctly choose. The canonical case is slot identity: the value shall correlate to the physical slot the OAC is installed in, the OAC cannot know that, and a plausible-looking guess such as `0` is worse than an obvious failure because `0` names a real slot.

Rather than weaken the mandatory-default rule for such fields, a descriptor may declare a **sentinel default**: a value lying deliberately *outside* the field's assignable range, denoting "not assigned." A descriptor declaring a sentinel default shall set `"sentinel_default": true`.

The following rules apply:

1. A descriptor with `"sentinel_default": true` shall declare a `default` that lies outside the range bounded by `min` and `max`.
2. A descriptor without `sentinel_default`, or with it set to `false`, shall declare a `default` that lies inside that range.
3. An Assignment shall not assign a sentinel value. The sentinel is a state the OAC may hold, not a value the upstream management controller may choose.
4. An OAC holding a sentinel value shall report the corresponding property as unknown rather than reporting a substitute.

The flag exists so that a validator can distinguish a deliberate out-of-range default from a typographical error. Without it the two are indistinguishable.

### 7.7 Response Classes

**Table 7.7-1: Response Classes**

| Class | Expectation | Semantics |
|-------|-------------|-----------|
| `required` | Should appear in the Assignment | The declared default exists for safety but is unlikely to be correct for any real platform. The controller is expected to supply a value. |
| `optional` | May appear in the Assignment | The declared default is safe and usually correct. Override only where the platform has a specific reason. |

There are exactly two response classes.

**`required` is advisory, not a hard gate.** An OAC shall not reject an Assignment solely because a `required` field is absent from it. This follows from the two rules in Section 7.6 and Section 9.4: every field has a default and the Assignment is sparse, so omission is always well-defined and always safe by construction. A hard gate would mean a generic controller could be unable to bring up a card it otherwise fully supports — which is precisely the per-OAC enablement burden that hardware straps imposed and that SCD exists to remove.

An OAC may report, through PLDM, that a `required` field fell back to its default, so that platform operators can identify under-configured OACs without the OAC refusing to run.

> NOTE: An earlier draft of this specification defined a third class, `informational`, for values the OAC reports but never accepts. It was removed. The Definition is a template of settable fields only; anything the OAC merely reports belongs in PLDM sensors, where discovery and refresh semantics are already defined.

### 7.8 cid_binding Object

A field descriptor may carry a `cid_binding` object associating the field with the CID object it constrains or applies to. Bindings are by name or by range and shall never be by array position, so that the two documents version independently and a CID edit that reorders protocol groups fails loudly rather than misconfiguring the OAC.

**Table 7.8-1: cid_binding Object Fields**

| Field Name | JSON Type | Required | Description |
|------------|-----------|----------|-------------|
| `cid_object` | string | Required | One of `"protocol_group"` or `"power.primary"`. |
| `cid_connector` | string | Required when `cid_object` is `"protocol_group"`; shall be absent otherwise | CID connector identifier in canonical form, e.g. `"CONN0"`. |
| `cid_group_name` | string | Required when `cid_object` is `"protocol_group"`; shall be absent otherwise | The `name` of the target protocol group within that connector. |
| `constraint` | string | Required when `cid_object` is `"power.primary"`; shall be absent otherwise | Currently only `"opl_range"` is defined. |

**Protocol group bindings take both the connector and the name.** Protocol groups are defined *inside* connectors in the CID; there is no global group namespace to address. A binding naming only the group would assert a flatter structure than the document has, and would force the CID to maintain document-wide name uniqueness solely to serve a foreign document's addressing convenience. Carrying both makes the locator match the structure it locates. Section 11.2.3 states the resolution rules normatively.

**Power bindings take no connector**, because `power.primary` is not inside a connector. A power binding declares that the field's `min` and `max` shall be validated against the CID OPL menu rather than standing alone.

### 7.9 applies_when Object

A field descriptor may carry an `applies_when` object declaring that the field is relevant only when another field holds a particular value.

**Table 7.9-1: applies_when Object Fields**

| Field Name | JSON Type | Required | Description |
|------------|-----------|----------|-------------|
| `field` | string | Required | The field identifier of the governing field. Shall refer to a field declared in the same Definition. |
| `equals` | any | Required | The value the governing field shall hold for this field to be relevant. |

`applies_when` is deliberately a single-field equality test and not a general expression language. An implementation encountering a constraint it cannot express with it should raise the case with the workstream so that a specific construct can be added, rather than generalizing the predicate.

An OAC shall ignore, without error, an assigned value for a field whose `applies_when` predicate is not satisfied.

### 7.10 Field Naming and Ordering Conventions

1. The section order within `"oac_scdd"` shall be `"metadata"`, then `"fields"`.
2. Within a field descriptor, keys should appear in the order given in Table 7.3-1.
3. Elements of the `fields` array should be grouped by namespace, with `ocp.` fields preceding `pen.` fields.
4. JSON keys shall use snake_case. CamelCase and hyphenated key names are non-conformant.
5. A JSON `null` shall not appear anywhere in either document.
6. Enumeration `value` strings are compared case-sensitively and shall be reproduced exactly.

---

## 8. SCD Assignment as a PLDM File

### 8.1 General

The SCD Assignment shall be delivered from the upstream management controller to the OAC's management controller as a PLDM file using PLDM for File Transfer (DSP0242), over the MCTP binding defined in DSP0241, carried on the OAC Management USB 2.0 interface per the OCP Open Adapter Card Base Specification.

The Assignment is written, not read. An OAC is not required to serve a previously accepted Assignment back, and an upstream management controller shall not rely on being able to read one. The Configuration State Sensor of Section 11.5 is the mechanism that replaces such a read.

The SCD Assignment shall not be stored in non-volatile memory. The Assignment as written, and any record the OAC decodes from it, shall be held only in volatile storage, and the OAC's retention of it shall be bounded by +12V Aux: when +12V Aux is removed, the Assignment and everything derived from it are gone, and the OAC returns to the `unassigned` state and shall be re-negotiated. Section 11.6 governs the lifetime in full, and Section 11.6.4 gives the reason the prohibition is absolute.

The SCD Assignment shall be represented in the OAC's PDR repository by a File Descriptor PDR as defined in DSP0248, with `EntityType` set to Device File and `FileClassification` set to `OtherFile`. The Assignment is not FRU data and shall not be classified as such.

The OAC shall set the `FileName` field of that File Descriptor PDR, which is a `strASCII` string, to:

```
OAC_SCDA.json
```

An upstream management controller shall use that name to locate the file it is to write, and shall not rely on PDR ordering to locate it. As with the Definition, the name identifies the record and the `FileIdentifier` carried in that same record is the parameter used to open it, per Section 6.3.

The OAC shall set the `FileCapabilities` bitfield16 so that writing and modification of the Assignment are permitted. `FcWritesPermitted` shall be one, which DSP0248 defines as writing or modifying the file being permitted by the File Client. `ExWriteOpen` shall be one, which is what admits an exclusive open for write. `FileModify` shall be one, indicating that updates are random rather than append-only, because Section 11.6.2 provides for an Assignment to be written again at offset zero on re-negotiation rather than appended to the previous one. `DataType` shall be zero, declaring a regular file rather than a streaming FIFO, and `Read Pushed` shall be one; that combination of three bits is what obliges the OAC to support the write command of Section 8.2, and an OAC that advertised anything less would not be obliged to accept the transfer at all. `ExReadOpen` shall be zero, since the OAC is not required to serve the Assignment back. Advertised capability describes what the transfer mechanism permits and does not oblige the OAC to retain or serve back an Assignment it has accepted; the preceding paragraph governs. The OAC shall set `FileMaximumSize` no greater than the Assignment size limit of Section 13.2, and shall reject an Assignment exceeding it with code `0x0E` per Section 11.4.

The SCD Assignment is a **Regular File** in the sense of DSP0242 — read, modify, or append after creation — and an OAC shall treat it as one. It is not a fixed-length file: Section 9 permits a sparse Assignment, so two successive Assignments for the same OAC may differ in length, and `FileMaximumSize` is a genuine upper bound here rather than the exact size it is for the Definition.

That characteristic is what settles the sensor requirements. DSP0242 keys those requirements to the file characteristic rather than to the classification, and for a Regular File it makes both the File Size Monitoring Sensor and the Device File State Sensor mandatory. Both are therefore mandatory for the SCD Assignment, and an OAC shall publish both. This specification adds a third, the Configuration State Sensor, which is likewise mandatory.

| Sensor | Kind | Purpose |
|--------|------|---------|
| File Size Monitoring Sensor | Compact or Numeric sensor per DSP0242 | Reports the size in bytes of the most recent Assignment transfer. Mandatory per DSP0242 for a Regular File. |
| Device File State Sensor | State sensor implementing DSP0249 State Set 68 (Device File) | Reports the state of the file and signals that its content has been modified. Mandatory per DSP0242 for a Regular File. |
| Configuration State Sensor | State sensor implementing DSP0249 State Set 15 (Configuration State) | Reports whether a valid Assignment is in force. Mandatory per this specification; defined in Section 11.5. |

DSP0242 recommends a `FatalHigh` threshold equal to `FileMaximumSize` on a Regular File's size sensor, to give the controller overflow detection. An OAC should set it, and shall not permit a controller to raise it above `FileMaximumSize`; a `SetSensorThresholds` attempting that shall be answered `ERROR_INVALID_DATA`.

Each of the three is associated with the Assignment file by carrying the same entity identification as the Assignment's File Descriptor PDR: the same `EntityType`, the same `EntityInstanceNumber`, and the same `ContainerID`. The OAC shall set all three accordingly on all three sensor PDRs.

The `ContainerID` shall be the one value the OAC carries on all of its SCD records, the Definition's included, per Section 6.3. The `EntityInstanceNumber` shall be the Assignment's own value, distinct from the Definition's.

The Device File State Sensor shall report the states of DSP0249 State Set 68 with the meanings that set assigns them. Three of the five are reachable for the Assignment; the remaining two describe overflow behaviours this specification does not permit.

**Table 8.1-1: State Set 68 Applied to the SCD Assignment**

| State | Name | Meaning for the Assignment |
|-------|------|----------------------------|
| 1 | File has Not Changed | No Assignment has been written since the last status check. |
| 2 | File is Updated | An Assignment has been written since the last status check. This reports a completed *transfer*, not an acceptance. |
| 3 | File is at Maximum Size | A transfer has filled the file to `FileMaximumSize`. An OAC may report this state; it does not imply acceptance or rejection. |
| 4 | File Data has Wrapped | An OAC shall not report this state. An Assignment exceeding `FileMaximumSize` shall be rejected with code `0x0E` per Section 11.4, not wrapped. |
| 5 | File Data has Truncated | An OAC shall not report this state, for the same reason. A silently truncated Assignment would be a valid-looking document missing its tail. |

Neither the File Size Monitoring Sensor nor the Device File State Sensor reports whether an Assignment was accepted. Acceptance is reported by the rejection code of Section 11.4 and by the Configuration State Sensor of Section 11.5, and an upstream management controller shall not infer acceptance from a file size or a file state. An aborted transfer leaves the OAC holding nothing per Section 8.2, and a rejected one leaves its prior SCD state unchanged per Section 11.3.2; neither outcome is distinguishable from a size or file-state reading alone.

### 8.2 Transfer Sequence

The Assignment shall be transferred using the DSP0242 command sequence below.

| Step | Command | Description |
|------|---------|-------------|
| 1 | `DfOpen` | Opens the SCD Assignment file for write and holds it exclusively, by setting the write-access and `DfOpenExclusive` bits of `DfOpenAttribute` to one. The file is located by matching the `FileName` `OAC_SCDA.json` per Section 8.1 and opened using the `FileIdentifier` carried in that same File Descriptor PDR. Returns a `FileDescriptor` identifying the session. |
| 2 | `DfWrite` | Transfers the Assignment payload against the open `FileDescriptor`, pushed to the OAC by the upstream management controller. One command transfers one section; an Assignment larger than a negotiated section is transferred by several, written sequentially from offset zero. |
| 3 | `DfClose` | Signals end of transfer, with the `ZeroLength` option set to zero, which obliges the OAC to flush pending updates and invalidate the `FileDescriptor`. The OAC shall not begin validation of the Assignment before `DfClose` is received. |

Exclusivity is not optional here. An Assignment transfer shall hold the file exclusively for the duration of the session, and an OAC receiving a non-exclusive write open shall answer `INVALID_DF_ATTRIBUTE`. Exclusivity is required because the Assignment is validated as a whole after `DfClose`, and a second writer interleaving with the first would produce a document neither of them composed. `DfOpenRegFIFO` shall be zero, selecting regular rather than streaming semantics. The upstream management controller shall not rely on `DfOpenPolledPushed` to select a transfer direction on a write open; the Assignment is always pushed to the OAC.

Within a session the controller shall write sequentially from offset zero. Seeking shall not be used: each section shall begin at a `SectionOffset` of zero and shall be carried in a single transfer part, and the controller shall compute the file offset of the next command by adding the byte count returned by the previous one. An OAC shall treat a write command received within the negotiated heartbeat interval as evidence that the session is alive, so a controller transferring a multi-section Assignment need not interleave `DfHeartbeat` commands.

A write session delivers one complete Assignment. The OAC shall take the document to be exactly the bytes written between `DfOpen` and `DfClose` in that session, and shall not consider any residual content of the file beyond them. This matters because a re-negotiated Assignment may be shorter than the one it replaces — Section 9 permits a sparse document, so successive Assignments differ in length — and because over-writing a file in place need not shorten it: the resulting length may be the greater of the previous and the new one. An OAC that instead parsed the file by its length would see the tail of the previous Assignment appended to the new one, yielding a document that can look well formed while carrying stale values. Requiring the session rather than the file length to delimit the document removes that failure without obliging the controller to zero the file first, which would in turn require `FcZeroLengthPermitted` and, through it, exclusive read access the Assignment does not otherwise need.

The OAC shall treat the Assignment as a single atomic unit. Validation shall occur after `DfClose` and shall consider the complete payload. An Assignment is accepted in whole or rejected in whole; partial application is non-conformant.

An OAC shall retain no state from an aborted or incomplete transfer. If the transfer does not reach `DfClose`, any buffered payload shall be discarded and the OAC shall remain in its prior SCD state.

### 8.3 Encoding

The SCD Assignment shall be encoded in UTF-8 per ECMA-404, with no byte order mark. Comments are not permitted.

The upstream management controller shall transfer the Assignment in minified format JSON. Assignments are small; see Section 13.2.

### 8.4 Timing

The Assignment shall be delivered while the OAC is in Operational State O3, after `OAC_MC_RDY` assertion and before the baseboard asserts `OAC_PWR_EN`. Section 11.1 defines the full sequence.

---

## 9. SCD Assignment Document Structure

### 9.1 General

The SCD Assignment is a single JSON object. The root key shall be `"oac_scda"`. Its value shall be a JSON object containing two sections, `"metadata"` and `"assignments"`, both of which shall be present and shall appear in that order.

```json
{
  "oac_scda": {
    "metadata":    { ... },
    "assignments": { ... }
  }
}
```

### 9.2 metadata Object

**Table 9.2-1: SCDA metadata Object Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `schema_version` | string | Required | e.g. `"0.9"` | Version of the SCDA schema this document conforms to. |
| `definition_revision` | integer | Required | >= 1 | Echo of the `definition_revision` from the Definition this Assignment was composed against. See Section 11.3.1. |
| `description` | string | Optional | Free text | Human-readable summary. Shall not affect OAC behavior. |

### 9.3 assignments Object

The value of `"assignments"` shall be a JSON object whose keys are field identifiers drawn from the Definition and whose values are the assigned values.

```json
"assignments": {
  "ocp.slot_id": 5,
  "ocp.max_power_w": 2000,
  "ocp.link_subdivision.conn0.pcie_primary": "x8x8"
}
```

The `assignments` object may be empty. An empty Assignment is valid and means the controller accepts every declared default.

Each key shall exactly match the `id` of a field descriptor in the Definition identified by `metadata.definition_revision`. A key not matching any declared field is an error; see rejection code `0x04` in Table 11.4-1.

Each value shall satisfy the type and constraint rules of Section 7.5 as declared by the corresponding descriptor.

### 9.4 Sparseness

An Assignment shall contain entries only for those fields the upstream management controller wishes to set. Absence of a field is not an error and is not a partial assignment; it selects the declared default.

An OAC shall not require that every declared field appear in an Assignment, and shall not require that every `required` field appear. See Section 7.7.

### 9.5 Duplicate Keys

A duplicate key within the `assignments` object is malformed. ECMA-404 does not define behavior for duplicate object keys, and implementations differ in whether the first or the last occurrence wins. An OAC shall reject an Assignment containing a duplicate key rather than silently resolving it.

---

## 10. OCP-Defined Field Registry

This section defines the field identifiers in the `ocp.` namespace. An OAC shall use these identifiers, with these semantics, for the corresponding functions, and shall not define a `pen.` field duplicating one of them.

An OAC is not required to declare every field in this registry. An OAC declares the fields that are meaningful for it; a field absent from an OAC's Definition is simply not configurable on that OAC.

### 10.1 ocp.slot_id

| Property | Value |
|----------|-------|
| Type | `integer` |
| Response class | `required` |
| Range | Platform-dependent; `min` `0`, `max` as declared by the OAC |
| Default | Sentinel, `255`, with `"sentinel_default": true` |
| `cid_binding` | None |

The logical slot identifier of the position the OAC occupies. This is the primary replacement for legacy slot-address strapping.

There is no value the OAC could correctly choose for this field, so its default is a sentinel per Section 7.6. An OAC holding the sentinel shall report its slot as unknown and shall not substitute a plausible value. An upstream management controller shall not assign the sentinel value.

### 10.2 ocp.max_power_w

| Property | Value |
|----------|-------|
| Type | `integer` |
| Response class | `required` |
| Units | `"watts"` |
| Range | `min` = CID `power.primary.opl_emg_w`; `max` = CID `power.primary.opl_max_w` |
| Default | CID `power.primary.opl_emg_w` |
| `cid_binding` | `{ "cid_object": "power.primary", "constraint": "opl_range" }` |

The sustained power the platform can supply to this slot.

This field runs opposite to every other field in the Definition: it is the platform describing *itself* to the OAC, not the platform configuring the OAC. It is in SCD rather than CID because it is not a property of the OAC at all, and the OAC needs it because otherwise it knows only what it is rated to draw and never what it is permitted to draw here.

The declared bounds follow from the CID: below `opl_emg_w` the OAC cannot run at all, and above `opl_max_w` the statement is unusable because the hardware ceiling binds first.

**The default runs downward.** `ocp.max_power_w` defaults to the OAC's emergency level. A controller that omits it leaves the OAC heavily throttled rather than assuming a budget the platform may not have. This matters because `required` is advisory, so omission is a permitted outcome, and a field describing the platform's own capability is exactly the kind a generic controller might skip.

### 10.3 ocp.initial_power_level_set_w

| Property | Value |
|----------|-------|
| Type | `integer` |
| Response class | `optional` |
| Units | `"watts"` |
| Range | `min` = CID `power.primary.opl_set_min_w`; `max` = CID `power.primary.opl_max_w` |
| Default | OAC-declared, within that range |
| `cid_binding` | `{ "cid_object": "power.primary", "constraint": "opl_range" }` |

The OPL-SET wattage at which the OAC is initially capped.

The settable band is the CID's to define; SCD selects a point inside it. The OAC shall round the assigned value internally to whatever step its power control loop resolves; no granularity is advertised in the Definition, and an OAC wishing to publish its step size shall do so as a PLDM sensor.

**The applied cap is a clamp, not a constraint.** The OAC shall apply:

```
applied_cap = min( ocp.initial_power_level_set_w,
                   ocp.max_power_w,
                   CID power.primary.opl_max_w )
```

Expressing this as a clamp rather than a cross-field validation rule means no assignable combination of the two SCD fields can produce an unsafe state, and it is why Section 11.3 requires no cross-field checks. An OAC shall not reject an Assignment on the grounds that `ocp.initial_power_level_set_w` exceeds `ocp.max_power_w`; it shall clamp.

### 10.4 ocp.link_subdivision.&lt;connector&gt;.&lt;group_name&gt;

| Property | Value |
|----------|-------|
| Type | `enumeration` |
| Response class | `required` |
| Values | Subdivision mode strings per Section 3.14 |
| Default | OAC-declared; typically the unsubdivided mode |
| `cid_binding` | `{ "cid_object": "protocol_group", "cid_connector": ..., "cid_group_name": ... }` |

How the lanes of one PCIe or CXL protocol group are partitioned into independent links.

Subdivision moved from the CID to SCD in this revision. A x16 group running as `x8x8` mates the same pins and draws the same power, so subdivision is invisible to the powering decision and fails the placement rule of Section 5.3.

**Both identifier segments are required.** The `<connector>` segment is the CID connector identifier lowercased; the `<group_name>` segment is the group's `name`. A bare `ocp.link_subdivision` cannot express two subdividable groups without duplicate identifiers, and field identifiers are the Assignment's keys, so they shall be unique. A two-segment form omitting the connector collides the moment two connectors reuse a group name — which is precisely the reuse that per-connector scoping permits.

An OAC shall declare one such field per subdividable protocol group, and shall declare none for groups it cannot subdivide.

Each declared mode's segments shall sum to the bound CID group's `total_lanes`. Segment order is positional over ascending lane indices within the group.

### 10.5 Reserved Identifiers

The following identifiers were defined in earlier drafts and shall not be used:

| Identifier | Disposition |
|------------|-------------|
| `ocp.config_apply_timeout_ms` | Removed. It sized the controller's wait *after* writing the Assignment, which determines no assigned value. The wait is now a poll of the Configuration State Sensor of Section 11.5. |
| `ocp.power_level_set_granularity_w` | Removed with the `informational` response class. An OAC may expose step size as a PLDM sensor. |
| `ocp.slot_label` | Removed. Human-facing labelling is not configuration. |
| `ocp.initial_power_level` | Superseded by `ocp.initial_power_level_set_w`, which is a wattage rather than an OPL name. |
| `ocp.secure_boot_enforce` | Removed as insufficiently specified for an OCP-defined field. A vendor requiring it shall define it in its own `pen.` namespace. |

---

## 11. Delivery, Validation, and Acceptance

### 11.1 Sequence in Operational State O3

The following sequence shall be followed. Steps 1 through 6 occur entirely within O3.

1. The upstream management controller retrieves the **CID** and determines electrical and mechanical compatibility, including whether the platform can supply the OAC's `opl_emg_w`. **Failure here terminates the sequence**; the Definition is never retrieved and the OAC is not powered.
2. The controller retrieves the **SCD Definition** and resolves each `cid_binding` against the CID it has just evaluated, per Section 11.2.
3. The controller composes the **SCD Assignment**, echoing `definition_revision` from the Definition.
4. The controller writes the Assignment using the `DfOpen` / `DfWrite` / `DfClose` sequence of Section 8.2.
5. The OAC validates the Assignment per Section 11.3 and accepts or rejects it **atomically**.
6. The controller confirms the Assignment is in force, then the baseboard asserts `OAC_PWR_EN`.
7. The configuration **latches** on the O3 to O4 transition. Subsequent power changes use the DSP0248 effecter of Section 12, not a new Assignment.

The admission decision at step 1 is answerable from the CID alone. The controller learns whether it can power the OAC before it has read a single line of configuration; this is the reason the OPL wattages remain in the CID.

> NOTE: The controller confirms at step 6 by reading the Configuration State Sensor of Section 11.5. That sensor reports whether a valid configuration is in force, but not which Assignment produced it; what remains unsettled in this draft is how a controller confirms that the configuration in force is the one it composed. See Annex D.2.

### 11.2 Binding Resolution

#### 11.2.1 General

For each field descriptor carrying a `cid_binding`, the upstream management controller shall resolve the binding against the CID before composing an Assignment. A binding that does not resolve indicates an inconsistency between the two documents; the upstream management controller shall treat the OAC as non-conformant and shall not proceed to step 3.

Bindings shall be resolved by name or by range and never by array position.

#### 11.2.2 Power Bindings

A binding with `"cid_object": "power.primary"` and `"constraint": "opl_range"` shall be resolved by verifying that the field descriptor's declared `min` and `max` match the CID values required for that field by Section 10.2 or Section 10.3.

A power binding shall not carry `cid_connector` or `cid_group_name`; `power.primary` is not contained within a connector.

#### 11.2.3 Protocol Group Bindings

A binding with `"cid_object": "protocol_group"` shall carry both `cid_connector` and `cid_group_name`, and shall be resolved as follows:

1. Locate the connector in the CID whose identifier equals `cid_connector`. The comparison is case-sensitive against the CID's canonical form, e.g. `"CONN0"`.
2. Within that connector's protocol groups, locate the group whose `name` equals `cid_group_name`.
3. If either lookup fails, the binding does not resolve.

Resolving either half alone is not sufficient. The pair is the key.

**Group names are unique within a connector and are not required to be unique across the CID document.** Two connectors may each declare a group named `pcie_primary`, and this shall be accepted. A validator that enforces document-wide uniqueness is over-implementing and will reject conformant CIDs; this is the more likely failure mode of the two, and implementors are directed to test it explicitly.

Two groups sharing a name *within one connector* make the pair ambiguous and shall be rejected.

#### 11.2.4 Subdivision Consistency

For each `ocp.link_subdivision.*` field, the upstream management controller shall verify that every declared mode's segments sum to the `total_lanes` of the bound CID group. A mismatch indicates a CID lane-count edit that has silently invalidated the subdivision menu, and the upstream management controller shall treat the OAC as non-conformant.

### 11.3 OAC-Side Validation

Upon `DfClose`, the OAC shall validate the Assignment in the following order and shall reject the Assignment in whole upon the first failure.

#### 11.3.1 Validation Checks

1. **Well-formedness.** The payload parses as JSON per ECMA-404, the root key is `"oac_scda"`, and both required sections are present.
2. **Schema version.** `metadata.schema_version` is a version the OAC supports.
3. **Definition revision.** `metadata.definition_revision` equals the `definition_revision` of the Definition the OAC is currently publishing. A mismatch means the controller composed against a stale Definition; the OAC rejects, and the controller re-reads the Definition and recomposes. This is the sole mechanism protecting against a stale Definition, and it is sufficient because the OAC increments the revision whenever its Definition content changes, per Section 6.4, so the value a controller echoes identifies exactly the Definition it composed against.
4. **Key validity.** Every key in `assignments` matches a declared field identifier.
5. **No duplicate keys.**
6. **Type conformance.** Every value matches its descriptor's declared type, with no coercion.
7. **Constraint conformance.** Integer values fall within declared `min` and `max`; string values fall within `max_length`; enumeration values match a declared `value` exactly.
8. **Sentinel prohibition.** No assigned value equals a sentinel default.
9. **OAC-specific feasibility.** Any constraint the OAC enforces that the Definition cannot express — for example, a restriction that two particular groups cannot both be subdivided. See Section 11.3.3.

Cross-field validation between `ocp.max_power_w` and `ocp.initial_power_level_set_w` is **not** performed. Those fields clamp per Section 10.3.

#### 11.3.2 Atomicity

The OAC shall apply the Assignment in whole or reject it in whole. An OAC shall not apply a subset of an Assignment and report partial success. Upon rejection the OAC shall remain in its prior SCD state, unchanged.

#### 11.3.3 Constraints the Definition Cannot Express

This specification provides no mechanism for expressing cross-field constraints in the Definition, and `applies_when` is deliberately limited to a single-field equality test.

Nothing becomes unsafe as a result, because OAC-side validation remains the backstop: an illegal combination is refused at step 5 whether or not the Definition could describe it. What is lost is advance discoverability — the controller learns about such a constraint by rejection rather than by construction. Implementations encountering a case they believe requires a richer predicate should raise it with the OCP OAC workstream so that a specific construct can be defined, rather than generalizing `applies_when`.

### 11.4 Rejection Reporting

When an OAC rejects an Assignment it shall report a rejection code and should report the field identifier at which validation failed.

**Table 11.4-1: SCD Assignment Rejection Codes**

| Code | Name | Meaning |
|------|------|---------|
| `0x00` | `ACCEPTED` | Not a rejection. The Assignment was accepted. |
| `0x01` | `MALFORMED_JSON` | Payload did not parse per ECMA-404. |
| `0x02` | `WRONG_ROOT_KEY` | Root key was not `oac_scda`. |
| `0x03` | `MISSING_SECTION` | `metadata` or `assignments` absent. |
| `0x04` | `UNKNOWN_FIELD_ID` | A key in `assignments` matches no declared field. |
| `0x05` | `DUPLICATE_KEY` | A key appeared more than once in `assignments`. |
| `0x06` | `TYPE_MISMATCH` | A value did not match its declared type. |
| `0x07` | `OUT_OF_RANGE` | An integer value fell outside declared `min` / `max`. |
| `0x08` | `LENGTH_EXCEEDED` | A string value exceeded `max_length`. |
| `0x09` | `INVALID_ENUM_VALUE` | An enumeration value matched no declared `value`. |
| `0x0A` | `SENTINEL_ASSIGNED` | An assigned value equalled a sentinel default. |
| `0x0B` | `NULL_VALUE` | A JSON `null` appeared as a value. |
| `0x0C` | `UNSUPPORTED_SCHEMA_VERSION` | `metadata.schema_version` is not supported by the OAC. |
| `0x0D` | `DEFINITION_REVISION_MISMATCH` | `metadata.definition_revision` does not match the Definition currently published. |
| `0x0E` | `SIZE_EXCEEDED` | Payload exceeded the limit of Section 13.2. |
| `0x0F` | `TRANSFER_INCOMPLETE` | `DfClose` was received before the declared payload length was transferred. |
| `0x10` | `CONSTRAINT_CONFLICT` | An OAC-enforced constraint not expressible in the Definition was violated. |
| `0x11` | `ALREADY_LATCHED_DIFFERENT` | The OAC is latched and the submitted Assignment differs from the one in force. See Section 11.6. |
| `0x12` | `INTERNAL_ERROR` | The OAC could not apply a valid Assignment for an implementation-specific reason. |
| `0x13` – `0x7F` | Reserved | Reserved for future use by this specification. |
| `0x80` – `0xFF` | Vendor-specific | Available for OAC-vendor-defined rejection reasons. An upstream management controller shall treat an unrecognized vendor code as a generic rejection. |

### 11.5 SCD Configuration State Reporting

An OAC shall expose its current SCD state as a PLDM state sensor implementing DSP0249 State Set 15 (Configuration State), associated with the SCD Assignment file by the identifiers of Section 8.1. This sensor is the Configuration State Sensor.

State Set 15 defines four states. The OAC shall report them with the following meanings. Where a meaning below narrows or departs from the description DSP0249 gives a state, the meaning below governs for SCD.

The table separates two phases, because a state read during initialization and the same state read at runtime do not carry the same operational consequence. *Initialization* covers Operational State O3, from management controller readiness until the Assignment latches on the O3 to O4 transition per Section 3.17. *Runtime* covers O4 onward, once the configuration is latched and the OAC is operating on it.

**Table 11.5-1: State Set 15 Applied to SCD**

| State | Name | During initialization (O3, before latch) | At runtime (O4 onward) |
|-------|------|------------------------------------------|------------------------|
| 1 | Valid Configuration | An Assignment has been written, validated, and accepted, and every field the Definition marked `required` carried an assigned value. The OAC is ready to latch. The state is reported from acceptance onward, before the latch of Section 3.17 has occurred. | The accepted Assignment is latched and in force, and every `required` field is carrying an assigned value. This is one of the two states an OAC reporting `latched` in Section 11.6.5 may hold; state 4 is the other. |
| 2 | Invalid Configuration | An Assignment was written and rejected under Section 11.3. The characteristic case is a document that was *well formed* — it parsed as JSON per Section 8.3, and its structure conformed to Section 9 — but that carried one or more values which are not valid against the Definition: out of range, of the wrong type, naming an unknown field identifier, echoing a superseded `definition_revision`, or failing a binding check of Section 11.2. The formatting was acceptable; the content was not. A malformed document is likewise rejected and likewise reported here. The OAC has applied nothing and remains on its declared defaults. The rejection code of Section 11.4 identifies the cause; this sensor only reports that there was one. | The same, for an Assignment written to a running OAC. An OAC that already holds an accepted configuration shall **not** move to state 2 on a rejection: it shall continue to report state 1 or state 4 as applicable, because rejection is atomic and leaves the configuration in force untouched per Section 11.3.2. State 2 at runtime therefore means a rejection occurred with no accepted configuration behind it. |
| 3 | Not Configured | **The default state.** An OAC shall report state 3 from management controller reset onward and shall continue to report it until an Assignment has been accepted or rejected. No Assignment has been received, the OAC is operating on the declared defaults of its own Definition, and it is waiting to be configured. This is the `unassigned` state of Section 11.6.5. | No Assignment is in force and none has been rejected since the last event requiring re-negotiation per Section 11.6.2 — the OAC was re-armed and has not yet been given an Assignment. A controller finding state 3 at runtime shall re-negotiate per Section 11.6. |
| 4 | Missing Configuration | An Assignment has been written and accepted, but one or more fields the Definition marked `required` were absent from it and fell back to their declared defaults. The OAC is ready to latch; it is not going to latch the configuration it asked for. | The accepted Assignment is latched and in force, and at least one `required` field is running on a declared default rather than an assigned value. The OAC is configured; it is not fully configured. |

An OAC shall report state 3 as its power-on and post-reset state. An OAC shall not report state 1, 2, or 4 before the first Assignment of the current configuration cycle has been written, because each of those three asserts something about an Assignment that has been received.

State 4 is the reportable consequence of `required` being advisory. Section 7 permits a controller to omit a `required` field, and Section 11.3 requires the OAC to accept the Assignment when it does, because a field the controller cannot determine must not prevent the OAC from powering on. Distinguishing states 1 and 4 lets an operator find, across a fleet, the OACs that were configured but not fully configured — a condition that is otherwise invisible and that no rejection code reports, since nothing was rejected.

Exposing state as a readable level rather than leaving it to be inferred makes the controller's algorithm stateless and level-triggered: read the sensor; if state 1, do nothing; if state 4, decide whether the defaulted fields are acceptable; if state 2 or 3, negotiate. The phase columns of Table 11.5-1 do not change that algorithm, only what the controller should conclude from the answer. This is strictly better than inferring from an `OAC_MC_RDY` edge or a boot counter, because a level can be polled at any time and an edge can be missed — and after an uncommanded management controller reset, the controller has no way of knowing an edge occurred.

The upstream management controller shall confirm at step 6 of Section 11.1 that the Assignment is in force by reading the Configuration State Sensor, and shall not infer that from a signal edge or a boot counter. The upstream management controller shall treat state 4 as configured rather than as a failure, and shall determine whether the defaulted `required` fields are acceptable before proceeding.

The sensor reports the condition of the configuration, not its identity. It does not tell a controller *which* Assignment produced the state it reads, so a controller that finds state 1 on an OAC it has not itself negotiated with — after a controller failover, for instance — learns that some valid configuration is in force but not that it is the one that controller would have composed. See Annex D.2.

### 11.6 Latching, Re-application, and Re-negotiation

#### 11.6.1 Vocabulary

Two distinct operations shall not be conflated:

- **Re-apply** — the OAC pushes its retained Assignment back into hardware. No upstream involvement, no Assignment transfer, invisible to the platform.
- **Re-negotiate** — the OAC has no retained Assignment, so the upstream management controller shall retrieve the Definition and write a fresh Assignment.

#### 11.6.2 When Re-negotiation Is Required

An OAC shall return to the `unassigned` state, requiring re-negotiation, only when **both** of the following have occurred:

1. Primary power has been removed, **and**
2. The OAC's management controller has been reset.

Either event alone is survivable and shall not force re-negotiation.

**Table 11.6-1: Assignment Survival**

| | MC not reset | MC reset |
|---|---|---|
| **Primary power retained** | Nothing happens; hardware stays configured | Hardware is still configured. The MC restores its view from the primary-domain latch. Re-apply nothing, re-negotiate nothing |
| **Primary power removed** | Latch is gone, but the MC still holds its copy on aux power. MC re-applies on next power-up | Both copies gone. **Re-negotiate** |

#### 11.6.3 Recommended Storage Topology

The conjunction in Section 11.6.2 is best satisfied by holding the Assignment in two places, in two different survival domains, rather than by enforcing an explicit rule.

**Table 11.6-2: Cache Copies and Required Survival Behavior**

| Copy | Domain | Survives primary power loss | Survives MC reset |
|------|--------|:---:|:---:|
| MC working copy | MC volatile RAM, aux-powered | Yes | **No — and this is required** |
| Shadow record | Primary power domain (e.g. CPLD/FPGA register file) | **No — and this is required** | Yes |

Each copy shall fail in exactly one of the two cases. Making either copy more durable than the table specifies breaks the rule.

The management controller already runs on aux power — it is alive in O3, before `OAC_PWR_EN` — so its copy survives a primary power cycle. A small latch in the primary power domain survives a management controller reset. The Assignment therefore survives if either domain survives and is lost only when both go.

A vendor that keeps SCD state only in management controller RAM cannot satisfy Section 11.6.2 at all. A vendor that keeps it only in the primary domain silently violates it on every management controller reset.

#### 11.6.4 Prohibition on Non-Volatile Retention

**The SCD cache shall not be stored in non-volatile memory.**

Persisting the Assignment to flash or EEPROM resembles robustness but prevents the OAC from ever re-arming — including when the OAC is removed and installed in a different chassis, where it would come up carrying the previous platform's slot identifier, subdivision, and *initial power level*, while reporting itself as `latched` so the new controller leaves it alone. A stale power level admitted into a platform that never budgeted for it is a safety-relevant failure.

Note further that management controller internal SRAM is generally not cleared by a warm reset; contents survive unless firmware acts. "Lost on management controller reset" is therefore a firmware obligation, not a property obtained for free.

+12V Aux is the outer bound on the lifetime of SCD state. The management controller's working copy lives in aux-powered volatile memory, and the shadow record lives in the primary power domain, which cannot be energized while aux is absent. Removing +12V Aux therefore destroys both copies, and the OAC shall come up `unassigned` and be re-negotiated. An OAC shall not retain SCD state across removal of +12V Aux by any means. This is the same prohibition as the one above, stated as a lifetime rather than as a storage class, and it is the property a controller may rely on: an OAC that has lost aux power has lost its Assignment.

#### 11.6.5 Management Controller Boot Algorithm

On any management controller reset, including power-on, the OAC's management controller shall:

1. Invalidate its own SCD cache, unconditionally, early in boot and before any consumer can read it, regardless of reset cause.
2. Read the primary-domain shadow record.
3. If the shadow record is valid, adopt its values as current, repopulate the management controller cache from it, and report `latched`. It shall **not** apply declared defaults and shall **not** re-arm.
4. If the shadow record is invalid, report `unassigned` and wait for an Assignment.

Step 3 is the single place implementations are most likely to err, because a freshly booted management controller looks exactly like a freshly inserted one from the inside.

On primary power removal while the management controller stays up, the shadow record is lost with its domain, the management controller cache is not, and the management controller re-applies from its cache and rewrites the shadow record on the next power-up.

#### 11.6.6 What Is Cached

The cached item shall not be the Assignment document. Two items are needed after acceptance, and neither is the JSON:

| Cached item | Purpose |
|-------------|---------|
| The **decoded record** — assigned values flattened into a fixed-layout binary structure | Re-application becomes a copy and a sequence of register writes. No JSON parser in the power-up path, and deterministic timing |
| The `definition_revision` the Assignment echoed, and whether any `required` field was defaulted | Feeds the Configuration State Sensor of Section 11.5, which distinguishes state 1 from state 4 on that basis |

The OAC shall retain the echoed `definition_revision` and whether any `required` field was defaulted, because the Configuration State Sensor of Section 11.5 cannot distinguish state 1 from state 4 without the latter and cannot survive a management controller reset without the former. The form the decoded record takes is an implementation matter; a fixed-layout binary structure is recommended.

The raw Assignment is needed only during validation and shall be discarded at `DfClose`. Keeping a parser off the re-application path matters: a power-up is the worst possible moment to discover that a document which parsed an hour ago no longer does.

#### 11.6.7 Writing While Latched

An OAC should accept an Assignment written while it is latched, and shall in that case either:

- accept it as a no-op if it is byte-identical in canonical form to the Assignment in force, or
- reject it with code `0x11` if it differs.

This gives the controller a safe recovery action when it is unsure of the OAC's state, without opening a path to reconfiguring a running OAC.

> NOTE: The definition of "primary power removed" against the O-state machine is not settled in this draft — specifically whether `OAC_PWR_EN` deassertion, which is a normal O4 to O3 transition, qualifies, or only full loss of the primary rail. See Annex D.1. Re-insertion is unambiguous either way, since both domains lose power.

---

## 12. Runtime Power Control

SCD is one-time configuration per negotiation. Everything dynamic goes through the PLDM effecter path, which already has clamping and reporting semantics defined in DSP0248.

An OAC shall expose a DSP0248 numeric effecter permitting the upstream management controller to move the OPL-SET level at runtime. The effecter shall be bounded below by the CID `power.primary.opl_set_min_w` and above by:

```
min( ocp.max_power_w, CID power.primary.opl_max_w )
```

`ocp.initial_power_level_set_w` sets the value the effecter holds at the point the OAC enters O5. It is not a separate control path.

An OAC shall not permit the effecter to raise the applied cap above `ocp.max_power_w`. The platform's declared budget binds the runtime path exactly as it binds the initial configuration.

> NOTE: A platform may legitimately budget an OAC below its own `opl_eff_w` — an `ocp.max_power_w` of 1000 W against an `opl_eff_w` of 2000 W is a valid, deliberate choice. Whether the OAC shall report that it is operating in a degraded band is open; see Annex D.3.

---

## 13. Size Limits

### 13.1 SCD Definition

The maximum transferred size of an SCD Definition payload shall be **32 KiB**, measured as transferred. The OAC shall minify the Definition per Section 6.2 and shall measure the limit on the minified byte sequence. A Definition exceeding the limit is non-conformant, and the OAC shall set `FileMaximumSize` no greater than it per Section 6.3.

> NOTE: For calibration, a five-field Definition of the kind shown in Annex A occupies approximately 2.2 KB minified, or roughly 440 bytes per field, most of which is prose `description` text. A Definition of purely machine-readable content runs well under 200 bytes per field. The 32 KiB limit therefore accommodates on the order of seventy-five verbose fields, and several times that for a Definition whose field descriptors carry no prose.

### 13.2 SCD Assignment

The maximum transferred size of an SCD Assignment payload shall be **8 KiB**.

Assignments are sparse and consist of scalar values keyed by identifier; a typical Assignment is a few hundred bytes, so the limit is not a practical constraint.

---

## 14. Compliance

### 14.1 OAC Requirements

**Table 14.1-1: OAC Compliance Requirements**

| Requirement | Classification | Reference |
|-------------|----------------|-----------|
| Publish an SCD Definition as a FRU file retrievable per DSP0257 | Mandatory | 6.1 |
| Expose the Definition as a FRU Data File per DSP0257 and support no alternative access path | Mandatory | 6.1 |
| Store the Definition in persistent, non-volatile storage | Recommended | 6.1 |
| Return identical Definition content for a given `definition_revision` | Mandatory | 6.1 |
| Describe the Definition with a File Descriptor PDR carrying `EntityType` Device File, `FileClassification` `FRUDataFile`, and `FileName` `OAC_SCDD.json` | Mandatory | 6.3 |
| Provide a Device File State sensor PDR for the Definition | Mandatory (DSP0242, Fixed Length File) | 6.3 |
| Provide a File Size Monitoring sensor PDR for the Definition | Mandatory (this specification; DSP0242 recommends) | 6.3 |
| Associate every SCD sensor PDR with its file by `EntityType`, `EntityInstanceNumber`, and `ContainerID` | Mandatory | 6.3, 8.1 |
| Declare the Definition as a DSP0242 Fixed Length File and set `FileMaximumSize` to its exact transferred size | Mandatory | 6.3 |
| Not report State Set 68 state 3 (File is at Maximum Size) on the Definition | Mandatory | 6.3 |
| Reject writes to the SCD Definition | Mandatory | 6.1 |
| Encode both documents as UTF-8 JSON per ECMA-404 with no BOM and no comments | Mandatory | 6.2, 8.3 |
| Publish the Definition in minified format | Mandatory | 6.2 |
| Increment `definition_revision` whenever Definition content changes | Mandatory | 6.4 |
| Declare a `default` on every field descriptor | Mandatory | 7.6 |
| Declare `sentinel_default` on, and only on, defaults lying outside the declared range | Mandatory | 7.6 |
| Use only `ocp.` and `pen.<PEN>.` field identifier prefixes | Mandatory | 7.4 |
| Use OCP-registry identifiers with registry semantics where the function applies | Mandatory | 10 |
| Carry `cid_connector` and `cid_group_name` on every `protocol_group` binding | Mandatory | 7.8 |
| Omit `cid_connector` and `cid_group_name` from `power.primary` bindings | Mandatory | 7.8 |
| Accept an Assignment via a DSP0242 `DfOpen` / `DfWrite` / `DfClose` sequence | Mandatory | 8.2 |
| Take the Assignment to be exactly the bytes written in one write session, disregarding residual file content | Mandatory | 8.2 |
| Describe the Assignment with a File Descriptor PDR carrying `EntityType` Device File, `FileClassification` `OtherFile`, and `FileName` `OAC_SCDA.json` | Mandatory | 8.1 |
| Provide File Size Monitoring and Device File State sensor PDRs for the Assignment | Mandatory (DSP0242, Regular File) | 8.1 |
| Provide a Configuration State sensor PDR for the Assignment | Mandatory (this specification) | 8.1, 11.5 |
| Declare the Assignment as a DSP0242 Regular File | Mandatory | 8.1 |
| Set `SuperiorDirectoryFileIdentifier` to `0xFFFF` on both File Descriptor PDRs, absent a directory | Mandatory | 6.3 |
| Set `FileMaximumSize` no greater than the applicable Section 13 limit on each File Descriptor PDR | Mandatory | 6.3, 8.1 |
| Defer validation until `DfClose` | Mandatory | 8.2 |
| Accept or reject an Assignment atomically | Mandatory | 11.3.2 |
| Accept a sparse Assignment, applying declared defaults for absent fields | Mandatory | 9.4 |
| Not reject an Assignment solely because a `required` field is absent | Mandatory | 7.7 |
| Reject an Assignment whose `definition_revision` does not match | Mandatory | 11.3.1 |
| Reject an Assignment containing a duplicate key | Mandatory | 9.5 |
| Reject an Assignment assigning a sentinel value | Mandatory | 11.3.1 |
| Report a rejection code per Table 11.4-1 | Mandatory | 11.4 |
| Report the field identifier at which validation failed | Recommended | 11.4 |
| Clamp rather than reject when the assigned initial power level exceeds the platform budget | Mandatory | 10.3 |
| Expose a DSP0248 numeric effecter for runtime OPL-SET control | Mandatory | 12 |
| Bound that effecter above by `min(ocp.max_power_w, opl_max_w)` | Mandatory | 12 |
| Latch the Assignment on the O3 to O4 transition | Mandatory | 11.1 |
| Require re-negotiation only when primary power was removed **and** the MC was reset | Mandatory | 11.6.2 |
| Hold the cache in two survival domains per Table 11.6-2 | Recommended | 11.6.3 |
| Not store the SCD cache in non-volatile memory | Mandatory | 11.6.4 |
| Not retain SCD state across removal of +12V Aux by any means | Mandatory | 8.1, 11.6.4 |
| Invalidate the MC cache unconditionally early in MC boot | Mandatory | 11.6.5 |
| Adopt a valid shadow record without applying defaults and without re-arming | Mandatory | 11.6.5 |
| Discard the raw Assignment at `DfClose` and cache the echoed `definition_revision` and whether any `required` field was defaulted | Mandatory | 11.6.6 |
| Cache a decoded fixed-layout record rather than the Assignment JSON | Recommended | 11.6.6 |
| Implement the Configuration State Sensor as DSP0249 State Set 15 and report the four states per Table 11.5-1 | Mandatory | 11.5 |
| Report State Set 15 state 4 when an accepted Assignment defaulted a `required` field | Mandatory | 11.5 |
| Report only the State Set 68 states this specification declares reachable for each file | Mandatory | 6.3, 8.1 |
| Carry one `ContainerID` across every File Descriptor PDR and associated sensor PDR of the OAC | Mandatory | 6.3, 8.1 |
| Accept a byte-identical Assignment while latched as a no-op | Recommended | 11.6.7 |
| Keep the Definition within 32 KiB as transferred | Mandatory | 13.1 |
| Retain no state from an aborted transfer | Mandatory | 8.2 |

### 14.2 Upstream Management Controller Requirements

**Table 14.2-1: Upstream Management Controller Compliance Requirements**

| Requirement | Classification | Reference |
|-------------|----------------|-----------|
| Retrieve and evaluate the CID before retrieving the Definition | Mandatory | 11.1 |
| Terminate the sequence without powering the OAC if CID evaluation fails | Mandatory | 11.1 |
| Retrieve the SCD Definition via DSP0257 | Mandatory | 6.1 |
| Locate each SCD file by its `FileName`, not by PDR order | Mandatory | 6.3, 8.1 |
| Open each SCD file using the `FileIdentifier` from its File Descriptor PDR, not the name string | Mandatory | 6.3, 8.1 |
| Read the Definition size from its File Size Monitoring Sensor rather than assuming it | Mandatory | 6.3 |
| Parse minified format JSON | Mandatory | 6.2 |
| Tolerate expanded format JSON | Recommended | 6.2 |
| Reject a Definition containing an unrecognized field identifier prefix | Mandatory | 7.4 |
| Resolve every `cid_binding` by name or range, never by array position | Mandatory | 11.2 |
| Resolve a `protocol_group` binding using the `(cid_connector, cid_group_name)` pair | Mandatory | 11.2.3 |
| **Accept protocol group names reused across different connectors** | Mandatory | 11.2.3 |
| Reject a CID in which two groups within one connector share a name | Mandatory | 11.2.3 |
| Verify subdivision segment sums against the bound group's `total_lanes` | Mandatory | 11.2.4 |
| Echo `definition_revision` into the Assignment | Mandatory | 9.2 |
| Omit unrecognized fields from the Assignment rather than failing | Mandatory | 7.7 |
| Not assign a sentinel value | Mandatory | 7.6 |
| Transfer the Assignment in minified format | Mandatory | 8.3 |
| Deliver the Assignment in O3, before `OAC_PWR_EN` assertion | Mandatory | 8.4 |
| Confirm the Assignment is in force before `OAC_PWR_EN` is asserted | Mandatory | 11.1 |
| Re-read the Definition and recompose upon a `DEFINITION_REVISION_MISMATCH` rejection | Mandatory | 11.3.1 |
| Treat an unrecognized vendor rejection code as a generic rejection | Mandatory | 11.4 |
| Not infer Assignment acceptance from a File Size Monitoring Sensor or Device File State Sensor reading | Mandatory | 8.1 |
| Treat `metadata.definition_revision`, not the Device File State Sensor, as the authoritative staleness check | Mandatory | 6.3 |
| Keep the Assignment within 8 KiB as transferred | Mandatory | 13.2 |
| Confirm at step 6 by reading the Configuration State Sensor rather than inferring state from signal edges | Mandatory | 11.1, 11.5 |
| Treat State Set 15 state 4 as configured, not as a failure, and decide whether the defaulted `required` fields are acceptable | Mandatory | 11.5 |
| Re-negotiate on finding State Set 15 state 3 at runtime | Mandatory | 11.5, 11.6 |

> NOTE: The emphasized requirement in Table 14.2-1 — accepting group names reused across connectors — is called out because the expected implementation error under per-connector scoping is over-enforcement, not under-enforcement. A validator carried forward from a document-wide-uniqueness draft will reject conformant CIDs. Implementors are directed to include a negative test covering it.

---

## Annex A (informative) -- Paired CID, Definition, and Assignment Example

This annex shows one OAC's three documents together. The CID fragment is abridged to the parts the SCD documents bind to.

### A.1 CID Fragment

```json
{
  "oac_cid": {
    "power": {
      "primary": {
        "input_voltage": "+50V",
        "connector_type": "125A",
        "opl_max_w": 2500,
        "opl_eff_w": 2000,
        "opl_red_w": 1200,
        "opl_emg_w": 625,
        "opl_set_min_w": 625
      }
    },
    "connectors": [
      {
        "id": "CONN0",
        "populated": true,
        "high_speed_lanes": [
          {
            "name": "pcie_primary",
            "protocol": "PCIe Gen6",
            "link_direction": "INBOUND",
            "total_lanes": 16
          },
          {
            "name": "eth_sideband",
            "protocol": "Ethernet 200G",
            "link_direction": "OUTBOUND",
            "total_lanes": 8
          }
        ]
      }
    ]
  }
}
```

Two details of this fragment are what the binding rules of Section 11.2 rely on: each protocol group carries a `name`, and no `link_subdivision` array is present, the subdivision menu having been declared by the Definition instead. Both are CID v0.8 features; a pre-v0.8 CID cannot satisfy a `protocol_group` binding.

### A.2 SCD Definition

```json
{
  "oac_scdd": {
    "metadata": {
      "schema_version": "0.9",
      "oac_spec_revision": "0.9",
      "definition_revision": 1,
      "description": "Example SCD Definition for a PCIe Gen6 x16 OAC.",
      "iana_pen": 32473
    },
    "fields": [
      {
        "id": "ocp.slot_id",
        "display_name": "Slot Identifier",
        "description": "Logical slot identifier of the position this OAC occupies.",
        "type": "integer",
        "response": "required",
        "default": 255,
        "sentinel_default": true,
        "min": 0,
        "max": 15
      },
      {
        "id": "ocp.max_power_w",
        "display_name": "Platform Power Budget",
        "description": "Sustained power the platform can supply to this slot.",
        "type": "integer",
        "response": "required",
        "default": 625,
        "units": "watts",
        "min": 625,
        "max": 2500,
        "cid_binding": {
          "cid_object": "power.primary",
          "constraint": "opl_range"
        }
      },
      {
        "id": "ocp.initial_power_level_set_w",
        "display_name": "Initial OPL-SET Wattage",
        "description": "Power cap applied when the OAC enters O5.",
        "type": "integer",
        "response": "optional",
        "default": 1200,
        "units": "watts",
        "min": 625,
        "max": 2500,
        "cid_binding": {
          "cid_object": "power.primary",
          "constraint": "opl_range"
        }
      },
      {
        "id": "ocp.link_subdivision.conn0.pcie_primary",
        "display_name": "Link Subdivision, CONN0 Primary PCIe Group",
        "description": "Partitioning of the primary PCIe group into independent links.",
        "type": "enumeration",
        "response": "required",
        "default": "x16",
        "cid_binding": {
          "cid_object": "protocol_group",
          "cid_connector": "CONN0",
          "cid_group_name": "pcie_primary"
        },
        "values": [
          { "value": "x16", "description": "Single x16 link, lanes 0-15" },
          { "value": "x8x8", "description": "Two x8 links, lanes 0-7 and 8-15" },
          { "value": "x4x4x4x4", "description": "Four x4 links, lanes 0-3, 4-7, 8-11, 12-15" }
        ]
      },
      {
        "id": "pen.32473.boot_source",
        "display_name": "OAC Boot Source",
        "description": "Where the OAC loads its operational firmware image from.",
        "type": "enumeration",
        "response": "required",
        "default": "local_flash",
        "values": [
          { "value": "local_flash", "description": "Boot from flash on the OAC" },
          { "value": "stream", "description": "Boot from an image streamed by the platform" }
        ]
      }
    ]
  }
}
```

### A.3 SCD Assignment

```json
{
  "oac_scda": {
    "metadata": {
      "schema_version": "0.9",
      "definition_revision": 1,
      "description": "Sets slot, budget, and subdivision. Omits the remaining two fields because their declared defaults are correct for this platform."
    },
    "assignments": {
      "ocp.slot_id": 5,
      "ocp.max_power_w": 2000,
      "ocp.link_subdivision.conn0.pcie_primary": "x8x8"
    }
  }
}
```

### A.4 Reading the Example

| Field | Class | Assigned | Rationale |
|-------|-------|----------|-----------|
| `ocp.slot_id` | required | `5` | Set here because the default is the sentinel, which is not a usable slot number |
| `ocp.max_power_w` | required | `2000` | The platform budgets 2000 W to this slot, below the OAC's 2500 W `opl_max_w` |
| `ocp.link_subdivision.conn0.pcie_primary` | required | `x8x8` | Differs from the `x16` default |
| `ocp.initial_power_level_set_w` | optional | omitted | The declared 1200 W default suits this platform |
| `pen.32473.boot_source` | required | omitted | The declared `local_flash` default suits this platform |

The two omissions are the more instructive half. `pen.32473.boot_source` is marked `required`, yet a controller that has never heard of PEN 32473 skips it and the OAC boots from local flash exactly as intended. An unrecognized field self-handles — which works only because `required` is advisory *and* every field carries a default.

The power fields demonstrate the clamp of Section 10.3. The OAC is rated to 2500 W by its CID, the platform declares a 2000 W budget, and the initial OPL-SET wattage falls back to its 1200 W default; the applied cap is the lowest of the three. Had the controller assigned 2400 W to `ocp.initial_power_level_set_w`, the OAC would clamp to 2000 W rather than reject.

Note what the declared defaults produce if the controller omits everything: slot unknown, 625 W budget, x16 link, local flash. The OAC comes up heavily throttled and unmistakably under-configured, which is the direction a default should fail in.

---

## Annex B (informative) -- Composing an Assignment from a Definition

The algorithm by which a controller chooses values is implementation-defined. The following is offered as a reference shape.

1. Retrieve and evaluate the CID. If the platform cannot supply `opl_emg_w`, stop; do not power the OAC.
2. Retrieve the Definition.
3. For each field descriptor:
   a. If a `cid_binding` is present, resolve it per Section 11.2. If it does not resolve, treat the OAC as non-conformant and stop.
   b. If `applies_when` is present and its predicate is not satisfied by the value the controller intends to assign to the governing field, skip the field.
   c. If the controller recognizes the field identifier and has a platform-specific value for it, record the value.
   d. Otherwise skip the field. Skipping is always safe: the OAC applies the declared default.
4. Verify every recorded value against its descriptor's type and constraints before transmission. Catching a violation locally is cheaper than a round-trip rejection.
5. Verify that no recorded value equals a sentinel default.
6. Emit the Assignment with `definition_revision` echoed from the Definition.
7. Minify and transfer.

Two practical notes. First, a controller should never fail composition because it does not recognize a field; step 3d is the whole mechanism by which vendor fields coexist with generic controllers. Second, a controller holding a cached Definition from a previous boot should re-read it rather than assume it is current — an OAC firmware update changes `definition_revision`, and composing against the stale copy costs a rejection round-trip.

---

## Annex C (informative) -- PLDM Protocol Field Value Reference

This annex collects the PLDM field values this specification constrains. It lists only those fields; every other field of each record is governed by the referenced DMTF specification and is an implementation matter. Byte offsets and field widths are not reproduced here — see DSP0248 for the File Descriptor PDR and the sensor PDR formats, DSP0242 for the file sensor requirements and the transfer commands, DSP0249 for entity type codes, State Set 68, and State Set 15, and DSP0257 for FRU Data File structure.

### C.1 SCD Definition

**Table C-1: PLDM FRU Record Fields for the SCD Definition**

| Field | Value |
|-------|-------|
| FRU Record Type | OEM (per DSP0257) |
| Access context | FRU Data File, per DSP0257 |
| Storage | Persistent, non-volatile storage recommended; on-demand generation permitted |
| Access | Read-only |
| File characteristic | Fixed Length File, per DSP0242 |

**Table C-2: SCD Definition File Descriptor PDR**

| Field | Value | Note |
|-------|-------|------|
| `EntityType` | 9 (Device File) | |
| `FileClassification` | `FRUDataFile` | The file content is FRU data per DSP0257. |
| `FileName` | `OAC_SCDD.json` (`strASCII`) | The discriminator a controller matches on. Not PDR order. |
| `FileIdentifier` | Implementation-chosen `uint16` | What `DfOpen` takes. A controller matches `FileName`, then opens with this. |
| `FileCapabilities` | `FcWritesPermitted` = 0, `ExWriteOpen` = 0, `DataType` = 0 | Wrap-versus-truncate behaviour is moot for a file the controller cannot write. `DataType` = 0 declares a regular file rather than a streaming FIFO. See Annex D.6 on the remaining bits. |
| `FileMaximumSize` | The exact transferred size of the Definition, not greater than the Section 13.1 limit | For a fixed-length file DSP0242 equates file size to this field, so it is exact rather than an upper bound. |
| `SuperiorDirectoryFileIdentifier` | `0xFFFF` | The SCD files are a flat set; no directory is required. |
| `ContainerID` | Implementation-chosen, one value per OAC | The same value appears on every record in this annex, the Assignment's included. It identifies the OAC. |
| `EntityInstanceNumber` | Implementation-chosen, distinct from the Assignment's | This is what separates the two files at the entity level. Both sensor PDRs below repeat it, per Section 6.3. |

**Table C-3: SCD Definition File Size Monitoring Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | Compact or Numeric sensor (DSP0242 File Size Monitoring Sensor) | |
| `EntityType` | 9 (Device File) | Matches Table C-2. |
| `EntityInstanceNumber`, `ContainerID` | As in Table C-2 | This match is what associates the sensor with the file. |
| Reading | Current Definition size in bytes, as transferred | The minified byte count. Changes when firmware changes the Definition. |
| Units | `BaseUnit` Bytes, `UnitModifier` 0 | Per DSP0242. Numeric: `RateUnit` None, `Offset` 0, `Resolution` 1.00. Compact: `OccurrenceRate` No Occurrence Rate. |
| Thresholds | Should not be set | DSP0242 advises against thresholds on a fixed-length file. |
| Requirement | Shall, per this specification | DSP0242 makes it a *should* for a Fixed Length File; Section 6.3 tightens it and gives the reason. |

**Table C-4: SCD Definition Device File State Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | State sensor | |
| State set | 68 (Device File), per DSP0249 | |
| `EntityType` | 9 (Device File) | Matches Table C-2. |
| `EntityInstanceNumber`, `ContainerID` | As in Table C-2 | |
| States reported | 1 (File has Not Changed), 2 (File is Updated) | Per Table 6.3-1. State 3 is not supported, as DSP0242 advises for a fixed-length file. States 4 and 5 are not applicable to a file published whole and never appended to. |
| Requirement | Shall, per DSP0242 | Mandatory for a Fixed Length File. |
| Interpretation | File state, including modification signalling | Not configuration state; see Section 6.3. |

### C.2 SCD Assignment

**Table C-5: PLDM File Fields for the SCD Assignment**

| Field | Value |
|-------|-------|
| Identified by | `FileName` `OAC_SCDA.json`; opened by the `FileIdentifier` in the same PDR |
| Direction of use | Written by the upstream management controller; not read back |
| File characteristic | Regular File, per DSP0242 |
| Transfer commands | `DfOpen` (write access, `DfOpenExclusive` = *Exclusive*), one or more `DfWrite`, `DfClose` (`ZeroLength` = 0) |
| Document extent | Exactly the bytes written between `DfOpen` and `DfClose`; residual file content is disregarded |
| Storage | Volatile only; lifetime bounded by +12V Aux per Sections 8.1 and 11.6.4 |

**Table C-6: SCD Assignment File Descriptor PDR**

| Field | Value | Note |
|-------|-------|------|
| `EntityType` | 9 (Device File) | |
| `FileClassification` | `OtherFile` | The Assignment is not FRU data. |
| `FileName` | `OAC_SCDA.json` (`strASCII`) | The name a controller matches on to locate the file it writes. Not PDR order. |
| `FileIdentifier` | Implementation-chosen `uint16`, distinct from the Definition's | What `DfOpen` takes. |
| `FileCapabilities` | `FcWritesPermitted` = 1, `ExWriteOpen` = 1, `ExReadOpen` = 0, `FileModify` = 1, `DataType` = 0, `Read Pushed` = 1 | Names are the DSP0248 ones. `DataType` = 0 with `Read Pushed` = 1 and `ExWriteOpen` = 1 is the combination that obliges the OAC to support `DfWrite`. `FileModify` = 1 because a re-negotiated Assignment is written at offset zero rather than appended. Describes what the transfer mechanism permits; it does not oblige the OAC to serve an accepted Assignment back; see Section 8.1. See Annex D.6 on the remaining bits. |
| `FileMaximumSize` | Not greater than the Section 13.2 limit | A genuine upper bound here, unlike the Definition's: a sparse Assignment varies in length. |
| `SuperiorDirectoryFileIdentifier` | `0xFFFF` | Flat set, as for the Definition. |
| `ContainerID` | As in Table C-2 | One value per OAC, shared with the Definition's records. |
| `EntityInstanceNumber` | Implementation-chosen, distinct from the Definition's | All three sensor PDRs below repeat it, per Section 8.1. |

**Table C-7: SCD Assignment File Size Monitoring Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | Compact or Numeric sensor (DSP0242 File Size Monitoring Sensor) | |
| `EntityType` | 9 (Device File) | Matches Table C-6. |
| `EntityInstanceNumber`, `ContainerID` | As in Table C-6 | |
| Reading | Size in bytes of the most recent Assignment transfer | Not a statement about what the OAC retains; see Section 11.6.6. |
| Units | `BaseUnit` Bytes, `UnitModifier` 0 | As for the Definition's sensor. |
| Thresholds | `FatalHigh` should equal `FileMaximumSize` | DSP0242 recommends this on a Regular File for overflow detection. A controller shall not raise it above `FileMaximumSize`. |
| Requirement | Shall, per DSP0242 | Mandatory for a Regular File. |

**Table C-8: SCD Assignment Device File State Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | State sensor | |
| State set | 68 (Device File), per DSP0249 | |
| `EntityType` | 9 (Device File) | Matches Table C-6. |
| `EntityInstanceNumber`, `ContainerID` | As in Table C-6 | |
| States reported | 1 (File has Not Changed), 2 (File is Updated), optionally 3 (File is at Maximum Size) | Per Table 8.1-1, which prohibits states 4 and 5; an oversize Assignment is rejected, not wrapped or truncated. |
| Requirement | Shall, per DSP0242 | Mandatory for a Regular File. |
| Interpretation | File state, including modification signalling | Acceptance is not a file state; see Section 8.1. |

**Table C-9: SCD Assignment Configuration State Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | State sensor | |
| State set | 15 (Configuration State), per DSP0249 | |
| `EntityType` | 9 (Device File) | Matches Table C-6. |
| `EntityInstanceNumber`, `ContainerID` | As in Table C-6 | |
| States reported | 1 (Valid Configuration), 2 (Invalid Configuration), 3 (Not Configured), 4 (Missing Configuration) | All four are reachable. State 3 is the post-reset default. See Table 11.5-1 for the initialization and runtime meaning of each. |
| Interpretation | Whether a valid Assignment is in force | This is the mechanism that replaces reading the Assignment back. The Definition has no counterpart sensor. |

---

## Annex D (informative) -- Items Open for Workstream Resolution

### D.1 Defining "primary power removed"

Section 11.6.2 requires re-negotiation only when primary power was removed and the management controller was reset. What counts as removal is not yet defined against the O-state machine: `OAC_PWR_EN` deassertion, which is a normal O4 to O3 transition, or only full loss of the primary rail. The two differ in how often re-negotiation occurs in practice. Re-insertion is unambiguous either way.

### D.2 Confirming *which* Assignment is in force

Step 6 of Section 11.1 is now answered by a poll rather than by a timeout: the controller reads the Configuration State Sensor. What the sensor does not answer is identity.

The Configuration State Sensor of Section 11.5 answers the timing question: "has the Assignment been applied yet" is the same poll as "does this OAC need negotiating," and one mechanism covers both, so no fixed timeout constant is needed. What it does not answer is *identity*. State Set 15 carries no reference to the document that produced the state, so a controller reading Valid Configuration on an OAC it did not itself negotiate with — after a failover, or after its own restart — cannot tell whether the configuration in force is the one it would have composed. Earlier drafts closed that gap with an Assignment digest cached at receive time and read back alongside the state; that mechanism was withdrawn in favour of the standard state set. Whether to reintroduce it as an OEM state effecter, an OEM sensor, or a dedicated command, and whether the gap is worth closing at all given that a controller can simply rewrite the Assignment and let Section 11.6.7 absorb the duplicate, is open.

### D.3 Reporting operation below `opl_eff_w`

A platform can legitimately budget an OAC below its efficiency level. Nothing currently surfaces that the OAC is operating in a degraded band rather than at its intended steady state, and an operator auditing a fleet would want to find those OACs. A PLDM sensor reporting the current level relative to the CID menu would cover it and would pair naturally with the Configuration State Sensor of Section 11.5.

### D.4 Connector-level group name override in the CID

If names live in a shared `connector_profile`, every OAC referencing that profile inherits the same group names, so a vendor cannot name a group `pcie_to_cpu0` in one connector and `pcie_to_cpu1` in another while using one profile for both. Whether that warrants an optional connector-level override is a CID-side decision. The SCD binding format is unaffected either way, since it addresses by connector and name regardless of where the name was authored.

### D.5 Field identifiers containing vendor-chosen segments

`ocp.link_subdivision.conn0.pcie_primary` is an OCP-namespaced identifier containing a vendor-chosen segment. The alternative — a bare `ocp.link_subdivision` disambiguated only by `cid_binding` — cannot express two subdividable groups without duplicate identifiers, and identifiers are the Assignment's keys, so they must be unique. The embedded form appears to be the lesser evil, but it is a legitimate subject for review.

### D.6 Bit-level encoding of `FileCapabilities`

Sections 6.3 and 8.1 fix the bits the transfer path depends on — `FcWritesPermitted`, `ExWriteOpen`, `ExReadOpen`, `FileModify`, `DataType`, and `Read Pushed`. `FileTrunc`, `DataVolatility`, `FcZeroLengthPermitted`, and `Read Polled` on the Assignment are not enumerated. DSP0248 Table 108 attaches configuration rules to several of them, notably that at least one of `Read Polled` and `Read Pushed` shall be set, and that `ExReadOpen` shall be permitted wherever `FcZeroLengthPermitted` is. The workstream should settle the full bit pattern for both files and record it in Annex C, and should check the bit names it adopts against the edition of DSP0242 current at the time, since the file transfer and platform monitoring specifications have not always named these bits identically. This specification uses the DSP0248 names throughout.

---

**End of Specification**
