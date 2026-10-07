# CID Reference Examples — v0.9

**Schema Version:** 0.9
**Specification Reference:** [OAC-CID-Specification-v0.9.md](../../specification/OAC-CID-Specification-v0.9.md)

Reference OAC Connector Interface Definition documents for CID schema version 0.9. Both are shown in
expanded form for readability; a production OAC publishes the minified equivalent.

| File | Form Factor | Power | Connectors |
|------|-------------|-------|-----------|
| [OAC-CID-0.9-2500W-PCIe-x16-(Example_using_connector_profile).json](OAC-CID-0.9-2500W-PCIe-x16-%28Example_using_connector_profile%29.json) | Double-wide offset | +50V, 125A (BK125), 2500 W OPL-MAX, 625 W OPL-EMG | CONN0 only, by profile reference |
| [OAC-CID-0.9-SW-2500W-16L_PCIe-96L_Ethernet(Example_mixed_definition).json](OAC-CID-0.9-SW-2500W-16L_PCIe-96L_Ethernet%28Example_mixed_definition%29.json) | Single-wide | +50V, 100A (BK100), 2500 W OPL-MAX, 625 W OPL-EMG, OPL-SET band 625–2500 W | CONN0 explicit + CONN1–CONN6 by profile reference |

---

## What Each Example Shows

### Profile reference — the short form

CONN0 is declared entirely by `connector_profile`, referencing
`OAC-PROF-CONN0-PCIeGen6-x16-IN-v1`. No `high_speed_lanes`, `clocking`, or `discrete_signals` appear
on that connector, because a profile reference and explicit declarations are mutually exclusive.

This is the shortest conformant CID shape. Where a ratified profile matches the card's pinout, the
per-lane pin map need not be repeated — the controller already has built-in knowledge of every
profile ratified at or before the declared `schema_version`, so there is no runtime fetch.

The card declares only the two mandatory power fields, `opl_max_w` and `opl_emg_w`, and no OPL-SET
band. A corresponding SCD Definition therefore has no `ocp.initial_power_level_set_w` to offer. For
that worked through end to end, see Triple A in [`../../../scd/examples/`](../../../scd/examples/).

### Mixed definition — both approaches in one document

CONN0 carries a full explicit per-lane pin map for PCIe Gen6 x16, while CONN1 through CONN6 each
reference `OAC-PROF-CONN-Eth200G-x16-OUT-v1` for 96 lanes of 200G Ethernet in aggregate.

This is the common real-world shape: a card's management and host connector is usually
vendor-specific enough to need explicit declaration, while its fabric connectors follow a ratified
standard pinout. The two approaches are exclusive *per connector*, not per document.

It also declares an OPL-SET band of 625–2500 W, which is what makes
`ocp.initial_power_level_set_w` available to the SCD Definition.

---

## Note on Filenames

Both filenames contain parentheses. These are legal on GitHub but must be percent-encoded as `%28`
and `%29` in a Markdown link, which is why the links in the table above look the way they do. New
example files should avoid parentheses, spaces, and `#` — the last of these is a URL fragment
delimiter and silently truncates direct links.

---

## Known Issues

Both examples have conformance defects against the v0.9 specification, recorded here so the files
are not taken as fully normative references until corrected:

| Issue | Detail |
|-------|--------|
| Missing required metadata | Both `metadata` objects contain only `description`. Table 7.2-1 marks **`schema_version` and `oac_spec_revision` as Required**, and neither is present in either file |
| Description contradicts data | Both descriptions read "645W OPL-EMG" while the declared `opl_emg_w` is `625`. The table above states the declared value, which is the one that governs |

The structural content of both examples — connector declarations, pin maps, profile references, and
power envelopes — is correct and useful. The defects are confined to the `metadata` object and the
free-text description.

---

## Related

- [Template](../../templates/v0.9/) — blank annotated starting point
- [Connector Profiles](../../profiles/) — the ratified profiles referenced here
- [CID Editor](../../tools/interactive/oac-cid-editor/) — load either file to inspect it visually
- [Insertion Emulator](../../tools/interactive/oac-cid-insertion-emulator/) — run either file against a baseboard capability declaration
- [SCD Examples](../../../scd/examples/) — matched CID + Definition + Assignment triples
