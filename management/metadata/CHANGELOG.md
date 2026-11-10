# Changelog

All notable changes to the OAC Metadata specification, schema, template, examples, and validator are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers are OCP OAC workstream draft revisions, not semantic versions; a minor increment may still be a breaking change, and each entry says so explicitly.

Only the current revision is carried in the working tree. Superseded revisions remain retrievable from git history at the commit noted in their entry.

---

## [0.9] — 2026-11-09 — Initial publication

First publication of the OAC Metadata file. The version identifier matches the CID and SCD specifications it accompanies, because the three are read together and a reader should not have to reconcile three revision numbers to know they hold a consistent set.

**Breaking against the previous discovery model**, which is to say against the CID and SCD specifications as published at v0.9 revision 2. An upstream management controller that locates the CID by matching the `FileName` `OAC_CID.json` against the OAC's File Descriptor PDRs will continue to work against an OAC built to that model and will not work against one built to this specification, which is not obliged to publish the files in any order a controller can predict. The change is to discovery only. No wire value moves: `FileIdentifier`, `FileName`, `FileClassification`, and the Device File State Sensor associations are all unchanged, and the three OCP-defined file names are the same three strings they were.

### Added

- **The OAC Metadata file.** A JSON document with the root key `oac_metadata`, published as a FRU Data File and retrieved over DSP0257, carrying a `schema_version` and a `files` object. Each member of `files` maps a role to the `file_identifier` and `file_name` of that file's DSP0248 File Descriptor PDR. The document carries nothing else, and Specification Section 5.1 states that an implementation shall not place connector, power, or configuration data in it.

- **The reserved `FileName` `OAC_METADATA.json`** (Specification Section 6.3). This is the bootstrap, and it is worth being plain that the metadata file does not eliminate the hard-coded name — it reduces the count from three reserved strings to one. That one is now the only reserved file name in the OAC management model, and an OAC shall not assign it to any other file.

- **The OCP-defined roles `cid`, `scdd`, and `scda`** (Specification Section 7.3). `cid` is mandatory; `scdd` and `scda` are declared together or not at all. The second rule has a consequence worth naming: an OAC that implements no Slot Configuration Data now says so explicitly, where previously a controller learned it by finding no matching PDR, which is indistinguishable from a card that failed to publish one.

- **Vendor-defined roles under `pen.<IANA PEN>.<name>`** (Specification Section 7.5). This follows the SCD's namespacing convention rather than the CID's `vendor_<name>_` prefix. The divergence is deliberate and is recorded here so it is not read as an oversight: a role key identifies a file in the same sense an SCD field identifier identifies a field, and an IANA PEN is globally unique where a vendor name string is not.

- **Major-version compatibility** (Specification Section 5.2). A controller accepts a document whose major component it implements and ignores roles it does not recognize. This is looser than the SCD's exact-match `SCHEMA_VERSIONS = {"0.9"}`, and the divergence is likewise deliberate: a partially understood SCD Definition can yield a configuration both sides believe is valid and that is not, whereas an unrecognized file role is simply a file the controller will not open — the same outcome as the role being absent.

- **An explicit prohibition on fallback** (Specification Section 8.3). A controller whose metadata retrieval fails shall not fall back to matching `OAC_CID.json` directly. The fallback is the obvious compatibility shim and it is exactly wrong: it would energize a slot on data obtained by a path the OAC never advertised, which is the failure the management model exists to prevent.

- **`OAC-Metadata-v0.9.schema.json`**, a JSON Schema Draft 2020-12 document, with `$id` pointing at its own raw location in this repository. It expresses the structure of Specification Section 7, including `required: ["cid"]` and the `dependentRequired` pairing of `scdd` and `scda`, and a `propertyNames` pattern admitting the three defined roles plus the `pen.` namespace.

- **`templates/OAC-METADATA-TEMPLATE.json`**, annotated with `$comment` keys in the manner of the CID and SCD templates.

- **Three reference examples.** A, the ordinary three-role case; B, adding a vendor role under PEN 32473, the value IANA reserves for documentation; and C, the conformance case — `cid` alone, which a validator treating SCD as mandatory will wrongly reject.

- **`tools/validate-metadata.py`**, schema validation plus the semantic layer. Four of its rules cannot be expressed in JSON Schema and are the reason the layer exists: `file_identifier` uniqueness, `file_name` uniqueness, the prohibition on `OAC_METADATA.json` appearing as an entry, and the fixed names of Table 7.4-2. The first of these is the one that matters. DSP0248 defines `FileIdentifier` as unique relative to the PLDM Terminus ID, so two roles sharing a value describe the same file; a controller handed such a document opens a file successfully, parses it successfully, and acts on the wrong content, with no error raised anywhere in the transport.

- **`tools/test-validate-metadata.py`**, 28 cases across a positive and a negative half, modelled on the SCD self-test. The positive half asserts the published examples and the template are accepted, on the principle that a validator rejecting its own reference material is wrong about the specification rather than about the material.

### Notes for implementers

- **The schema sits at the top of this directory**, not in a `schema/` subfolder, so that the raw GitHub URL in its `$id` stays short and stable.

- **`$comment` is permitted at every level** of the document and shall be ignored. It is a JSON string member and not a comment in the ECMA-404 sense, which defines no comment syntax. Delete them before shipping and minify the result.

- **Unrecognized keys are ignored at any level of nesting**, not only at the root (Specification Section 7.1). The corresponding CID rule has been extended to match; see the CID changelog. A rule scoped to the root object alone would leave undefined precisely the case this document's extensibility depends on.

- **`file_name` remains fixed for the three OCP-defined roles** (Table 7.4-2), which reads at first as a contradiction of the whole exercise. The distinction is that those names are no longer the discovery mechanism. They are descriptive now, retained so the three files stay identifiable in a PDR dump, a firmware image, and diagnostic tooling. Fixing them costs nothing because the CID and SCD specifications fix them anyway, and a vendor-defined role carries no such constraint.

### Companion changes

Changes made outside this directory in the same pass, recorded here so the set is traceable from one place:

- **CID specification Section 6.3** — the WORK IN PROGRESS annotation is lifted and the metadata file becomes the normative discovery mechanism. For the CID this resolves a declared open item.
- **SCD specification Section 6.3 and Section 8.1** — the same mechanism, which for SCD is a change to text that was already settled rather than the resolution of a hedge. The SCD changelog entry supersedes the earlier `OemFileClassificationName` → `FileName` entry.
- **`management/README.md`** — the three-document model becomes four, and the stale PLDM data model row carrying `OemFileClassificationName` values is corrected.
