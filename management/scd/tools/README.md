# tools

Tooling for validating OAC Slot Configuration Data documents against the CID and against the SCD Definition they were composed from.

## Contents

| File | Description |
|------|-------------|
| [validate-scd.py](validate-scd.py) | Validator implementing Specification Sections 7, 9, 11, and 13, reporting the Table 11.5-1 rejection codes |
| [test-validate-scd.py](test-validate-scd.py) | Self-test. Asserts every shipped example is accepted, then mutates them one defect at a time and asserts the expected rejection code comes back |

## Requirements

Python 3.8 or later. No third-party dependencies.

## Usage

```
python3 validate-scd.py --scdd <scdd.json> [--scda <scda.json>]
                        [--cid <cid.json>] [--profiles <dir>]
```

| Argument | Description |
|----------|-------------|
| `--scdd` | Path to the SCD Definition. Required |
| `--scda` | Path to an SCD Assignment to check against that Definition. Optional |
| `--cid` | Path to the OAC's CID. Optional, and needed to resolve `cid_binding` entries |
| `--profiles` | Directory containing OCP-ratified connector profiles (`OAC-PROF-*.json`) |

A Definition can be checked on its own, which is what an OAC vendor wants during authoring:

```
python3 validate-scd.py \
    --scdd ../examples/OAC-SCDD-0.9-ExampleB-Bifurcatable-VendorField.json
```

A full triple resolves every binding as well:

```
python3 validate-scd.py \
    --cid  ../examples/OAC-CID-0.9-ExampleC-MultiConnector-NameReuse.json \
    --scdd ../examples/OAC-SCDD-0.9-ExampleC-MultiConnector-NameReuse.json \
    --scda ../examples/OAC-SCDA-0.9-ExampleC-Slot1-PartialSubdivision.json
```

An unresolvable `connector_profile` reference is reported only when some field actually binds into that connector. A CID may legitimately reference profiles this invocation was not given, and complaining about one nothing depends on is noise. When a binding does reach into a profile-declared connector, supply `--profiles`; a profile can be the sole source of a connector's protocol groups and therefore of the names those bindings resolve against.

Exit status: `0` accepted, `1` rejected, `2` tool or input error.

One caveat on the codes. Table 11.5-1 enumerates what an *OAC* reports when rejecting an *Assignment*. This tool also checks the Definition, which no OAC ever rejects, and it reuses the nearest Table 11.5-1 code for those defects — `0x03 MISSING_SECTION` for a descriptor with no `default`, for instance. The code and name always pair as the table defines them, but a Definition-side finding is an authoring diagnostic rather than a wire-reportable rejection.

## What It Checks

| Area | Checks |
|------|--------|
| Definition document | Well-formed JSON, `oac_scdd` root key, recognized `schema_version`, a closed `metadata` key set per Table 7.2-1, `definition_revision` an integer ≥ 1 *where declared*, non-empty `fields`, no `null` values |
| Field descriptors | Identifier namespace (`ocp.` or `pen.<PEN>.`), membership of the Section 10 registry for anything `ocp.` prefixed, character set, 128-character limit, uniqueness, `display_name` and `description`, type — the retired `string` type and its `max_length` key are both reported — response class, **mandatory default**, min/max declared as a pair and only on integers, enumeration values and value uniqueness, default membership in the enumeration |
| Sentinel semantics | A `sentinel_default` must be an integer field with min/max and a default **outside** the range; an out-of-range default **not** flagged is reported, which is what distinguishes a deliberate sentinel from a typo |
| CID bindings | `protocol_group` bindings carry both `cid_connector` and `cid_group_name` and no `constraint`; `power.primary` bindings carry `constraint: "opl_range"` and neither connector field |
| Subdivision identifiers | The identifier's connector and group segments must agree with its binding, and every declared mode must be a well-formed `x`-notation string |
| Against the CID | Every binding resolves to a real `(connector, group name)` pair; subdivision mode lane counts sum to the group's `total_lanes`; registry power fields' `min`/`max`/`default` match the CID's OPL fields; no residual `link_subdivision` left in the CID |
| Group names | Duplicate names **within** a connector are rejected. Names reused **across** connectors are accepted — see below |
| Assignment document | `oac_scda` root key, recognized `schema_version`, a closed `metadata` key set per Table 9.2-1, duplicate JSON keys, `null` values. The `definition_revision` echo is deliberately **not** compared against the Definition |
| Assignment values | Every key declared in the Definition, type conformance with no coercion, integer range, enumeration membership by value, and refusal of the sentinel value |
| Cross-field power | `ocp.initial_power_max_w` does not exceed `ocp.max_power_w`, and `ocp.initial_power_min_w` does not exceed `ocp.initial_power_max_w`. A field omitted from the Assignment is compared at the default it falls back to |
| Transferred size | Both documents are re-serialized minified and measured against the 64 KB limit of Section 13 |

## The Case Worth Calling Out

Protocol group names are unique within a connector, not across the document. Example C declares a group named `pcie_primary` on both CONN0 and CONN2, which is conformant. Under per-connector scoping the expected implementation error is **over**-enforcement, so the self-test carries an explicit case asserting that cross-connector reuse is *not* flagged — it exists to fail loudly if anyone reintroduces a document-wide uniqueness check. The matching negative case, the same name twice on one connector, must still be rejected.

## Self-Test

```
python3 test-validate-scd.py
```

Runs 42 cases: the three shipped triples, each both as a full set and as a Definition alone; 35 deliberate mutations covering assigned sentinels, out-of-range and mistyped values, undeclared identifiers and `ocp.` identifiers outside the Section 10 registry, metadata keys outside the closed sets, the retired `string` type and `max_length` key, contradictory power pairs including the case where the ceiling was defaulted rather than assigned, an oversized Definition, null and duplicate keys, unsupported schema versions, the wrong root key, missing defaults, mis-flagged sentinels, duplicated field declarations, contradictory subdivision identifiers, malformed bindings, lane counts that do not sum, and `applies_when` pointing at a field that was never declared; and the cross-connector-reuse non-regression case described above. Exit status is `0` when every case behaves as expected.

Two of those cases assert that something is **not** reported: cross-connector group name reuse, and an Assignment echoing a `definition_revision` that differs from the Definition's. Both guard against a check being reintroduced after it was deliberately removed.

The two duplicate-key cases are re-parsed through the validator's own `object_pairs_hook` rather than mutated in place. A duplicate cannot be built by editing a dictionary, and `json.load` on its own collapses duplicates silently — which is exactly the resolution Section 9.5 refuses to pick, and therefore exactly what a test that skipped this step would fail to notice.

All shipped examples validate clean.

## Limitations

The tool validates documents against each other. It does not validate a CID against the CID specification, evaluate baseboard capability — whether the *platform* can supply the selected power or accept the selected subdivision — or exercise the PLDM transport. Its Section 13 size check re-serializes each document minified and measures that, which is the right quantity but not the identical byte sequence a given OAC will transmit; treat a result near the limit as advisory. For CID authoring and platform compatibility, see the [interactive tools](../../cid/tools/interactive/) in the CID directory.
