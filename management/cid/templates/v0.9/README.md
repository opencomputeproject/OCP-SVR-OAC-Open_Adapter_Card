# CID Template — v0.9

**Schema Version:** 0.9
**Specification Reference:** [OAC-CID-Specification-v0.9.md](../../specification/OAC-CID-Specification-v0.9.md)

Blank annotated OAC Connector Interface Definition template, for authoring a CID conforming to
schema version 0.9.

| File | Description |
|------|-------------|
| [OAC-CID-TEMPLATE.json](OAC-CID-TEMPLATE.json) | Annotated template. Carries both a profile-referencing connector and an explicitly-declared connector so that either approach can be used as the starting point, and a `power.excursion` array pre-filled at the Base Specification ceiling |

Annotations are carried in `$comment` keys. They are not part of the schema — a CID reader ignores
them, under the unrecognized-key rule of specification Section 7.1, which applies at every nesting
level. Deleting them before publishing is optional but reduces the transferred payload.

## Usage

1. Copy `OAC-CID-TEMPLATE.json`.
2. Replace every `"<placeholder>"` value with a real value for your OAC. `schema_version` is already
   set to `"0.9"`; set `oac_spec_revision` to the Base Specification revision the card was designed
   against. Both are **required**.
3. For each connector, keep **either** the `connector_profile` reference **or** the explicit
   `high_speed_lanes` / `clocking` / `discrete_signals` block — never both on the same connector.
   Different connectors in one CID may use different approaches.
4. Delete connector objects for positions your card does not populate. CONN0 is always present.
5. Replace the `power.excursion` ratios with your OAC's characterized values, or delete the whole
   array. The values shipped in the template are the Base Specification Section 10.1.4 ceiling, which
   is what the controller assumes anyway when the array is absent — leaving them in place declares
   nothing the platform did not already have to budget for.
6. Delete optional fields that do not apply.
7. Validate that the JSON is well-formed per ECMA-404. Comments are not permitted — a `//` or
   `/* */` sequence outside a string literal makes the document malformed.
8. Publish as UTF-8 with no byte order mark. Expanded and minified are both valid; minifying first is recommended for production, to reduce the transferred payload.

The [CID Editor](../../tools/interactive/oac-cid-editor/) does all of this interactively, with a
visual pin map and live JSON preview, and is usually faster than editing the template by hand.

## Reminders

- **Pin A1 is permanently reserved** for `OAC_PRSNT#` / M-PESTI and is not assignable.
- **CONN0 has 9 assignable columns; CONN1–CONN6 have 8.** CONN0 carries the OAC Management USB 2.0
  interface on columns 10–11, with `OAC_MC_RDY` on column 11.
- **Protocol group names** are snake_case and unique within their connector — not across the
  document. The SCD binds to the `(connector, group name)` pair, so a group without a name cannot be
  referenced by an SCD field.
- **No more than 8 protocol groups** on any connector.
- **Power envelopes belong here, not in the SCD.** `OPL-MAX ≥ OPL-EFF ≥ OPL-RED ≥ OPL-EMG`.
  `opl_max_w` and `opl_emg_w` are required; the rest are optional.
- **`power.excursion` ratios are normalized to `opl_max_w` only.** They do not rescale when the slot
  runs at OPL-EFF, and the declared profile does not apply at all at OPL-RED, OPL-EMG, or OPL-SET,
  where the effective ratio is 1. A card that needs transient headroom below OPL-EFF has to raise
  `opl_emg_w` or `opl_red_w` instead — there is no field that grants it.
- **An excursion ratio that implies a current above the connector's derated continuous rating is not
  an error.** The derated rating is thermal; the declared figure is a microsecond-scale average. The
  validator reports the implied current and does not judge it.
- Use **IANA PEN 32473** in any example or test document. It is the number IANA reserves for
  documentation. Substitute your own Private Enterprise Number in a real CID.
