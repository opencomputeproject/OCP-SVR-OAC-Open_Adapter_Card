# OAC CID Specification — Changelog

All notable changes to the OAC Connector Interface Definition (CID) specification and associated tooling are documented here.

---

## [0.9] — 2026-11-09 — Workstream review revision 3

Third in-place revision of the v0.9 document. The version identifier is unchanged, by workstream decision: every change below is additive or confined to discovery, and a reader holding the CID, SCD, and Metadata documents should not have to reconcile three revision numbers to know the set is consistent.

Three changes to the specification, plus the tooling that implements them. The first resolves the open item that Section 6.3 had carried since the first publication of this document. The second and third implement the power excursion proposal — the nesting clarification is listed separately because it stands on its own, but it is the prerequisite the proposal identified as the one item that had to be settled before the field could be adopted safely.

### Changed — file discovery now goes through the OAC Metadata file

**Breaking for upstream management controllers.** A controller that locates the CID by matching the `FileName` `OAC_CID.json` against the OAC's File Descriptor PDRs will not work against an OAC built to this revision. OAC implementations are affected only by the addition of the metadata file itself; no field on the CID's own File Descriptor PDR changes value.

- **Section 6.3 is rewritten, and its WORK IN PROGRESS annotation is lifted.** The annotation had flagged the hard-coded `FileName` and the match-on-name-then-open-by-identifier sequence as under review, and named the metadata-file alternative as the thing being considered. The workstream has adopted that alternative. Discovery now proceeds from the OAC Metadata file, defined in the new [OAC-METADATA-SPEC](../metadata/specification/); the CID is declared under its `cid` role, and a controller resolves that role to obtain the `FileIdentifier` it opens.

- **`FileName` remains `OAC_CID.json` and remains fixed.** This is worth stating plainly because it reads as a contradiction. The name is no longer the discovery mechanism — it is descriptive, retained so the CID stays identifiable in a PDR repository dump, in a firmware image, and to diagnostic tooling, and so that the `file_name` the metadata advertises can be checked against the record it describes. An OAC shall assign the name to no other file.

- **Fallback is prohibited, not merely discouraged.** A controller whose metadata retrieval fails shall not drop back to matching `OAC_CID.json`. That shim is the obvious compatibility move and it is exactly the wrong one: it energizes a slot on data obtained by a path the OAC never advertised, which is the failure the whole management model exists to prevent.

- **Section 9.2 step 3 is rewritten** to retrieve and validate the metadata file and resolve the `cid` role, and the step list now states what changed and why rather than leaving an implementer to infer it from a diff. The failure paragraph is extended to cover metadata retrieval failure and the dangling-identifier case — a `FileIdentifier` advertised under `cid` for which no File Descriptor PDR exists is a *malformed metadata document*, not a missing CID, because the card said the file was there and it was not.

- **Table 10.1-1 gains two OAC rows** — declare the CID under the `cid` role, and assign `OAC_CID.json` to no other file. **Table 10.2-1's locate-by-FileName row is replaced** by a resolve-the-`cid`-role row, and a second row is added prohibiting the fallback.

- **Annex B's scoping NOTE is removed.** It existed only to mark the annex's values provisional to the extent Section 6.3 was provisional. Section 6.3 is settled, so the note has nothing left to scope. Table B-2's `FileName` and `FileIdentifier` rows are reworded: the name is no longer "the discriminator an upstream management controller matches on."

- **Section 2 adds OAC-METADATA-SPEC** to the normative references.

### Changed — unrecognized keys are ignored at every level of nesting

**Section 7.1.** The rule previously read, in a single sentence shared with the vendor-prefix requirement, that "the upstream management controller shall ignore unrecognized keys" — stated among the rules governing top-level keys within `"oac_cid"`, and so readable as scoped to that level alone.

It is now stated separately and explicitly for any level of nesting, with the reason given: scoped to the top level, the rule leaves undefined the behavior of a controller that meets an unfamiliar member inside `"power"`, inside a connector object, or inside anything nested within them — which is exactly where this specification's own extensions arrive, the `power.excursion` array below being the immediate case. A paragraph is added clarifying that ignoring a key means proceeding as though it were absent, and does not license treating the containing object as malformed or skipping validation of the keys that *are* recognized.

This is a clarification rather than a new requirement, but it is a load-bearing one: a controller that rejected an unfamiliar nested key would be conformant under the old wording's narrowest reading, and would fail against every CID carrying an extension.

### Added — `power.excursion`, an optional declared power excursion profile

Adopted from proposal `2026-11-power-excursion`. **Additive and backward compatible in both directions.** A controller that does not implement the field ignores it under the nesting rule above and budgets as it does today; an OAC that does not declare it is budgeted against the Base Specification ceiling, which is today's behavior.

- **Section 7.3 is amended.** `"power"` now has two members: the mandatory `"primary"` and the optional `"excursion"`. The division is stated as sustained versus transient, and the absence of `"excursion"` is given its meaning explicitly — an OAC that omits it has not claimed it makes no excursions, it has declined to characterize them.

- **New Section 7.3.2 defines the field.** A bare array of 2 to 8 `{ interval_us, ratio_max }` entries in strictly ascending interval order. The shape is a bare array rather than an object because the quantity being declared is one curve, and an enclosing object would exist to hold a single key.

- **`ratio_max` is normalized to `opl_max_w` and to nothing else.** Two consequences are stated in the specification because neither is what a reader expects: the profile does not rescale at OPL-EFF, so a lower sustained level does not buy a larger absolute excursion; and the profile applies only at OPL-MAX and OPL-EFF, with an effective ratio of 1 at OPL-RED, OPL-EMG, and OPL-SET. An excursion allowance at a level entered specifically to relieve a platform constraint would defeat the level. No `reference_level` field and no absolute peak wattage field are defined — both would be derivable from `opl_max_w`, and a derivable field is a field that can disagree with its source.

- **Table 7.3.2-2 recommends a canonical interval grid** of 10, 100, 1,000, 10,000, 100,000, and 1,000,000 microseconds, so that profiles from different vendors compare without interpolation. The ceilings tabulated beside it are the Base Specification Section 10.1.4 envelope rounded *down* to two decimal places — `4 − 0.2171 × ln(1000)` is 2.5003, not 2.5000 — and the specification directs validators to evaluate the envelope rather than consult the table, because a conformant declaration may sit in the gap. The envelope is stated piecewise, which Table 29 of the Base Specification makes explicit and which the logarithmic form alone does not: it is 3 for T ≤ 100 µs and 1 for T ≥ 1,000,000 µs, and the logarithm applies strictly between them. A validator that extrapolates the logarithm to 10 µs admits a ratio of 3.50 against a true ceiling of 3.

- **Interpolation is nearest-shorter-interval, not linear.** For an undeclared interval T the controller uses the `ratio_max` of the nearest declared interval shorter than T; below the shortest declared point it uses the Section 10.1.4 envelope; above the longest it uses the longest point's ratio. The rule rounds toward the larger ratio in every direction, which is the conservative direction for a power budget. Linear interpolation would hand the controller a smaller number than the OAC actually guaranteed, about a gap the OAC guaranteed nothing across.

- **Section 9.3 gains check 12 and new Table 9.3-1**, carrying six checks: ascending intervals, `ratio_max` within the Section 10.1.4 envelope, monotonically non-increasing ratios, `ratio_max` ≥ 1.0, 2-to-8 entry count, and the implied peak current. The envelope check is the one that makes the field enforceable rather than advisory; without it a declaration constrains nothing.

- **The implied-current check is reported, not judged.** `ratio_max × opl_max_w ÷ input_voltage` is computed and logged but no threshold is applied, because the Base Specification states rated and derated *continuous* current for BK100 and BK125 and continuous current is a thermal figure. It is not comparable to a 10 microsecond transient, and no pulse rating exists to compare against. The question of whether the connectors carry an I²t limit or a current-versus-duration curve is open with the connector and mechanical subgroup; if one arrives, this check can be promoted from informational to normative without any change to the field.

- **Tables 10.1-1 and 10.2-1 gain conditional conformance rows.** Five OAC rows, all classified *Mandatory (if power.excursion present)* except the declaration itself, which is Optional. Five controller rows, including the obligation to budget against the Section 10.1.4 envelope when the field is absent and the prohibition on linear interpolation. The controller table also gains the nesting rule from the previous section, which had been stated in Section 7.1 without a conformance row.

- **Annex A.1 now declares an excursion profile**, and the accompanying discussion works the arithmetic through: at `opl_max_w` of 3,000 W the 2.8 ratio at 10 microseconds implies 168 A at the +50V input, against 180 A had the OAC declared nothing. The example is annotated this way because the implied current is above the BK125 derated continuous rating and a reader meeting that for the first time will reasonably suspect a validation failure. Sections 5 and 7.6 are updated in step: the overview lists excursion behavior among the declared categories, and the ordering conventions fix `primary` before `excursion` and `interval_us` before `ratio_max`.

**Not in this revision.** The proposal's companion SCD field, `ocp.excursion_ratio_max`, which would let a platform clamp a declared profile from the Assignment side, is not adopted here. The CID half stands alone: it improves the platform's budget whether or not the clamp exists.

### Changed — tooling

All three interactive tools are updated in the same pass, per this project's rule that a field is not adopted until the tooling that produces and consumes it agrees with the specification.

- **CID Editor.** A new Power Excursion card, off by default. The recommended grid of Table 7.3.2-2 loads in one click, or intervals can be entered by hand; each row displays the Section 10.1.4 ceiling beside the declared ratio, and a plot draws the declared profile against the envelope. The profile is drawn as a **step function**, because the nearest-shorter-interval rule is literally a step — a connected line would show the reader an interpolation the specification does not permit. All six checks of Table 9.3-1 run live, and the implied-current figure is emitted as an informational warning rather than an error.

- **Insertion Emulator.** A new check 5, evaluating the declared profile against the slot's transient capability. The comparison is made in **absolute watts**, not ratio against ratio: each document's ratios are normalized to its own `opl_max_w`, so comparing them directly is meaningless when the two OPL-MAX values differ. A baseboard that declares no profile is assumed to support the full Section 10.1.4 envelope, since the Base Specification requires it to tolerate any conformant OAC. A malformed OAC profile is rejected rather than budgeted against — the log states that the transient budget was not evaluated instead of reporting a PASS it did not earn. The remaining checks renumber from 5–10 to 6–11.

- **Compliance Logic diagram.** A new check 6 card, and the flow now starts from the OAC Metadata file rather than from an already-retrieved CID. Three pre-existing defects are fixed while the file was open: the verdict condition read "checks 1–11" against a 12-check diagram and now reads 1–13; the high-speed lane check compared `link_role`, which was removed from the v0.9 schema in revision 2; and the profile resolution check described a profile as a set of defaults that could be partially overridden, which Section 8.2 prohibits. The caveat note in its README, recording that the diagram had not been regenerated since the Section 8.3 to 9.3 renumbering, is retired because the diagram now has been.

- **Version strings.** Stale `0.7` and `0.8` strings surviving in the Editor's About panel and export-filename fallbacks and in the Insertion Emulator's subtitle and log banner are corrected to `0.9`. These were cosmetic — the field sets and rules were already v0.9 — but they were the kind of cosmetic error that gets quoted back as fact.

---

## [0.9] — 2026-10-09 — Workstream review revision 2

Second in-place revision of the v0.9 document, applying three decisions taken in the OCP OAC
workstream review of 2026-10-09. The version identifier is unchanged.

### Changed

- **Table 7.3.1-1 `opl_set_max_w` removed** — the configurable OPL-SET range is now bounded below by
  `opl_set_min_w` and above by `opl_max_w`. A settable level above the OAC's maximum validated
  operating point would not be a valid operating point, so a separately declared ceiling could only
  restate `opl_max_w` or contradict it. The presence of `opl_set_min_w` is now what declares OPL-SET
  support. Section 7.3.1 and the Section 10.1 compliance table were reworded accordingly.
- **Connector profile `is_conn0` replaced by `applicable_conns`** — a boolean naming one connector
  position could not express a CABLE profile at all, and it stated the answer rather than the
  question. `applicable_conns` is a non-empty array of position tokens drawn from `"CONN0"`,
  `"CONN1"` through `"CONN6"`, the all-six shorthand `"CONN1-6"`, and `"CABLE"`, each token
  appearing at most once. A profile may therefore be ratified against one specific position, against
  an arbitrary subset of CONN1 through CONN6, or against all six. CONN1 through CONN6 share a pin
  field, so naming one of them is not an electrical claim; it records where the profile was ratified
  for use, which is a property of the baseboard the profile was drawn up against rather than of the
  connector. What the array shall not do is mix geometry classes: CONN0 has nine assignable columns,
  CONN1 through CONN6 have eight, and CABLE is its own case, so an array spanning more than one of
  them would leave the assignable column count of the profile undefined and shall be treated as
  unrecognized.
- **Profile identifier grammar extended to `CABLE` and to per-position segments** — the connector
  segment of a profile identifier is now `CONN0`, one of `CONN1` through `CONN6`, `CONN`, or
  `CABLE`. Section 8.3 makes the segment derived rather than independent information: `["CONN0"]`
  yields `CONN0`; a single-token array naming one of CONN1 through CONN6 yields that position, so
  `["CONN6"]` yields `OAC-PROF-CONN6-…`; an array naming more than one of them, including by the
  `"CONN1-6"` shorthand, yields `CONN`; and `["CABLE"]` yields `CABLE`. A profile whose segment
  and `applicable_conns` value disagree shall be treated as unrecognized. Per-position segments
  fragment the namespace by design — the identifier records what the profile was ratified for, not
  every position that would accept it physically. The existing namespace is unaffected — no ratified
  identifier changes.
- **`presence_detect` object flattened to the `mpesti_capable` field** — the wrapper object held one
  field, and its optionality made the absent case ambiguous to tooling. `mpesti_capable` is now a
  direct member of the connector object, defined in Table 7.4.1-1 alongside the other top-level
  connector fields. It is **required in the CONN0 connector object and prohibited in the CONN1
  through CONN6 and CABLE connector objects**, because the M-PESTI overload is defined only for
  CONN0. A `false` value is now a positive statement that the overload is not implemented rather
  than an absence of information. Section 7.4.2 was retitled from "presence_detect Object" to
  "mpesti_capable Field" rather than deleted, so Sections 7.4.3 through 7.4.5 and every
  cross-reference to them are unchanged. Table 7.4.2-1 was removed.
- **Section 7.6 field ordering** — a sixth rule fixes the order of the top-level connector fields as
  `id`, `populated`, `impedance_ohm`, `mpesti_capable` (CONN0 only), `connector_profile`, followed by
  the signal sections in the order `high_speed_lanes`, `clocking`, `discrete_signals`.
- **Section 8.5 open case restated** — the first work-in-progress case is now expressed in terms of
  `["CONN1-6"]`. `applicable_conns` can express the resolution directly, as `["CONN0", "CONN1-6"]`,
  once the workstream settles the ninth column; the prohibition in Table 8.4-1 on mixing geometry
  classes within one array is what holds the case closed in the meantime. The case itself remains
  open.

### Revisited from the 2026-10-08 revision

- The 2026-10-08 revision recorded the collapse of `opl_set_min_w` and `opl_set_max_w` as declined.
  That decision stands for the **floor**, and for the reason recorded then: `opl_set_min_w` is what
  lets a vendor keep a platform from throttling the OAC into uselessness. Only the **ceiling** is
  removed here, and it is removed as redundant with `opl_max_w` specifically. The floor is not up
  for re-proposal.

### Associated artifacts

- **OAC SCD Specification v0.9** — `opl_set_max_w` was load-bearing in the SCD and could not be left
  behind. The Section 9 `ocp.initial_power_level_set_w` effecter `Range.max`, the Section 12 clamp,
  the Section 12 mandatory conformance row, the Section 7 placement narrative, the Section 13
  embedded CID fragment, and SCD Examples B and C now bound the effecter by `opl_max_w`.
- **`scd/tools/validate-scd.py`** — the `POWER_REGISTRY` entry for `ocp.initial_power_level_set_w`
  resolves its upper bound to `opl_max_w`.
- **Connector profiles** — all four ratified profiles and their `-minified` variants carry
  `applicable_conns` in place of `is_conn0`.
- **CID template and examples** — `opl_set_max_w` removed; `mpesti_capable` added to every CONN0
  connector object in the CID examples, the SCD examples, and both Annex A documents.
- **`OAC-CID-Editor.html`** — the `opl_set_max_w` input removed, the `is_conn0` checkbox replaced by
  an `applicable_conns` control, and `mpesti_capable` emitted as a flat field in Section 7.6 order.
  The `applicable_conns` control is a row of per-position checkboxes — CONN0, CONN1 through CONN6,
  and CABLE — that enforces the no-mixed-class rule interactively and can never be left empty.
  Selecting all six of CONN1 through CONN6 emits the `"CONN1-6"` shorthand. The selection drives the
  pin map column count and the connector segment of the suggested identifier, so a profile ratified
  against one position is offered `OAC-PROF-CONN6-…` rather than `OAC-PROF-CONN-…`. Switching away
  from CONN0 still prompts before clearing column-9 pin assignments, and declining the prompt now
  restores the previous selection rather than snapping back to CONN0. The loader still reads
  pre-revision documents: `is_conn0` and `presence_detect` are accepted on input and reported as
  superseded, so existing work is not lost.
- **`OAC-CID-Editor.html` CID-mode placement check** — now that a profile identifier can name one
  specific position, the editor verifies in CID mode that a referenced `connector_profile` is
  applied to a position its connector segment names, per the Section 8.5 rejection rule. The segment
  is derivable from the identifier alone, so no profile document is needed to make the check.

---

## [0.9] — 2026-10-08 — Workstream review revision

Revision of the published v0.9 document in response to the OAC workstream review recorded in
`OAC_WS_CID_Feedback_20261008.docx`. The version identifier is unchanged; v0.9 was edited in place.

### Added

- **Section 8, Connector Profile JSON Document Structure** — connector profiles are no longer a
  subsection of the `connectors` array. The former Sections 7.4.1.1 (mutual exclusivity), 7.4.1.2
  (profile identifiers), and 7.4.1.3 (profile file format) are now Sections 8.2, 8.3, and 8.4, joined
  by a new 8.1 General and a new 8.5 Profile Applicability to Connector Positions. Section 8 is
  written to reference Section 7 for shared field definitions and to state its differences from it
  explicitly. CID Retrieval and Validation moved from Section 8 to Section 9, and Compliance from
  Section 9 to Section 10; Annex C became Annex B.
- **Table 7.4.3-2, lanes Array Element Fields** — the lane-level fields `lane_index`, `direction`,
  `pin_positive`, and `pin_negative` are now a table of their own. Table 7.4.3-1 gains an explicit
  `lanes` row and describes the protocol group alone. The two had previously been run together into
  a single malformed table, which made it look as though lane counts and individual pin assignments
  were fields of the same object.
- **Section 9.3 validation item 11** — a connector that carries high-speed signals but declares
  neither a profile nor explicit lane definitions is incompletely defined, and the slot shall not be
  energized.
- **Normative references DSP0236, DSP0248, and DSP0249** — all three were cited normatively in the
  body without appearing in Section 2.

### Changed

- **Mechanical keying and the CID** (Sections 1 and 5) — rewritten. Keying discriminates on exactly
  one attribute, the +12 V / +50 V primary input voltage class, per Base Specification Section
  7.9.3.1. For every other class of incompatibility the CID *is* the enforcement mechanism and is
  intended to be, which is safe because the primary busbar is not energized until interoperability
  has been determined from the CID and configuration applied through the SCD. The previous claim that
  the CID "shall not be used as a substitute for hardware mechanical keying" is withdrawn.
- **Section 6.3 Fixed Length File semantics** — the CID's size is fixed for as long as a given CID is
  being served, not across firmware updates. A firmware update may replace the CID with one of a
  different size, and `FileMaximumSize` is updated accordingly. The previous "size unchanged between
  firmware updates" wording was incorrect.
- **Section 7.2.2 `platform_token`** — "closed platform" replaced throughout by "tightly coupled" and
  "validated pairings", with a new paragraph stating that a validated pairing is defined by the act
  of validation and not by who owns the two parts. Three of the six constraints — multi-vendor,
  multi-generation, and open-market use — are demoted from *shall* to advisory notes; the matched-set
  requirement, the unrecognized-token fallback, and the `iana_pen` dependency remain *shall*.
- **Section 7.4.2 `presence_detect`** — rewritten. Presence detection is neither optional nor
  negotiable; every populated connector ties Pin A1 to GND per Base Specification Section 9.4.8.2.12,
  and that is never declared in the CID. The object exists for exactly one purpose, to declare the
  M-PESTI overload on CONN0 Pin A1 permitted by Base Specification Section 9.4.8.2.12.1. Its absence
  is complete information, not missing information.
- **Section 7.4.3 `high_speed_lanes` presence** — stated as three explicit rules keyed on whether the
  connector declares a `connector_profile`, replacing "optional … if and only if". The section now
  says plainly that the field is optional only in the sense that a conformant connector object may
  omit it, never in the sense of a free choice.
- **Section 8.3 profile knowledge requirement** — a conformant upstream management controller carries
  built-in knowledge of the ratified profiles *its baseboard can support*, not of every ratified
  profile, and handles every other identifier robustly rather than treating it as a parse failure.
  The previous text required knowledge of all ratified profiles and said "baseboard management
  controllers".
- **Section 6.2** — the `-minified` suffix paragraph relocated here from the connector profile
  identifier section, generalized to cover profile files as well as the CID.
- **Section 6.2 encoding is no longer a mandate.** The relocated text had hardened into a
  requirement that production OACs publish minified JSON, with expanded format merely
  tolerated. That was never the intent. Expanded and minified are now both stated to be
  valid encodings of the CID; an upstream management controller shall accept either and
  shall not reject a CID, or treat it as malformed, over its whitespace encoding. Minified
  is **recommended** for production CID files as a size and retrieval-latency optimization,
  and the clause says so explicitly. Section 3.5 no longer restricts expanded format to
  authoring and debugging "only", Section 3.6 no longer calls minified "the normative
  encoding", and the Annex B file-size sensor reading is no longer described as the
  minified byte count. For profile files, the minified form is now the *recommended* choice
  for firmware integration rather than one that "takes precedence". Matching corrections
  were made in `README.md`, `specification/README.md`, `templates/v0.9/README.md`, and
  `examples/v0.9/README.md`, each of which had restated the mandate.
- **Section 9.1 storage and exposure** — the CID is stored in non-volatile memory on the OAC and
  *exposed* by the OAC management controller. Storage and exposure are now distinguished explicitly.
  "the OAC adapter's management controller" is gone, as is a duplicated "upstream upstream".
- **Section 9.4 retrieval timeout** — the ≥ 5 s floor is retained; the justification "to accommodate
  adapters with management controllers that perform initialization at power-on" is deleted, since
  `OAC_MC_RDY` is already asserted before retrieval begins.
- **Annex A** — replaced. Two complete, labelled, schema-valid documents: A.1 Profile-Referencing CID
  and A.2 Explicitly Defined CID, with the prose between them reworked. The previous second example
  combined `connector_profile` with an explicit `discrete_signals` override on the same connector,
  which Section 8.2 prohibits and the CID editor already rejects, and referenced a malformed profile
  identifier. The first example declared no signal definitions of any kind.
- **Terminology** — the document now says "the OAC" throughout, matching the SCD specification.
  "adapter" is reserved for the proper name *Open Adapter Card*. "Baseboard management controller"
  is gone in favour of "upstream management controller".
- **Base Specification cross-references** — Sections 9.1.1, 9.1.2, and 9.1.4 corrected to 10.1.1,
  10.1.2, and 10.1.4 against the v0.9-Final numbering.
- **Section 2** — the `OCP OAC v0.9` row cited "Version 0.8"; corrected. The MessagePack and
  RFC 1952 rows are removed, orphaned when compression was dropped at v0.9. DSP0242 is now cited
  undated, matching the SCD specification's convention.
- **Contents block** — rebuilt. It had numbered the Section 7 subsections one lower than the body and
  listed Compliance as Section 10 while the body numbered it 9.
- **Numbering gaps closed** — Section 7.4.3.2 became 7.4.3.1 (there was no 7.4.3.1), and Annex C
  became Annex B (there was no Annex B). The Section 9.2 retrieval steps ran 1–5 then 8, 9.

### Annotated as work in progress

- **Section 6.3 in its entirety** — the hard-coded `FileName`, the match-on-name-then-open-by-
  identifier discovery sequence, and the File Descriptor PDR and sensor PDR field constraints that
  follow from them. An alternative has been raised in which an OAC publishes a metadata file
  enumerating the files it exposes together with their identifiers and roles. Annex B carries a note
  scoping it to the same annotation.
- **Section 8.5** — whether an `is_conn0: false` profile may be applied to CONN0, which would leave
  CONN0's ninth assignable column undefined; and whether a CID may supplement or partially override a
  referenced profile at all. Section 8.2 forbids both today. The normative rule is unchanged: a
  profile applied to an inconsistent connector position is rejected.

### Considered and declined

Three review items were declined by the workstream and should not be re-proposed:

- Renaming OPL-EMG to drop "Operational". The Base Specification defines it as an Operational Power
  Level and the OAC is operational at it; the change would propagate back into the Base Specification.
- Collapsing `opl_set_min_w` and `opl_set_max_w` as redundant with OPL-EMG and OPL-MAX. They are
  optional, and they let a vendor enforce a configurable floor above OPL-EMG so that a platform
  cannot throttle the OAC into uselessness.
- Dropping the Section 7.6 section-order and CONN0-first ordering rules. They are retained
  deliberately, as a defense against implementations that index into the arrays positionally.

### Associated artifacts

- `profiles/README.md` — the protocol abbreviation table reference updated from Table 7.4.1.2-1 to
  Table 8.3-1. The "BMC Support Requirement" clause is retitled "Controller Support Requirement"
  and rewritten: it required built-in knowledge of *all* OCP-ratified profiles, where Section 8.3
  now requires knowledge only of those the baseboard supports, plus robust handling of an
  unrecognized reference.
- README terminology — the sweep that renamed "adapter" to "OAC" and "baseboard management
  controller" to "upstream management controller" was extended across the CID README set
  (`examples/`, `profiles/`, `templates/`, `tools/`, and the three `tools/interactive/` tool
  READMEs). Literal UI labels that the interactive HTML renders — the **Adapter CID JSON** and
  **Insert Adapter** buttons — are quoted verbatim and deliberately unchanged, because the HTML
  itself is out of scope for this revision and a README that renamed its own buttons would
  misdescribe the tool.
- `tools/interactive/oac-cid-compliance-logic/README.md` — annotated to record that the diagram
  was authored against the original Section 8.3 numbering and has not been regenerated.
- `tools/interactive/oac-cid-editor/README.md` — the minified-output description no longer directs
  implementers to compress with MessagePack or Gzip per DSP0220; compression was removed from the
  CID at v0.9.
- `specification/README.md` — section coverage map, key normative points, and open items rebuilt.
- `../scd/README.md` and `../scd/specification/OAC-SCD-Specification-v0.9.md` — DSP0257 corrected
  from Version 1.0 to Version 2.0, and the SCD README's DSP0242 row brought in line with the
  undated-reference convention the SCD specification already follows.

---

## [0.9] — 2026-10-06 — Initial publication

### Added

- **Protocol group `name` field** — Optional string field on each `high_speed_lanes` protocol group. Allows upstream management controllers, diagnostic tools, and CID authoring software to reference specific protocol groups by a stable, human-readable label (e.g. `"pcie_primary"`, `"eth_fabric"`). Convention: lowercase letters with underscores for word separation.
- **`ssc_supported` field on clocks** — Required boolean on each clock entry indicating whether the clock supports Spread Spectrum Clocking. Applies to both `INPUT` and `OUTPUT` clocks.
- **`connector_profile` mutual exclusivity enforcement** — Normative language clarified: when `connector_profile` is declared, `high_speed_lanes`, `clocking`, and `discrete_signals` shall not be present in the same connector object.
- **`minimum_lanes` field** — Optional vendor-imposed operational floor on protocol groups. The upstream management controller should block slot energization if fewer lanes than this value are electrically routed from the baseboard to the connector.
- **Clocking maximum** — A connector shall not declare more than 16 clock signals. Implementations that encounter a `clocking` array with more than 16 elements shall treat the connector as malformed.
- **`is_conn0` field on Connector Profiles** — Boolean field distinguishing CONN0 profiles (9 assignable columns) from CONN1–6 profiles (8 assignable columns).
- **Connector Profile `profile_version` field** — Semantic version of the specific profile definition, distinct from `schema_version`.
- **Profile naming convention** — OCP-ratified profiles use the pattern `OAC-PROF-<CONN0|CONN>-<proto>-x<lanes>-<dir>-v<n>[-minified]`.
- **`-minified` file suffix** — Minified JSON profile variants (functionally equivalent to expanded form, whitespace removed for firmware storage).
- **Protocol group numbering** — Protocol groups are now numbered starting at index 0 throughout all tooling and documentation.

### Changed

- **`link_subdivision` removed from CID** — Lane bifurcation mode selection has been moved to the Slot Configuration Data (SCD) mechanism. The `link_subdivision` field is no longer part of the CID schema. Adapters that previously declared `link_subdivision` shall omit it; the upstream management controller shall use SCD to communicate the selected bifurcation mode to the adapter.
- **`ssc_capable` and `ssc_default` removed** — Replaced by the simpler `ssc_supported` boolean. SSC capability and default state are no longer part of the clock schema; `ssc_supported` indicates only whether SSC is supported on the clock.
- **`link_role` removed** — The `link_role` field (ENDPOINT/ROOT/SWITCH) has been removed from the protocol group schema. Link role is an architectural property of the system topology and is not required for BMC compliance evaluation.
- **`minimum_lanes` is Optional** (was Required) — Vendors should declare `minimum_lanes` only when a specific minimum bandwidth is required for correct adapter operation. When absent, the adapter accepts any lane count the host negotiates.
- **`sris_capable` removed** — SRIS (Separate Reference Clock with Independent Spread Spectrum) is a PCIe link-training concern handled autonomously by the PCIe hardware and is not required in the CID.
- **Protocol group `link_direction`** — Restored as a direct field on the protocol group (previously considered under `link_role`). Values: `"INBOUND"` or `"OUTBOUND"`.

### Tooling (CID Editor)

- Added Connector Profile authoring mode
- Added Visual Pin Map with per-pin assignment picker
- Added real-time validation with error/warning panel
- Added syntax-highlighted Manual JSON editing mode
- Added live two-way sync between Guided and Manual modes
- Added Export JSON dropdown (Formatted / Minified)
- Added Import JSON with auto-detection of CID vs. Connector Profile
- Added `✦ Suggest ID` button for Connector Profile identifiers
- Added help modal with Getting Started, Field Reference, Keyboard Shortcuts, and About tabs
- Added `?` hover tooltip icons on key fields
- Added keyboard shortcuts (Alt+G, Alt+M, Alt+I, Alt+E, ?, Esc)
- Pin A1 blocked in Visual Pin Map (reserved for OAC_PRSNT#/M-PESTI)
- Protocol group numbering changed to 0-based

---

## [0.7] — Previous

Initial DMTF-style specification. JSON encoding replacing YAML. FRU File alignment per DSP0220. Operational Power Levels (OPL-MAX, OPL-EFF, OPL-RED, OPL-EMG, OPL-SET). Connector naming updated to CONN0–CONN6. `connector_profile` field for standard pinout references. Updated power connector types (100A/125A). Discrete signals updated with `driver_type`, `default_state`, `pulldown` fields.

---

## [0.3-draft]

Initial draft. YAML encoding. Basic power, connector, and lane schema.
