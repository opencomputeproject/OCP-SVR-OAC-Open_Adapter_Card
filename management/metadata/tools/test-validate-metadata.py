#!/usr/bin/env python3
"""
Self-test for validate-metadata.py.

Two halves, on the model of the SCD's test-validate-scd.py. The positive half
asserts every published example in examples/ is accepted; a validator that
rejects the reference material is wrong about the specification, not about the
material. The negative half mutates those examples in memory, one defect at a
time, and asserts a rejection comes back. The negative half is the load-bearing
one, because a validator that accepts everything is worth nothing.

Two cases deserve naming.

DUPLICATE_IDENTIFIER is the defect this artifact exists to prevent. The whole
point of the metadata file is that a controller opens a file by the identifier
the metadata handed it. Two roles sharing one identifier sends the controller
to the wrong file with no error anywhere in the transport, and JSON Schema
cannot express the constraint.

MULTI_DIGIT_VERSION_OK is here because the source package shipped an example
with schema_version "11.31" purely to exercise the multi-digit pattern. That
belongs in a test, not in reference material a vendor might copy, so the
pattern is exercised here and the published examples all read 0.9.

Usage:
    python3 tools/test-validate-metadata.py
Exit status is 0 when every case behaves as expected, 1 otherwise.
"""

import copy
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EX = os.path.join(ROOT, "examples")
SCHEMA = os.path.join(ROOT, "OAC-Metadata-v0.9.schema.json")
TEMPLATE = os.path.join(ROOT, "templates", "OAC-METADATA-TEMPLATE.json")

_spec = importlib.util.spec_from_file_location(
    "validate_metadata", os.path.join(HERE, "validate-metadata.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: Missing dependency 'jsonschema'. "
          "Install it with: python -m pip install jsonschema", file=sys.stderr)
    sys.exit(3)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


SCHEMA_DOC = load(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA_DOC)


def findings(instance):
    """Every complaint the tool would make, schema and semantic together."""
    out = [(V.format_json_path(list(e.absolute_path)), e.message)
           for e in VALIDATOR.iter_errors(instance)]
    out.extend(V.semantic_errors(instance))
    return out


class Report:
    def __init__(self):
        self.total = 0
        self.failures = 0

    def expect_valid(self, label, instance):
        self.total += 1
        found = findings(instance)
        if found:
            self.failures += 1
            print("FAIL  %s" % label)
            for path, message in found:
                print("        %s: %s" % (path, message))
        else:
            print("ok    %s" % label)

    def expect_invalid(self, label, instance):
        self.total += 1
        found = findings(instance)
        if not found:
            self.failures += 1
            print("FAIL  %s -- accepted, should have been rejected" % label)
        else:
            print("ok    %s  (%d finding%s)"
                  % (label, len(found), "" if len(found) == 1 else "s"))


def examples():
    return sorted(fn for fn in os.listdir(EX) if fn.endswith(".json"))


def run_positive(rep):
    print("\n-- positive: published material is accepted --")
    rep.expect_valid("schema is itself valid Draft 2020-12",
                     {"oac_metadata": {"schema_version": "0.9",
                                       "files": {"cid": {"file_identifier": 1,
                                                         "file_name": "OAC_CID.json"}}}})
    for name in examples():
        rep.expect_valid("example %s" % name, load(os.path.join(EX, name)))
    rep.expect_valid("template OAC-METADATA-TEMPLATE.json", load(TEMPLATE))

    doc = load(os.path.join(EX, "OAC-METADATA-0.9-ExampleA-Minimal.json"))
    doc["oac_metadata"]["schema_version"] = "0.31"
    rep.expect_valid("MULTI_DIGIT_VERSION_OK -- 0.31 matches the pattern and major 0", doc)

    doc = load(os.path.join(EX, "OAC-METADATA-0.9-ExampleA-Minimal.json"))
    doc["$comment"] = "root"
    doc["oac_metadata"]["$comment"] = "body"
    doc["oac_metadata"]["files"]["$comment"] = "file set"
    doc["oac_metadata"]["files"]["cid"]["$comment"] = "descriptor"
    rep.expect_valid("$comment permitted at every level", doc)

    doc = load(os.path.join(EX, "OAC-METADATA-0.9-ExampleB-VendorFile.json"))
    doc["oac_metadata"]["files"]["pen.32473.second_file"] = {
        "file_identifier": 1713, "file_name": "VENDOR_SECOND.json"}
    rep.expect_valid("two vendor roles under one PEN", doc)


def run_negative(rep):
    print("\n-- negative: each defect is caught --")
    base = load(os.path.join(EX, "OAC-METADATA-0.9-ExampleA-Minimal.json"))

    doc = copy.deepcopy(base)
    del doc["oac_metadata"]["files"]["cid"]
    rep.expect_invalid("metadata omitting the cid role", doc)

    doc = copy.deepcopy(base)
    del doc["oac_metadata"]["files"]["scda"]
    rep.expect_invalid("scdd declared without its scda", doc)

    doc = copy.deepcopy(base)
    del doc["oac_metadata"]["files"]["scdd"]
    rep.expect_invalid("scda declared without its scdd", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["scdd"]["file_identifier"] = \
        doc["oac_metadata"]["files"]["cid"]["file_identifier"]
    rep.expect_invalid("DUPLICATE_IDENTIFIER -- two roles sharing one file_identifier", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["scdd"]["file_name"] = "OAC_CID.json"
    rep.expect_invalid("two roles sharing one file_name", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["cid"]["file_name"] = "CID.json"
    rep.expect_invalid("cid role naming CID.json rather than OAC_CID.json", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["cid"]["file_identifier"] = 65536
    rep.expect_invalid("file_identifier above the uint16 ceiling", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["cid"]["file_identifier"] = -1
    rep.expect_invalid("negative file_identifier", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["cid"]["file_name"] = ""
    rep.expect_invalid("empty file_name", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["pen.32473.extra"] = {
        "file_identifier": 1900, "file_name": "OAC_METADATA.json"}
    rep.expect_invalid("an entry claiming the reserved OAC_METADATA.json name", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["TelemetryMap"] = {
        "file_identifier": 1900, "file_name": "VENDOR.json"}
    rep.expect_invalid("vendor role outside the pen.<PEN>.<name> namespace", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["pen.32473.bad name"] = {
        "file_identifier": 1900, "file_name": "VENDOR.json"}
    rep.expect_invalid("vendor role with a space in the name segment", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["schema_version"] = "1.0"
    rep.expect_invalid("major version this tool does not implement", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["schema_version"] = "0.9.1"
    rep.expect_invalid("three-component schema_version", doc)

    doc = copy.deepcopy(base)
    del doc["oac_metadata"]["schema_version"]
    rep.expect_invalid("metadata with no schema_version", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"]["cid"]["role"] = "primary"
    rep.expect_invalid("unrecognized key inside a file descriptor", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["file_type"] = "OAC Metadata"
    rep.expect_invalid("redundant file_type key -- the root key already identifies the document", doc)

    doc = copy.deepcopy(base)
    doc["oac_cid"] = doc.pop("oac_metadata")
    rep.expect_invalid("document under the wrong root key", doc)

    doc = copy.deepcopy(base)
    doc["oac_metadata"]["files"] = {}
    rep.expect_invalid("empty files object", doc)

    doc = copy.deepcopy(base)
    del doc["oac_metadata"]["files"]["cid"]["file_identifier"]
    rep.expect_invalid("file descriptor missing its file_identifier", doc)


def main():
    rep = Report()
    run_positive(rep)
    run_negative(rep)
    print("\n%d/%d cases behaved as expected"
          % (rep.total - rep.failures, rep.total))
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main())
