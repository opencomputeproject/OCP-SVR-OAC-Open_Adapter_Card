# Templates

**OAC Metadata Specification Version:** 0.9  
**OAC CID Specification Reference:** v0.9  
**OAC SCD Specification Reference:** v0.9

## Contents

| File | Authored by | Description |
|------|-------------|-------------|
| [OAC-METADATA-TEMPLATE.json](OAC-METADATA-TEMPLATE.json) | OAC vendor | Annotated template for the OAC Metadata file |

There is one template because there is one document, and only the OAC authors it. The upstream management controller never composes a metadata file and never writes one — unlike the SCD, where the Assignment travels back the other way.

The template carries `$comment` keys for authoring guidance. **Every `$comment` key must be deleted before transfer.** ECMA-404 permits no comment syntax, and `$comment` is a convention of this repository rather than part of the schema. The schema does permit the key — at every level, so the template can annotate itself — but a production metadata file is minified and carries none.

## Authoring a metadata file

1. Copy `OAC-METADATA-TEMPLATE.json`.

2. **Set `schema_version` to the revision of the specification you built against**, currently `0.9`. A controller matches on the major component and ignores roles it does not recognize, so a later minor revision remains readable by an older controller. That tolerance does not extend to redefining an existing field; see Specification Section 5.2.

3. **Fill in `file_identifier` for each role from your own PDR repository.** These are the `FileIdentifier` values you assigned in each file's DSP0248 File Descriptor PDR. The template ships `1`, `2`, `3` as obvious placeholders — they are valid, they are almost certainly not yours, and shipping them unchanged is the most likely way to get this file wrong in a way that still validates.

   The values must be **distinct across roles**. `FileIdentifier` is unique relative to the PLDM Terminus ID, so two roles sharing one describe the same file. This is the failure the metadata file exists to prevent and the one with the worst consequences: a controller handed a duplicate opens a file successfully, parses it successfully, and acts on the wrong content. Nothing in the transport reports an error. The validator catches it; JSON Schema cannot.

4. **Leave `file_name` alone for the three OCP-defined roles.** `OAC_CID.json`, `OAC_SCDD.json`, and `OAC_SCDA.json` are fixed by Table 7.4-2 and must match the `FileName` strings in the corresponding PDRs. If your PDR carries a different string, change the PDR, not this file.

5. **Delete `scdd` and `scda` together if your OAC implements no Slot Configuration Data.** Deleting one and keeping the other is rejected. They are halves of one exchange: a Definition with no Assignment to write gives the controller nothing to do with the fields it describes, and an Assignment with no Definition gives it nothing to compose one from. An OAC declaring neither is fully conformant and the controller proceeds to energization on the CID alone — see [Example C](../examples/).

6. **Do not delete `cid`.** It is mandatory. The CID is what the energization decision is made on, and an OAC that publishes no CID cannot be evaluated.

7. **Add vendor files under `pen.<your IANA PEN>.<name>`.** No OCP registration is needed. The name segment is lowercase `a`–`z`, `0`–`9`, and underscore. A vendor role carries no fixed `file_name` — use whatever your PDR carries. A controller that does not recognize the role ignores it.

8. **Do not add an entry for the metadata file itself.** `OAC_METADATA.json` is reserved for it, and an entry carrying that name would describe a file that is already open. The validator rejects it.

9. **Do not add a file-type key.** The root key `oac_metadata` already identifies the document. A second type declaration admits the case where the two disagree, and then something has to arbitrate.

10. Delete every `$comment`, validate with [`tools/validate-metadata.py`](../tools/), minify, and publish as a FRU Data File whose File Descriptor PDR carries the `FileName` `OAC_METADATA.json`, with `FcWritesPermitted` and `ExWriteOpen` both zero.

## Checking your work against the PDR repository

The validator can check names against a directory with `--resolve`:

```
python3 ../tools/validate-metadata.py OAC-METADATA-TEMPLATE.json --resolve /path/to/staged/image
```

That is useful against a staged firmware image, where the files sit under their `FileName` values. It is meaningless against this repository, where the artifacts carry repository names like `OAC-CID-0.9-ExampleA-Minimal.json`.

What the tool cannot check from here is the part most worth checking: that each `file_identifier` you declared corresponds to a File Descriptor PDR that actually exists on the card. Specification Section 8.2 requires a controller to verify this as it resolves each role, and treats a dangling identifier as a malformed metadata document rather than a missing file. Verify it on the card.

## Schema structure

```json
{
  "oac_metadata": {
    "schema_version": "0.9",
    "files": {
      "<role>": {
        "file_identifier": 0,
        "file_name": "..."
      }
    }
  }
}
```

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `schema_version` | string | Yes | `major.minor`, multiple digits permitted in each |
| `files` | object | Yes | At least one member; `cid` mandatory |
| `files.<role>.file_identifier` | integer | Yes | 0–65535; distinct across roles; what `DfOpen` takes |
| `files.<role>.file_name` | string | Yes | Fixed per Table 7.4-2 for `cid`, `scdd`, `scda`; free for vendor roles; distinct across roles |
| `$comment` | string | No | Permitted at any level; ignored; delete before shipping |

The full structural rules are in the [schema](../OAC-Metadata-v0.9.schema.json); the rules the schema cannot express are in [`tools/validate-metadata.py`](../tools/).
