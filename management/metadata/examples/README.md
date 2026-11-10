# Reference Examples

**OAC Metadata Specification Version:** 0.9

Three reference documents, each validating cleanly against [`../OAC-Metadata-v0.9.schema.json`](../OAC-Metadata-v0.9.schema.json) and [`../tools/validate-metadata.py`](../tools/). All are pretty-printed for readability; a production metadata file is minified.

| File | Exercises |
|------|-----------|
| [OAC-METADATA-0.9-ExampleA-Minimal.json](OAC-METADATA-0.9-ExampleA-Minimal.json) | The ordinary case — all three OCP-defined roles |
| [OAC-METADATA-0.9-ExampleB-VendorFile.json](OAC-METADATA-0.9-ExampleB-VendorFile.json) | A vendor-defined role alongside the three defined ones |
| [OAC-METADATA-0.9-ExampleC-CID-Only.json](OAC-METADATA-0.9-ExampleC-CID-Only.json) | **Conformance case.** `cid` alone; no Slot Configuration Data |

---

## Example A — Minimal

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

What a fully featured OAC publishes, and the shape most implementations will carry. There is no metadata entry for the metadata file itself; it is located by the reserved `FileName` `OAC_METADATA.json`, and an entry describing it would describe a file that is already open.

The identifiers are not consecutive and not ordered, which is deliberate. They are drawn from an OAC's own PDR repository alongside whatever other device files it publishes, and nothing in the model gives the three management files adjacent numbering. A controller that assumes `cid + 1` is the Definition will work against an example and fail against a card.

What they must be is **distinct**. Setting `scdd` to 1608 here would produce a document that passes every structural check and sends the controller to the CID when it asked for the Definition. See the `DUPLICATE_IDENTIFIER` case in [`../tools/test-validate-metadata.py`](../tools/).

---

## Example B — Vendor file

Example A plus a fourth role:

```json
"pen.32473.telemetry_map": {
  "file_identifier": 1712,
  "file_name": "VENDOR_TELEMETRY_MAP.json"
}
```

This is the extensibility the metadata file exists to provide, in the smallest form that shows it. Under the previous model this file was unreachable: a controller located management files by matching `FileName` strings fixed in OCP specifications, and no specification fixes `VENDOR_TELEMETRY_MAP.json`. Here the OAC simply advertises it, and a controller that knows the role opens it with the identifier given.

Three details are load-bearing.

**The namespace is `pen.<IANA PEN>.<name>`**, following the SCD field-identifier convention rather than the CID's `vendor_<name>_` prefix. A PEN is globally unique; a vendor name string is not, and two companies both calling themselves `acme` is not a hypothetical. No OCP registration is required.

**PEN 32473 is IANA's documentation PEN.** It appears throughout this repository's examples for the same reason `192.0.2.0/24` appears in networking documentation. A real OAC uses its own.

**The `file_name` is unconstrained.** Table 7.4-2 fixes names only for `cid`, `scdd`, and `scda`. A vendor role names its file whatever its PDR carries — but the name must still be distinct from every other role's in the document, and must not be `OAC_METADATA.json`.

A controller that has never heard of `pen.32473.telemetry_map` ignores it and proceeds. That is the whole mechanism: the unknown role costs it nothing, and the known roles are unaffected.

---

## Example C — CID only

```json
{
  "oac_metadata": {
    "schema_version": "0.9",
    "files": {
      "cid": { "file_identifier": 1608, "file_name": "OAC_CID.json" }
    }
  }
}
```

**This is the conformance case, and it is here to be failed by a wrong validator.** An OAC that implements no Slot Configuration Data declares `cid` and nothing else. A tool that treats `scdd` and `scda` as mandatory — a reasonable-seeming assumption, since they appear in every other example — rejects this document, and the card it describes never gets powered.

The document also pins the rule in the other direction. Adding `scdd` here *without* `scda`, or `scda` without `scdd`, is rejected. The two are halves of one exchange: a Definition the controller cannot answer leaves the fields it describes unset with no way to set them, and an Assignment with no Definition gives the controller no field descriptors to compose one from. The schema expresses this with `dependentRequired`; the negative half of the self-test asserts both directions.

A controller finding neither role proceeds to energization on the CID alone. That is a normal outcome, not a degraded one.

---

## What the examples cannot show

The structural rules are all visible above. Two requirements are not, because they concern the card rather than the document.

**Every `file_identifier` must correspond to a File Descriptor PDR that actually exists.** Specification Section 8.2 requires the controller to verify this as it resolves each role, and classifies a dangling identifier as a *malformed metadata document* rather than a missing file — the card said the file was there, and it was not. No amount of validating this JSON detects it.

**Every `file_name` must match the `FileName` in that same PDR.** The validator checks the three OCP-defined roles against Table 7.4-2, which catches a typo in the document. It cannot catch a PDR that disagrees with a document that is correct.

Both are checked on hardware, or against a staged firmware image with `--resolve`.
