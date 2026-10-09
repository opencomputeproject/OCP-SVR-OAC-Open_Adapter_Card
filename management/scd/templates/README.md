# Templates

**OAC SCD Specification Version:** 0.9  
**OAC CID Specification Reference:** v0.9  
**OAC Base Specification Reference:** v0.9

SCD is two documents travelling in opposite directions, so there are two templates. The OAC publishes the Definition; the controller composes the Assignment. They are not interchangeable and have different root keys, `oac_scdd` and `oac_scda`.

## Contents

| File | Authored by | Description |
|------|-------------|-------------|
| [OAC-SCDD-TEMPLATE.json](OAC-SCDD-TEMPLATE.json) | OAC vendor | Annotated template for the SCD **Definition** — the OAC's declaration of every field it will accept, with type, constraints, and a mandatory default |
| [OAC-SCDA-TEMPLATE.json](OAC-SCDA-TEMPLATE.json) | Platform integrator | Annotated template for the SCD **Assignment** — the controller's sparse response, keyed by field identifier |

Both templates carry `$comment` keys for authoring guidance. **Every `$comment` key must be deleted before transfer**; ECMA-404 permits no comment syntax, and `$comment` is a convention of this repository rather than part of the schema.

## Authoring a Definition

1. Enumerate what is genuinely configurable about the OAC. Keep the subjects apart: a value that describes the *card* belongs in the **CID**, and only a value that describes the *slot* — the platform identity, conditions, and operational configuration of Specification Section 5.2.1 — belongs here.
2. Copy `OAC-SCDD-TEMPLATE.json` and delete the descriptors that do not apply.
3. Give every field a `default`. There is no such thing as a field without one — it is what makes a sparse Assignment safe. Where no correct value exists, use a sentinel default per Specification Section 7.6 and flag it with `"sentinel_default": true`.
4. Set the power field bounds from the OAC's own CID `power.primary` object. `ocp.max_power_w` takes `opl_emg_w` / `opl_max_w` and defaults to `opl_max_w`; `ocp.initial_power_max_w` and `ocp.initial_power_min_w` both take `opl_set_min_w` / `opl_max_w` — the CID declares no separate set-point ceiling, because the configurable range is always bounded above by the OAC's maximum validated operating point. The minimum defaults to `opl_set_min_w`; the maximum takes an OAC-declared default inside the range.
5. Declare one `ocp.link_subdivision.<connector>.<group>` field per subdividable protocol group, with the connector segment lowercased in the `id` and canonical in the `cid_binding`.
6. Put anything outside the `ocp.` registry under `pen.<your IANA PEN>.`. No OCP registration is needed.
7. Declare `definition_revision` if you find it useful. It is optional and informational — nothing validates it, and an OAC whose firmware update changes Definition content signals that by resetting its management controller, which deasserts `OAC_MC_RDY`.
8. Delete every `$comment`, validate with [`tools/validate-scd.py`](../tools/), minify, and publish as a FRU Data File named `OAC_SCDD.json`. The minified result shall not exceed 64 KB.

## Authoring an Assignment

1. Read and evaluate the OAC's **CID** first. If the platform cannot supply `opl_emg_w`, stop — do not power the OAC and do not read its Definition.
2. Read the OAC's **Definition** and resolve every `cid_binding` against the CID you just evaluated.
3. Copy `OAC-SCDA-TEMPLATE.json`. Echo `definition_revision` from the Definition if you want the provenance recorded; it is optional and the OAC will not check it.
4. Add a key only for a field you actually want to set. **Delete every other line.** Omitted fields take their declared defaults, and that is a normal, expected outcome — including for fields marked `required`, since the class describes the value rather than obliging the document. Expect the OAC to report the omission as State Set 15 state 4, Missing Configuration; that is a reading, not a refusal.
5. **Omit any field you do not recognize.** A vendor field you have never heard of self-handles; the OAC applies its default.
6. Do not assign a sentinel value, and do not use `null` anywhere.
7. Reconcile the power fields before you transfer. `ocp.initial_power_max_w` shall not exceed `ocp.max_power_w`, and `ocp.initial_power_min_w` shall not exceed `ocp.initial_power_max_w`. The OAC rejects a contradictory pair with code `0x10` rather than reducing one of the values to fit; a field you omit is compared at the default it falls back to.
8. Delete every `$comment`, validate, minify, and transfer with `DfOpen` / `DfWrite` / `DfClose` while the OAC is in O3, before `OAC_PWR_EN` is asserted.

## Schema Structure

```json
{ "oac_scdd": { "metadata": { ... }, "fields":      [ ... ] } }

{ "oac_scda": { "metadata": { ... }, "assignments": { ... } } }
```

**Definition sections**

| Section | Required | Description |
|---------|----------|-------------|
| `metadata` | Yes | `schema_version` and `oac_spec_revision` required; `definition_revision` and `description` optional. No other key is permitted |
| `fields` | Yes | Array of field descriptors, at least one element |

**Assignment sections**

| Section | Required | Description |
|---------|----------|-------------|
| `metadata` | Yes | `schema_version` required; `definition_revision` and `description` optional. No other key is permitted |
| `assignments` | Yes | Object keyed by field identifier. May be empty |

## Field Descriptor Constraints

| Key | Constraint |
|-----|------------|
| `id` | Prefixed `ocp.` or `pen.<PEN>.`; lowercase snake_case segments; unique within the document; max 128 characters |
| `display_name` | String, 1–64 characters |
| `type` | One of `integer`, `boolean`, `enumeration`. There is no text type — a value the OAC cannot validate is a value it cannot act on |
| `response` | `required` or `optional`. The class describes the value, not the document — never a hard gate |
| `default` | Mandatory on every descriptor. Inside `[min, max]` unless `sentinel_default` is true |
| `sentinel_default` | Boolean. When true, `default` must lie **outside** `[min, max]` |
| `min` / `max` | Integer fields only. Supply both or neither |
| `values` | Enumeration fields only. Each element carries `value` and `description`; `value` unique within the array |
| `cid_binding.cid_object` | `protocol_group` or `power.primary` |
| `cid_binding.cid_connector` | Required for `protocol_group`, forbidden for `power.primary`. Canonical CID casing, e.g. `CONN0` |
| `cid_binding.cid_group_name` | Required for `protocol_group`, forbidden for `power.primary`. Unique within its connector only |
| `cid_binding.constraint` | Required for `power.primary`, forbidden for `protocol_group`. Currently only `opl_range` |
| `applies_when` | `field` must name a descriptor in the same Definition. Single-field equality only |

Machine-readable constraints must not be restated in `description` prose — a descriptor whose prose contradicts its own `min`, `max`, or `values` is defective, and not duplicating them removes the possibility.

A `null` value is not the same as an absent field. Supplying `null` anywhere is a rejection (`0x0B`); omit the field instead.

## Two Traps Worth Naming

**Group names are unique per connector, not per document.** Two connectors may each declare a group named `pcie_primary`, and a conformant validator must accept that. The expected implementation error here is over-enforcement — a validator carried forward from a document-wide-uniqueness draft will reject conformant CIDs. Test it explicitly.

**Never persist an Assignment to flash or EEPROM.** It looks like robustness. What it actually does is prevent the OAC from ever re-arming, so an OAC moved to a different chassis comes up carrying the previous platform's slot identifier, subdivision, and *initial power level* while reporting itself as `latched`. See Specification Section 11.6.4.

## CID Dependency

These templates assume two CID features introduced in OAC-CID-SPEC v0.8: a `name` on every protocol group, and no `link_subdivision` in the CID. A `protocol_group` binding resolves against the `(connector, group name)` pair, so a pre-v0.8 CID cannot satisfy one. See the "CID dependencies" section of [CHANGELOG.md](../CHANGELOG.md).
