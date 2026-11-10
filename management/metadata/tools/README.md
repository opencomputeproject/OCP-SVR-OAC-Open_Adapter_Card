# Tools

**OAC Metadata Specification Version:** 0.9

| File | Description |
|------|-------------|
| [validate-metadata.py](validate-metadata.py) | Validates an OAC Metadata document against the schema and the specification's semantic rules |
| [test-validate-metadata.py](test-validate-metadata.py) | Self-test for the validator — 28 cases, positive and negative |

## Requirements

Python 3.8 or later and `jsonschema` 4.x:

```
python3 -m pip install jsonschema
```

Version 4 is required, not merely recommended. The schema is Draft 2020-12 and uses `dependentRequired`; `jsonschema` 3.x provides neither `Draft202012Validator` nor that keyword, and will fail to import rather than silently skipping the check.

## Usage

```
python3 validate-metadata.py ../examples/OAC-METADATA-0.9-ExampleA-Minimal.json
```

The schema defaults to the sibling `../OAC-Metadata-v0.9.schema.json`, so `--schema` is needed only when validating against a revision other than the one in this tree. Multiple documents may be given at once.

| Option | Effect |
|--------|--------|
| `--schema PATH` | Validate against a schema other than the sibling default |
| `--resolve DIR` | Also check that every advertised `file_name` exists in `DIR` |

`--resolve` is meant for a staged firmware image, where files sit under their `FileName` values. It is meaningless against this repository, where the artifacts carry repository names like `OAC-CID-0.9-ExampleA-Minimal.json` — point it at a repository directory and every role will report as missing.

| Exit status | Meaning |
|-------------|---------|
| 0 | Schema valid and every instance valid |
| 1 | At least one instance failed validation |
| 2 | The schema or an input file could not be processed |
| 3 | The `jsonschema` dependency is missing |

Running the self-test:

```
python3 test-validate-metadata.py
```

Exit status is 0 when every case behaves as expected, 1 otherwise.

---

## Why there is a semantic layer

JSON Schema expresses the structure of the document: the root key, the required members, the integer bounds, the role-name pattern, and the `dependentRequired` pairing of `scdd` and `scda`. Five rules in the specification are not structural and are implemented in `semantic_errors()`.

**`file_identifier` uniqueness across roles** is the one the artifact exists to enforce. DSP0248 defines `FileIdentifier` as unique relative to the PLDM Terminus ID, so two roles carrying the same value describe the same file and at most one can be right. JSON Schema has no vocabulary for "these sibling values must differ" — `uniqueItems` applies to arrays, and `files` is an object. The failure mode is what makes it worth a dedicated check: a controller handed a duplicate performs a successful `DfOpen`, a successful read, and a successful parse, and then acts on the contents of the wrong file. Nothing in the PLDM transport reports anything.

**`file_name` uniqueness** is the same failure in a different place, and is checked the same way.

**The fixed names of Table 7.4-2** — `cid` must name `OAC_CID.json`, and so on. Only the three OCP-defined roles are checked; a vendor role may name its file anything.

**The reserved-name prohibition** — no role may carry `file_name` `OAC_METADATA.json`. That name denotes the metadata file itself, and an entry carrying it would describe a file that is already open.

**Major-version compatibility** — `SUPPORTED_MAJOR = "0"`. A document whose major component this tool does not implement is rejected; the minor component is not consulted, per Specification Section 5.2. This is looser than the SCD validator's exact-match `SCHEMA_VERSIONS` set, deliberately, and the constant is deliberately a single value rather than a set so that the looseness is visible in the source.

Findings from both layers are reported in the same format, as a JSON path and a message, with the specification section cited. They are sorted together, so a document with a structural defect and a semantic one reports both in one run rather than requiring two passes.

---

## The self-test

Two halves, on the model of the SCD's `test-validate-scd.py`.

**The positive half** asserts that every published example in `../examples/`, and the template in `../templates/`, is accepted. A validator that rejects its own reference material is wrong about the specification, not about the material — and this half has already caught exactly that: an early template used `file_identifier: 0` for all three roles and tripped the duplicate-identifier rule, and a later schema revision closing `additionalProperties` would have rejected the templates' `$comment` annotations had the test not been there to object.

**The negative half** mutates a published example in memory, one defect at a time, and asserts a rejection comes back. This is the load-bearing half; a validator that accepts everything passes the positive half perfectly.

Two cases are named in the source because they carry more than their own weight.

`DUPLICATE_IDENTIFIER` is the defect described above — the one no schema keyword catches and no transport reports.

`MULTI_DIGIT_VERSION_OK` exists because the source package this artifact derives from shipped an example with `schema_version` `"11.31"`, purely to exercise the multi-digit pattern. That belongs in a test and not in reference material a vendor might copy, so the published examples all read `0.9` and the pattern is exercised here instead.

The positive half also asserts that `$comment` is accepted at all four levels of the document and that two vendor roles may share one PEN namespace. Both are permitted by the specification and both are the kind of permission that gets closed off by accident when a schema is tightened.
