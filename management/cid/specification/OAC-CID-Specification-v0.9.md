# OAC Connector Interface Definition (CID) Specification
## Version: 0.9
### Document Identifier: OAC-CID-SPEC
### Document Status: Draft
### Document Language: en-US
### Normative Reference: OCP Open Adapter Card Base Specification v0.9

---

## Foreword

This specification is authored by the OCP Open Adapter Card (OAC) workstream under the Open Compute Project Foundation. It defines the Connector Interface Definition (CID), a machine-readable descriptor that OAC implementations shall expose to the upstream management controller. The OCP OAC workstream retains editorial authority over this document. Contributions, errata reports, and change proposals shall be submitted through the OCP OAC project repository.

This document is a Draft specification. Contents are subject to revision by the OCP OAC workstream prior to final publication.

---

## Contents

1. Scope
2. Normative References
3. Terms and Definitions
4. Symbols and Abbreviated Terms
5. CID Overview
6. CID as a FRU File
   - 6.1 General
   - 6.2 Encoding
   - 6.3 File Classification and Access
7. CID JSON Document Structure
   - 7.1 General
   - 7.2 metadata Object
   - 7.3 power Object
   - 7.4 connectors Array
   - 7.5 Enumerated Values Summary
   - 7.6 Field Naming and Ordering Conventions
8. Connector Profile JSON Document Structure
   - 8.1 General
   - 8.2 Referencing a Profile from a CID
   - 8.3 Profile Identifiers
   - 8.4 Profile Document Structure
   - 8.5 Profile Applicability to Connector Positions
9. CID Retrieval and Validation
   - 9.1 Storage and Exposure
   - 9.2 Retrieval Sequence
   - 9.3 Validation Requirements
   - 9.4 Timeout Handling
10. Compliance
   - 10.1 OAC Implementation Requirements
   - 10.2 Upstream Management Controller Requirements

Annex A (informative) -- Example CID JSON Documents
Annex B (informative) -- PLDM Protocol Field Value Reference

---

## 1. Scope

This specification defines the Connector Interface Definition (CID), a normative machine-readable JSON document stored in OAC firmware that declares all connector, power, clocking, and signaling attributes of an OAC. The CID is published by the OAC management controller as a FRU Data File and retrieved by the upstream management controller using PLDM for FRU Data (DMTF DSP0257) over MCTP on the OAC Management USB 2.0 interface.

The CID enables the upstream management controller to evaluate connector compatibility, power budget feasibility, signaling protocol alignment, and clocking requirements before enabling primary busbar power to the OAC.

Mechanical keying and the CID address different failure modes and are not alternatives to one another. The mechanical keying defined in OCP Open Adapter Card Base Specification v0.9 Section 7.9.3.1 discriminates on exactly one attribute — the nominal primary input voltage class, +12 V DC or +50 V DC — and exists to prevent an electrically unsafe mating. It makes no determination about signaling, protocol, lane count, impedance class, clocking, or power envelope. Every compatibility determination beyond the primary input voltage class is made from the CID. The CID additionally re-checks the input voltage class in software, so that the one attribute keying does cover is enforced by both mechanisms rather than by keying alone, as required by OCP OAC Base Specification v0.9 Section 9.3.1.

The following are within the scope of this specification:

- The structure and encoding of the CID JSON document
- The retrieval mechanism via DSP0257 PLDM for FRU Data
- Compliance requirements for OAC implementations and upstream management controller implementations

The following are outside the scope of this specification:

- Physical connector mechanical design (governed by OCP Open Adapter Card Base Specification v0.9)
- Protocol-specific electrical signaling parameters (governed by the respective protocol specifications)
- Upstream management controller firmware implementation details

---

## 2. Normative References

The following documents are normative references for this specification. For dated references, only the edition cited applies. For undated references, the latest edition of the referenced document applies.

| Reference | Document |
|-----------|----------|
| DSP0220 | DMTF, "FRU Data Specification," Version 1.0.1 |
| DSP0236 | DMTF, "Management Component Transport Protocol (MCTP) Base Specification" |
| DSP0240 | DMTF, "PLDM Base Specification," Version 1.2 |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification," Version 1.3.1 |
| DSP0249 | DMTF, "PLDM State Set Specification," Version 1.4.0 |
| DSP0257 | DMTF, "PLDM for FRU Data Specification," Version 2.0 |
| ECMA-404 | ECMA International, "JSON Data Interchange Syntax," 2nd Edition |
| OCP OAC v0.9 | OCP, "Open Adapter Card Base Specification," Version 0.9 |

---

## 3. Terms and Definitions

For the purposes of this specification, the following terms and definitions apply. Terms not defined here shall have the meaning ascribed to them in DSP0220, DSP0257, or the OCP Open Adapter Card Base Specification v0.9.

**3.1 CID (Connector Interface Definition)**
A machine-readable JSON document conforming to this specification that declares the connector population, power requirements, Operational Power Levels, high-speed signaling assignments, reference clocking, and vendor-defined discrete signals of a specific OAC.

**3.2 FRU File**
As defined in DSP0220 and DSP0257: a logically coherent data unit published by a PLDM FRU Data agent and retrieved using PLDM for FRU Data. The CID is a FRU File of classification `FRUDataFile` per DSP0257.

**3.4 OAC (Open Adapter Card)**
An OAC form factor defined by the OCP Open Adapter Card Base Specification v0.9, characterized by a standardized connector topology supporting up to seven high-speed connector positions (CONN0 through CONN6) and one cable connector position (CABLE).

**3.5 Expanded Format JSON**
A JSON encoding that includes optional whitespace characters (spaces, tabs, newlines) to improve human readability. Expanded format is a valid CID encoding. It is typically used for authoring, documentation, and debugging.

**3.6 Minified Format JSON**
A JSON encoding with all optional whitespace removed. Minified format is a valid CID encoding and is the recommended encoding for production CID storage.

**3.7 FRU Bundle**
As used informally in this specification: the complete set of FRU Files exposed by an OAC management controller via PLDM for FRU Data. The FRU Bundle includes the CID FRU File and may include additional vendor-defined FRU Files.

**3.8 upstream management controller**
The management processor on the host baseboard that communicates with OAC management controllers over the OAC Management USB 2.0 interface. The upstream management controller is responsible for retrieving and evaluating the CID before enabling primary busbar power.

**3.9 Operational Power Level (OPL)**
A discrete operating profile, defined in OCP OAC Base Specification v0.9 Section 10.1.2, that specifies a sustained power limit and associated performance characteristics for an OAC. OPLs are declared in the CID so that the upstream management controller can evaluate power budget feasibility before enabling primary power.

**3.10 Operational State**
A defined condition of the OAC with respect to power domain availability, management controller readiness, and device initialization, as defined in OCP OAC Base Specification v0.9 Section 10.1.1. CID retrieval occurs in Operational State O3 (Management Initialized).

---

## 4. Symbols and Abbreviated Terms

| Symbol / Abbreviation | Meaning |
|-----------------------|---------|
| CID | Connector Interface Definition |
| FRU | Field Replaceable Unit |
| JSON | JavaScript Object Notation |
| MCTP | Management Component Transport Protocol |
| OAC | Open Adapter Card |
| OPL | Operational Power Level |
| PLDM | Platform Level Data Model |
| RX | Receive (signal direction toward the OAC) |
| SRIS | Separate Reference clock with Independent Spread |
| TX | Transmit (signal direction from the OAC toward the baseboard or fabric peer) |
| UUID | Universally Unique Identifier |

---

## 5. CID Overview

The CID is a structured JSON document that an OAC exposes to the upstream management controller during enumeration. It provides a complete, self-describing declaration of the OAC's interface characteristics, enabling the upstream management controller to make an informed determination of hardware compatibility without requiring physical enumeration of all connected protocols.

The CID declares the following categories of information:

- **Connector population**: which connector positions (CONN0 through CONN6, CABLE) are physically populated on the OAC
- **Connector impedance**: the differential impedance class (85 ohms or 92 ohms) of each populated connector, which corresponds to the color-coded mechanical keying on the OAC connector
- **Power requirements**: the primary input voltage rail, Operational Power Level definitions (OPL-MAX, OPL-EFF, OPL-RED, OPL-EMG, OPL-SET), and minimum and maximum current draw
- **M-PESTI capability**: whether M-PESTI functionality is implemented on CONN0 Pin A1
- **High-speed signaling assignments**: per-lane protocol, direction, link subdivision topology, and physical pin mapping for each populated connector
- **Reference clocking**: frequency, type, direction, and lane associations for each reference clock
- **Vendor-defined discrete signals**: signal name, pin, direction, voltage level, pull termination requirements, driver type, default state, and operational role

CID content can be substantial for fully-populated OACs with per-lane pin mappings across all seven connectors. The CID is transmitted over the OAC Management USB 2.0 interface; minifying the JSON before storage reduces payload size and enumeration latency. 

Mechanical keying is the first line of defense for electrical safety, but it is not the only line of defense, and it is deliberately narrow. The keying defined in OCP Open Adapter Card Base Specification v0.9 Section 7.9.3.1 discriminates only between the +12 V DC and +50 V DC primary input voltage classes, and prevents a voltage-incompatible OAC from fully engaging a baseboard power position. It makes no other compatibility determination, and it cannot: keying is a physical feature with two defined states.

For every other class of incompatibility — a connector presenting UALink on one side and NVLink on the other, a lane count the platform cannot route, an impedance class mismatch, a reference clock the baseboard does not source, or a power envelope the slot cannot provision — the CID is the enforcement mechanism, and it is the only one. In that sense the CID is a substitute for mechanical keying, and is intended to be. This is safe because the primary busbar is not energized until after interoperability has been determined from the CID and the OAC has been configured through the Slot Configuration Data (SCD). An incompatible OAC that mates mechanically is therefore never powered beyond the auxiliary domain.

The CID does not remove the need for mechanical keying on the primary input voltage class, and mechanical keying does not remove the need for the CID. The two are complementary, and the input voltage class is the one attribute both enforce.

---

## 6. CID as a FRU File

### 6.1 General

The CID shall be published by the OAC's management controller as PLDM FRU data and retrieved by the upstream management controller using PLDM for FRU Data (DSP0257), over the MCTP session established on the OAC Management USB 2.0 interface (CONN0 Columns 10–11).

DSP0257 provides that aggregated FRU data is identified and formatted in the context of a FRU Data File, and that this context, together with the format of DMTF-specified FRU data files, is defined in FRU Data File. The CID shall be accessed by that method and by no other. The OAC shall expose the CID as a FRU Data File described by the File Descriptor PDR of Section 6.3, and an upstream management controller shall locate and retrieve it through that record. This specification defines no alternative access path to the CID, and an OAC shall not require one.

The CID shall be read-only from the perspective of the upstream management controller. An OAC shall not accept a write to the CID.

The CID should be stored in persistent, non-volatile storage on the OAC, so that it is available to be served as soon as the OAC's management controller is ready and does not have to be reconstructed on every retrieval. An OAC may instead generate the CID on demand from its own firmware configuration.

A CID generated on demand shall be deterministic for a given firmware configuration. An OAC shall not return differing CID content for the same hardware and firmware version, as the upstream management controller uses the CID to make slot energization decisions and a non-deterministic CID would undermine that evaluation.

The CID shall be retrievable whenever the OAC is in Operational State O3 or later. An OAC shall not require primary power to serve its CID.

The upstream management controller shall retrieve the CID before evaluating slot energization eligibility and before retrieving the Slot Configuration Definition (SCD), which is a separate FRU Data File published by the same OAC management controller.

### 6.2 Encoding

The CID shall be encoded in UTF-8 per ECMA-404. No byte order mark shall be present. The JSON document shall be syntactically valid per ECMA-404. Comments are not permitted; ECMA-404 defines no comment syntax, and a document containing `//` or `/* */` sequences outside a string literal is malformed.

The OAC shall publish the CID in either expanded format JSON or minified format JSON. Both are valid encodings of the CID. An upstream management controller shall accept either, and shall not reject a CID, or treat it as malformed, on the basis of its whitespace encoding.

Minified format is recommended for production CID files. The CID is transmitted over the OAC Management USB 2.0 interface, and removing optional whitespace reduces the transferred payload and the time taken to retrieve it; the saving grows with the size of the document. This is an optimization and nothing more. The encoding carries no semantic weight: a minified CID and its expanded counterpart that differ only in optional whitespace describe the same OAC, and an upstream management controller shall evaluate them identically.

The same encoding rules apply to the connector profile definition files of Section 8. A profile file published in the OAC CID project repository may be supplied in expanded or minified form, and a file name carrying the optional `-minified` suffix contains minified JSON, which is suitable for direct firmware storage. A minified profile file shall be functionally equivalent to its expanded counterpart — only the whitespace encoding differs. Both forms may coexist in the repository, and an implementation may use either; the minified form is the recommended choice for firmware integration.

### 6.3 File Classification and Access

> **WORK IN PROGRESS — subject to change by the OCP OAC workstream.**
>
> The whole of Section 6.3 is under active review. This covers the hard-coded `FileName` value, the
> match-on-name-then-open-by-identifier discovery sequence, and the File Descriptor PDR and sensor
> PDR field constraints that follow from them. An alternative approach has been raised in which an
> OAC publishes a metadata file enumerating the files it exposes, together with their identifiers and
> roles, and discovery proceeds from that file rather than from a well-known name. Resolving the
> question depends on the workstream's assessment of DMTF work currently in progress.
>
> The requirements below are stated normatively so that they can be implemented and tested today, and
> the field values collected in Annex B are scoped identically. Implementers should expect this
> mechanism to be revisited before this specification is published as final.

The CID shall be represented in the OAC's PDR repository by a File Descriptor PDR as defined in DSP0248, with EntityType set to Device File and FileClassification set to FRUDataFile. The file so described is a FRU Data File per DSP0257 and is retrieved as required by Section 6.1.

The OAC shall set the FileName field of that File Descriptor PDR, which is a strASCII string, to:

```
OAC_CID.json
```

An upstream management controller shall use that name to distinguish the CID from every other FRU Data File the OAC publishes, the Slot Configuration Definition among them, and shall not rely on PDR ordering to make that distinction.

FileName is how the CID is recognised; it is not how it is opened. The same File Descriptor PDR carries a FileIdentifier, a uint16 that DSP0248 defines as unique relative to the PLDM Terminus ID, and DSP0242 requires that value, rather than the name string, as the parameter to DfOpen, DfGetFileAttribute, and DfSetFileAttribute. An upstream management controller shall therefore match on FileName to find the record and then use the FileIdentifier from that same record to open the file. The OAC assigns the FileIdentifier; this specification fixes no value for it, and a controller shall not assume one.

The OAC shall set the FileCapabilities bitfield16 so that no write and no modification of the CID is permitted: FcWritesPermitted and ExWriteOpen shall both be zero.

The CID is a Fixed Length File in the sense of DSP0242 — read, not written, after creation, and of a size that does not vary while a given CID is being served — and an OAC shall treat it as one.

Fixed length constrains the file within a firmware revision. It does not constrain the file across firmware revisions. The size of the CID may change when a firmware update replaces it, and an OAC is neither required nor expected to preserve the previous size. Because DSP0242 equates a fixed-length file's size to the FileMaximumSize field of its File Descriptor PDR, the OAC shall set FileMaximumSize to the exact transferred size of the CID it is currently serving, and shall update that field whenever a firmware update replaces the CID with one of a different size.

DSP0242 requires the Device File State Sensor for a Fixed Length File and recommends the File Size Monitoring Sensor. This specification tightens both requirements: an OAC shall publish both sensors for the CID. The Device File State Sensor signals when the CID content has changed (e.g. following a firmware update), and the File Size Monitoring Sensor provides the exact current size for correct retrieval.

| Sensor | Kind | DSP0242 | This specification |
|--------|------|---------|--------------------|
| Device File State Sensor | State sensor implementing DSP0249 State Set 68 (Device File) | Shall, for a Fixed Length File | Shall. Reports the state of the file and signals that its content has been modified. |
| File Size Monitoring Sensor | Compact or Numeric sensor per DSP0242 | Should, for a Fixed Length File | Shall. Reports the current size of the CID in bytes, as transferred. |

An OAC shall not report the File is at Maximum Size state (State 3 of DSP0249 State Set 68) for the CID. A fixed-length file is always at its maximum size, and the state therefore carries no information; DSP0242 advises against supporting it for this file characteristic.

A File Size Monitoring Sensor published for the CID shall set BaseUnit to Bytes and UnitModifier to zero. If it is a Numeric sensor, RateUnit shall be None, Offset shall be zero, and Resolution shall be 1.00; if it is a Compact Numeric sensor, OccurrenceRate shall be No Occurrence Rate.

A sensor is associated with the CID by carrying the same entity identification as the CID's File Descriptor PDR: the same EntityType, the same EntityInstanceNumber, and the same ContainerID. The OAC shall set all three accordingly on both sensor PDRs.

---

## 7. CID JSON Document Structure

### 7.1 General

The CID is a single JSON object. The root key of the JSON document shall be `"oac_cid"`. The value associated with `"oac_cid"` shall be a JSON object containing three sections: `"metadata"`, `"power"`, and `"connectors"`. These three sections shall appear in this order within the `"oac_cid"` object. Additional top-level keys within `"oac_cid"` are permitted for vendor extensions but shall use a vendor-namespaced prefix of the form `"vendor_<name>_"`. The upstream management controller shall ignore unrecognized keys.

The complete CID document structure is:

```json
{
  "oac_cid": {
    "metadata": { ... },
    "power": { ... },
    "connectors": [ ... ]
  }
}
```

### 7.2 metadata Object

The `"metadata"` object shall be present. It contains fields that identify the schema version and the OAC specification revision the OAC was designed against.

**Table 7.2-1: metadata Object Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `schema_version` | string | Required | e.g. `"0.9"` | Version of the CID schema this document conforms to. Shall match a published or draft version identifier of this specification. |
| `oac_spec_revision` | string | Required | e.g. `"0.9"` | OAC Base Specification revision the OAC was designed against. |
| `description` | string | Optional | Free text | Human-readable summary of OAC function, protocol mix, and power profile. Shall not be relied upon by automated systems for compatibility evaluation. |
| `iana_pen` | integer | Optional | > 0 | The IANA Private Enterprise Number (PEN) of the organization responsible for the CID and any associated `platform_token` value. When declared, `platform_token` shall only be present if `iana_pen` is also present. See Section 7.2.1. |
| `platform_token` | string | Optional | Vendor-defined | A vendor-defined identifier used as a simplified interoperability validation token for tightly coupled, pre-validated baseboard and OAC pairings. Requires `iana_pen` to be declared in the same metadata object. See Section 7.2.2. |

The value of `schema_version` shall be a string recognized by the upstream management controller. If a upstream management controller receives a CID with a `schema_version` value it does not recognize, it shall log a compatibility warning and may decline to enable primary power.

#### 7.2.1 iana_pen (Optional)

The `iana_pen` field is an optional integer field that declares the IANA Private Enterprise Number (PEN) of the organization responsible for the CID and any associated `platform_token`. IANA PENs are assigned by the Internet Assigned Numbers Authority and serve as globally unique, authoritative identifiers for organizations. The IANA PEN registry is publicly accessible at https://www.iana.org/assignments/enterprise-numbers/.

The `iana_pen` field may be declared independently of `platform_token` to identify the enterprise responsible for the CID. When `platform_token` is also declared, `iana_pen` shall be present; a CID containing `platform_token` without `iana_pen` is malformed. When both fields are present, the upstream management controller may use the PEN to confirm that the `platform_token` value was issued by the enterprise identified by the PEN, providing a namespace that prevents token collision between different organizations. The `iana_pen` field itself does not constitute a compatibility validation mechanism and shall not be used as a substitute for the standard CID validation sequence defined in Section 9.3.

#### 7.2.2 platform_token (Optional)

The `platform_token` field is an optional vendor-defined string that enables a simplified compatibility validation mechanism for tightly coupled deployments — that is, for validated pairings of a specific baseboard with a specific OAC. Its purpose is to reduce bring-up complexity and time-to-power in scenarios where the baseboard and the OAC have been co-designed, co-validated, or explicitly pre-approved as a supported combination, and where full field-by-field CID compatibility evaluation is not required.

A validated pairing is defined by the act of validation, not by the ownership of the two parts. A baseboard vendor that validates OACs from two different OAC vendors against the same baseboard has created two validated pairings, and may issue a token for each; an OAC vendor that validates its card against several baseboards has done the same. Nothing in this section is intended to prevent that. What the mechanism does assume is that some organization has taken responsibility for validating each combination in which a token is honored.

When a upstream management controller receives a CID containing a `platform_token`, it may compare the token value against a set of internally known or pre-configured approved token values. If the token matches an approved value, the upstream management controller may bypass or abbreviate the standard CID validation sequence defined in Section 9.3 and proceed directly to primary power enablement.

Implementations that use `platform_token` as the sole or primary interoperability validation mechanism shall comply with all of the following constraints:

- The platform shall be a co-designed, co-validated, or explicitly approved matched set in which the baseboard and the OAC have been tested together by the same organization or under an explicit approval agreement.
- The upstream management controller implementation shall treat an unrecognized `platform_token` value as if the field were absent and shall fall back to the full CID validation sequence defined in Section 9.3.
- The `platform_token` field shall not be present in a CID unless `iana_pen` is also declared in the same `metadata` object. A CID containing `platform_token` without a corresponding `iana_pen` shall be treated as malformed; the upstream management controller shall log a warning and fall back to the full CID validation sequence.

It should be noted that implementations using `platform_token` as the sole or primary interoperability validation mechanism should also note the following. These are consequences of the mechanism rather than constraints upon it, and they do not prohibit any deployment:

- Multi-vendor interoperability — that is, the use of an OAC from a vendor other than the one that defined the token, or a baseboard from a vendor other than the one that validates the token — is not guaranteed when this field is used as the primary compatibility check, because the token conveys only that some specific combination was validated, not which one.
- Multi-generation interoperability — that is, the use of a `platform_token` value defined for one OAC generation with a baseboard or an OAC of a different generation — should not be assumed without explicit re-validation by the organization that issued the token.
- Deployments in which the baseboard and the OAC are procured independently on the open market, and in which general OAC interoperability is therefore required, should use the full CID validation sequence defined in Section 9.3 rather than relying on `platform_token`.

The format and content of the token value are vendor-defined. Common implementations include a hash of validated platform identifiers, a platform model string, or a deployment-specific opaque string. The token value should be sufficiently specific to distinguish between distinct validated combinations and should not be reused across combinations that have not been jointly validated.

### 7.3 power Object

The `"power"` object shall be present. It contains one mandatory sub-object, `"primary"`, which declares the OAC's primary power requirements and Operational Power Level definitions.

#### 7.3.1 power.primary Object

The `"primary"` object shall be present within `"power"`. It declares the OAC's primary power requirements and the set of Operational Power Levels (OPLs) supported by the OAC, as defined in OCP OAC Base Specification v0.9 Section 10.1.2.

The OAC primary power connector is defined in OCP OAC Base Specification v0.9 Section 9.3 in two variants that determine the maximum continuous current the busbar interface may carry:

| Connector Variant | Rated Current | Derated Continuous Current (80%) | Compatible Form Factors |
|-------------------|---------------|----------------------------------|-------------------------|
| `"100A"` (4KW, BK100) | 100 A | 80 A | Single-wide, double-wide, double-wide offset |
| `"125A"` (5KW, BK125) | 125 A | 100 A | Double-wide, double-wide offset only |

The `connector_type` field declares which of these two variants is implemented on the OAC. The upstream management controller shall use this value, together with `input_voltage`, to determine the maximum power the OAC may draw at the busbar interface and to verify that the host slot can physically support the declared connector variant.

**Table 7.3.1-1: power.primary Object Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `input_voltage` | string | Required | `"+12V"`, `"+50V"` | Nominal primary input voltage with sign prefix. Mechanical keying defined in OCP OAC v0.9 ensures that only compatible voltage pairs are physically matable; this field provides the software-visible declaration of the same attribute. |
| `connector_type` | string | Required | `"100A"`, `"125A"` | Primary power connector variant implemented on the OAC, as defined in OCP OAC Base Specification v0.9 Section 9.3. `"100A"` corresponds to the 4KW BK100 variant (80 A derated continuous, compatible with all form factors). `"125A"` corresponds to the 5KW BK125 variant (100 A derated continuous, double-wide and double-wide offset form factors only). The upstream management controller shall verify that the host slot supports the declared connector variant before enabling primary power. |
| `opl_max_w` | number | Required | > 0.0 | Maximum Performance Operational Power Level (OPL-MAX) in watts. Vendor-defined operating profile intended to deliver the maximum validated performance supported by the OAC. Power excursions above this sustained level are permitted per OCP OAC v0.9 Section 10.1.4. Shall not exceed the continuous power capacity implied by `connector_type` and `input_voltage`. |
| `opl_emg_w` | number | Required | > 0.0, <= `opl_max_w` | Emergency Power Reduction Operational Power Level (OPL-EMG) in watts. The lowest validated operational power level supported by the OAC. The OAC shall transition to this level upon assertion of OAC_PWRBRK#. |
| `opl_eff_w` | number | Optional | <= `opl_max_w`, >= `opl_emg_w` | Efficiency Optimized Operational Power Level (OPL-EFF) in watts. Vendor-defined operating profile intended to optimize performance-per-watt. If absent, no OPL-EFF profile is defined for this OAC. |
| `opl_red_w` | number | Optional | <= `opl_eff_w` (if present) or <= `opl_max_w`, >= `opl_emg_w` | Reduced Power Operational Power Level (OPL-RED) in watts. Vendor-defined operating profile for operation under significant platform power constraints. If absent, no OPL-RED profile is defined for this OAC. |
| `opl_set_min_w` | number | Optional | >= `opl_emg_w`, <= `opl_max_w` | Minimum value in watts that may be configured for the user-configurable power level (OPL-SET). No corresponding maximum is declared: the upper bound of the configurable range is always `opl_max_w`, because a settable level above the OAC's maximum validated operating point would not be a valid operating point. If absent, OPL-SET is not supported by this OAC. |

The OPL hierarchy shall satisfy the following ordering constraint:

```
opl_max_w >= opl_eff_w >= opl_red_w >= opl_emg_w
```

Where optional OPL fields are absent, the ordering constraint applies only to those OPLs that are present. Where `opl_set_min_w` is declared, the configurable OPL-SET range is `opl_set_min_w` through `opl_max_w` inclusive. The upstream management controller shall use the declared OPL values to evaluate power budget feasibility before enabling primary power.

### 7.4 connectors Array

The value of `"connectors"` shall be a JSON array. Each element of the array shall be a JSON object describing one connector position. CONN0 shall always be present in the array with `populated` set to `true`. CONN1 through CONN6 and CABLE shall be listed in the array only if the corresponding physical connector is populated on the OAC. Connector positions absent from the array shall be treated as not populated by the upstream management controller. The order of elements within the array should follow the natural connector index order: CONN0, CONN1, CONN2, CONN3, CONN4, CONN5, CONN6, CABLE.

#### 7.4.1 Connector Top-Level Fields

**Table 7.4.1-1: Connector Object Top-Level Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `id` | string | Required | `"CONN0"` through `"CONN6"`, `"CABLE"` | Connector position identifier. Each value shall be unique within the `connectors` array. |
| `populated` | boolean | Required | `true` or `false` | `true` if a physical connector is installed at this position on the OAC. An element with `populated` set to `false` may be included for informational purposes but shall convey no signaling or power information. |
| `impedance_ohm` | integer | Required if `populated=true` | `85` or `92` | Target differential impedance in ohms. The value `85` corresponds to the black connector variant used for PCIe-class and USB-class high-speed standards. The value `92` corresponds to the white connector variant used for Ethernet-class standards. |
| `mpesti_capable` | boolean | Required on CONN0 | `true` or `false` | Declares whether Pin A1 on CONN0 is overloaded to carry M-PESTI (Modular-Peripheral Sideband Tunneling Interface) in addition to presence detect, as permitted by OCP OAC Base Specification v0.9 Section 9.4.8.2.12.1. `true` — Pin A1 carries M-PESTI in addition to presence detect. `false` — Pin A1 serves presence detect alone through a GND tie, per OCP OAC Base Specification v0.9 Section 9.4.8.2.12. This field shall be present in the CONN0 connector object and shall not appear in the CONN1 through CONN6 or CABLE connector objects. See Section 7.4.2. |
| `connector_profile` | string | Optional | OCP-ratified profile identifier | References an OCP-ratified connector profile that defines the `high_speed_lanes`, `clocking`, and `discrete_signals` assignments for this connector position. When `connector_profile` is present, the `high_speed_lanes`, `clocking`, and `discrete_signals` sections shall not be present in the connector object; when it is absent, those sections follow the presence requirements stated in Sections 7.4.3, 7.4.4, and 7.4.5. Connector profiles, their identifiers, their document format, and the rules governing their use are defined in Section 8. |

#### 7.4.2 mpesti_capable Field

Presence detection is neither optional nor negotiable, and nothing in the CID makes it so. Every populated connector asserts its corresponding `OAC_PRSNT[0:6]#` signal by tying Pin A1 to GND on the OAC, as specified in OCP OAC Base Specification v0.9 Section 9.4.8.2.12. The pin, the signal name, the active-low sense, and the assertion method are fixed by the Base Specification for every connector position, are identical on every conformant OAC, and are therefore never declared in the CID.

One property of Pin A1 is not fixed by the Base Specification. On CONN0, and on CONN0 alone, Pin A1 may additionally be overloaded with M-PESTI (Modular-Peripheral Sideband Tunneling Interface) functionality, as permitted by OCP OAC Base Specification v0.9 Section 9.4.8.2.12.1. The `"mpesti_capable"` field exists to declare that overload, and it is the only place in the CID where the overload can be declared.

The field is a direct member of the connector object and is defined in Table 7.4.1-1 with the other top-level connector fields. It shall be present in the CONN0 connector object and shall not appear in the CONN1 through CONN6 or CABLE connector objects, because the M-PESTI overload is defined only for CONN0. A connector object other than CONN0 that declares `"mpesti_capable"` shall be treated as malformed and the slot shall not be energized.

When `"mpesti_capable"` is `true`, Pin A1 on CONN0 carries M-PESTI in addition to presence detect. When it is `false`, Pin A1 on CONN0 serves presence detect alone through a GND tie, per OCP OAC Base Specification v0.9 Section 9.4.8.2.12. Presence detect itself is unaffected in either case: the GND tie and the resulting `OAC_PRSNT0#` assertion are present regardless of the value of this field, and a `false` value is a positive statement that the overload is not implemented rather than an absence of information.

#### 7.4.3 high_speed_lanes Object

The presence of `"high_speed_lanes"` is determined by whether the connector declares a `connector_profile`, and is not a free choice:

- If the connector object declares a `connector_profile`, `"high_speed_lanes"` shall not be present. The referenced profile supplies the high-speed lane definition in its entirety, and the mutual exclusivity rule of Section 8.2 applies.
- If the connector object does not declare a `connector_profile` and the connector carries high-speed differential signals, `"high_speed_lanes"` shall be present. There is no other means by which those signals can be described to the upstream management controller.
- If the connector object does not declare a `connector_profile` and the connector carries no high-speed differential signals, `"high_speed_lanes"` shall be absent, and the connector is presumed to carry only sideband, power, or discrete signals.

`"high_speed_lanes"` is therefore optional only in the sense that a conformant connector object may omit it. It is never optional in the sense that an OAC carrying high-speed signals may decline to describe them.

Its value is either a single protocol group object or an array of protocol group objects. An array shall be used when the connector carries lanes of more than one protocol (for example, 8 lanes of PCIe and 8 lanes of Ethernet on the same 16-lane physical connector). Each element of the array is a self-contained protocol group with its own protocol, lane assignments, and optional link subdivision. If the value is a single object, it is treated equivalently to a one-element array.

The sum of `total_lanes` across all protocol group elements should not exceed the physical lane capacity of the connector. Additionally, the number of protocol groups within a single connector object shall not exceed 8. This limit ensures compatibility with the uint32 SCD effecter encoding used to communicate lane subdivision selections to the OAC, which reserves one 4-bit nibble per protocol group. No more than 8 protocol groups shall be declared on any connector, regardless of physical lane capacity.

A protocol group is described in two parts. Table 7.4.3-1 defines the fields of the protocol group itself, which describe the group as a whole. Table 7.4.3-2 defines the fields of each element of the group's `lanes` array, which describe one individual lane and its pin assignment. The two tables are distinct; group-level fields do not appear on a lane, and lane-level fields do not appear on a group.

**Table 7.4.3-1: high_speed_lanes Protocol Group Object Fields**

Each element of the `high_speed_lanes` array (or the single object when only one protocol is used) is a protocol group defined by the following fields:

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `name` | string | Required | snake_case: lowercase letters, digits, and underscores only (e.g. `"pcie_primary"`, `"eth_fabric"`) | Human-readable identifier for this protocol group within the connector. Allows upstream management controllers, diagnostic tools, and CID authoring software to reference specific protocol groups by a stable, descriptive label. The value shall follow snake_case convention: lowercase letters with underscores separating words. Group names shall be unique within a connector's `high_speed_lanes` array. |
| `protocol` | string | Required | See Table 7.5-1 | Protocol and generation carried on the high-speed lanes of this connector. Allowed values include PCIe Gen4 through Gen7; UALink 1.0, 2.0, and 3.0; UALoE 200G; CXL 1.1/2.0/3.0 and CXL 4.0; NVLink 4.0, 5.0, and 6.0; Ethernet 200G, 400G, and 800G; USB 2.0, USB 3.2 Gen1, USB 3.2 Gen2, USB4 Gen2, and USB4 Gen3. |
| `link_direction` | string | Required | `"INBOUND"`, `"OUTBOUND"` | Primary direction of data flow on this protocol group from the baseboard perspective. `"INBOUND"` — signal flows from the baseboard into the OAC (e.g. a PCIe endpoint or switch upstream port). `"OUTBOUND"` — signal flows from the OAC toward a fabric peer or downstream device (e.g. a PCIe root port or switch downstream port). |
| `total_lanes` | integer | Required | 1 through 32 | Total number of high-speed lane positions allocated to this connector (one-directional count; the physical implementation includes both TX and RX for each lane). Each OAC connector supports a maximum of 16 lanes; a value up to 32 is reserved for future multi-connector aggregation definitions. |
| `minimum_lanes` | integer | Optional | 1 through `total_lanes` | Vendor-declared minimum lane count required for the OAC to establish a functional link on this protocol group. When present, this field represents a vendor-imposed operational floor beyond the protocol baseline: the upstream management controller should block slot energization if the number of lanes electrically routed from the baseboard to the connector is less than this value. When absent, the OAC shall operate with any lane count the host negotiates, down to the protocol minimum. Vendors should only declare `minimum_lanes` when a specific minimum bandwidth is required for correct OAC operation. |
| `lanes` | array of objects | Required | One element per lane position, per direction | Pin assignments for the individual lanes of this protocol group. Each element is defined by Table 7.4.3-2. The ordering rule of Section 7.6 item 3 applies to this array. |

**Table 7.4.3-2: lanes Array Element Fields**

Each element of a protocol group's `lanes` array describes one lane in one direction:

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `lane_index` | integer | Required | 0 through (`total_lanes` minus 1) | Zero-based index of the lane. Lane indices restart at 0 for each direction within a given connector. |
| `direction` | string | Required | `"TX"`, `"RX"`, or `"BI"` | Direction of this lane from the OAC's perspective. `"TX"` — the OAC transmits; `"RX"` — the OAC receives; `"BI"` — bidirectional, used for half-duplex protocols such as USB 2.0 whose single D+/D− differential pair carries traffic in both directions. |
| `pin_positive` | string | Required | e.g. `"C1"` | Label of the physical pin carrying the positive differential signal for this lane. |
| `pin_negative` | string | Required | e.g. `"D1"` | Label of the physical pin carrying the negative differential signal for this lane. |

> **NOTE:** A lane's required status is implicitly defined by the `minimum_lanes` field of the enclosing protocol group. When `minimum_lanes` is present, required lanes always begin at lane index 0 and form a contiguous block: lanes 0 through (`minimum_lanes` − 1) are required, and all remaining lanes are optional. For example, if `minimum_lanes` = 4 on a 16-lane group, then lanes 0–3 (both RX and TX) must be connected for functional operation, while lanes 4–15 are negotiated performance lanes. When `minimum_lanes` is absent, no vendor-imposed floor applies and all lanes are treated as negotiated beyond the protocol baseline. No explicit `required` field is present on individual lane objects; the upstream management controller shall derive each lane's required status from `minimum_lanes` using this rule.


#### 7.4.3.1 Protocol Generation Compatibility

The `protocol` field declares the maximum operating speed or generation that the OAC is designed to support on a given protocol group. Many high-speed protocols support link speed negotiation, allowing a link to train to a lower generation when the baseboard or attached device does not support the declared maximum generation.

The upstream management controller shall apply the compatibility hierarchy defined in Table 7.4.3.1-1 when evaluating whether a protocol group's `protocol` value is compatible with the platform's capabilities. Protocol backwards compatibility is bidirectional: a link negotiates to the highest generation supported by both the OAC and the platform. Therefore, a protocol group declared by the OAC shall be considered compatible with the platform if the platform supports **any generation within the same protocol family** as the declared `protocol` value — whether that generation is older or newer. The link will train to the highest common generation between the two endpoints. For example, a PCIe Gen6 OAC is compatible with a PCIe Gen4, Gen5, Gen6, or Gen7 platform: on a Gen4 or Gen5 platform the OAC negotiates down to the platform's generation; on a Gen7 platform the platform negotiates down to the OAC's generation. In all cases a functional link is established at the highest mutually supported speed.

**Table 7.4.3.1-1: Protocol Backwards Compatibility Hierarchy**

| Protocol Family | Compatibility Chain (highest to lowest) | Notes |
|----------------|----------------------------------------|-------|
| PCIe | Gen7 → Gen6 → Gen5 → Gen4 | Each generation negotiates down to the lower generation at the PHY level. A Gen6 OAC is compatible on a Gen7 platform (operates at Gen6). |
| CXL | CXL 4.0 → CXL 3.0 → CXL 2.0 → CXL 1.1 | CXL is built on the PCIe physical layer and inherits PCIe link speed negotiation. |
| UALink | UALink 3.0 → UALink 2.0 → UALink 1.0 | UALink generations are intended to be compatible within the family per the UALink specification. Implementors should verify interoperability against the applicable UALink specification for the specific generations involved. |
| USB SuperSpeed | USB4 Gen3 → USB4 Gen2 → USB 3.2 Gen2 → USB 3.2 Gen1 | SuperSpeed differential pairs (SSTX+/SSTX−, SSRX+/SSRX−) used by USB 3.x and USB4. PHY-level speed negotiation within this family is well-defined. |
| USB 2.0 | None | Electrically distinct single differential pair (D+/D−) operating at up to 480 Mbps. USB 2.0 lanes are not interchangeable with USB SuperSpeed lanes and shall not be treated as compatible with USB SuperSpeed protocol groups. An exact match is required. |
| NVLink | None | NVLink generations are not backwards compatible. Each generation requires matching silicon on both ends of the link. |
| Ethernet | None | Ethernet speed variants (200G, 400G, 800G) do not negotiate down at the PHY layer in the same manner. Link speed compatibility is managed by higher-layer configuration outside the scope of the CID. |
| UALoE | None | UALoE 200G does not define a backwards compatibility fallback within the CID scope. |

For protocol families with a defined compatibility chain in Table 7.4.3.1-1, the bidirectional rule above applies: any generation within the chain is considered compatible. For protocol families listed as **None** in the Compatibility Chain column (NVLink, Ethernet, UALoE), no cross-generation negotiation is defined within the scope of this specification. For these protocols, the upstream management controller shall require an exact match between the OAC's declared `protocol` value and the platform's supported protocol. If no match is found — either because the platform supports no generation of the declared protocol family (for chained protocols), or because the exact protocol string is not supported (for non-chained protocols) — the upstream management controller shall treat the protocol group as incompatible and shall not enable primary busbar power unless all mandatory protocol groups on the connector are otherwise satisfied.

The compatibility information in Table 7.4.3.1-1 is provided as guidance to assist upstream management controller implementations in evaluating CID declarations. The definitive authority on protocol version negotiation, interoperability, and link training behavior for each protocol family is the respective protocol specification (e.g. PCI Express Base Specification, CXL Specification, USB Specification). In any case of conflict between Table 7.4.3.1-1 and the applicable protocol specification, the protocol specification shall take precedence.

#### 7.4.4 clocking Array

The `"clocking"` array is optional and shall be present within a connector object if and only if that connector carries reference clock signals. Each element of the array describes one reference clock. A connector object shall not declare more than **16** clock signals; implementations that encounter a `clocking` array with more than 16 elements shall treat the connector as malformed.

**Table 7.4.4-1: clocking Array Element Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `clock_id` | string | Required | e.g. `"REFCLK0"` | Unique identifier for this clock within the connector. |
| `clock_type` | string | Required | `"REFCLK_DIFF"` or `"REFCLK_SINGLE"` | Whether the reference clock is a differential pair or a single-ended signal. |
| `frequency_mhz` | number | Required | > 0.0 | Nominal clock frequency in megahertz (e.g., `100.0` for PCIe and UALink, `156.25` for Ethernet). |
| `pin_positive` | string | Required if `clock_type="REFCLK_DIFF"`, omit otherwise | e.g. `"E1"` | Positive pin of the differential clock pair. |
| `pin_negative` | string | Required if `clock_type="REFCLK_DIFF"`, omit otherwise | e.g. `"F1"` | Negative pin of the differential clock pair. |
| `pin` | string | Required if `clock_type="REFCLK_SINGLE"`, omit otherwise | e.g. `"G1"` | Signal pin for a single-ended reference clock. |
| `direction` | string | Required | `"INPUT"` or `"OUTPUT"` | Direction of the reference clock from the OAC's perspective. `"INPUT"` indicates that the baseboard provides the clock to the OAC. `"OUTPUT"` indicates that the OAC sources the clock. |
| `associated_lanes` | array of integers | Optional | Valid lane indices | Lane indices that this reference clock serves. An empty array (`[]`) indicates that the clock is not associated with specific lanes (e.g., a system reference). |
| `required` | boolean | Required | `true` or `false` | `true` if this clock must be present and valid for the connector to operate. |
| `ssc_supported` | boolean | Required | `true` or `false` | `true` if this clock supports Spread Spectrum Clocking (SSC). Applies to both `INPUT` and `OUTPUT` clocks. |
| `description` | string | Optional | Free text | Informational description of the reference clock and its role. |


#### 7.4.5 discrete_signals Array

The `"discrete_signals"` array is optional and shall be present within a connector object if and only if that connector carries vendor-defined or protocol-defined discrete (non-differential, non-clock) signals. Each element of the array describes one discrete signal.

Vendor-defined signal names shall use the prefix `"VENDOR_"`. Active-low signals shall use the suffix `"#"` in the signal name. Signal names that do not originate from vendor extension and that are defined in OCP OAC v0.9 shall use the signal name as specified in that document.

**Table 7.4.5-1: discrete_signals Array Element Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `signal_name` | string | Required | Vendor-defined names shall use `VENDOR_` prefix; active-low signals shall end with `#` | Name of the discrete signal. |
| `pin` | string | Required | e.g. `"H3"` | Physical pin carrying this signal. |
| `direction` | string | Required | `"INPUT"` or `"OUTPUT"` | Direction from the OAC's perspective. `"INPUT"` indicates that the baseboard drives the signal into the OAC. `"OUTPUT"` indicates that the OAC drives the signal. |
| `active_level` | string | Required | `"ACTIVE_LOW"` or `"ACTIVE_HIGH"` | Logic level at which the signal is considered asserted. |
| `voltage_level_v` | number | Required | e.g. `1.8`, `3.3` | Nominal signal voltage level in volts. |
| `driver_type` | string | Required | `"PUSH_PULL"` or `"OPEN_DRAIN"` | Output driver type for this signal. `"PUSH_PULL"` indicates a totem-pole driver that actively drives both logic levels. `"OPEN_DRAIN"` indicates an open-drain driver that pulls low when asserted and requires external pull-up termination when deasserted. |
| `default_state` | string | Required | `"HIGH"`, `"LOW"`, `"HIZ"` | Default logic state of this signal when it is not actively asserted. `"HIGH"` indicates the signal rests at logic high. `"LOW"` indicates the signal rests at logic low. `"HIZ"` indicates the signal is high-impedance when not driven. |
| `pullup_required` | boolean | Optional | `true` or `false` | `true` if the baseboard is required to provide an external pull-up resistor on this signal. Applicable when `driver_type` is `"OPEN_DRAIN"` or when the signal is an input that requires a defined high state. If absent, no pull-up is required. |
| `pullup_voltage_v` | number | Required if `pullup_required=true` | > 0.0 | Pull-up voltage in volts that the baseboard shall apply. |
| `pullup_kohm` | number | Optional | > 0.0 | Recommended pull-up resistance in kilohms. If absent and `pullup_required` is `true`, the baseboard shall select a pull-up value appropriate for the `voltage_level_v` and `pullup_voltage_v`. |
| `pulldown_required` | boolean | Optional | `true` or `false` | `true` if the baseboard is required to provide an external pull-down resistor on this signal. Applicable when the signal is an input or output that requires a defined low state without active drive. If absent, no pull-down is required. |
| `pulldown_voltage_v` | number | Required if `pulldown_required=true` | >= 0.0 | Pull-down voltage in volts (typically 0 V / GND) that the baseboard shall apply. |
| `pulldown_kohm` | number | Optional | > 0.0 | Recommended pull-down resistance in kilohms. If absent and `pulldown_required` is `true`, the baseboard shall select a pull-down value appropriate for the `voltage_level_v`. |
| `required` | boolean | Required | `true` or `false` | `true` if the baseboard must implement this signal for the OAC to operate correctly. |
| `description` | string | Optional | Free text | Informational description of the signal and its function. |

Note: `pullup_required` and `pulldown_required` are mutually exclusive. A single signal shall not require both a pull-up and a pull-down termination simultaneously.

### 7.5 Enumerated Values Summary

**Table 7.5-1: Enumerated String Field Values**

| Field | Allowed Values |
|-------|----------------|
| `power.primary.input_voltage` | `"+12V"`, `"+50V"` |
| `power.primary.connector_type` | `"100A"`, `"125A"` |
| `connectors[].id` | `"CONN0"`, `"CONN1"`, `"CONN2"`, `"CONN3"`, `"CONN4"`, `"CONN5"`, `"CONN6"`, `"CABLE"` |
| `connectors[].impedance_ohm` | `85`, `92` (integer, not string) |
| `connectors[].high_speed_lanes.protocol` | `"PCIe Gen4"`, `"PCIe Gen5"`, `"PCIe Gen6"`, `"PCIe Gen7"`, `"UALink 1.0"`, `"UALink 2.0"`, `"UALink 3.0"`, `"UALoE 200G"`, `"CXL 1.1/2.0/3.0"`, `"CXL 4.0"`, `"NVLINK 6.0"`, `"NVLink 4.0"`, `"NVLink 5.0"`, `"Ethernet 200G"`, `"Ethernet 400G"`, `"Ethernet 800G"`, `"USB 2.0"`, `"USB 3.2 Gen1"`, `"USB 3.2 Gen2"`, `"USB4 Gen2"`, `"USB4 Gen3"` |
| `connectors[].high_speed_lanes.link_direction` | `"INBOUND"`, `"OUTBOUND"` |
| `connectors[].high_speed_lanes.lanes[].direction` | `"TX"`, `"RX"`, `"BI"` |
| `connectors[].clocking[].clock_type` | `"REFCLK_DIFF"`, `"REFCLK_SINGLE"` |
| `connectors[].clocking[].direction` | `"INPUT"`, `"OUTPUT"` |
| `connectors[].discrete_signals[].direction` | `"INPUT"`, `"OUTPUT"` |
| `connectors[].discrete_signals[].active_level` | `"ACTIVE_LOW"`, `"ACTIVE_HIGH"` |
| `connectors[].discrete_signals[].driver_type` | `"PUSH_PULL"`, `"OPEN_DRAIN"` |
| `connectors[].discrete_signals[].default_state` | `"HIGH"`, `"LOW"`, `"HIZ"` |

### 7.6 Field Naming and Ordering Conventions

The following ordering conventions shall be observed in all conformant CID documents:

1. The section order within `"oac_cid"` shall be: `"metadata"`, then `"power"`, then `"connectors"`.
2. `"CONN0"` shall always appear as the first element of the `"connectors"` array. Subsequent connectors should appear in ascending index order: CONN1, CONN2, CONN3, CONN4, CONN5, CONN6, CABLE.
3. Within a connector's `"lanes"` array, all RX entries (in ascending `lane_index` order) shall precede all TX entries (in ascending `lane_index` order).
4. Optional fields that are absent from a CID document shall be treated as absent (not as null or zero) by the upstream management controller. A JSON `null` value for a field defined in this specification is not equivalent to field absence and shall be treated as a malformed CID.
5. JSON keys shall use snake_case (underscore-separated lowercase). CamelCase or hyphenated key names are not conformant.
6. Within a connector object, the top-level fields shall appear in the order `id`, `populated`, `impedance_ohm`, `mpesti_capable` (CONN0 only), `connector_profile`, followed by the signal sections in the order `high_speed_lanes`, `clocking`, `discrete_signals`. A connector object that declares a `connector_profile` contains none of `high_speed_lanes`, `clocking`, or `discrete_signals`, per Section 8.2; their absence is not an error.

---

## 8. Connector Profile JSON Document Structure

### 8.1 General

A connector profile is a standalone JSON document, ratified by the OCP OAC workstream, that defines
the complete signal assignment of one connector position: its high-speed lanes, its reference clocks,
and its discrete signals. A CID references a profile by identifier instead of restating that
assignment inline.

The mechanism exists because the signal assignment of a connector is by a wide margin the largest
part of a CID, and because most OAC designs use a small number of conventional assignments. A CID
that references two ratified profiles is a fraction of the size of the equivalent CID that enumerates
every lane and pin, which matters when the document is transferred over the management USB 2.0 link
and stored in OAC firmware. It also removes a class of transcription error, since a ratified profile
is validated once by the workstream rather than once per vendor.

A profile document describes the same signal sections as a connector object in Section 7 and uses the
same field definitions, with the differences stated in Section 8.4. The encoding rules of Section 6.2
apply to profile documents as they do to the CID itself.

This section defines how a CID references a profile (Section 8.2), how profile identifiers are formed
(Section 8.3), what a profile document contains (Section 8.4), and which connector positions a given
profile may be applied to (Section 8.5).

### 8.2 Referencing a Profile from a CID

A CID references a profile by placing the profile identifier in the `connector_profile` field of a
connector object, as defined in Table 7.4.1-1.

When `connector_profile` is present on a connector object, the connector's signal definition is
provided entirely by the referenced OCP-ratified profile. The `high_speed_lanes`, `clocking`, and
`discrete_signals` sections shall not be present in the connector object. The use of
`connector_profile` is mutually exclusive with explicit signal definitions on the same connector.

If an OAC's connector configuration matches an OCP-ratified profile exactly, the OAC shall reference
the profile by identifier and omit all explicit signal sections. If the OAC's connector configuration
does not match any available OCP-ratified profile, the OAC shall define `high_speed_lanes`,
`clocking`, and `discrete_signals` explicitly in the CID and shall not use `connector_profile`.

The reference is whole or not at all. No mechanism is defined by this specification for a CID to
amend, extend, or partially override a referenced profile. A connector either takes the profile
exactly as ratified, or declares its signals explicitly.

The upstream management controller shall reject any CID connector object that contains both a
`connector_profile` field and any of the `high_speed_lanes`, `clocking`, or `discrete_signals`
sections. Such a connector object shall be treated as malformed and the slot shall not be energized.

### 8.3 Profile Identifiers

Connector profiles are defined and maintained exclusively by the OCP OAC workstream. All profile
identifiers shall use the prefix `OAC-PROF-` and follow the naming convention:

```
OAC-PROF-<CONN0|CONN1..CONN6|CONN|CABLE>-<proto1>-x<lanes1>-<dir1>[-<proto2>-x<lanes2>-<dir2>]-v<n>[-minified]
```

The connector segment names the connector position or positions the profile targets. It shall
be `CONN0` for a profile targeting CONN0, which has nine assignable pin columns; `CONN1`
through `CONN6` for a profile targeting one specific position among CONN1 through CONN6, each
of which has eight assignable pin columns; `CONN` for a profile applicable to more than one of
the CONN1 through CONN6 positions; and `CABLE` for a profile targeting the CABLE connector
position.

The segment is not independent information. It shall be derived from the profile's
`applicable_conns` field as defined in Table 8.4-1. Where `applicable_conns` is `["CONN0"]`
the segment shall be `CONN0`. Where it is a single-token array naming one position among CONN1
through CONN6, the segment shall be that position — `["CONN6"]` yields `CONN6`. Where it
names more than one of the CONN1 through CONN6 positions, including by the `"CONN1-6"`
shorthand, the segment shall be `CONN`. Where it is `["CABLE"]` the segment shall be `CABLE`.
A profile whose connector segment and `applicable_conns` value disagree shall be treated as
unrecognized.

A profile ratified against one specific position carries that position in its identifier even
though CONN1 through CONN6 share a pin field and would each accept it physically. The
identifier records what the profile was ratified for, not everything it would fit.

The following abbreviations shall be used for protocol names within `OAC-PROF-` identifiers. The
direction suffix shall be `IN` for `"INBOUND"` and `OUT` for `"OUTBOUND"`.

**Table 8.3-1: Protocol Name Abbreviations for Profile Identifiers**

| Protocol (CID `protocol` field) | Abbreviation |
|----------------------------------|-------------|
| PCIe Gen4 | PCIeGen4 |
| PCIe Gen5 | PCIeGen5 |
| PCIe Gen6 | PCIeGen6 |
| PCIe Gen7 | PCIeGen7 |
| UALink 1.0 | UALink1 |
| UALink 2.0 | UALink2 |
| UALink 3.0 | UALink3 |
| UALoE 200G | UALoE200G |
| CXL 1.1/2.0/3.0 | CXL3 |
| CXL 4.0 | CXL4 |
| NVLINK 6.0 | NVLink6 |
| NVLink 4.0 | NVLink4 |
| NVLink 5.0 | NVLink5 |
| Ethernet 200G | Eth200G |
| Ethernet 400G | Eth400G |
| Ethernet 800G | Eth800G |
| USB 2.0 | USB2 |
| USB 3.2 Gen1 | USB3Gen1 |
| USB 3.2 Gen2 | USB3Gen2 |
| USB4 Gen2 | USB4Gen2 |
| USB4 Gen3 | USB4Gen3 |

**Examples:**
- `OAC-PROF-CONN0-PCIeGen6-x16-IN-v1` — CONN0, single PCIe Gen6 group, 16 lanes, inbound
- `OAC-PROF-CONN0-PCIeGen6-x8-IN-Eth200G-x8-OUT-v1` — CONN0, mixed PCIe and Ethernet
- `OAC-PROF-CONN-Eth200G-x16-OUT-v1` — any CONN1–6, Ethernet 200G outbound

The optional `-minified` suffix identifies the encoding of the profile file and is described in
Section 6.2. It does not alter the meaning of the profile.

Connector profiles are published in the OAC CID project repository under `profiles/`. An upstream
management controller that claims conformance with this specification shall have built-in knowledge
of every OCP-ratified profile that the baseboard it is installed in can actually support, published
at or before the specification version declared in the CID `schema_version` field, and shall not
require a runtime fetch to resolve those profiles. It is neither required nor expected to recognize
profiles describing configurations the baseboard cannot support. It shall, however, handle a
reference to any other profile identifier robustly: an identifier it does not recognize, or
recognizes but cannot support, is a compatibility failure to be reported, not a parse failure and not
a condition that may leave the slot in an indeterminate state.

If an upstream management controller receives a CID that references a `connector_profile` identifier
it does not recognize, or one it recognizes but the baseboard cannot support, the upstream management
controller shall log a compatibility warning and shall not enable primary busbar power to the OAC
slot.

If an OAC vendor determines that a new profile is necessary and will be broadly applicable, the
vendor shall submit the proposed profile to the OCP OAC workstream for review and ratification before
referencing it in a CID. A profile identifier that is not present in the OCP-ratified profile
registry shall be treated as unrecognized.

### 8.4 Profile Document Structure

**Table 8.4-1: Connector Profile Document Fields**

| Field Name | JSON Type | Required | Constraints | Description |
|------------|-----------|----------|-------------|-------------|
| `applicable_conns` | array of strings | Required | Non-empty array drawn from `"CONN0"`, `"CONN1"` through `"CONN6"`, `"CONN1-6"`, and `"CABLE"`; each token appearing at most once; all tokens drawn from a single geometry class | Declares the connector position or positions the profile was ratified against. `"CONN0"` — the CONN0 position, which has nine assignable pin columns (columns 1–9). `"CONN1"` through `"CONN6"` — one specific position among CONN1 through CONN6, each of which has eight assignable pin columns (columns 1–8). `"CONN1-6"` — shorthand that shall be interpreted as exactly equivalent to naming all six of CONN1 through CONN6, and that shall not be combined with any individual `"CONN1"` through `"CONN6"` token. `"CABLE"` — the CABLE connector position. The three geometry classes are CONN0, the CONN1 through CONN6 set, and CABLE; an array naming positions from more than one class shall be treated as unrecognized, because the assignable column count of the profile would be undefined. See Section 8.5. |
| `high_speed_lanes` | object or array of objects | Optional | Per Section 7.4.3 | High-speed differential lane definition for the connector position. |
| `clocking` | array of objects | Optional | Per Section 7.4.4 | Reference clock definition for the connector position. |
| `discrete_signals` | array of objects | Optional | Per Section 7.4.5 | Discrete signal definition for the connector position. |

The `high_speed_lanes`, `clocking`, and `discrete_signals` sections within a profile document shall
conform to the same field definitions given in Sections 7.4.3, 7.4.4, and 7.4.5 respectively,
including Tables 7.4.3-1, 7.4.3-2, 7.4.4-1, and 7.4.5-1, and including the protocol generation
compatibility rules of Section 7.4.3.1.

Three differences from Section 7 apply, and are the only differences:

1. The presence rules of Sections 7.4.3, 7.4.4, and 7.4.5 — which are stated in terms of whether a
   connector object declares a `connector_profile` — do not apply within a profile document. A
   profile declares whichever of the three sections it needs and is not required to declare all
   three.
2. A section omitted from a profile document means that the connector position carries no signals of
   that class. The upstream management controller shall treat the omitted section as absent and shall
   not apply any default signal definition in its place.
3. A profile document does not declare `id`, `populated`, `impedance_ohm`, `mpesti_capable`, or
   `connector_profile`. Those fields describe a specific connector position on a specific OAC and
   belong to the CID connector object, not to the profile. Impedance in particular is a property of
   the installed connector variant and is declared by the CID in every case, whether or not a profile
   is referenced.

### 8.5 Profile Applicability to Connector Positions

CONN0, CONN1 through CONN6, and CABLE are not interchangeable. CONN0 has nine assignable pin
columns, with columns 10 and 11 reserved for the management USB 2.0 interface and `OAC_MC_RDY`;
CONN1 through CONN6 have eight. A profile's `applicable_conns` field declares which position or
positions it was ratified against.

The upstream management controller shall reject a profile applied to a connector position that
the profile's `applicable_conns` value does not name. A profile declaring `["CONN0"]` shall
be referenced only by the CONN0 connector object; a profile declaring `["CABLE"]` shall be
referenced only by the CABLE connector object; and a profile naming one or more of the CONN1
through CONN6 positions shall be referenced only by a connector object whose `id` is among
those named, with `"CONN1-6"` naming all six. A CID that violates this rule shall be treated
as malformed and the slot shall not be energized.

The field is an array and its vocabulary is per position, so a profile may be ratified against
one specific position, against an arbitrary subset of CONN1 through CONN6, or against all six
by the `"CONN1-6"` shorthand. CONN1 through CONN6 share a pin field and are electrically
equivalent, so a subset such as `["CONN2", "CONN5"]` is not an electrical statement. It is a
statement about where the profile was ratified for use, which is a property of the baseboard
the profile was drawn up against — what that platform routes to which position — rather than a
property of the connector. Both facts are real, they are not the same fact, and this field
records the second. A profile that is genuinely position-agnostic says so with `["CONN1-6"]`.

What the array shall not do is mix geometry classes. CONN0, the CONN1 through CONN6 set, and
CABLE differ in assignable column count, so an array naming positions from more than one of
them would leave the column count of the profile undefined. Such an array shall be treated as
unrecognized.

> **WORK IN PROGRESS — subject to change by the OCP OAC workstream.**
>
> Two related cases are open and are not resolved by the rule above.
>
> The first is the application of a `["CONN1-6"]` profile to CONN0. The eight columns such a
> profile defines map onto CONN0's first eight assignable columns without conflict, which makes the
> combination physically meaningful, but it leaves CONN0's ninth assignable column undefined. The
> rule above rejects the combination outright. Whether to permit it instead, and if so how the ninth
> column is to be declared, has not been decided. The `applicable_conns` array can express the
> resolution directly, as `["CONN0", "CONN1-6"]`, once the workstream settles the ninth column; the
> prohibition in Table 8.4-1 on mixing geometry classes within one array is what holds the case
> closed in the meantime.
>
> The second is supplementation and partial override more generally — a CID that references a profile
> and adds to, or amends, what the profile declares. Section 8.2 forbids this today, which is what
> makes the first case a rejection rather than a question of syntax. Permitting either case requires a
> mechanism for a CID to contribute signal definitions alongside a referenced profile, together with
> rules for resolving pin conflicts between the two.
>
> Until the workstream resolves both cases, an upstream management controller shall apply the rule
> stated above and no more.

---

## 9. CID Retrieval and Validation

### 9.1 Storage and Exposure

The CID shall be stored in non-volatile memory on the OAC and exposed by the OAC management controller as a FRU Data File per DSP0257. The OAC shall expose the CID via a File Descriptor PDR as specified in Section 6.3, and an upstream management controller shall locate and retrieve it through that record. No alternative access path is defined by this specification.

Storage and exposure are distinct. The management controller is the agent that serves the CID; it is not required to be the medium that holds it. An implementation may hold the CID in memory attached to the management controller, in memory shared with another device on the OAC, or in any other non-volatile medium the management controller can read, provided the CID survives loss of auxiliary power and is available to be served by the time the OAC reaches Operational State O3. This specification constrains what the upstream management controller observes, not how the OAC arranges its storage internally.

Communication between the upstream management controller and the OAC management controller shall occur over MCTP as defined in DMTF DSP0236, carrying PLDM as defined in DMTF DSP0240, transported over the OAC Management USB 2.0 interface at CONN0 Columns 10 through 11 as specified in OCP Open Adapter Card Base Specification v0.9.

### 9.2 Retrieval Sequence

CID retrieval is performed while the OAC is in Operational State O3 (Management Initialized), as defined in OCP OAC Base Specification v0.9 Section 10.1.1. In O3, the OAC management controller has completed initialization and asserted OAC_MC_RDY, MCTP and PLDM services are available, and the management interface is active, but primary power has not yet been enabled. The OAC shall remain in Operational State O3 or a later state throughout the following retrieval steps. The baseboard shall not assert OAC_PWR_EN (and shall not transition the OAC beyond O3) until all steps in this section have completed successfully.

The upstream management controller shall complete the following steps before enabling primary busbar power to any OAC slot:

1. Confirm that the OAC has reached Operational State O3 by detecting assertion of OAC_MC_RDY on CONN0 Column 11.
2. Establish an MCTP session with the OAC management controller over the OAC Management USB 2.0 interface.
3. Locate the CID File Descriptor PDR in the OAC's PDR repository by matching `FileName` equal to `OAC_CID.json` (per Section 6.3).
4. Use the `FileIdentifier` from the matched PDR to open the file via `DfOpen` (DSP0242), specifying read access.
5. Issue one or more `DfRead` commands to retrieve the CID payload, then issue `DfClose` to terminate the transfer session.
6. Parse and validate the resulting JSON against the schema defined in Section 7.
7. Resolve any `connector_profile` references per Section 8, and evaluate the resulting complete connector definitions.
8. Evaluate the CID content for compatibility with the baseboard's available resources (power budget, connector impedance class, protocol support).

If any step fails, the upstream management controller shall not enable primary busbar power to the OAC slot and shall log an error indicating the failure mode and slot identifier.

### 9.3 Validation Requirements

The upstream management controller shall perform at minimum the following validation checks on a retrieved CID:

1. The JSON document is syntactically valid per ECMA-404.
2. The root key `"oac_cid"` is present.
3. The `"metadata"`, `"power"`, and `"connectors"` sections are all present.
4. The `schema_version` value is a recognized CID schema version.
5. CONN0 is present in the `"connectors"` array with `populated` set to `true`.
6. The `input_voltage` value matches the mechanical keying configuration detected for the slot.
7. The `connector_type` value is compatible with the host slot (e.g., a `"125A"` OAC shall not be enabled in a slot that only supports the `"100A"` variant).
8. The `opl_max_w` value does not exceed the continuous power capacity implied by the declared `connector_type` and `input_voltage` (per OCP OAC v0.9 Section 9.3, Table 8).
9. The `opl_emg_w` value is present and satisfies the OPL ordering constraint (`opl_emg_w` <= `opl_max_w`).
10. For each populated connector that declares a `connector_profile`: the profile identifier is recognized as an OCP-ratified profile (`OAC-PROF-` prefix) that the baseboard supports, the connector position it is applied to is covered by the profile's `applicable_conns` value per Section 8.5, and the connector object contains no `high_speed_lanes`, `clocking`, or `discrete_signals` sections. If the profile identifier is unrecognized or unsupported, if the connector position is not covered by `applicable_conns`, or if any signal section is present alongside `connector_profile`, the connector shall be treated as incompletely defined or malformed and the slot shall not be energized.
11. For each populated connector that does not declare a `connector_profile` and that carries high-speed differential signals: the `high_speed_lanes` section is present, per Section 7.4.3. A connector that carries high-speed signals but describes neither a profile nor explicit lane definitions is incompletely defined and the slot shall not be energized.

An upstream management controller may perform additional validation beyond these minimum requirements. Validation failures shall be logged with sufficient detail to identify the specific field and the nature of the failure.

### 9.4 Timeout Handling

The upstream management controller shall apply a retrieval timeout to the CID file transfer sequence (DfOpen through DfClose per DSP0242). If the CID is not successfully retrieved within the timeout period, the upstream management controller shall not enable primary busbar power to the OAC slot. The specific timeout value is implementation-defined but should be no less than 5 seconds.

---

## 10. Compliance

### 10.1 OAC Implementation Requirements

An OAC implementation that claims conformance with this specification shall satisfy the requirements in Table 10.1-1.

**Table 10.1-1: OAC Compliance Requirements**

| Requirement | Classification | Reference |
|-------------|----------------|-----------|
| CONN0 shall be populated (`populated=true`) | Mandatory | Section 7.4.1 |
| CID shall be stored in non-volatile memory and exposed by the OAC management controller, accessible via PLDM for FRU Data over MCTP | Mandatory | Section 9.1 |
| CID shall be accessible when the OAC is in Operational State O3 or later | Mandatory | Section 9.2 |
| CID shall be a syntactically valid JSON document per ECMA-404 | Mandatory | Section 7.1 |
| CID shall conform to the JSON schema defined in Section 7 | Mandatory | Section 7 |
| The `"metadata"`, `"power"`, and `"connectors"` sections shall be present in the CID | Mandatory | Section 7.1 |
| `connector_type`, `opl_max_w`, and `opl_emg_w` shall be declared in `power.primary` | Mandatory | Section 7.3.1 |
| CONN1 through CONN6 connector positions may be populated | Optional | Section 7.4 |
| CABLE connector position may be populated | Optional | Section 7.4 |
| `mpesti_capable` shall be declared in the CONN0 connector object, and shall not appear in the CONN1 through CONN6 or CABLE connector objects | Mandatory | Section 7.4.2 |
| `opl_eff_w` and `opl_red_w` OPL fields may be declared if supported | Optional | Section 7.3.1 |
| `opl_set_min_w` may be declared if OPL-SET is supported, bounding the configurable range below; the upper bound is `opl_max_w` | Optional | Section 7.3.1 |
| `connector_profile` may be declared on any populated connector to reference an OCP-ratified connector profile | Optional | Section 8.2 |
| A referenced `connector_profile` shall have an `applicable_conns` value that covers the connector position it is applied to | Mandatory (if connector_profile present) | Section 8.5 |
| `high_speed_lanes` shall be present on any populated connector that carries high-speed differential signals and does not declare a `connector_profile` | Mandatory | Section 7.4.3 |
| When `connector_profile` is declared, `high_speed_lanes`, `clocking`, and `discrete_signals` shall not be present in the same connector object | Mandatory (if connector_profile present) | Section 8.2 |
| `connector_profile` values shall use only OCP-ratified identifiers with the `OAC-PROF-` prefix | Mandatory (if connector_profile present) | Section 8.3 |

### 10.2 Upstream Management Controller Requirements

An upstream management controller implementation that claims conformance with this specification shall satisfy the requirements in Table 10.2-1.

**Table 10.2-1: Upstream Management Controller Compliance Requirements**

| Requirement | Classification | Reference |
|-------------|----------------|-----------|
| upstream management controller shall retrieve the CID after the OAC reaches Operational State O3, and before enabling primary busbar power | Mandatory | Section 9.2 |
| upstream management controller shall locate the CID by FileName (OAC_CID.json) in the File Descriptor PDR, not by ordinal position | Mandatory | Section 6.3 |
| upstream management controller shall perform all minimum validation checks defined in Section 9.3 | Mandatory | Section 9.3 |
| upstream management controller shall not enable primary busbar power if CID retrieval or validation fails | Mandatory | Section 9.2 |
| upstream management controller shall apply a retrieval timeout and handle timeout without enabling power | Mandatory | Section 9.4 |
| upstream management controller shall evaluate `connector_type` against host slot capability and declared OPL values against provisioned slot power capacity | Mandatory | Section 9.3 |
| upstream management controller shall recognize, without runtime fetch, every OCP-ratified profile identifier (`OAC-PROF-` prefix) the baseboard can support, published at or before the declared `schema_version`, and shall handle every other profile identifier robustly | Mandatory | Section 8.3 |
| upstream management controller shall reject any connector object that contains both `connector_profile` and any of `high_speed_lanes`, `clocking`, or `discrete_signals` | Mandatory | Section 8.2 |
| upstream management controller shall not enable primary power when `connector_profile` references a profile identifier that is unrecognized or that the baseboard cannot support | Mandatory | Section 8.3 |
| upstream management controller shall reject a profile applied to a connector position not covered by the profile's `applicable_conns` value | Mandatory | Section 8.5 |
| upstream management controller may perform additional validation beyond the minimum requirements in Section 9.3 | Optional | Section 9.3 |

---

## Annex A (informative) -- Example CID JSON Documents

This annex contains two complete, conformant example CID documents. They illustrate the two mutually
exclusive styles in which a connector's signal assignment may be expressed, and they are labelled so
that they can be referenced individually.

Example A.1 references OCP-ratified connector profiles and declares no signal sections of its own.
Example A.2 declares its signal sections explicitly and references no profile. A conformant CID may
mix the two styles across connectors — one connector referencing a profile while another declares its
signals explicitly — but never within a single connector object, per Section 8.2.

Further examples, including multi-protocol connectors and link subdivision configurations, are
maintained in the OAC CID project repository under `examples/`.

### A.1 Profile-Referencing CID

This OAC populates CONN0 and CONN1, and both match OCP-ratified profiles exactly. Each connector
object therefore carries only its position, population state, and impedance class, plus the profile
identifier. No `high_speed_lanes`, `clocking`, or `discrete_signals` section appears anywhere in the
document.

```json
{
  "oac_cid": {
    "metadata": {
      "schema_version": "0.9",
      "oac_spec_revision": "0.9",
      "description": "Example OAC -- PCIe Gen6 x16 inbound on CONN0, Ethernet 200G outbound on CONN1, both from ratified profiles"
    },
    "power": {
      "primary": {
        "input_voltage": "+50V",
        "connector_type": "125A",
        "opl_max_w": 3000.0,
        "opl_eff_w": 2200.0,
        "opl_red_w": 800.0,
        "opl_emg_w": 300.0
      }
    },
    "connectors": [
      {
        "id": "CONN0",
        "populated": true,
        "impedance_ohm": 85,
        "mpesti_capable": false,
        "connector_profile": "OAC-PROF-CONN0-PCIeGen6-x16-IN-v1"
      },
      {
        "id": "CONN1",
        "populated": true,
        "impedance_ohm": 92,
        "connector_profile": "OAC-PROF-CONN-Eth200G-x16-OUT-v1"
      }
    ]
  }
}
```

Three points are worth noting about this document.

The two profile identifiers differ in their connector segment. `OAC-PROF-CONN0-...` carries
`applicable_conns: ["CONN0"]` and may be referenced only by the CONN0 connector object;
`OAC-PROF-CONN-...` carries `applicable_conns: ["CONN1-6"]` and may be referenced only by CONN1
through CONN6. The connector segment and the field shall agree, per Section 8.3. Applying either
profile to the other class of position is a validation failure, per Section 8.5.

`impedance_ohm` is declared on both connectors even though the profiles supply everything else. It is
a property of the installed connector variant on this particular OAC rather than of the ratified
signal assignment, and it is declared by the CID in every case, per Section 8.4.

`mpesti_capable` is declared on CONN0 as `false`. Presence detect itself appears nowhere in the
document: Pin A1 of each populated connector is tied to GND in the standard manner, which the Base
Specification fixes and the CID therefore never restates. The `false` value says only that CONN0
Pin A1 is not additionally overloaded with M-PESTI, per Section 7.4.2.

### A.2 Explicitly Defined CID

This OAC populates CONN0 only, and its connector configuration does not match any ratified profile.
It therefore declares `high_speed_lanes`, `clocking`, and `discrete_signals` inline, and declares no
`connector_profile`.

```json
{
  "oac_cid": {
    "metadata": {
      "schema_version": "0.9",
      "oac_spec_revision": "0.9",
      "description": "Example OAC -- PCIe Gen5 x4 inbound on CONN0 with a vendor alert signal",
      "iana_pen": 32473
    },
    "power": {
      "primary": {
        "input_voltage": "+12V",
        "connector_type": "100A",
        "opl_max_w": 450.0,
        "opl_emg_w": 75.0
      }
    },
    "connectors": [
      {
        "id": "CONN0",
        "populated": true,
        "impedance_ohm": 85,
        "mpesti_capable": false,
        "high_speed_lanes": {
          "name": "pcie_primary",
          "protocol": "PCIe Gen5",
          "link_direction": "INBOUND",
          "total_lanes": 4,
          "minimum_lanes": 2,
          "lanes": [
            { "lane_index": 0, "direction": "RX", "pin_positive": "C1", "pin_negative": "D1" },
            { "lane_index": 1, "direction": "RX", "pin_positive": "C2", "pin_negative": "D2" },
            { "lane_index": 2, "direction": "RX", "pin_positive": "C3", "pin_negative": "D3" },
            { "lane_index": 3, "direction": "RX", "pin_positive": "C4", "pin_negative": "D4" },
            { "lane_index": 0, "direction": "TX", "pin_positive": "E1", "pin_negative": "F1" },
            { "lane_index": 1, "direction": "TX", "pin_positive": "E2", "pin_negative": "F2" },
            { "lane_index": 2, "direction": "TX", "pin_positive": "E3", "pin_negative": "F3" },
            { "lane_index": 3, "direction": "TX", "pin_positive": "E4", "pin_negative": "F4" }
          ]
        },
        "clocking": [
          {
            "clock_id": "REFCLK0",
            "clock_type": "REFCLK_DIFF",
            "frequency_mhz": 100.0,
            "pin_positive": "G1",
            "pin_negative": "H1",
            "direction": "INPUT",
            "associated_lanes": [0, 1, 2, 3],
            "required": true,
            "ssc_supported": true,
            "description": "PCIe reference clock sourced by the baseboard"
          }
        ],
        "discrete_signals": [
          {
            "signal_name": "VENDOR_ALERT#",
            "pin": "J9",
            "direction": "OUTPUT",
            "active_level": "ACTIVE_LOW",
            "voltage_level_v": 3.3,
            "driver_type": "OPEN_DRAIN",
            "default_state": "HIGH",
            "pullup_required": true,
            "pullup_voltage_v": 3.3,
            "pullup_kohm": 10.0,
            "pulldown_required": false,
            "required": false,
            "description": "Vendor-defined out-of-band alert to the upstream management controller"
          }
        ]
      }
    ]
  }
}
```

The absence of `connector_profile` is what permits the three signal sections to appear. Had a profile
been declared, all three would be prohibited on this connector object and the document would be
malformed, per Section 8.2. There is no partial form: an OAC whose connector almost matches a ratified
profile declares its signals explicitly, as this example does.

`minimum_lanes` is set to 2 against a `total_lanes` of 4. Per the rule in Section 7.4.3, this makes
lanes 0 and 1 required in both directions and lanes 2 and 3 negotiated, and the upstream management
controller should decline to energize the slot if the baseboard routes fewer than two lanes to the
connector. The `lanes` array lists all four RX entries in ascending index order before all four TX
entries, per Section 7.6 item 3.

The `iana_pen` value shown, 32473, is the Private Enterprise Number IANA reserves for use in
documentation. A production CID declares the PEN of the organization responsible for the document. No
`platform_token` is declared here; had one been, `iana_pen` would be required rather than optional,
per Section 7.2.1.

---

## Annex B (informative) -- PLDM Protocol Field Value Reference

> **NOTE:** The values collected in this annex are scoped by the WORK IN PROGRESS annotation in
> Section 6.3. Where that annotation marks a mechanism as under review, the corresponding field
> values here are provisional to the same extent.

This annex collects the PLDM field values this specification constrains. It lists only those fields; every other field of each record is governed by the referenced DMTF specification and is an implementation matter. Byte offsets and field widths are not reproduced here — see DSP0248 for the File Descriptor PDR and the sensor PDR formats, DSP0242 for the file sensor requirements and the transfer commands, DSP0249 for entity type codes and State Set 68, and DSP0257 for FRU Data File structure.

### B.1 CID

**Table B-1: PLDM FRU Record Fields for the CID**

| Field | Value |
|-------|-------|
| FRU Record Type | OEM (per DSP0257) |
| Access context | FRU Data File, per DSP0257 |
| Storage | Persistent, non-volatile storage recommended; on-demand generation permitted |
| Access | Read-only |
| File characteristic | Fixed Length File, per DSP0242 |

**Table B-2: CID File Descriptor PDR**

| Field | Value | Note |
|-------|-------|------|
| `EntityType` | 9 (Device File) | |
| `FileClassification` | `FRUDataFile` | The file content is FRU data per DSP0257. |
| `FileName` | `OAC_CID.json` (`strASCII`) | The discriminator an upstream management controller matches on. Not PDR order. |
| `FileIdentifier` | Implementation-chosen `uint16` | What `DfOpen` takes. A controller matches `FileName`, then opens with this value. |
| `FileCapabilities` | `FcWritesPermitted` = 0, `ExWriteOpen` = 0, `DataType` = 0 | The CID is read-only from the upstream management controller's perspective. `DataType` = 0 declares a regular file rather than a streaming FIFO. |
| `FileMaximumSize` | The exact transferred size of the CID, not greater than the applicable size limit | For a fixed-length file DSP0242 equates file size to this field, so it is exact rather than an upper bound. The OAC shall update this field whenever the CID is replaced by a firmware update. |
| `SuperiorDirectoryFileIdentifier` | `0xFFFF` | The CID is a flat file; no directory is required. |
| `ContainerID` | Implementation-chosen, one value per OAC | The same value appears on every File Descriptor PDR and associated sensor PDR published by the OAC management controller. It identifies the OAC. |
| `EntityInstanceNumber` | Implementation-chosen, unique within the `ContainerID` | This value is repeated on both sensor PDRs below, per Section 6.3. |

**Table B-3: CID File Size Monitoring Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | Compact or Numeric sensor (DSP0242 File Size Monitoring Sensor) | |
| `EntityType` | 9 (Device File) | Matches Table B-2. |
| `EntityInstanceNumber`, `ContainerID` | As in Table B-2 | This match is what associates the sensor with the file. |
| Reading | Current CID size in bytes, as transferred | The byte count of the CID as published, in whichever encoding the OAC uses. Changes when a firmware update replaces the CID. |
| Units | `BaseUnit` Bytes, `UnitModifier` 0 | Per DSP0242. Numeric: `RateUnit` None, `Offset` 0, `Resolution` 1.00. Compact: `OccurrenceRate` No Occurrence Rate. |
| Thresholds | Should not be set | DSP0242 advises against thresholds on a fixed-length file. |
| Requirement | Shall, per this specification | DSP0242 makes it a *should* for a Fixed Length File; Section 6.3 tightens it. The sensor allows the upstream management controller to detect a change in CID size without a second PDR lookup. |

**Table B-4: CID Device File State Sensor**

| Field | Value | Note |
|-------|-------|------|
| Sensor kind | State sensor | |
| State set | 68 (Device File), per DSP0249 | |
| `EntityType` | 9 (Device File) | Matches Table B-2. |
| `EntityInstanceNumber`, `ContainerID` | As in Table B-2 | |
| States reported | 1 (File has Not Changed), 2 (File is Updated) | State 3 (File is at Maximum Size) shall not be reported — a fixed-length file is always at its maximum size, so the state carries no information. States 4 and 5 are not applicable to a file published whole and never appended to. |
| Requirement | Shall, per DSP0242 | Mandatory for a Fixed Length File. |
| Interpretation | File state, including modification signalling | State 2 indicates the CID has changed, typically following a firmware update. The upstream management controller shall re-retrieve the CID when State 2 is observed before the next slot energization evaluation. |

