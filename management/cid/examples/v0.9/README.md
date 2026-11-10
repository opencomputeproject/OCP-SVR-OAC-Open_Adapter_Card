# CID Reference Examples — v0.9

**Schema Version:** 0.9
**Specification Reference:** [OAC-CID-Specification-v0.9.md](../../specification/OAC-CID-Specification-v0.9.md)

Reference OAC Connector Interface Definition documents for CID schema version 0.9. All are shown in
expanded form for readability. A production OAC may publish either form; the minified equivalent is recommended, and is the same document with optional whitespace removed.

The first two illustrate the two ways a connector's signal assignment may be expressed. The three
excursion examples illustrate `power.excursion`, and are deliberately plain on the connector side so
that the power declaration is the only thing varying between them.

| File | Form Factor | Power | Connectors |
|------|-------------|-------|-----------|
| [OAC-CID-0.9-2500W-PCIe-x16-(Example_using_connector_profile).json](OAC-CID-0.9-2500W-PCIe-x16-%28Example_using_connector_profile%29.json) | Double-wide offset | +50V, 125A (BK125), 2500 W OPL-MAX, 625 W OPL-EMG | CONN0 only, by profile reference |
| [OAC-CID-0.9-SW-2500W-16L_PCIe-96L_Ethernet(Example_mixed_definition).json](OAC-CID-0.9-SW-2500W-16L_PCIe-96L_Ethernet%28Example_mixed_definition%29.json) | Single-wide | +50V, 100A (BK100), 2500 W OPL-MAX, 625 W OPL-EMG, OPL-SET floor 625 W | CONN0 explicit + CONN1–CONN6 by profile reference |
| [OAC-CID-0.9-ExampleA-Excursion-4800W.json](OAC-CID-0.9-ExampleA-Excursion-4800W.json) | Double-wide | +50V, 125A (BK125), 4800 W OPL-MAX, 1200 W OPL-EMG, OPL-SET floor 1200 W | CONN0 only, by profile reference |
| [OAC-CID-0.9-ExampleB-Excursion-600W.json](OAC-CID-0.9-ExampleB-Excursion-600W.json) | Single-wide | +12V, 100A (BK100), 600 W OPL-MAX, 200 W OPL-EMG, OPL-SET floor 200 W | CONN0 only, by profile reference |
| [OAC-CID-0.9-ExampleC-Excursion-3000W.json](OAC-CID-0.9-ExampleC-Excursion-3000W.json) | Single-wide | +50V, 100A (BK100), 3000 W OPL-MAX, 750 W OPL-EMG, OPL-SET floor 750 W | CONN0 + CONN1, both by profile reference |

---

## What Each Example Shows

### Profile reference — the short form

CONN0 is declared entirely by `connector_profile`, referencing
`OAC-PROF-CONN0-PCIeGen6-x16-IN-v1`. No `high_speed_lanes`, `clocking`, or `discrete_signals` appear
on that connector, because a profile reference and explicit declarations are mutually exclusive.

This is the shortest conformant CID shape. Where a ratified profile matches the card's pinout, the
per-lane pin map need not be repeated — the controller already has built-in knowledge of every
profile ratified at or before the declared `schema_version`, so there is no runtime fetch.

The card declares only the two mandatory power fields, `opl_max_w` and `opl_emg_w`, and no
`opl_set_min_w`, so OPL-SET is not supported. A corresponding SCD Definition therefore has no settable power band, and offers neither
`ocp.initial_power_max_w` nor `ocp.initial_power_min_w`. For
that worked through end to end, see Triple A in [`../../../scd/examples/`](../../../scd/examples/).

### Mixed definition — both approaches in one document

CONN0 carries a full explicit per-lane pin map for PCIe Gen6 x16, while CONN1 through CONN6 each
reference `OAC-PROF-CONN-Eth200G-x16-OUT-v1` for 96 lanes of 200G Ethernet in aggregate.

This is the common real-world shape: a card's management and host connector is usually
vendor-specific enough to need explicit declaration, while its fabric connectors follow a ratified
standard pinout. The two approaches are exclusive *per connector*, not per document.

It also declares `opl_set_min_w` of 625 W, which makes the SCD power set points
`ocp.initial_power_max_w` and `ocp.initial_power_min_w` available to the SCD Definition. The
configurable range runs from that floor up to `opl_max_w`, 2500 W; the ceiling is not declared
separately.

### Declared power excursion — three positions against the same ceiling

Examples A, B, and C all declare `power.excursion` on the recommended interval grid of Table 7.3.2-2,
and the point of having three is that they sit in different places relative to the Base Specification
Section 10.1.4 envelope.

**Example A** is the case the field was added for. At 10 µs the specification permits 3.00 and the
card declares 2.60; at 10 ms the specification permits 2.0004 and the card declares 1.55. A platform
budgeting eight of these slots against the ceiling instead of the declaration provisions for
transients that will never occur.

**Example B** is the case the validation rules have to keep legal. Every ratio sits at or just under
the envelope — 3.00 at both 10 µs and 100 µs — so the declaration buys the platform nothing. It is
still worth making: a declared ceiling is a verified claim, and the absence of a declaration is not.
A validator that treated "declares the maximum" as suspicious would be wrong about the field.

**Example C** sits between them, and is the one to read if only one is read. At `opl_max_w` of
3,000 W the declared 2.80 at 10 µs implies 168 A at the +50V input, which is above the BK100
variant's 80 A derated continuous rating. That is not a validation failure. The derated rating is a
thermal limit on *sustained* current; 168 A is a 10 µs average. Check 6 of Table 9.3-1 computes and
reports this number precisely because no pulse-current rating exists to judge it against — the
question of whether the BK100 and BK125 connectors carry an I²t limit or a current-versus-duration
curve is open with the connector and mechanical subgroup. If an answer arrives, the check becomes
normative without the field changing.

All three declare a `ratio_max` of exactly 1.00 at 1,000,000 µs. At a one-second average an OAC is
not excursing, it is running; the final point is where the profile rejoins `opl_max_w`.

Note what none of the three declare: an absolute peak wattage, or a reference level. `ratio_max` is
normalized to `opl_max_w` and to nothing else, so Example A's 2.60 at 10 µs means 12,480 W whether
the card is running at OPL-MAX or at OPL-EFF — the profile does not rescale downward at the lower
sustained level. At OPL-RED, OPL-EMG, and OPL-SET the effective ratio is 1 regardless of what the
file says, per Section 7.3.2.

---

## Note on Filenames

Both filenames contain parentheses. These are legal on GitHub but must be percent-encoded as `%28`
and `%29` in a Markdown link, which is why the links in the table above look the way they do. New
example files should avoid parentheses, spaces, and `#` — the last of these is a URL fragment
delimiter and silently truncates direct links.

---

## Known Issues

The two original examples — the profile-reference and mixed-definition files — have conformance
defects against the v0.9 specification, recorded here so the files are not taken as fully normative
references until corrected. The three excursion examples are not affected; they declare
`schema_version` and `oac_spec_revision` and their descriptions agree with their declared values.

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
