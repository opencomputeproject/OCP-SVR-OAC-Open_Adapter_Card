# OAC Metadata Specification
## Version: 0.9
### Document Identifier: OAC-METADATA-SPEC
### Document Status: Draft
### Document Language: en-US
### Normative Reference: OCP Open Adapter Card Base Specification v0.9

---

## Foreword

This specification is authored by the OCP Open Adapter Card (OAC) workstream under the Open Compute Project Foundation. It defines the OAC Metadata file, a machine-readable descriptor that an OAC exposes to the upstream management controller and that enumerates the management files the OAC publishes. The OCP OAC workstream retains editorial authority over this document. Contributions, errata reports, and change proposals shall be submitted through the OCP OAC project repository.

This document is a Draft specification. Contents are subject to revision by the OCP OAC workstream prior to final publication.

---

## Contents

1. Scope
2. Normative References
3. Terms and Definitions
4. Symbols and Abbreviated Terms
5. Metadata Overview
   - 5.1 Purpose
   - 5.2 Schema Version and Compatibility
6. Metadata as a FRU File
   - 6.1 General
   - 6.2 Encoding
   - 6.3 File Classification and Access
7. Metadata JSON Document Structure
   - 7.1 General
   - 7.2 oac_metadata Object
   - 7.3 files Object
   - 7.4 File Descriptor Object
   - 7.5 Vendor-Defined Roles
8. Metadata Retrieval and Validation
   - 8.1 Retrieval Sequence
   - 8.2 Validation Requirements
   - 8.3 Failure Handling
9. Compliance
   - 9.1 OAC Implementation Requirements
   - 9.2 Upstream Management Controller Requirements

Annex A (informative) -- Example OAC Metadata Documents
Annex B (informative) -- PLDM Protocol Field Value Reference

---

## 1. Scope

This specification defines the OAC Metadata file, a normative machine-readable JSON document stored in OAC firmware that enumerates the management files the OAC exposes, and for each one carries the `FileIdentifier` and `FileName` of the DSP0248 File Descriptor PDR that describes it.

The OAC Metadata file is the entry point to the OAC management model. An upstream management controller retrieves it first, in Operational State O3, and uses its contents to locate the Connector Interface Definition (CID), the Slot Configuration Definition (SCDD), and the Slot Configuration Assignment (SCDA).

The mechanism this specification replaces is worth stating plainly, because it determines what the file is for. Previously the CID and SCD specifications each fixed a `FileName` string — `OAC_CID.json`, `OAC_SCDD.json`, `OAC_SCDA.json` — and required an upstream management controller to match that string against the File Descriptor PDRs the OAC published. Each new management file therefore required a new reserved name in a specification, and a controller could locate only the files whose names were known to it at build time. The metadata file replaces that arrangement with a single indirection: one file enumerates the rest, and a new file role is added by extending a JSON document rather than by reserving a further name.

This does not eliminate the well-known name. The metadata file is itself a file in the OAC's PDR repository and must be located before it can be read, so one reserved `FileName` remains. Section 6.3 fixes it. The reduction is from three reserved names to one, and that one is the only reserved file name in the OAC management model.

The following are within the scope of this specification:

- The structure and encoding of the OAC Metadata JSON document
- The reserved `FileName` by which the metadata file is itself located
- The retrieval mechanism via DSP0257 PLDM for FRU Data
- Compliance requirements for OAC implementations and upstream management controller implementations

The following are outside the scope of this specification:

- The content, structure, and semantics of the CID (governed by the OAC Connector Interface Definition Specification)
- The content, structure, and semantics of the SCD Definition and Assignment (governed by the OAC Slot Configuration Data Specification)
- Physical connector mechanical design (governed by OCP Open Adapter Card Base Specification v0.9)
- Upstream management controller firmware implementation details

---

## 2. Normative References

The following documents are normative references for this specification. For dated references, only the edition cited applies. For undated references, the latest edition of the referenced document applies.

| Reference | Document |
|-----------|----------|
| DSP0236 | DMTF, "Management Component Transport Protocol (MCTP) Base Specification" |
| DSP0240 | DMTF, "PLDM Base Specification," Version 1.2 |
| DSP0242 | DMTF, "PLDM for File Transfer Specification" |
| DSP0248 | DMTF, "PLDM for Platform Monitoring and Control Specification," Version 1.3.1 |
| DSP0249 | DMTF, "PLDM State Set Specification," Version 1.4.0 |
| DSP0257 | DMTF, "PLDM for FRU Data Specification," Version 2.0 |
| ECMA-404 | ECMA International, "JSON Data Interchange Syntax," 2nd Edition |
| OCP OAC v0.9 | OCP, "Open Adapter Card Base Specification," Version 0.9 |
| OAC-CID-SPEC | OCP, "OAC Connector Interface Definition (CID) Specification," Version 0.9 |
| OAC-SCD-SPEC | OCP, "OAC Slot Configuration Data (SCD) Specification," Version 0.9 |

---

## 3. Terms and Definitions

**OAC Metadata file** — the JSON document defined by this specification, enumerating the management files an OAC exposes.

**File role** — the key under which a management file appears in the `files` object. The OCP-defined roles are `cid`, `scdd`, and `scda`.

**File Descriptor PDR** — the Platform Descriptor Record defined in DSP0248 that describes a device file, carrying among other fields the `FileIdentifier` and `FileName` of that file.

**`FileIdentifier`** — a `uint16` carried in a File Descriptor PDR, unique relative to the PLDM Terminus ID, and the parameter DSP0242 requires for `DfOpen`.

**`FileName`** — a `strASCII` string carried in a File Descriptor PDR, naming the file it describes.

**Upstream management controller** — the baseboard management entity that retrieves the OAC's management files and decides whether the OAC may be energized.

**Reserved file name** — a `FileName` value fixed by this specification and not available for any other use. This specification defines exactly one.

---

## 4. Symbols and Abbreviated Terms

| Term | Expansion |
|------|-----------|
| CID | Connector Interface Definition |
| MCTP | Management Component Transport Protocol |
| OAC | Open Adapter Card |
| PDR | Platform Descriptor Record |
| PEN | Private Enterprise Number (IANA) |
| PLDM | Platform Level Data Model |
| SCD | Slot Configuration Data |
| SCDA | Slot Configuration Assignment |
| SCDD | Slot Configuration Definition |

---

## 5. Metadata Overview

### 5.1 Purpose

The OAC Metadata file carries one thing: a mapping from file role to the pair of values needed to open that file. It carries no connector data, no power data, and no configuration data, and an implementation shall not place such data in it. Its sole function is indirection, and the value of that indirection is extensibility — a management file role can be added to the OAC model without reserving a new `FileName` in a specification and without a controller needing to know the name in advance.

A controller that does not recognize a role ignores it. This is what permits the set of roles to grow: an OAC publishing a role from a later revision of this specification, or a vendor-defined role under Section 7.5, remains fully usable by a controller that understands only `cid`, `scdd`, and `scda`.

The metadata file is read before the CID. This ordering is load-bearing and is stated normatively in Section 8.1.

### 5.2 Schema Version and Compatibility

The `schema_version` field declares the revision of this specification the document conforms to, as `major.minor`. Both components may carry multiple digits.

An upstream management controller shall accept a metadata document whose `major` component matches a revision the controller implements, and shall ignore any file role within it that the controller does not recognize. A controller shall reject a document whose `major` component it does not implement.

This rule deliberately differs from the SCD, where `SCHEMA_VERSIONS` is the exact set `{"0.9"}` and any other value is answered `UNSUPPORTED_SCHEMA_VERSION`. The difference is intentional and follows from what each document is. The SCD Definition describes a configuration contract whose field semantics a controller must understand exactly or not at all; a partially understood Definition could produce a configuration both sides believe is valid and that is not. The metadata file describes only where files are. A role a controller does not recognize is a file it will not open, which is the same outcome as the role not being present, and is safe. Minor-version tolerance here costs nothing and is the mechanism by which the extensibility described in Section 5.1 is actually realized.

An implementation shall not infer from this rule that minor revisions may change the meaning of an existing field. A minor revision may add roles and may add optional members; it shall not alter the semantics of `cid`, `scdd`, `scda`, `file_identifier`, or `file_name`.

---

## 6. Metadata as a FRU File

### 6.1 General

The OAC Metadata file shall be published by the OAC's management controller as PLDM FRU data and retrieved by the upstream management controller using PLDM for FRU Data (DSP0257), over the MCTP session established on the OAC Management USB 2.0 interface (CONN0 Columns 10–11). This is the same access method the CID and the SCD Definition use.

The OAC Metadata file shall be read-only from the perspective of the upstream management controller. An OAC shall not accept a write to it. This holds even though the file may describe a writable file: the metadata file states where the SCD Assignment is, and the Assignment is written, but the metadata itself is not.

The OAC Metadata file should be stored in persistent, non-volatile storage on the OAC, so that it is available as soon as the OAC's management controller is ready. An OAC may instead generate it on demand from its own firmware configuration.

A metadata file generated on demand shall be deterministic for a given firmware configuration. An OAC shall not return differing metadata content for the same hardware and firmware version.

The OAC Metadata file shall be retrievable whenever the OAC is in Operational State O3 or later. An OAC shall not require primary power to serve it.

The OAC Metadata file is a Fixed Length File in the sense of DSP0242 — read, not written, after creation, and of a size that does not vary while a given metadata file is being served — and an OAC shall treat it as one. As with the CID, fixed length constrains the file within a firmware revision and not across firmware revisions; an OAC shall set `FileMaximumSize` to the exact transferred size of the metadata file it is currently serving and shall update that field whenever a firmware update replaces it with one of a different size.

### 6.2 Encoding

The OAC Metadata file shall be encoded in UTF-8 per ECMA-404. No byte order mark shall be present. The JSON document shall be syntactically valid per ECMA-404. Comments are not permitted; ECMA-404 defines no comment syntax, and a document containing `//` or `/* */` sequences outside a string literal is malformed.

The `$comment` member described in Section 7.1 is a JSON string member and is not a comment in the ECMA-404 sense. It is permitted.

The OAC shall publish the metadata file in either expanded format JSON or minified format JSON. An upstream management controller shall accept either and shall not reject a metadata file, or treat it as malformed, on the basis of its whitespace encoding. Minified format is recommended for production.

### 6.3 File Classification and Access

The OAC Metadata file shall be represented in the OAC's PDR repository by a File Descriptor PDR as defined in DSP0248, with `EntityType` set to Device File and `FileClassification` set to `FRUDataFile`. The file so described is a FRU Data File per DSP0257 and is retrieved as required by Section 6.1.

The OAC shall set the `FileName` field of that File Descriptor PDR, which is a `strASCII` string, to:

```
OAC_METADATA.json
```

This value is reserved. It is the only reserved `FileName` in the OAC management model, and an OAC shall not assign it to any other file. An upstream management controller shall use this name to locate the metadata file, and shall not rely on PDR ordering to locate it.

`FileName` is how the metadata file is recognised; it is not how it is opened. The same File Descriptor PDR carries a `FileIdentifier`, a `uint16` that DSP0248 defines as unique relative to the PLDM Terminus ID, and DSP0242 requires that value, rather than the name string, as the parameter to `DfOpen`, `DfGetFileAttribute`, and `DfSetFileAttribute`. An upstream management controller shall therefore match on `FileName` to find the record and then use the `FileIdentifier` from that same record to open the file. The OAC assigns the `FileIdentifier` of the metadata file; this specification fixes no value for it, and a controller shall not assume one.

The reason only the name is fixed, and not the identifier, is that a `FileName` is a property of the specification while a `FileIdentifier` is a property of a particular OAC's PDR repository. Fixing an identifier would constrain every OAC to the same numbering, which DSP0248 does not contemplate and which no OAC can guarantee against its other device files.

The OAC shall set the `FileCapabilities` bitfield16 so that no write and no modification of the metadata file is permitted: `FcWritesPermitted` and `ExWriteOpen` shall both be zero.

The OAC shall set `SuperiorDirectoryFileIdentifier` to `0xFFFF` on the metadata file's File Descriptor PDR, absent a directory, consistent with the treatment of the CID and SCD files.

An OAC shall associate a Device File State Sensor with the metadata file, on DSP0249 State Set 68, as it does for the CID and the SCD Definition.

---

## 7. Metadata JSON Document Structure

### 7.1 General

The OAC Metadata file is a single JSON object. The root key of the JSON document shall be `"oac_metadata"`. The value associated with `"oac_metadata"` shall be a JSON object containing two members: `"schema_version"` and `"files"`.

The root key alone identifies the document. This specification defines no separate file-type member, and an implementation shall not add one. A document carrying both a root key and a redundant type declaration admits the case in which the two disagree, and this specification would then have to arbitrate between them.

A `"$comment"` member of type string is permitted within any object defined by this specification, including the root object. It is an authoring aid. An upstream management controller shall ignore it. A production metadata file is minified and would not normally carry one.

An upstream management controller shall ignore unrecognized keys wherever they appear in this document, at any level of nesting, and shall not treat their presence as an error. This rule is stated for every level deliberately: a rule written only for the root object would leave the behavior of a controller encountering a new member inside `files` or inside a file descriptor object unspecified, which is precisely the case this document's extensibility depends on.

### 7.2 oac_metadata Object

**Table 7.2-1: `oac_metadata` members**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `schema_version` | string | Required | Pattern `^[0-9]+\.[0-9]+$` | Revision of this specification the document conforms to, as `major.minor`. See Section 5.2. |
| `files` | object | Required | At least one member; see Section 7.3 | The management files this OAC exposes, keyed by role. |

### 7.3 files Object

The `files` object maps a file role to a File Descriptor object. Each member key is a role.

**Table 7.3-1: OCP-defined file roles**

| Role | Required | Describes |
|------|----------|-----------|
| `cid` | Mandatory | The Connector Interface Definition, per OAC-CID-SPEC |
| `scdd` | Conditional | The Slot Configuration Definition, per OAC-SCD-SPEC |
| `scda` | Conditional | The Slot Configuration Assignment, per OAC-SCD-SPEC |

An OAC shall declare the `cid` role. The CID is the artifact on which the energization decision is made, and an OAC that publishes no CID cannot be evaluated.

An OAC shall declare `scdd` and `scda` together or declare neither. The two are halves of one exchange: a Definition with no Assignment to write gives a controller nothing to do with the fields it describes, and an Assignment with no Definition gives it no field descriptors to compose one from. An OAC that implements no Slot Configuration Data declares neither role, and a controller that finds neither shall proceed to energization on the CID alone.

Role keys are case-sensitive and shall appear exactly as given.

### 7.4 File Descriptor Object

Each member of `files` is an object with the following members.

**Table 7.4-1: File Descriptor object members**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `file_identifier` | integer | Required | 0 to 65535 inclusive | The `FileIdentifier` field of this file's DSP0248 File Descriptor PDR. This is the parameter `DfOpen` takes. |
| `file_name` | string | Required | Minimum length 1; fixed per Table 7.4-2 for the OCP-defined roles | The `FileName` field of that same File Descriptor PDR, as a `strASCII` string. |

The two members are snake_case renderings of the DSP0248 File Descriptor PDR fields `FileIdentifier` and `FileName`, and carry those values unchanged. The renaming is for consistency with the CID and SCD documents, which are snake_case throughout; it signifies no transformation of the values.

**Table 7.4-2: Fixed `file_name` values**

| Role | `file_name` |
|------|-------------|
| `cid` | `OAC_CID.json` |
| `scdd` | `OAC_SCDD.json` |
| `scda` | `OAC_SCDA.json` |

The `file_name` values for the OCP-defined roles remain fixed by specification. This may appear to contradict the purpose of the metadata file, and the distinction is worth stating. Before this specification, those names were the *discovery mechanism* — a controller had no other way to find the files. They are now descriptive: a controller locates each file by the `file_identifier` the metadata hands it, and the name is retained so that the three OCP-defined files remain identifiable in a PDR repository dump, in a firmware image, and to diagnostic tooling. Fixing them costs nothing, because these three roles are defined by OCP specifications that fix the names anyway. A vendor-defined role under Section 7.5 carries no such constraint.

`file_identifier` values shall be distinct across all roles within one metadata document. DSP0248 defines `FileIdentifier` as unique relative to the PLDM Terminus ID, so two roles sharing a value describe the same file and at most one of them can be correct. This is the defect with the worst failure mode in this document: a controller handed a duplicate identifier opens a file successfully, parses it successfully, and finds the wrong content, with no error raised anywhere in the transport. An OAC shall not publish such a document and a validator shall reject it.

`file_name` values shall likewise be distinct across all roles within one metadata document.

The value `OAC_METADATA.json` shall not appear as a `file_name` in any role. That name denotes the metadata file itself, per Section 6.3, and an entry carrying it would describe a file that is already open.

### 7.5 Vendor-Defined Roles

A vendor may declare additional file roles. A vendor-defined role key shall take the form:

```
pen.<IANA PEN>.<name>
```

where `<IANA PEN>` is the vendor's IANA Private Enterprise Number expressed in decimal and `<name>` is a lowercase identifier composed of `a`–`z`, `0`–`9`, and underscore.

This follows the namespacing convention of the SCD field catalogue rather than the `vendor_<name>_` prefix convention of the CID. The choice is deliberate: a role key identifies a file in the same sense that an SCD field identifier identifies a field, and an IANA PEN is globally unique where a vendor name string is not. No OCP registration is required to use a PEN namespace.

An upstream management controller shall ignore any role it does not recognize, whether vendor-defined or defined by a later revision of this specification. A vendor-defined role carries no fixed `file_name`.

---

## 8. Metadata Retrieval and Validation

### 8.1 Retrieval Sequence

The upstream management controller shall perform the following sequence in Operational State O3, before asserting `OAC_PWR_EN`.

1. Locate the File Descriptor PDR whose `FileName` is `OAC_METADATA.json`, per Section 6.3.
2. Open the file using the `FileIdentifier` carried in that same PDR, specifying read access.
3. Retrieve and parse the metadata file.
4. Validate it per Section 8.2.
5. Resolve the `cid` role to a `file_identifier` and retrieve the CID using it. Evaluate slot energization eligibility per OAC-CID-SPEC Section 9.
6. If the OAC may not be energized, stop. The busbar is never energized and the remaining roles are not retrieved.
7. If the `scdd` and `scda` roles are present, resolve and retrieve the SCD Definition, compose an Assignment, and write it per OAC-SCD-SPEC. If they are absent, proceed.
8. Assert `OAC_PWR_EN`.

The metadata file shall be retrieved before the CID. A controller shall not retrieve the CID by assuming a `FileName`, and an OAC shall not require it to.

Step 6 is unchanged from the previous model and remains the point at which an incompatible OAC is rejected. The metadata file introduces no new energization criterion; it changes only how the files on which that decision is made are located.

### 8.2 Validation Requirements

An upstream management controller shall verify the following before using the contents of a metadata document. A document failing any check shall be treated as malformed, and the slot shall not be energized.

1. The document is syntactically valid JSON per ECMA-404 and is encoded in UTF-8 with no byte order mark.
2. The root key is `oac_metadata`.
3. `schema_version` is present, matches the pattern `^[0-9]+\.[0-9]+$`, and declares a `major` component the controller implements, per Section 5.2.
4. `files` is present and declares the `cid` role.
5. `scdd` and `scda` are either both present or both absent.
6. Every declared role carries both `file_identifier` and `file_name`.
7. Every `file_identifier` is in the range 0 to 65535 inclusive.
8. No two roles share a `file_identifier`.
9. No two roles share a `file_name`.
10. No role carries the reserved `file_name` `OAC_METADATA.json`.
11. For the roles `cid`, `scdd`, and `scda`, `file_name` matches Table 7.4-2.
12. Every vendor-defined role key matches the form of Section 7.5.

A controller shall additionally verify, as it resolves each role, that a File Descriptor PDR exists carrying the `file_identifier` the metadata declared. A role naming an identifier the PDR repository does not contain is a malformed document, not a missing file.

### 8.3 Failure Handling

If the metadata file cannot be located, cannot be retrieved within the retrieval timeout defined for the CID in OAC-CID-SPEC Section 9.4, or fails any check of Section 8.2, the upstream management controller shall not assert `OAC_PWR_EN`.

The failure direction is deliberate. The metadata file is the only path to the CID, and the CID is what establishes that the slot can supply the card. A controller that cannot read the metadata file does not know what it is holding, and energizing a slot on that basis is exactly the outcome the OAC management model exists to prevent.

An upstream management controller shall not fall back to matching a `FileName` of `OAC_CID.json` when metadata retrieval fails. Such a fallback would reintroduce the assumption this specification removes, and would energize a slot on data obtained by a path the OAC did not advertise.

---

## 9. Compliance

### 9.1 OAC Implementation Requirements

| Requirement | Status | Section |
|-------------|--------|---------|
| Publish an OAC Metadata file as a FRU Data File per DSP0257 | Mandatory | 6.1 |
| Serve the metadata file in Operational State O3 without primary power | Mandatory | 6.1 |
| Generate a deterministic metadata file for a given firmware configuration | Mandatory | 6.1 |
| Reject writes to the metadata file | Mandatory | 6.1 |
| Encode the metadata file in UTF-8 per ECMA-404 with no byte order mark | Mandatory | 6.2 |
| Set `FileName` to `OAC_METADATA.json` on the metadata File Descriptor PDR | Mandatory | 6.3 |
| Assign `OAC_METADATA.json` to no other file | Mandatory | 6.3 |
| Set `FcWritesPermitted` and `ExWriteOpen` to zero on the metadata File Descriptor PDR | Mandatory | 6.3 |
| Set `FileMaximumSize` to the exact transferred size of the metadata file being served | Mandatory | 6.1 |
| Set `SuperiorDirectoryFileIdentifier` to `0xFFFF`, absent a directory | Mandatory | 6.3 |
| Associate a Device File State Sensor on DSP0249 State Set 68 with the metadata file | Mandatory | 6.3 |
| Use `oac_metadata` as the root key | Mandatory | 7.1 |
| Declare `schema_version` and `files` | Mandatory | 7.2 |
| Declare the `cid` role | Mandatory | 7.3 |
| Declare `scdd` and `scda` together or declare neither | Mandatory | 7.3 |
| Use the `file_name` values of Table 7.4-2 for the OCP-defined roles | Mandatory | 7.4 |
| Assign distinct `file_identifier` values across roles | Mandatory | 7.4 |
| Assign distinct `file_name` values across roles | Mandatory | 7.4 |
| Omit `OAC_METADATA.json` from every role's `file_name` | Mandatory | 7.4 |
| Namespace vendor-defined roles as `pen.<IANA PEN>.<name>` | Mandatory | 7.5 |
| Publish the metadata file in minified format | Recommended | 6.2 |
| Store the metadata file in persistent, non-volatile storage | Recommended | 6.1 |

### 9.2 Upstream Management Controller Requirements

| Requirement | Status | Section |
|-------------|--------|---------|
| Locate the metadata file by the `FileName` `OAC_METADATA.json` | Mandatory | 6.3 |
| Open the metadata file using the `FileIdentifier` from its File Descriptor PDR | Mandatory | 6.3 |
| Retrieve the metadata file before the CID | Mandatory | 8.1 |
| Resolve the CID and SCD files through the metadata file rather than by assuming a `FileName` | Mandatory | 8.1 |
| Accept a document whose `schema_version` major component the controller implements | Mandatory | 5.2 |
| Reject a document whose `schema_version` major component the controller does not implement | Mandatory | 5.2 |
| Ignore unrecognized file roles | Mandatory | 5.1, 7.5 |
| Ignore unrecognized keys at any level of nesting | Mandatory | 7.1 |
| Ignore `$comment` members | Mandatory | 7.1 |
| Perform every check of Section 8.2 before using the document | Mandatory | 8.2 |
| Treat a `file_identifier` with no corresponding File Descriptor PDR as a malformed document | Mandatory | 8.2 |
| Withhold `OAC_PWR_EN` when metadata retrieval or validation fails | Mandatory | 8.3 |
| Proceed to energization on the CID alone when `scdd` and `scda` are absent | Mandatory | 7.3, 8.1 |
| Refrain from falling back to a `FileName` match when metadata retrieval fails | Mandatory | 8.3 |
| Accept either expanded or minified JSON | Mandatory | 6.2 |

---

## Annex A (informative) -- Example OAC Metadata Documents

Three examples accompany this specification in `../examples/`. All are pretty-printed for readability; a production metadata file is minified.

| File | Illustrates |
|------|-------------|
| `OAC-METADATA-0.9-ExampleA-Minimal.json` | The ordinary case. All three OCP-defined roles, distinct identifiers, fixed names. |
| `OAC-METADATA-0.9-ExampleB-VendorFile.json` | A vendor-defined role under `pen.32473.telemetry_map`, alongside the three OCP-defined roles. PEN 32473 is the value IANA reserves for documentation. |
| `OAC-METADATA-0.9-ExampleC-CID-Only.json` | An OAC that implements no Slot Configuration Data. `cid` alone; `scdd` and `scda` both absent, per Section 7.3. |

A template for authoring is provided at `../templates/OAC-METADATA-TEMPLATE.json`, and the JSON Schema at `../OAC-Metadata-v0.9.schema.json`. The schema expresses the structural rules of Section 7; the rules of Section 8.2 that JSON Schema cannot express — identifier uniqueness, name uniqueness, the reserved-name prohibition, and the fixed names of Table 7.4-2 — are implemented in `../tools/validate-metadata.py`.

### A.1 Minimal document

```json
{
  "oac_metadata": {
    "schema_version": "0.9",
    "files": {
      "cid":  { "file_identifier": 1608, "file_name": "OAC_CID.json"  },
      "scdd": { "file_identifier": 1601, "file_name": "OAC_SCDD.json" },
      "scda": { "file_identifier": 1604, "file_name": "OAC_SCDA.json" }
    }
  }
}
```

---

## Annex B (informative) -- PLDM Protocol Field Value Reference

Values an OAC sets on the File Descriptor PDR describing the OAC Metadata file.

| Field | Value | Note |
|-------|-------|------|
| `EntityType` | Device File | Per DSP0248 §28.30. |
| `FileClassification` | `FRUDataFile` | Retrieved per DSP0257, as the CID and Definition are. |
| `FileName` | `OAC_METADATA.json` | Reserved. The only reserved file name in the OAC management model. |
| `FileIdentifier` | Implementation-chosen `uint16` | What `DfOpen` takes. A controller matches `FileName`, then opens with this value. |
| `FcWritesPermitted` | 0 | The metadata file is read-only. |
| `ExWriteOpen` | 0 | The metadata file is read-only. |
| `FileMaximumSize` | Exact transferred size | Fixed Length File semantics; updated on firmware replacement. |
| `SuperiorDirectoryFileIdentifier` | `0xFFFF` | The OAC management files are a flat set; no directory is required. |
| `ContainerID` | Common to all OAC file and sensor PDRs | One `ContainerID` per OAC; `EntityInstanceNumber` distinguishes the files. |

Associated sensor:

| Sensor | State Set | Note |
|--------|-----------|------|
| Device File State Sensor | DSP0249 State Set 68 (Device File) | As for the CID and the SCD Definition. |
