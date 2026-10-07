# CID Template — v0.9

**Schema Version:** 0.9
**Specification Reference:** [OAC-CID-Specification-v0.9.md](../../specification/OAC-CID-Specification-v0.9.md)

Blank annotated OAC Connector Interface Definition template, for authoring a CID conforming to
schema version 0.9.

| File | Description |
|------|-------------|
| [OAC-CID-TEMPLATE.json](OAC-CID-TEMPLATE.json) | Annotated template. Carries both a profile-referencing connector and an explicitly-declared connector so that either approach can be used as the starting point |

## Usage

1. Copy `OAC-CID-TEMPLATE.json`.
2. Replace every `"<placeholder>"` value with a real value for your OAC. `schema_version` is already
   set to `"0.9"`; set `oac_spec_revision` to the Base Specification revision the card was designed
   against. Both are **required**.
3. For each connector, keep **either** the `connector_profile` reference **or** the explicit
   `high_speed_lanes` / `clocking` / `discrete_signals` block — never both on the same connector.
   Different connectors in one CID may use different approaches.
4. Delete connector objects for positions your card does not populate. CONN0 is always present.
5. Delete optional fields that do not apply.
6. Validate that the JSON is well-formed per ECMA-404. Comments are not permitted — a `//` or
   `/* */` sequence outside a string literal makes the document malformed.
7. Minify before publishing. Production OACs serve minified UTF-8 with no byte order mark.

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
- Use **IANA PEN 32473** in any example or test document. It is the number IANA reserves for
  documentation. Substitute your own Private Enterprise Number in a real CID.
