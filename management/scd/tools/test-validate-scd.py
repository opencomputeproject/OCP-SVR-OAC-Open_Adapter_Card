#!/usr/bin/env python3
"""
Self-test for validate-scd.py.

Two halves. The positive half asserts that every published example in
examples/ is accepted -- a validator that rejects the reference material is
wrong about the specification, not about the material. The negative half
mutates those examples in memory, one defect at a time, and asserts the
expected rejection code comes back. A validator that accepts everything is
worth nothing, so the negative half is the load-bearing one.

The case that matters most is NAME_REUSE_OK. Protocol group names are unique
within a connector, not across the document, so Example C declares a group
named pcie_primary on both CONN0 and CONN2. That is conformant. Under
per-connector scoping the expected implementation error is over-enforcement,
which means this case exists to fail loudly if anyone reintroduces a
document-wide uniqueness check.

Usage:
    python3 tools/test-validate-scd.py
Exit status is 0 when every case behaves as expected, 1 otherwise.
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EX = os.path.join(ROOT, "examples")

sys.path.insert(0, HERE)
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "validate_scd", os.path.join(HERE, "validate-scd.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)


def load(path):
    with open(path) as fh:
        return json.load(fh)


def triple(letter):
    """Return the (cid, scdd, scda) documents for one example letter."""
    out = []
    for prefix in ("OAC-CID-0.9-Example", "OAC-SCDD-0.9-Example", "OAC-SCDA-0.9-Example"):
        matches = [fn for fn in sorted(os.listdir(EX))
                   if fn.startswith(prefix + letter)]
        if len(matches) != 1:
            raise SystemExit("expected exactly one %s%s* file, found %s"
                             % (prefix, letter, matches))
        out.append(load(os.path.join(EX, matches[0])))
    return out


def codes(findings):
    return sorted({c for c, _, _ in findings.items})


class Report:
    def __init__(self):
        self.failures = 0
        self.total = 0

    def check(self, name, ok, detail=""):
        self.total += 1
        if ok:
            print("  pass  %s" % name)
        else:
            self.failures += 1
            print("  FAIL  %s%s" % (name, ("  -- " + detail) if detail else ""))

    def expect_accept(self, name, findings):
        self.check(name, not findings,
                   "expected acceptance, got %s"
                   % ["0x%02X %s" % (c, n) for c, n, _ in findings.items])

    def expect_code(self, name, findings, code):
        got = codes(findings)
        self.check(name, code in got,
                   "expected 0x%02X, got %s" % (code, ["0x%02X" % c for c in got]))

    def expect_not_code(self, name, findings, code):
        got = codes(findings)
        self.check(name, code not in got,
                   "0x%02X was reported and should not have been: %s"
                   % (code, [d for c, _, d in findings.items if c == code]))


def run_positive(rep):
    print("published examples")
    for letter in "ABC":
        cid, scdd, scda = triple(letter)
        rep.expect_accept("Triple %s, full" % letter,
                          V.validate(scdd, scda, cid, {}))
        rep.expect_accept("Triple %s, Definition alone" % letter,
                          V.validate(scdd, None, None, {}))


def field(scdd, fid):
    for d in scdd["oac_scdd"]["fields"]:
        if d["id"] == fid:
            return d
    raise KeyError(fid)


def dup_key(doc, opener, key):
    """Return doc re-parsed with key appearing twice in the object that opener
    introduces. A duplicate cannot be built by mutating a dict, so the document
    is serialized, the key injected textually, and the result parsed back
    through the validator's own object_pairs_hook -- the same path the CLI
    takes. The injected copy comes first, so the original value is the one that
    survives and DUPLICATE_KEY is the only defect present."""
    text = json.dumps(doc)
    if opener not in text:
        raise SystemExit("dup_key: %r not found in the serialized document" % opener)
    text = text.replace(opener, opener + json.dumps(key) + ": 0, ", 1)
    return json.loads(text, object_pairs_hook=V._dup_key_hook)


def run_negative(rep):
    print("negative cases")
    cidA, scddA, scdaA = triple("A")
    cidB, scddB, scdaB = triple("B")
    cidC, scddC, scdaC = triple("C")

    SUB0 = "ocp.link_subdivision.conn0.pcie_primary"

    # The case this suite exists for.
    rep.expect_not_code("NAME_REUSE_OK: cross-connector pcie_primary accepted",
                        V.validate(scddC, scdaC, cidC, {}), 0x10)

    # ... and the case it must still catch: the same name twice on one connector.
    cid = copy.deepcopy(cidC)
    for conn in cid["oac_cid"]["connectors"]:
        if conn.get("id") == "CONN0":
            groups = conn["high_speed_lanes"]
            groups = groups if isinstance(groups, list) else [groups]
            groups[1]["name"] = groups[0]["name"]
            conn["high_speed_lanes"] = groups
    rep.expect_code("within-connector duplicate group name",
                    V.validate(scddC, scdaC, cid, {}), 0x10)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["assignments"]["ocp.slot_id"] = 255
    rep.expect_code("assigning the sentinel",
                    V.validate(scddB, scda, cidB, {}), 0x0A)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["assignments"]["ocp.max_power_w"] = 9000
    rep.expect_code("assignment above declared max",
                    V.validate(scddB, scda, cidB, {}), 0x07)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["assignments"]["ocp.nonexistent_field"] = 1
    rep.expect_code("assignment to an undeclared field",
                    V.validate(scddB, scda, cidB, {}), 0x04)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["assignments"]["ocp.max_power_w"] = None
    rep.expect_code("null assignment",
                    V.validate(scddB, scda, cidB, {}), 0x0B)

    # Duplicate JSON keys, both documents. These two cases are re-parsed through
    # the validator's own object_pairs_hook rather than mutated in place, because
    # that is the only way to have a duplicate at all: json.load collapses them
    # silently, which is precisely the resolution Section 9.5 refuses to pick.
    rep.expect_code("duplicate key in the Assignment",
                    V.validate(scddB, dup_key(scdaB, '"assignments": {',
                                              next(iter(scdaB["oac_scda"]["assignments"]))),
                               cidB, {}), 0x05)

    rep.expect_code("duplicate key in the Definition metadata",
                    V.validate(dup_key(scddB, '"metadata": {', "schema_version"),
                               None, None, {}), 0x05)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["assignments"]["ocp.max_power_w"] = "2000"
    rep.expect_code("string where an integer is declared",
                    V.validate(scddB, scda, cidB, {}), 0x06)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["assignments"][SUB0] = "x4x4x4x4x4"
    rep.expect_code("subdivision mode not in the enumeration",
                    V.validate(scddB, scda, cidB, {}), 0x09)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["metadata"]["definition_revision"] = 99
    rep.expect_code("Assignment echoes a stale definition_revision",
                    V.validate(scddB, scda, cidB, {}), 0x0D)

    scda = copy.deepcopy(scdaB)
    scda["oac_scda"]["metadata"]["schema_version"] = "0.7"
    rep.expect_code("Assignment declares an unsupported schema_version",
                    V.validate(scddB, scda, cidB, {}), 0x0C)

    scda = copy.deepcopy(scdaB)
    scda["oac_scd"] = scda.pop("oac_scda")
    rep.expect_code("Assignment with the wrong root key",
                    V.validate(scddB, scda, cidB, {}), 0x02)

    # Definition-side defects.
    scdd = copy.deepcopy(scddB)
    del field(scdd, "ocp.max_power_w")["default"]
    rep.expect_code("field descriptor with no default",
                    V.validate(scdd, None, None, {}), 0x03)

    scdd = copy.deepcopy(scddB)
    field(scdd, "ocp.slot_id")["sentinel_default"] = False
    rep.expect_code("out-of-range default not flagged as a sentinel",
                    V.validate(scdd, None, None, {}), 0x07)

    scdd = copy.deepcopy(scddB)
    field(scdd, "ocp.slot_id")["default"] = 7
    rep.expect_code("sentinel_default with an in-range default",
                    V.validate(scdd, None, None, {}), 0x07)

    scdd = copy.deepcopy(scddB)
    scdd["oac_scdd"]["fields"].append(copy.deepcopy(field(scdd, "ocp.slot_id")))
    rep.expect_code("the same field id declared twice",
                    V.validate(scdd, None, None, {}), 0x05)

    scdd = copy.deepcopy(scddB)
    field(scdd, SUB0)["id"] = "ocp.link_subdivision.conn3.pcie_primary"
    rep.expect_code("subdivision id whose connector segment contradicts its binding",
                    V.validate(scdd, None, None, {}), 0x04)

    scdd = copy.deepcopy(scddB)
    del field(scdd, SUB0)["cid_binding"]["cid_group_name"]
    rep.expect_code("protocol_group binding missing cid_group_name",
                    V.validate(scdd, None, None, {}), 0x03)

    scdd = copy.deepcopy(scddB)
    field(scdd, "ocp.max_power_w")["cid_binding"]["cid_connector"] = "CONN0"
    rep.expect_code("power.primary binding carrying a connector",
                    V.validate(scdd, None, None, {}), 0x10)

    scdd = copy.deepcopy(scddB)
    field(scdd, "pen.32473.boot_source")["id"] = "acme.boot_source"
    rep.expect_code("field id outside the ocp. and pen. namespaces",
                    V.validate(scdd, None, None, {}), 0x04)

    scdd = copy.deepcopy(scddB)
    field(scdd, "ocp.slot_id")["id"] = "ocp.slot_label"
    rep.expect_code("a retired identifier reused",
                    V.validate(scdd, None, None, {}), 0x10)

    scdd = copy.deepcopy(scddB)
    field(scdd, "ocp.max_power_w")["min"] = 1
    rep.expect_code("declared min contradicting CID opl_emg_w",
                    V.validate(scdd, None, cidB, {}), 0x07)

    scdd = copy.deepcopy(scddB)
    field(scdd, SUB0)["values"].append(
        {"value": "x4x4x4", "description": "twelve lanes into a sixteen lane group"})
    rep.expect_code("subdivision mode whose lanes do not sum to total_lanes",
                    V.validate(scdd, None, cidB, {}), 0x10)

    scdd = copy.deepcopy(scddB)
    field(scdd, SUB0)["cid_binding"]["cid_group_name"] = "no_such_group"
    rep.expect_code("binding to a group the CID does not declare",
                    V.validate(scdd, None, cidB, {}), 0x04)

    scdd = copy.deepcopy(scddC)
    field(scdd, "pen.32473.stream_image_slot")["applies_when"]["field"] = "ocp.ghost"
    rep.expect_code("applies_when referencing an undeclared field",
                    V.validate(scdd, None, None, {}), 0x04)

    scdd = copy.deepcopy(scddA)
    scdd["oac_scdd"]["metadata"]["schema_version"] = "0.7"
    rep.expect_code("Definition declaring an unsupported schema_version",
                    V.validate(scdd, None, None, {}), 0x0C)


def main():
    rep = Report()
    run_positive(rep)
    run_negative(rep)
    print("\n%d/%d cases behaved as expected" % (rep.total - rep.failures, rep.total))
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main())
