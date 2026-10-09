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

---

## Contents

1. Scope
2. Normative References
3. Terms and Definitions
4. Symbols and Abbreviated Terms
5. SCD Overview
   - 5.1 The Two Artifacts
   - 5.2 Relationship to the CID
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

---

## 1. Scope

This specification defines Slot Configuration Data (SCD), a two-part machine-readable mechanism by which an OAC and its platform negotiate the OAC's slot-specific configuration during initialization.

SCD comprises two JSON documents travelling in opposite directions. The **SCD Definition (SCDD)** is published by the OAC and read by the upstream management controller; it enumerates every configuration field the OAC will accept, together with each field's type, constraints, and declared default. The **SCD Assignment (SCDA)** is composed by the upstream management controller and written to the OAC; it supplies values for those fields the platform wishes to set.

SCD replaces the hardware strapping mechanisms that earlier add-in card form factors used to communicate slot-specific configuration. A strapped interface encodes configuration in a fixed number of discrete inputs whose count and pull network are committed at board layout: its information capacity is bounded by pin count, and the set of representable values is fixed at the same time. Extending it is an electrical change — an additional pin, its termination, a board revision, and re-qualification of the assembly — which is why strapped interfaces in practice carry a small number of coarse, universally applicable values and nothing else. SCD carries that same class of information as a typed, self-describing document whose capacity is bounded by the maximum transferred Definition size of Section 13 rather than by pin count, and whose fields are named rather than positional. Adding an attribute is therefore a schema revision propagated by firmware update rather than by an electrical respin, and the `pen.` namespace of Section 7.4 admits vendor-defined attributes without OCP registration and without risk of collision. SCD is exchanged while the OAC is in Operational State O3 and shall be validated and accepted by the OAC before the baseboard asserts OAC_PWR_EN.

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

Third, **SCD is not the admission decision, but it is on the power enablement path**. Whether the platform can power the OAC at all is settled from the CID, before any SCD exchange begins, and SCD presumes that question has already been answered in the affirmative. What SCD adds is the OAC's own answer. The OAC shall accept an Assignment before the baseboard energizes the primary busbar and asserts `OAC_PWR_EN`, and an OAC that rejects the configuration it is offered does not proceed to be powered. The CID settles whether the platform and the OAC are electrically and mechanically compatible; SCD settles whether the OAC consents to the slot conditions it has been given. Both shall succeed. Section 5.2 relates the two documents.

### 5.2 Relationship to the CID

The OCP Open Adapter Card Base Specification states the relationship between the two documents directly:

> SCD serves a purpose complementary to the Connector Interface Definition (CID). CID describes the characteristics, requirements, and capabilities of the OAC to the platform, whereas SCD describes the platform environment and operational configuration provided to the OAC.

The two are therefore not two halves of one schema. They have different subjects. The CID's subject is the OAC: the connectors it populates, the protocol groups and lane counts it presents, its reference clocking and discrete signals, and the Operational Power Levels it is built to run at. A platform reads the CID to learn what it has been handed. SCD's subject is the slot: what this chassis, in this position, with this cooling capability and this concurrent OAC population, is able to provide, and how the OAC is to be set up within it. An OAC reads SCD to learn where it has been installed.

That difference is why SCD is two documents rather than one. The OAC is the authority on what is configurable about itself and publishes the Definition; the platform is the authority on the conditions and composes the Assignment. Neither endpoint could author the whole exchange, because neither holds both halves of the subject matter.

#### 5.2.1 What SCD Carries

The platform environment an OAC needs falls into three kinds, and the OCP-defined registry of Section 10 is organized around them.

**Platform identity the OAC cannot infer.** The canonical case is slot identity. The value shall correlate to the physical position the OAC occupies, the OAC has no way of determining that position from its own hardware, and no plausible substitute exists — this is exactly the information a slot-address strap carried, and Section 10.1 is its replacement.

**The conditions the slot provides.** The sustained power the platform can supply to this position is the case this specification defines, in Section 10.2. It is a property of the chassis and its budget rather than of the OAC, so it cannot be expressed in the CID at all; an OAC without it knows only what it is rated to draw and never what it is permitted to draw here. The same class would admit thermal and airflow conditions should the workstream define them.

**The operational configuration the platform selects.** Where an OAC can be set up in more than one way, SCD is how the platform chooses. Link subdivision is the case defined here, in Section 10.5: a sixteen-lane PCIe group may serve one host as a single wide link or two hosts as a pair of narrower ones, and which of those the OAC is to present depends entirely on the baseboard it is installed in. The initial power set points of Sections 10.3 and 10.4 are of the same kind.

#### 5.2.2 What Remains in the CID

Content that describes the OAC remains in the CID, and SCD does not restate it. Connector population, lane counts, pin maps, reference clocking, and discrete signals are all properties of the card and bear on whether the platform can accept it physically; they are the CID's to declare.

The Operational Power Level menu — `opl_max_w`, `opl_eff_w`, `opl_red_w`, `opl_emg_w`, and the `opl_set_min_w` floor on the configurable level — likewise remains in the CID. Those wattages describe the OAC's own rating, they are what a platform weighs when deciding whether it can supply the card, and `opl_max_w` is additionally a hardware safety bound that a configuration document shall never be able to raise. SCD's power fields describe the slot and are bounded by the CID's, which is the general shape of the relationship: SCD selects within what the CID declares, and never beyond it.

#### 5.2.3 Vendor Extension

A platform environment is not fully describable by an OCP-defined registry, because the attributes an OAC needs from its slot depend on what the OAC is. The `pen.` namespace of Section 7.4 therefore admits vendor-defined fields alongside the OCP-defined ones, without registration and without collision risk. A vendor field is as much a first-class SCD field as an OCP-defined one; the prefix records who defined it, not how it is treated. Section 7.6 and Section 9.4 are what make this safe: every field carries a default and the Assignment is sparse, so a controller that encounters a field it does not recognize omits it and the OAC applies its declared default. Unknown fields self-handle, and a generic controller can bring up a card whose vendor extensions it has never heard of.

---

## 6. SCD Definition as a FRU File

### 6.1 General

The SCD Definition shall be published by the OAC's management controller as PLDM FRU data and retrieved by the upstream management controller using PLDM for FRU Data (DSP0257), over the same MCTP session that carries the CID.

DSP0257 provides that aggregated FRU data is identified and formatted in the context of a FRU Data File, and that this context, together with the format of DMTF-specified FRU data files, is defined in FRU Data File. The SCD Definition shall be accessed by that method and by no other. The OAC shall expose the Definition as a FRU Data File described by the File Descriptor PDR of Section 6.3, and an upstream management controller shall locate and retrieve it through that record. This specification defines no alternative access path to the Definition, and an OAC shall not require one.

The SCD Definition shall be read-only from the perspective of the upstream management controller. An OAC shall not accept a write to the SCD Definition.

The SCD Definition should be stored in persistent, non-volatile storage on the OAC, so that it is available to be served as soon as the OAC's management controller is ready and does not have to be reconstructed on every retrieval. An OAC may instead generate the Definition on demand from its own firmware configuration.

A Definition generated on demand shall be deterministic for a given firmware configuration. An OAC shall return identical Definition content for as long as its firmware configuration is unchanged, so that two retrievals within one negotiation cannot disagree.

**A firmware update that changes the Definition requires re-negotiation.** Because the Definition may be held in non-volatile storage, a copy written before a firmware update can otherwise outlive the firmware it describes. An OAC whose firmware update changes Definition content shall reset its management controller, deasserting `OAC_MC_RDY` for the duration of the reset, and the SCD exchange shall then begin again from Definition retrieval: the upstream management controller re-retrieves the Definition and composes a fresh Assignment against it. The deassertion is the notification. A controller that has observed no `OAC_MC_RDY` deassertion since it retrieved the Definition holds a current copy; one that has observed a deassertion shall re-retrieve before composing. An OAC that changes its Definition without resetting its management controller is non-conformant.

This specification defines no per-field removal or deprecation semantics. A Definition is replaced whole.

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

**The record and sensor field values this specification constrains are tabulated in Annex C.** Tables C-2 through C-4 give the Definition's File Descriptor PDR, File Size Monitoring Sensor, and Device File State Sensor field by field, and an implementer should work from those tables. Every field not listed there is governed by the referenced DMTF specification and is an implementation matter. Three rules govern how the records relate to one another, and they are stated here because they are requirements rather than field values.

1. **A sensor is associated with the file it reports on by entity identification.** The OAC shall set a sensor PDR's `EntityType`, `EntityInstanceNumber`, and `ContainerID` to the values carried on that file's File Descriptor PDR.
2. **One `ContainerID` identifies the OAC.** The OAC shall carry a single `ContainerID` value across every File Descriptor PDR and every associated sensor PDR this specification requires of it, the Definition's records and the Assignment's alike, so that a controller which has found one SCD record can find the rest.
3. **`EntityInstanceNumber` separates the two files.** The OAC shall assign the Definition and the Assignment distinct values and shall repeat each file's value on that file's sensor PDRs. DSP0248 requires this independently: every file within a `ContainerID` shall have a unique `EntityInstanceNumber`.

This specification requires no directory. The SCD files form a flat set, and an OAC shall set `SuperiorDirectoryFileIdentifier` to `0xFFFF` on both File Descriptor PDRs to declare them outside any hierarchy. An OAC that does place its files in a directory shall do so as DSP0242 requires — a Device File Directory PDR and an Entity Association Record, with the directory's identifier as the `ContainerID` — and rule 2 above then names that directory rather than the OAC.

The Definition's size is not a constant of the OAC design, since it changes whenever firmware changes, and an upstream management controller shall read it from the File Size Monitoring Sensor rather than assume it. A modification reported by the Device File State Sensor indicates that the controller's copy of the Definition is stale and shall be re-retrieved. A Definition change also resets the OAC's management controller per Section 6.1, so a controller that negotiates afresh on every `OAC_MC_RDY` assertion will not be holding a stale copy in the first place; the sensor is how a controller that has been holding a copy across an interval learns it has become stale.

The Device File State Sensor shall report the states of DSP0249 State Set 68 with the meanings that set assigns them. For the Definition only two of the five are reachable, and an OAC shall not report the remaining three.

**Table 6.3-1: State Set 68 Applied to the SCD Definition**

| State | Name | Meaning for the Definition |
|-------|------|----------------------------|
| 1 | File has Not Changed | The Definition has not changed since the last status check. A controller holding a previously retrieved copy need not retrieve it again. |
| 2 | File is Updated | The Definition has changed since the last status check. The upstream management controller shall re-retrieve it before composing an Assignment. |
| 3 | File is at Maximum Size | An OAC shall not report this state. A fixed-length file is always at its maximum size, so the state distinguishes nothing; DSP0242 advises against supporting it for this file characteristic. A Definition that would exceed `FileMaximumSize` is a conformance failure of Section 13.1, not a reportable file state. |
| 4 | File Data has Wrapped | Not applicable. The Definition is published whole and is never appended to. |
| 5 | File Data has Truncated | Not applicable, for the same reason. |

> NOTE: The Device File State Sensor reports the state of the *file*. It is not the Configuration State Sensor of Section 11.4, which reports whether a valid Assignment is in force. The two are unrelated.

The SCD Definition shall be retrievable whenever the OAC is in Operational State O3 or later. An OAC shall not require primary power to serve its Definition.

The upstream management controller shall retrieve the Definition after the CID and before composing an Assignment. Retrieving the Definition has no side effects and may be repeated.

### 6.4 Definition Revision

The SCDD `metadata.definition_revision` field is an **optional, informational** monotonically increasing integer. An OAC that declares it should increment it whenever the content of its Definition changes, and an upstream management controller that reads it may echo it into the Assignment to record which Definition that Assignment was composed against. Both documents are conformant without it.

**The field carries no normative weight.** An OAC shall not reject an Assignment on the grounds of the value echoed in it, nor on the grounds that it echoes none, nor on the grounds that it echoes one where the Definition declares none. The value is a label for logs, traces, and bug reports, and it is useful there precisely because it is cheap.

Currency of the Definition is established by the re-negotiation model of Section 6.1, not by comparing revisions. A firmware update that changes Definition content resets the OAC's management controller, `OAC_MC_RDY` deasserts, and the exchange begins again from Definition retrieval. A controller that has observed no deassertion since reading the Definition holds a current copy; one that has observed a deassertion re-retrieves. The signal edge, rather than a value inside the document, is what carries the information.

> NOTE: An earlier draft made `definition_revision` mandatory in both documents and made a mismatch between them a rejection — the sole staleness check, backed by rejection code `0x0D`. The check was removed in this revision in favour of the `OAC_MC_RDY` model above, which obtains the same guarantee without obliging every OAC to maintain a monotonic counter in non-volatile storage and without obliging every controller to track one. Code `0x0D` is retired to Reserved in Table 11.5-1 rather than reused, so no wire value shifts.

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
| `definition_revision` | integer | Optional | >= 1 | Informational revision of this Definition's content, incremented when that content changes. Carries no normative weight. See Section 6.4. |
| `description` | string | Optional | Free text | Human-readable summary. Shall not be relied upon for any configuration decision. |

An OAC shall not declare a `metadata` key this table does not define. Vendor-specific metadata belongs in a `pen.<IANA PEN>.` prefixed top-level key per Section 7.1.

### 7.3 fields Array

The value of `"fields"` shall be a JSON array of field descriptors. The array shall contain at least one element. Each element describes exactly one configurable field.

**Table 7.3-1: Field Descriptor Schema**

| Key | Applies To | Required | Description |
|-----|-----------|----------|-------------|
| `id` | All | Required | Stable machine key and Assignment key. Namespaced per Section 7.4. Shall be unique within the document. |
| `display_name` | All | Required | Short human-facing label. 1 to 64 characters. |
| `description` | All | Required | Human-facing explanation. No OAC behavior shall derive from it. |
| `type` | All | Required | One of `"integer"`, `"boolean"`, `"enumeration"`. See Section 7.5. |
| `response` | All | Required | One of `"required"`, `"optional"`. See Section 7.7. |
| `default` | All | Required | The value applied when the field is absent from an Assignment. See Section 7.6. |
| `sentinel_default` | All | Optional | Boolean. When `true`, marks `default` as a reserved not-assigned marker lying outside the assignable range. See Section 7.6. |
| `min`, `max` | `integer` | Optional | Inclusive bounds on assignable values. Shall be supplied together. |
| `units` | `integer` | Optional | Unit of measure. Omitted when the value is unitless. |
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

> NOTE: Certain OCP-defined identifiers embed a CID connector identifier as a segment — for example `ocp.link_subdivision.conn0.pcie_primary`. The connector segment is the CID connector identifier lowercased, so `CONN0` becomes `conn0`, while the `cid_binding` carries the canonical uppercase form. The two casings are deliberate: the field identifier follows the snake_case convention that governs all identifiers, and the binding quotes the CID verbatim. Section 10.5 explains why both the connector and the group name are required.

### 7.5 Types and Constraints

**There are three types.** A configuration value is a number, a flag, or a choice from a fixed set, and `integer`, `boolean`, and `enumeration` cover those three exhaustively. A descriptor declaring any other `type` is non-conformant, and an upstream management controller shall reject a Definition containing one.

Free-form text is deliberately not a configuration type. A value an OAC cannot validate is a value an OAC cannot act on, and a field whose permissible values are known is an `enumeration` by construction. Text that identifies or labels rather than configures belongs in `display_name` and `description`, where no OAC behavior derives from it, or in a PLDM sensor.

An Assignment value shall match the JSON type its descriptor declares. Type coercion is not permitted: the string `"5"` is not a valid value for an `integer` field, and the integer `1` is not a valid value for a `boolean` field.

For `integer` fields, when `min` and `max` are declared, an assigned value shall satisfy `min <= value <= max` inclusive. A descriptor declaring one bound without the other is malformed.

For `enumeration` fields, an assigned value shall exactly match, as a case-sensitive comparison, one of the `value` entries in the descriptor's `values` array. Matching shall be by value and never by array position. The `value` entries are themselves JSON strings; this is a property of the encoding and does not make the field a free-text one, since only a declared member may be assigned.

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

| Class | What the declared default is | What is expected of the controller |
|-------|------------------------------|------------------------------------|
| `required` | A fallback. It is safe to apply, but it is unlikely to be the right answer for any particular platform. | Assign a value wherever the platform knows one. Omission is permitted and is reported per Section 11.4. |
| `optional` | A good answer. It is correct for most platforms. | Override only where the platform has a specific reason to. |

There are exactly two response classes.

**`response` classifies the value, not the document.** A `required` field is one the OAC needs a value for in order to operate as intended. It is not a statement that the field shall appear in an Assignment. Every field carries a declared default per Section 7.6, so a `required` field always holds a value — either the one the controller assigned or the one the OAC declared. What `required` records is that the declared default is a fallback rather than a good answer.

It follows that **an OAC shall not reject an Assignment solely because a `required` field is absent from it.** Absence is not a missing value. It is a selection of the declared default, which Section 9.4 makes the defined meaning of omission, and a controller that is content with the declared default of a `required` field omits the key and has composed a complete Assignment. The two rules reinforce each other: because every field has a default and the Assignment is sparse, omission is always well defined.

Two worked cases make the distinction concrete. `ocp.slot_id` is `required` and its declared default is a sentinel meaning *not assigned* — a controller that omits it leaves the OAC without a slot identity, which is a real deficiency and is exactly what State Set 15 state 4 exists to report. `ocp.initial_power_min_w` is `optional` because its declared default is the CID's own configurable floor, which is correct on nearly every platform, so a controller that omits it has lost nothing.

**Why omission is reported rather than refused.** A hard gate would mean a generic controller could be unable to bring up a card it otherwise fully supports — precisely the per-OAC enablement burden that hardware straps imposed and that SCD exists to remove. The under-configured case is therefore surfaced instead: Section 11.4 requires an OAC to report State Set 15 state 4 when an accepted Assignment defaulted a `required` field, which lets an operator find under-configured OACs across a fleet without any OAC refusing to run.

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

The Assignment is written, not read. An OAC is not required to serve a previously accepted Assignment back, and an upstream management controller shall not rely on being able to read one. The Configuration State Sensor of Section 11.4 is the mechanism that replaces such a read.

The SCD Assignment shall not be stored in non-volatile memory. The Assignment as written, and any record the OAC decodes from it, shall be held only in volatile storage, and the OAC's retention of it shall be bounded by +12V Aux: when +12V Aux is removed, the Assignment and everything derived from it are gone, and the OAC returns to the `unassigned` state and shall be re-negotiated. Section 11.6 governs the lifetime in full, and Section 11.6.4 gives the reason the prohibition is absolute.

The SCD Assignment shall be represented in the OAC's PDR repository by a File Descriptor PDR as defined in DSP0248, with `EntityType` set to Device File and `FileClassification` set to `OtherFile`. The Assignment is not FRU data and shall not be classified as such.

The OAC shall set the `FileName` field of that File Descriptor PDR, which is a `strASCII` string, to:

```
OAC_SCDA.json
```

An upstream management controller shall use that name to locate the file it is to write, and shall not rely on PDR ordering to locate it. As with the Definition, the name identifies the record and the `FileIdentifier` carried in that same record is the parameter used to open it, per Section 6.3.

The OAC shall set the `FileCapabilities` bitfield16 so that writing and modification of the Assignment are permitted. `FcWritesPermitted` shall be one, which DSP0248 defines as writing or modifying the file being permitted by the File Client. `ExWriteOpen` shall be one, which is what admits an exclusive open for write. `FileModify` shall be one, indicating that updates are random rather than append-only, because Section 11.6.2 provides for an Assignment to be written again at offset zero on re-negotiation rather than appended to the previous one. `DataType` shall be zero, declaring a regular file rather than a streaming FIFO, and `Read Pushed` shall be one; that combination of three bits is what obliges the OAC to support the write command of Section 8.2, and an OAC that advertised anything less would not be obliged to accept the transfer at all. `ExReadOpen` shall be zero, since the OAC is not required to serve the Assignment back. Advertised capability describes what the transfer mechanism permits and does not oblige the OAC to retain or serve back an Assignment it has accepted; the preceding paragraph governs. The OAC shall set `FileMaximumSize` no greater than the Assignment size limit of Section 13.2, and shall reject an Assignment exceeding it with code `0x0E` per Section 11.5.

The SCD Assignment is a **Regular File** in the sense of DSP0242 — read, modify, or append after creation — and an OAC shall treat it as one. It is not a fixed-length file: Section 9 permits a sparse Assignment, so two successive Assignments for the same OAC may differ in length, and `FileMaximumSize` is a genuine upper bound here rather than the exact size it is for the Definition.

That characteristic is what settles the sensor requirements. DSP0242 keys those requirements to the file characteristic rather than to the classification, and for a Regular File it makes both the File Size Monitoring Sensor and the Device File State Sensor mandatory. Both are therefore mandatory for the SCD Assignment, and an OAC shall publish both. This specification adds a third, the Configuration State Sensor, which is likewise mandatory.

| Sensor | Kind | Purpose |
|--------|------|---------|
| File Size Monitoring Sensor | Compact or Numeric sensor per DSP0242 | Reports the size in bytes of the most recent Assignment transfer. Mandatory per DSP0242 for a Regular File. |
| Device File State Sensor | State sensor implementing DSP0249 State Set 68 (Device File) | Reports the state of the file and signals that its content has been modified. Mandatory per DSP0242 for a Regular File. |
| Configuration State Sensor | State sensor implementing DSP0249 State Set 15 (Configuration State) | Reports whether a valid Assignment is in force. Mandatory per this specification; defined in Section 11.4. |

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
| 4 | File Data has Wrapped | An OAC shall not report this state. An Assignment exceeding `FileMaximumSize` shall be rejected with code `0x0E` per Section 11.5, not wrapped. |
| 5 | File Data has Truncated | An OAC shall not report this state, for the same reason. A silently truncated Assignment would be a valid-looking document missing its tail. |

Neither the File Size Monitoring Sensor nor the Device File State Sensor reports whether an Assignment was accepted. Acceptance is reported by the Configuration State Sensor of Section 11.4 and, where there was a rejection, by the rejection code of Section 11.5, and an upstream management controller shall not infer acceptance from a file size or a file state. An aborted transfer leaves the OAC holding nothing per Section 8.2, and a rejected one leaves its prior SCD state unchanged per Section 11.3.2; neither outcome is distinguishable from a size or file-state reading alone.

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
| `definition_revision` | integer | Optional | >= 1 | Informational echo of the `definition_revision` from the Definition this Assignment was composed against, where the Definition declared one. Carries no normative weight and is not validated. See Section 6.4. |
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

The `assignments` object may be empty. An empty Assignment is valid: it states that the upstream management controller has read the Definition and accepts the declared default of every field in it. It is a complete Assignment, not an absent one, and an OAC shall accept it on the same terms as any other.

That is a narrow case rather than a typical one, and it will not apply to many implementations. It is the right document only where every declared default happens to be correct for the installation — a single-OAC system, for instance, in which slot identity is a don't-care and the sentinel of Section 10.1 is an acceptable outcome, the slot can supply the OAC's full rated power, and nothing is subdivided. A controller that sends an empty Assignment to an OAC declaring `required` fields should expect the OAC to accept it and then report the under-configured condition per Section 11.4.

Each key shall exactly match the `id` of a field descriptor in the Definition the OAC is currently publishing. A key not matching any declared field is an error; see rejection code `0x04` in Table 11.5-1.

Each value shall satisfy the type and constraint rules of Section 7.5 as declared by the corresponding descriptor.

### 9.4 Sparseness

An Assignment shall contain entries only for those fields the upstream management controller wishes to set. Absence of a field is not an error and is not a partial assignment; it selects the declared default.

An OAC shall not require that every declared field appear in an Assignment, and shall not require that every `required` field appear. See Section 7.7.

> **Work in progress.** The interaction between sparseness and the `required` response class is flagged for OCP OAC workstream resolution. The behavior is settled and is retained unchanged in this revision: absence selects the declared default, and no OAC refuses an Assignment over an absent key. What is unsettled is the vocabulary. Describing a field as `required` when the document need not contain it was found confusing in workstream review, and the workstream is to decide whether the `response` key should be renamed, restated, or kept as it stands with the clarification of Section 7.7. Implementers should expect the terminology of this area to be revisited, not the behavior it describes.

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
| Default | CID `power.primary.opl_max_w` |
| `cid_binding` | `{ "cid_object": "power.primary", "constraint": "opl_range" }` |

The sustained power the platform can supply to this slot.

This field runs opposite to every other field in the Definition: it is the platform describing *itself* to the OAC, not the platform configuring the OAC. It is in SCD rather than CID because it is not a property of the OAC at all, and the OAC needs it because otherwise it knows only what it is rated to draw and never what it is permitted to draw here.

The declared bounds follow from the CID: below `opl_emg_w` the OAC cannot run at all, and above `opl_max_w` the statement is unusable because the hardware ceiling binds first.

**The default is the OAC's own ceiling.** `ocp.max_power_w` defaults to the CID `opl_max_w`, so an OAC that receives no assignment for this field behaves as though the slot can supply everything the card is rated to draw.

The alternative — defaulting to the emergency level — was considered and rejected. It would leave every OAC in every conforming slot heavily throttled unless the controller spoke up, which makes the field mandatory in all but name and leaves the default serving no purpose. It would also place the burden on the wrong party: a slot that can supply `opl_max_w` has nothing to declare, whereas a slot that cannot is a slot whose designer knows the budget figure and can assign it.

It follows that **a platform whose slot cannot supply the OAC's `opl_max_w` shall assign this field.** Omitting it asserts a budget the slot does not have. The `required` response class records that expectation, and because an OAC reports a defaulted `required` field per Section 11.4, a platform that has skipped the field is visible to an operator rather than silent.

### 10.3 ocp.initial_power_max_w

| Property | Value |
|----------|-------|
| Type | `integer` |
| Response class | `required` |
| Units | `"watts"` |
| Range | `min` = CID `power.primary.opl_set_min_w`; `max` = CID `power.primary.opl_max_w` |
| Default | OAC-declared, within that range |
| `cid_binding` | `{ "cid_object": "power.primary", "constraint": "opl_range" }` |

The upper power set point the OAC starts from.

An OAC exposes its operating power band to the upstream management controller as a pair of PLDM effecters, so that the band can be read and moved while the card is running. `ocp.initial_power_max_w` is the value the power maximum effecter holds at the point the OAC enters O5, and it is enforced from that point onward. It is a starting value and not a permanent one: the controller may move the effecter afterwards, within the bounds Section 12 sets, and what the OAC enforces at any moment is whatever the effecter then holds. SCD seeds the band; it does not own it.

The settable band itself is the CID's to define, and SCD selects a point inside it. The OAC shall round the assigned value internally to whatever step its power control loop resolves; no granularity is advertised in the Definition, and an OAC wishing to publish its step size shall do so as a PLDM sensor.

**The set point shall not exceed the platform's budget.** An OAC shall reject an Assignment in which `ocp.initial_power_max_w` exceeds `ocp.max_power_w`, with rejection code `0x10` per Section 11.5. A relation between two SCD fields is not expressible in a Definition, which is exactly the case that code describes. The same bound binds at runtime — Section 12 does not permit the effecter to be raised above `ocp.max_power_w` either — so the rule is one rule stated in two places rather than two rules. A slot budget is not a figure the configuration may argue with, and a controller that has composed a contradictory pair has made an error worth reporting rather than one worth silently absorbing.

### 10.4 ocp.initial_power_min_w

| Property | Value |
|----------|-------|
| Type | `integer` |
| Response class | `optional` |
| Units | `"watts"` |
| Range | `min` = CID `power.primary.opl_set_min_w`; `max` = CID `power.primary.opl_max_w` |
| Default | CID `power.primary.opl_set_min_w` |
| `cid_binding` | `{ "cid_object": "power.primary", "constraint": "opl_range" }` |

The lower power set point the OAC starts from. It seeds the power minimum effecter at the point the OAC enters O5, exactly as Section 10.3 describes for the maximum, and is likewise modifiable at runtime.

This field is `optional` because most platforms have no reason to set it, and its declared default — the CID's own configurable floor — is the right answer wherever they do not. A floor matters only where the platform needs the OAC to hold a minimum draw, for instance to keep a shared supply within a stable load band, and that is a deliberate platform decision rather than a routine one.

An OAC shall reject an Assignment in which `ocp.initial_power_min_w` exceeds `ocp.initial_power_max_w`, with rejection code `0x10` per Section 11.5. Where `ocp.initial_power_max_w` was omitted from the Assignment, the comparison is against the value it defaulted to.

> **Work in progress.** The PLDM power minimum and maximum effecters that Sections 10.3 and 10.4 seed, and that Section 12 moves at runtime, are referenced by this specification but are not themselves defined by it. The OCP OAC workstream is to specify them — effecter semantics, units, the bounds they enforce, and the PDRs that describe them — so that this specification can cite that definition rather than imply it. The field semantics above are not expected to change as a result.

### 10.5 ocp.link_subdivision.&lt;connector&gt;.&lt;group_name&gt;

| Property | Value |
|----------|-------|
| Type | `enumeration` |
| Response class | `required` |
| Values | Subdivision mode strings per Section 3.14 |
| Default | OAC-declared; typically the unsubdivided mode |
| `cid_binding` | `{ "cid_object": "protocol_group", "cid_connector": ..., "cid_group_name": ... }` |

How the lanes of one PCIe or CXL protocol group are partitioned into independent links.

Subdivision moved from the CID to SCD in this revision. A x16 group running as `x8x8` mates the same pins and draws the same power, so subdivision is invisible to the powering decision; it is the platform selecting an operational configuration, which is the third of the three kinds of content Section 5.2.1 places in SCD.

**Both identifier segments are required.** The `<connector>` segment is the CID connector identifier lowercased; the `<group_name>` segment is the group's `name`. A bare `ocp.link_subdivision` cannot express two subdividable groups without duplicate identifiers, and field identifiers are the Assignment's keys, so they shall be unique. A two-segment form omitting the connector collides the moment two connectors reuse a group name — which is precisely the reuse that per-connector scoping permits.

An OAC shall declare one such field per subdividable protocol group, and shall declare none for groups it cannot subdivide.

Each declared mode's segments shall sum to the bound CID group's `total_lanes`. Segment order is positional over ascending lane indices within the group.

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

> NOTE: The controller confirms at step 6 by reading the Configuration State Sensor of Section 11.4. That sensor reports whether a valid configuration is in force, but not which Assignment produced it; what remains unsettled in this draft is how a controller confirms that the configuration in force is the one it composed. Section 11.4 records the same point as open for OCP OAC workstream resolution.

### 11.2 Binding Resolution

#### 11.2.1 General

For each field descriptor carrying a `cid_binding`, the upstream management controller shall resolve the binding against the CID before composing an Assignment. A binding that does not resolve indicates an inconsistency between the two documents; the upstream management controller shall treat the OAC as non-conformant and shall not proceed to step 3.

Bindings shall be resolved by name or by range and never by array position.

#### 11.2.2 Power Bindings

A binding with `"cid_object": "power.primary"` and `"constraint": "opl_range"` shall be resolved by verifying that the field descriptor's declared `min` and `max` match the CID values required for that field by Section 10.2, Section 10.3, or Section 10.4.

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
3. **Key validity.** Every key in `assignments` matches a declared field identifier.
4. **No duplicate keys.**
5. **Type conformance.** Every value matches its descriptor's declared type, with no coercion.
6. **Constraint conformance.** Integer values fall within declared `min` and `max`, and enumeration values match a declared `value` exactly.
7. **Sentinel prohibition.** No assigned value equals a sentinel default.
8. **Cross-field feasibility.** The two relations this specification defines between assigned values hold: `ocp.initial_power_max_w` does not exceed `ocp.max_power_w`, and `ocp.initial_power_min_w` does not exceed `ocp.initial_power_max_w`. See Sections 10.3 and 10.4.
9. **OAC-specific feasibility.** Any constraint the OAC enforces that the Definition cannot express — for example, a restriction that two particular groups cannot both be subdivided. See Section 11.3.3.

There is no check on `metadata.definition_revision`. The field is informational and carries no normative weight; currency of the Definition is established by the management controller reset model of Section 6.4 rather than by a revision comparison.

#### 11.3.2 Atomicity

The OAC shall apply the Assignment in whole or reject it in whole. An OAC shall not apply a subset of an Assignment and report partial success. Upon rejection the OAC shall remain in its prior SCD state, unchanged.

#### 11.3.3 Constraints the Definition Cannot Express

This specification provides no mechanism for expressing cross-field constraints in the Definition, and `applies_when` is deliberately limited to a single-field equality test.

Nothing becomes unsafe as a result, because OAC-side validation remains the backstop: an illegal combination is refused at the feasibility checks of Section 11.3.1 whether or not the Definition could describe it. What is lost is advance discoverability — the controller learns about such a constraint by rejection rather than by construction. Implementations encountering a case they believe requires a richer predicate should raise it with the OCP OAC workstream so that a specific construct can be defined, rather than generalizing `applies_when`.

### 11.4 SCD Configuration State Reporting

An OAC shall expose its current SCD state as a PLDM state sensor implementing DSP0249 State Set 15 (Configuration State), associated with the SCD Assignment file by the identifiers of Section 8.1. This sensor is the Configuration State Sensor.

State Set 15 defines four states. The OAC shall report them with the following meanings. Where a meaning below narrows or departs from the description DSP0249 gives a state, the meaning below governs for SCD.

The table separates two phases, because a state read during initialization and the same state read at runtime do not carry the same operational consequence. *Initialization* covers Operational State O3, from management controller readiness until the Assignment latches on the O3 to O4 transition per Section 3.17. *Runtime* covers O4 onward, once the configuration is latched and the OAC is operating on it.

**Table 11.4-1: State Set 15 Applied to SCD**

| State | Name | During initialization (O3, before latch) | At runtime (O4 onward) |
|-------|------|------------------------------------------|------------------------|
| 1 | Valid Configuration | An Assignment has been written, validated, and accepted, and every field the Definition marked `required` carried an assigned value. The OAC is ready to latch. The state is reported from acceptance onward, before the latch of Section 3.17 has occurred. | The accepted Assignment is latched and in force, and every `required` field is carrying an assigned value. This is one of the two states an OAC reporting `latched` in Section 11.6.5 may hold; state 4 is the other. |
| 2 | Invalid Configuration | An Assignment was written and rejected under Section 11.3. The characteristic case is a document that was *well formed* — it parsed as JSON per Section 8.3, and its structure conformed to Section 9 — but that described conditions the OAC cannot operate under. A slot power budget that falls below the OAC's `opl_emg_w` is the clearest example: the document is correctly constructed and the controller composed it in good faith, and the OAC still cannot run on what it has been offered, so it refuses with code `0x07` rather than powering on in a state it cannot sustain. Values that are simply invalid against the Definition are reported here too — of the wrong type, naming an unknown field identifier, failing a cross-field relation of Sections 10.3 and 10.4, or failing a binding check of Section 11.2 — as is a malformed document. In every case the formatting may have been acceptable while the content was not, the OAC has applied nothing, and it remains on its declared defaults. The rejection code of Section 11.5 identifies the cause; this sensor reports only that there was one. | The same, for an Assignment written to a running OAC. An OAC that already holds an accepted configuration shall **not** move to state 2 on a rejection: it shall continue to report state 1 or state 4 as applicable, because rejection is atomic and leaves the configuration in force untouched per Section 11.3.2. State 2 at runtime therefore means a rejection occurred with no accepted configuration behind it. |
| 3 | Not Configured | **The default state.** An OAC shall report state 3 from management controller reset onward and shall continue to report it until an Assignment has been accepted or rejected. No Assignment has been received, the OAC is operating on the declared defaults of its own Definition, and it is waiting to be configured. This is the `unassigned` state of Section 11.6.5. | No Assignment is in force and none has been rejected since the last event requiring re-negotiation per Section 11.6.2 — the OAC was re-armed and has not yet been given an Assignment. A controller finding state 3 at runtime shall re-negotiate per Section 11.6. |
| 4 | Missing Configuration | An Assignment has been written and accepted, but one or more fields the Definition marked `required` were absent from it and fell back to their declared defaults. The OAC is ready to latch; it is not going to latch the configuration it asked for. | The accepted Assignment is latched and in force, and at least one `required` field is running on a declared default rather than an assigned value. The OAC is configured; it is not fully configured. |

An OAC shall report state 3 as its power-on and post-reset state. An OAC shall not report state 1, 2, or 4 before the first Assignment of the current configuration cycle has been written, because each of those three asserts something about an Assignment that has been received.

State 4 is the reportable consequence of the response class model of Section 7.7. A controller may omit a `required` field, and Section 11.3 requires the OAC to accept the Assignment when it does, because a field the controller cannot determine must not prevent the OAC from powering on. Distinguishing states 1 and 4 lets an operator find, across a fleet, the OACs that were configured but not fully configured — a condition that is otherwise invisible and that no rejection code reports, since nothing was rejected.

Exposing state as a readable level rather than leaving it to be inferred makes the controller's algorithm stateless and level-triggered: read the sensor; if state 1, do nothing; if state 4, decide whether the defaulted fields are acceptable; if state 2 or 3, negotiate. The phase columns of Table 11.4-1 do not change that algorithm, only what the controller should conclude from the answer. This is strictly better than inferring from an `OAC_MC_RDY` edge or a boot counter, because a level can be polled at any time and an edge can be missed — and after an uncommanded management controller reset, the controller has no way of knowing an edge occurred.

The upstream management controller shall confirm at step 6 of Section 11.1 that the Assignment is in force by reading the Configuration State Sensor, and shall not infer that from a signal edge or a boot counter. The upstream management controller shall treat state 4 as configured rather than as a failure, and shall determine whether the defaulted `required` fields are acceptable before proceeding.

The sensor reports the condition of the configuration, not its identity. It does not tell a controller *which* Assignment produced the state it reads, so a controller that finds state 1 on an OAC it has not itself negotiated with — after a controller failover, or after its own restart — learns that some valid configuration is in force but not that it is the one that controller would have composed.

> **Work in progress.** Whether to close that identity gap is open for OCP OAC workstream resolution. An earlier draft closed it with a digest of the Assignment, cached at receive time and read back alongside the state; that mechanism was withdrawn in favour of the standard state set. Whether to reintroduce it, in what form, and whether the gap is worth closing at all — a controller can simply rewrite the Assignment and let Section 11.6.7 absorb the duplicate — is for the workstream to settle.

### 11.5 Rejection Reporting

When an OAC rejects an Assignment it shall report a rejection code and should report the field identifier at which validation failed.

This section follows Section 11.4 because that is the order in which a controller uses the two. A rejection code is consulted only once the Configuration State Sensor has shown that something went wrong: the controller reads state first, and the code below is what tells it why.

> **Work in progress.** How a rejection code reaches the upstream management controller is flagged for OCP OAC workstream resolution. This section defines what an OAC reports and the vocabulary it reports in; it does not define the transport. A PLDM sensor carrying the most recent rejection code, associated with the Assignment file by the identifiers of Section 8.1 and read alongside the Configuration State Sensor of Section 11.4, is the expected direction and is what the workstream is to settle. Until it does, the table below should be read as an agreed vocabulary rather than as a wire format.

**Table 11.5-1: SCD Assignment Rejection Codes**

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
| `0x08` | Reserved | Formerly `LENGTH_EXCEEDED`. Retired in this revision with the `string` type and the `max_length` key it enforced; see Section 7.5. Not reused. |
| `0x09` | `INVALID_ENUM_VALUE` | An enumeration value matched no declared `value`. |
| `0x0A` | `SENTINEL_ASSIGNED` | An assigned value equalled a sentinel default. |
| `0x0B` | `NULL_VALUE` | A JSON `null` appeared as a value. |
| `0x0C` | `UNSUPPORTED_SCHEMA_VERSION` | `metadata.schema_version` is not supported by the OAC. |
| `0x0D` | Reserved | Formerly `DEFINITION_REVISION_MISMATCH`. Retired in this revision with the revision check it reported; see Section 6.4. Not reused. |
| `0x0E` | `SIZE_EXCEEDED` | Payload exceeded the limit of Section 13.2. |
| `0x0F` | `TRANSFER_INCOMPLETE` | `DfClose` was received before the declared payload length was transferred. |
| `0x10` | `CONSTRAINT_CONFLICT` | A constraint not expressible in the Definition was violated. This covers the cross-field power relations of Sections 10.3 and 10.4 as well as OAC-specific constraints under Section 11.3.3. |
| `0x11` | `ALREADY_LATCHED_DIFFERENT` | The OAC is latched and the submitted Assignment differs from the one in force. See Section 11.6. |
| `0x12` | `INTERNAL_ERROR` | The OAC could not apply a valid Assignment for an implementation-specific reason. |
| `0x13` – `0x7F` | Reserved | Reserved for future use by this specification. |
| `0x80` – `0xFF` | Vendor-specific | Available for OAC-vendor-defined rejection reasons. An upstream management controller shall treat an unrecognized vendor code as a generic rejection. |

Two codes are marked Reserved rather than removed. The mechanisms they reported were withdrawn in this revision, but reusing their values would shift the meaning of a byte an implementation may already have built against, and every other code keeps its current position precisely because these two were left where they were.

### 11.6 Latching, Re-application, and Re-negotiation

> **Work in progress.** This section as a whole is flagged for OCP OAC workstream resolution. It arose from experiments into what an OAC should do when primary power is removed and when its management controller is reset, and the model set out below — survival in two domains, re-negotiation only when both are lost — is what those experiments suggested. The simpler alternative is to require re-negotiation unconditionally whenever either event occurs, which is easier to specify and easier to test. That alternative is not adopted here because there appear to be cases in which it is problematic, and identifying them is part of what the workstream is to settle. Implementers should read this section as a working model rather than as a settled requirement.

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
| Whether any `required` field was defaulted | Feeds the Configuration State Sensor of Section 11.4, which distinguishes state 1 from state 4 on that basis |

The OAC shall retain whether any `required` field was defaulted, because the Configuration State Sensor of Section 11.4 cannot distinguish state 1 from state 4 without it, and the distinction shall survive a management controller reset that adopts a valid shadow record. The form the decoded record takes is an implementation matter; a fixed-layout binary structure is recommended.

The raw Assignment is needed only during validation and shall be discarded at `DfClose`. Keeping a parser off the re-application path matters: a power-up is the worst possible moment to discover that a document which parsed an hour ago no longer does.

#### 11.6.7 Writing While Latched

An OAC should accept an Assignment written while it is latched, and shall in that case either:

- accept it as a no-op if it is byte-identical in canonical form to the Assignment in force, or
- reject it with code `0x11` if it differs.

This gives the controller a safe recovery action when it is unsure of the OAC's state, without opening a path to reconfiguring a running OAC.

> NOTE: The definition of "primary power removed" against the O-state machine is not settled in this draft — specifically whether `OAC_PWR_EN` deassertion, which is a normal O4 to O3 transition, qualifies, or only full loss of the primary rail. It is part of what the work in progress note at the head of Section 11.6 covers. Re-insertion is unambiguous either way, since both domains lose power.

---

## 12. Runtime Power Control

SCD is one-time configuration per negotiation. Everything dynamic goes through the PLDM effecter path, which already has clamping and reporting semantics defined in DSP0248.

An OAC shall expose DSP0248 numeric effecters permitting the upstream management controller to move its operating power band at runtime. The band shall be bounded below by the CID `power.primary.opl_set_min_w` and above by:

```
min( ocp.max_power_w, CID power.primary.opl_max_w )
```

`ocp.initial_power_max_w` and `ocp.initial_power_min_w` set the values those effecters hold at the point the OAC enters O5, per Sections 10.3 and 10.4. They are starting values on the one control path, not a second one, and nothing in SCD moves power after O5.

An OAC shall not permit the power maximum effecter to be raised above `ocp.max_power_w`. The platform's declared budget binds the runtime path exactly as it binds the initial configuration, and an OAC shall answer an attempt to exceed it with an error rather than silently clamping, so that a controller is never left believing it holds more budget than it does.

> **Work in progress.** The PLDM power minimum and maximum effecters that Sections 10.3 and 10.4 seed, and that Section 12 moves at runtime, are referenced by this specification but are not themselves defined by it. The OCP OAC workstream is to specify them — effecter semantics, units, the bounds they enforce, and the PDRs that describe them — so that this specification can cite that definition rather than imply it. The field semantics above are not expected to change as a result.

> NOTE: A platform may legitimately budget an OAC below its own `opl_eff_w` — an `ocp.max_power_w` of 1000 W against an `opl_eff_w` of 2000 W is a valid, deliberate choice. Whether the OAC shall report that it is operating in a degraded band is open, and the OCP OAC workstream should settle it alongside the effecter definition noted above.

---

## 13. Size Limits

Both limits are stated in kilobytes, written KB, and both are powers of two: 64 KB means 65,536 bytes exactly. The limits are deliberately generous. A size limit that has to be raised later is more disruptive than one that was ample from the start, because every OAC and every controller built against the smaller number has to be revisited.

### 13.1 SCD Definition

The maximum transferred size of an SCD Definition payload shall be **64 KB** (65,536 bytes), measured as transferred. The OAC shall minify the Definition per Section 6.2 and shall measure the limit on the minified byte sequence. A Definition exceeding the limit is non-conformant, and the OAC shall set `FileMaximumSize` no greater than it per Section 6.3.

> NOTE: For calibration, the six-field Definition shown in Annex A occupies approximately 2.5 KB minified, or roughly 420 bytes per field, most of which is prose `description` text. A Definition of purely machine-readable content runs well under 200 bytes per field. The 64 KB limit therefore accommodates on the order of a hundred and fifty verbose fields, and several times that for a Definition whose field descriptors carry no prose — far beyond anything the examples of Annex A or the registry of Section 10 suggest an OAC will need.

### 13.2 SCD Assignment

The maximum transferred size of an SCD Assignment payload shall be **64 KB** (65,536 bytes), the same limit as the Definition.

**An Assignment cannot be larger than the Definition it was composed against.** It is sparse, it carries at most one entry per declared field, and each entry is an identifier and a scalar where the Definition carried that same identifier, the same scalar as a `default`, and the whole descriptor around them. The bound is therefore inherent in the two documents rather than something a number has to impose, and the two limits are set equal so that the specification states the real bound once. A smaller Assignment limit would be a second constraint that the first has already made redundant, and would risk being the one that binds first on some future Definition nobody has yet written.

In practice a typical Assignment is a few hundred bytes, and neither limit is a practical constraint on any OAC this specification anticipates.

---

## 14. Compliance

### 14.1 OAC Requirements

**Table 14.1-1: OAC Compliance Requirements**

| Requirement | Classification | Reference |
|-------------|----------------|-----------|
| Publish an SCD Definition as a FRU file retrievable per DSP0257 | Mandatory | 6.1 |
| Expose the Definition as a FRU Data File per DSP0257 and support no alternative access path | Mandatory | 6.1 |
| Store the Definition in persistent, non-volatile storage | Recommended | 6.1 |
| Return identical Definition content for as long as its management controller remains ready | Mandatory | 6.1, 6.4 |
| Describe the Definition with a File Descriptor PDR carrying `EntityType` Device File, `FileClassification` `FRUDataFile`, and `FileName` `OAC_SCDD.json` | Mandatory | 6.3 |
| Provide a Device File State sensor PDR for the Definition | Mandatory (DSP0242, Fixed Length File) | 6.3 |
| Provide a File Size Monitoring sensor PDR for the Definition | Mandatory (this specification; DSP0242 recommends) | 6.3 |
| Associate every SCD sensor PDR with its file by `EntityType`, `EntityInstanceNumber`, and `ContainerID` | Mandatory | 6.3, 8.1 |
| Declare the Definition as a DSP0242 Fixed Length File and set `FileMaximumSize` to its exact transferred size | Mandatory | 6.3 |
| Not report State Set 68 state 3 (File is at Maximum Size) on the Definition | Mandatory | 6.3 |
| Reject writes to the SCD Definition | Mandatory | 6.1 |
| Encode both documents as UTF-8 JSON per ECMA-404 with no BOM and no comments | Mandatory | 6.2, 8.3 |
| Publish the Definition in minified format | Mandatory | 6.2 |
| Reset the management controller, deasserting `OAC_MC_RDY`, when a firmware update changes Definition content | Mandatory | 6.4 |
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
| Provide a Configuration State sensor PDR for the Assignment | Mandatory (this specification) | 8.1, 11.4 |
| Declare the Assignment as a DSP0242 Regular File | Mandatory | 8.1 |
| Set `SuperiorDirectoryFileIdentifier` to `0xFFFF` on both File Descriptor PDRs, absent a directory | Mandatory | 6.3 |
| Set `FileMaximumSize` no greater than the applicable Section 13 limit on each File Descriptor PDR | Mandatory | 6.3, 8.1 |
| Defer validation until `DfClose` | Mandatory | 8.2 |
| Accept or reject an Assignment atomically | Mandatory | 11.3.2 |
| Accept a sparse Assignment, applying declared defaults for absent fields | Mandatory | 9.4 |
| Not reject an Assignment solely because a `required` field is absent | Mandatory | 7.7 |
| Reject an Assignment in which `ocp.initial_power_max_w` exceeds `ocp.max_power_w`, or `ocp.initial_power_min_w` exceeds `ocp.initial_power_max_w` | Mandatory | 10.3, 10.4, 11.3.1 |
| Reject an Assignment containing a duplicate key | Mandatory | 9.5 |
| Reject an Assignment assigning a sentinel value | Mandatory | 11.3.1 |
| Report a rejection code per Table 11.5-1 | Mandatory | 11.5 |
| Report the field identifier at which validation failed | Recommended | 11.5 |
| Expose DSP0248 numeric effecters for runtime control of the power band | Mandatory | 12 |
| Bound the power maximum effecter above by `min(ocp.max_power_w, opl_max_w)` | Mandatory | 12 |
| Seed those effecters from `ocp.initial_power_max_w` and `ocp.initial_power_min_w` on entry to O5 | Mandatory | 10.3, 10.4, 12 |
| Latch the Assignment on the O3 to O4 transition | Mandatory | 11.1 |
| Require re-negotiation only when primary power was removed **and** the MC was reset | Mandatory | 11.6.2 |
| Hold the cache in two survival domains per Table 11.6-2 | Recommended | 11.6.3 |
| Not store the SCD cache in non-volatile memory | Mandatory | 11.6.4 |
| Not retain SCD state across removal of +12V Aux by any means | Mandatory | 8.1, 11.6.4 |
| Invalidate the MC cache unconditionally early in MC boot | Mandatory | 11.6.5 |
| Adopt a valid shadow record without applying defaults and without re-arming | Mandatory | 11.6.5 |
| Discard the raw Assignment at `DfClose` and cache whether any `required` field was defaulted | Mandatory | 11.6.6 |
| Cache a decoded fixed-layout record rather than the Assignment JSON | Recommended | 11.6.6 |
| Implement the Configuration State Sensor as DSP0249 State Set 15 and report the four states per Table 11.4-1 | Mandatory | 11.4 |
| Report State Set 15 state 4 when an accepted Assignment defaulted a `required` field | Mandatory | 11.4 |
| Report only the State Set 68 states this specification declares reachable for each file | Mandatory | 6.3, 8.1 |
| Carry one `ContainerID` across every File Descriptor PDR and associated sensor PDR of the OAC | Mandatory | 6.3, 8.1 |
| Accept a byte-identical Assignment while latched as a no-op | Recommended | 11.6.7 |
| Keep the Definition within 64 KB as transferred | Mandatory | 13.1 |
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
| Echo `definition_revision` into the Assignment as informational provenance | Optional | 9.2 |
| Not assign a value to `ocp.initial_power_max_w` exceeding the value it assigns to `ocp.max_power_w` | Mandatory | 10.3 |
| Omit unrecognized fields from the Assignment rather than failing | Mandatory | 7.7 |
| Not assign a sentinel value | Mandatory | 7.6 |
| Transfer the Assignment in minified format | Mandatory | 8.3 |
| Deliver the Assignment in O3, before `OAC_PWR_EN` assertion | Mandatory | 8.4 |
| Confirm the Assignment is in force before `OAC_PWR_EN` is asserted | Mandatory | 11.1 |
| Re-read the Definition and recompose after the OAC's management controller has reset | Mandatory | 6.4 |
| Treat an unrecognized vendor rejection code as a generic rejection | Mandatory | 11.5 |
| Not infer Assignment acceptance from a File Size Monitoring Sensor or Device File State Sensor reading | Mandatory | 8.1 |
| Treat `OAC_MC_RDY` deassertion, not the Device File State Sensor, as the signal that a cached Definition shall be discarded | Mandatory | 6.3, 6.4 |
| Keep the Assignment within 64 KB as transferred | Mandatory | 13.2 |
| Confirm at step 6 by reading the Configuration State Sensor rather than inferring state from signal edges | Mandatory | 11.1, 11.4 |
| Treat State Set 15 state 4 as configured, not as a failure, and decide whether the defaulted `required` fields are acceptable | Mandatory | 11.4 |
| Re-negotiate on finding State Set 15 state 3 at runtime | Mandatory | 11.4, 11.6 |

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
      "description": "Example SCD Definition for a PCIe Gen6 x16 OAC."
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
        "default": 2500,
        "units": "watts",
        "min": 625,
        "max": 2500,
        "cid_binding": {
          "cid_object": "power.primary",
          "constraint": "opl_range"
        }
      },
      {
        "id": "ocp.initial_power_max_w",
        "display_name": "Initial Power Maximum",
        "description": "Upper power set point applied when the OAC enters O5.",
        "type": "integer",
        "response": "required",
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
        "id": "ocp.initial_power_min_w",
        "display_name": "Initial Power Minimum",
        "description": "Lower power set point applied when the OAC enters O5.",
        "type": "integer",
        "response": "optional",
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
| `ocp.max_power_w` | required | `2000` | This slot cannot supply the OAC's 2500 W `opl_max_w`, so the platform shall declare what it can supply |
| `ocp.link_subdivision.conn0.pcie_primary` | required | `x8x8` | Differs from the `x16` default |
| `ocp.initial_power_max_w` | required | omitted | The declared 1200 W default suits this platform |
| `ocp.initial_power_min_w` | optional | omitted | This platform imposes no power floor; the declared default is the CID's own 625 W configurable minimum |
| `pen.32473.boot_source` | required | omitted | The declared `local_flash` default suits this platform |

The omissions are the more instructive half. `pen.32473.boot_source` is marked `required`, yet a controller that has never heard of PEN 32473 skips it and the OAC boots from local flash exactly as intended. An unrecognized field self-handles — which works because `response` classifies the value rather than obliging the document, per Section 7.7, *and* because every field carries a default.

The power fields show the cross-field rule of Section 10.3 rather than a clamp. The OAC is rated to 2500 W by its CID; the platform declares a 2000 W budget because this slot cannot supply the full rating, which is exactly the case in which `ocp.max_power_w` shall be assigned. The initial upper set point falls back to its declared 1200 W default, which sits below the budget and is therefore consistent with it. Had the controller instead assigned 2400 W to `ocp.initial_power_max_w`, the OAC would reject the Assignment with code `0x10` rather than silently clamp it to 2000 W, so the contradiction is returned to the controller that composed it rather than absorbed.

Note what the declared defaults produce if the controller omits everything: slot unknown, a budget of 2500 W equal to the OAC's own `opl_max_w`, an initial upper set point of 1200 W, no floor beyond the CID's 625 W configurable minimum, an x16 link, and local flash. The OAC comes up running and unmistakably under-configured — its slot identity is the sentinel and it reports State Set 15 state 4 — which is the direction a default should fail in. It does not come up throttled: a budget defaulting below the card's rating would throttle every OAC in every conforming slot, and Section 10.2 explains why that trade is made the other way.

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
6. Emit the Assignment. `definition_revision` may be echoed from the Definition as informational provenance; it is not required, and the OAC does not validate it.
7. Minify and transfer.

Two practical notes. First, a controller should never fail composition because it does not recognize a field; step 3d is the whole mechanism by which vendor fields coexist with generic controllers. Second, a controller holding a cached Definition from a previous boot should re-read it rather than assume it is current. An OAC whose firmware update changes its Definition resets its management controller and deasserts `OAC_MC_RDY` per Section 6.4, and that deassertion is the controller's signal to discard the cached copy and begin again from retrieval.

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
| `FileCapabilities` | `FcWritesPermitted` = 0, `ExWriteOpen` = 0, `DataType` = 0 | Wrap-versus-truncate behaviour is moot for a file the controller cannot write. `DataType` = 0 declares a regular file rather than a streaming FIFO. Bits not listed are not constrained here; see the note at the end of this annex. |
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
| `FileCapabilities` | `FcWritesPermitted` = 1, `ExWriteOpen` = 1, `ExReadOpen` = 0, `FileModify` = 1, `DataType` = 0, `Read Pushed` = 1 | Names are the DSP0248 ones. `DataType` = 0 with `Read Pushed` = 1 and `ExWriteOpen` = 1 is the combination that obliges the OAC to support `DfWrite`. `FileModify` = 1 because a re-negotiated Assignment is written at offset zero rather than appended. Describes what the transfer mechanism permits; it does not oblige the OAC to serve an accepted Assignment back; see Section 8.1. Bits not listed are not constrained here; see the note at the end of this annex. |
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
| States reported | 1 (Valid Configuration), 2 (Invalid Configuration), 3 (Not Configured), 4 (Missing Configuration) | All four are reachable. State 3 is the post-reset default. See Table 11.4-1 for the initialization and runtime meaning of each. |
| Interpretation | Whether a valid Assignment is in force | This is the mechanism that replaces reading the Assignment back. The Definition has no counterpart sensor. |

> **Work in progress.** The `FileCapabilities` bits this specification does not fix — `FileTrunc`, `DataVolatility`, `FcZeroLengthPermitted`, and `Read Polled` — are flagged for OCP OAC workstream resolution. Sections 6.3 and 8.1 constrain only the bits the transfer path depends on. DSP0248 attaches configuration rules to several of the remainder, notably that at least one of `Read Polled` and `Read Pushed` shall be set and that `ExReadOpen` shall be permitted wherever `FcZeroLengthPermitted` is. The workstream should settle the full pattern for both files and record it in this annex, and should check the bit names it adopts against the edition of the DMTF file transfer specification current at that time, since these bits have not always been named identically across the DMTF specifications that reference them. This specification uses the DSP0248 names throughout.

---

**End of Specification**
