#!/usr/bin/env python3
"""
OAC SCD validator.

Validates an SCD Definition and, optionally, an SCD Assignment composed
against it, applying the checks of OAC-SCD-Specification-v0.9 Sections 7, 9
and 11 and reporting the rejection codes of Table 11.4-1.

A Definition may be checked on its own. Supplying --cid additionally resolves
every cid_binding against the OAC's Connector Interface Definition, and
--profiles supplies the directory of ratified connector profiles needed to
resolve a CID connector declared by connector_profile reference.

Usage:
    validate-scd.py --scdd <scdd.json> [--scda <scda.json>]
                    [--cid <cid.json>] [--profiles <dir>]

Exit status is 0 when the documents would be accepted, 1 when they would be
rejected, and 2 on a usage or I/O error.
"""

import argparse
import json
import os
import re
import sys

SCHEMA_VERSIONS = {"0.9"}
VALID_CONNECTOR_IDS = {"CONN0", "CONN1", "CONN2", "CONN3",
                       "CONN4", "CONN5", "CONN6", "CABLE"}


class Findings:
    def __init__(self):
        self.items = []

    def add(self, code, name, detail):
        self.items.append((code, name, detail))

    def __bool__(self):
        return bool(self.items)


def load_profiles(directory):
    """Map profile_id -> profile object, for resolving connector_profile refs."""
    profiles = {}
    if not directory or not os.path.isdir(directory):
        return profiles
    for fn in os.listdir(directory):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(directory, fn)) as fh:
                obj = json.load(fh)
        except (OSError, ValueError):
            continue
        prof = obj.get("oac_connector_profile")
        if isinstance(prof, dict) and "profile_id" in prof:
            profiles[prof["profile_id"]] = prof
    return profiles


def protocol_groups(cid_connector, profiles, f, code=0x10,
                    name="CONSTRAINT_CONFLICT"):
    """
    Resolve a CID connector to its ordered list of protocol groups, following a
    connector_profile reference when present.
    Returns None when the structure cannot be resolved.
    """
    profile_id = cid_connector.get("connector_profile")
    source = cid_connector
    if profile_id is not None:
        if profile_id not in profiles:
            f.add(code, name,
                  "connector %s references profile %r which could not be resolved; "
                  "protocol group structure is indeterminate"
                  % (cid_connector.get("id"), profile_id))
            return None
        source = profiles[profile_id]

    hsl = source.get("high_speed_lanes")
    if hsl is None:
        return []
    return hsl if isinstance(hsl, list) else [hsl]


def find_nulls(node, f, path="oac_scdd", code=0x0B, name="NULL_VALUE"):
    """Walk a document reporting every null. Absence and null are not the same
    thing: absence selects a declared default, null selects nothing."""
    if isinstance(node, dict):
        for k, v in node.items():
            if v is None:
                f.add(code, name,
                      "%s.%s is null; absence and null are not equivalent" % (path, k))
            else:
                find_nulls(v, f, "%s.%s" % (path, k), code, name)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            find_nulls(v, f, "%s[%d]" % (path, i), code, name)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

VALID_TYPES = {"integer", "string", "boolean", "enumeration"}
VALID_RESPONSE = {"required", "optional"}
VALID_CID_OBJECTS = {"protocol_group", "power.primary"}

ID_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")
PEN_RE = re.compile(r"^pen\.[1-9][0-9]*\.")
MODE_RE = re.compile(r"^(x[0-9]+)+$")
SUBDIV_PREFIX = "ocp.link_subdivision."

# Specification Section 10.5 -- identifiers that were defined in earlier drafts
# and must not be used.
RETIRED_IDS = {
    "ocp.config_apply_timeout_ms",
    "ocp.power_level_set_granularity_w",
    "ocp.slot_label",
    "ocp.initial_power_level",
    "ocp.secure_boot_enforce",
}

# Specification Section 10 -- registry fields whose bounds derive from the CID.
# field id -> (min source, max source, default source or None)
POWER_REGISTRY = {
    "ocp.max_power_w": ("opl_emg_w", "opl_max_w", "opl_emg_w"),
    "ocp.initial_power_level_set_w": ("opl_set_min_w", "opl_set_max_w", None),
}


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _dup_key_hook(pairs):
    """object_pairs_hook that records duplicate keys instead of silently
    dropping them -- ECMA-404 leaves duplicate resolution undefined, so the
    specification requires rejection rather than first-wins or last-wins."""
    seen = {}
    dups = []
    for k, v in pairs:
        if k in seen:
            dups.append(k)
        seen[k] = v
    if dups:
        seen.setdefault("__duplicate_keys__", []).extend(dups)
    return seen


def mode_segments(mode):
    """Return the list of lane-segment widths in a subdivision mode string,
    or None if the string is not a well-formed mode."""
    if not isinstance(mode, str) or not MODE_RE.match(mode):
        return None
    return [int(n) for n in re.findall(r"x([0-9]+)", mode)]


def cid_group_index(cid, profiles, f):
    """Build {(connector_id, group_name): group} from a v0.9 CID, enforcing
    per-connector name uniqueness. Names reused across different connectors are
    conformant and must not be reported.

    Returns (index, unresolved), where unresolved maps a connector identifier to
    the profile reference that could not be read. An unresolved profile is not
    itself a finding: a CID may legitimately reference profiles this invocation
    was not given, and it only matters if some field actually binds into that
    connector. check_bindings reports it there, where it is actionable."""
    index = {}
    unresolved = {}
    for conn in cid.get("connectors", []):
        cid_id = conn.get("id")
        if not conn.get("populated", True):
            continue
        probe = Findings()
        groups = protocol_groups(conn, profiles, probe)
        if groups is None:
            unresolved[cid_id] = conn.get("connector_profile")
            continue
        local = set()
        for grp in groups:
            name = grp.get("name")
            if name is None:
                # A CID predating the group-name requirement, or a profile not
                # yet republished with names. Unnameable groups are simply not
                # bindable; a field that targets one is reported by
                # check_bindings as an unresolved key.
                continue
            if name in local:
                f.add(0x10, "CONSTRAINT_CONFLICT",
                      "connector %s declares two protocol groups named %r; names must "
                      "be unique within a connector, which makes the "
                      "(cid_connector, cid_group_name) pair ambiguous here"
                      % (cid_id, name))
                continue
            local.add(name)
            index[(cid_id, name)] = grp
    return index, unresolved


def check_descriptor(d, i, f, declared_ids):
    """Structural checks on a single field descriptor. Returns the id, or None."""
    where = "fields[%d]" % i
    fid = d.get("id")

    if not isinstance(fid, str) or not fid:
        f.add(0x01, "MALFORMED_JSON", "%s has no usable id" % where)
        return None
    where = "field %s" % fid

    if fid in declared_ids:
        f.add(0x05, "DUPLICATE_KEY",
              "%s is declared more than once; field identifiers are the "
              "Assignment's keys and must be unique" % where)
    if fid in RETIRED_IDS:
        f.add(0x10, "CONSTRAINT_CONFLICT",
              "%s is a retired identifier (Specification Section 10.5) and must "
              "not be used" % where)
    if not (fid.startswith("ocp.") or PEN_RE.match(fid)):
        f.add(0x04, "UNKNOWN_FIELD_ID",
              "%s uses an unrecognized namespace prefix; expected 'ocp.' or "
              "'pen.<IANA PEN>.'" % where)
    if not ID_RE.match(fid):
        f.add(0x04, "UNKNOWN_FIELD_ID",
              "%s contains characters outside lowercase snake_case segments" % where)
    if len(fid) > 128:
        f.add(0x08, "LENGTH_EXCEEDED",
              "%s is %d characters; the limit is 128" % (where, len(fid)))

    dn = d.get("display_name")
    if not isinstance(dn, str) or not 1 <= len(dn) <= 64:
        f.add(0x06, "TYPE_MISMATCH",
              "%s display_name must be a string of 1..64 characters" % where)
    if not isinstance(d.get("description"), str):
        f.add(0x06, "TYPE_MISMATCH", "%s description must be a string" % where)

    ftype = d.get("type")
    if ftype not in VALID_TYPES:
        f.add(0x06, "TYPE_MISMATCH",
              "%s type is %r; expected one of %s" % (where, ftype, sorted(VALID_TYPES)))
    if d.get("response") not in VALID_RESPONSE:
        f.add(0x06, "TYPE_MISMATCH",
              "%s response is %r; expected 'required' or 'optional'"
              % (where, d.get("response")))

    if "default" not in d:
        f.add(0x03, "MISSING_SECTION",
              "%s declares no default; every field descriptor must carry one, "
              "which is what makes a sparse Assignment safe" % where)

    has_min, has_max = "min" in d, "max" in d
    if has_min != has_max:
        f.add(0x07, "OUT_OF_RANGE",
              "%s declares one of min/max without the other" % where)
    if ftype != "integer" and (has_min or has_max):
        f.add(0x06, "TYPE_MISMATCH",
              "%s declares min/max but is not an integer field" % where)
    if ftype != "string" and "max_length" in d:
        f.add(0x06, "TYPE_MISMATCH",
              "%s declares max_length but is not a string field" % where)

    default = d.get("default")
    sentinel = d.get("sentinel_default", False)
    if not isinstance(sentinel, bool):
        f.add(0x06, "TYPE_MISMATCH", "%s sentinel_default must be a boolean" % where)
        sentinel = bool(sentinel)

    if ftype == "integer":
        if "default" in d and not _is_int(default):
            f.add(0x06, "TYPE_MISMATCH",
                  "%s is an integer field but its default is %r" % (where, default))
        elif has_min and has_max and _is_int(default):
            inside = d["min"] <= default <= d["max"]
            if sentinel and inside:
                f.add(0x07, "OUT_OF_RANGE",
                      "%s is flagged sentinel_default but its default %r lies inside "
                      "[%r, %r]; a sentinel must be unassignable"
                      % (where, default, d["min"], d["max"]))
            if not sentinel and not inside:
                f.add(0x07, "OUT_OF_RANGE",
                      "%s default %r lies outside [%r, %r] and is not flagged "
                      "sentinel_default; the flag exists so a deliberate "
                      "out-of-range default is distinguishable from a typo"
                      % (where, default, d["min"], d["max"]))
        elif sentinel:
            f.add(0x07, "OUT_OF_RANGE",
                  "%s is flagged sentinel_default but declares no min/max, so there "
                  "is no range for the sentinel to sit outside of" % where)
    elif sentinel:
        f.add(0x07, "OUT_OF_RANGE",
              "%s is flagged sentinel_default but is not an integer field" % where)

    if ftype == "boolean" and "default" in d and not isinstance(default, bool):
        f.add(0x06, "TYPE_MISMATCH",
              "%s is a boolean field but its default is %r" % (where, default))
    if ftype == "string" and "default" in d and not isinstance(default, str):
        f.add(0x06, "TYPE_MISMATCH",
              "%s is a string field but its default is %r" % (where, default))

    if ftype == "enumeration":
        values = d.get("values")
        if not isinstance(values, list) or not values:
            f.add(0x09, "INVALID_ENUM_VALUE",
                  "%s is an enumeration but declares no values array" % where)
        else:
            literals = []
            for v in values:
                if not isinstance(v, dict) or "value" not in v or "description" not in v:
                    f.add(0x09, "INVALID_ENUM_VALUE",
                          "%s has a values element missing value or description" % where)
                    continue
                if v["value"] in literals:
                    f.add(0x05, "DUPLICATE_KEY",
                          "%s declares the value %r more than once" % (where, v["value"]))
                literals.append(v["value"])
            if "default" in d and default not in literals:
                f.add(0x09, "INVALID_ENUM_VALUE",
                      "%s default %r is not among its declared values %s"
                      % (where, default, literals))
    elif "values" in d:
        f.add(0x06, "TYPE_MISMATCH",
              "%s declares a values array but is not an enumeration" % where)

    cb = d.get("cid_binding")
    if cb is not None:
        if not isinstance(cb, dict):
            f.add(0x06, "TYPE_MISMATCH", "%s cid_binding must be an object" % where)
        else:
            obj = cb.get("cid_object")
            if obj not in VALID_CID_OBJECTS:
                f.add(0x06, "TYPE_MISMATCH",
                      "%s cid_binding.cid_object is %r; expected one of %s"
                      % (where, obj, sorted(VALID_CID_OBJECTS)))
            elif obj == "protocol_group":
                for k in ("cid_connector", "cid_group_name"):
                    if not isinstance(cb.get(k), str):
                        f.add(0x03, "MISSING_SECTION",
                              "%s has a protocol_group binding without %s; protocol "
                              "groups live inside connectors, so the pair is the key"
                              % (where, k))
                if cb.get("cid_connector") not in VALID_CONNECTOR_IDS and \
                        isinstance(cb.get("cid_connector"), str):
                    f.add(0x04, "UNKNOWN_FIELD_ID",
                          "%s cid_binding.cid_connector is %r; expected canonical CID "
                          "casing, one of %s"
                          % (where, cb.get("cid_connector"), sorted(VALID_CONNECTOR_IDS)))
                if "constraint" in cb:
                    f.add(0x10, "CONSTRAINT_CONFLICT",
                          "%s carries constraint on a protocol_group binding" % where)
            else:
                if cb.get("constraint") != "opl_range":
                    f.add(0x03, "MISSING_SECTION",
                          "%s power.primary binding must carry constraint 'opl_range'"
                          % where)
                for k in ("cid_connector", "cid_group_name"):
                    if k in cb:
                        f.add(0x10, "CONSTRAINT_CONFLICT",
                              "%s carries %s on a power.primary binding; "
                              "power.primary is not inside a connector" % (where, k))

    aw = d.get("applies_when")
    if aw is not None:
        if not isinstance(aw, dict) or "field" not in aw or "equals" not in aw:
            f.add(0x03, "MISSING_SECTION",
                  "%s applies_when must carry both field and equals" % where)

    # Registry rules for subdivision identifiers.
    if fid.startswith(SUBDIV_PREFIX):
        if ftype != "enumeration":
            f.add(0x06, "TYPE_MISMATCH",
                  "%s is a link subdivision field but is not an enumeration" % where)
        if not isinstance(cb, dict) or cb.get("cid_object") != "protocol_group":
            f.add(0x03, "MISSING_SECTION",
                  "%s is a link subdivision field but carries no protocol_group "
                  "binding" % where)
        else:
            segs = fid[len(SUBDIV_PREFIX):].split(".")
            if len(segs) != 2:
                f.add(0x04, "UNKNOWN_FIELD_ID",
                      "%s must be ocp.link_subdivision.<connector>.<group_name>; both "
                      "segments are required, because a two-segment id collides as "
                      "soon as two connectors reuse a group name" % where)
            else:
                conn_seg, name_seg = segs
                want_conn = str(cb.get("cid_connector", "")).lower()
                if conn_seg != want_conn:
                    f.add(0x04, "UNKNOWN_FIELD_ID",
                          "%s connector segment is %r but the binding names %r; the "
                          "segment is the CID connector identifier lowercased"
                          % (where, conn_seg, cb.get("cid_connector")))
                if name_seg != cb.get("cid_group_name"):
                    f.add(0x04, "UNKNOWN_FIELD_ID",
                          "%s group segment is %r but the binding names %r"
                          % (where, name_seg, cb.get("cid_group_name")))
        for v in (d.get("values") or []):
            if isinstance(v, dict) and mode_segments(v.get("value")) is None:
                f.add(0x09, "INVALID_ENUM_VALUE",
                      "%s declares %r, which is not a well-formed subdivision mode"
                      % (where, v.get("value")))

    if fid in POWER_REGISTRY and not isinstance(cb, dict):
        f.add(0x03, "MISSING_SECTION",
              "%s is a registry power field and must carry a power.primary binding"
              % where)

    return fid


def check_scdd(scdd, f):
    """Structure-only Definition checks. Returns {id: descriptor}."""
    md = scdd.get("metadata")
    if not isinstance(md, dict):
        f.add(0x03, "MISSING_SECTION", "oac_scdd.metadata is absent")
    else:
        if md.get("schema_version") not in SCHEMA_VERSIONS:
            f.add(0x0C, "UNSUPPORTED_SCHEMA_VERSION",
                  "metadata.schema_version is %r; recognized versions are %s"
                  % (md.get("schema_version"), sorted(SCHEMA_VERSIONS)))
        if "oac_spec_revision" not in md:
            f.add(0x03, "MISSING_SECTION", "metadata.oac_spec_revision is required")
        dr = md.get("definition_revision")
        if not _is_int(dr) or dr < 1:
            f.add(0x0D, "DEFINITION_REVISION_MISMATCH",
                  "metadata.definition_revision is %r; expected an integer >= 1" % (dr,))

    fields = scdd.get("fields")
    if not isinstance(fields, list) or not fields:
        f.add(0x03, "MISSING_SECTION",
              "oac_scdd.fields must be a non-empty array")
        return {}

    declared = {}
    for i, d in enumerate(fields):
        if not isinstance(d, dict):
            f.add(0x01, "MALFORMED_JSON", "fields[%d] is not an object" % i)
            continue
        fid = check_descriptor(d, i, f, declared)
        if fid is not None and fid not in declared:
            declared[fid] = d

    for fid, d in declared.items():
        aw = d.get("applies_when")
        if isinstance(aw, dict) and aw.get("field") not in declared:
            f.add(0x04, "UNKNOWN_FIELD_ID",
                  "field %s has applies_when.field %r, which is not declared in this "
                  "Definition" % (fid, aw.get("field")))

    for key in ("__duplicate_keys__",):
        if key in scdd.get("metadata", {}) or key in scdd:
            f.add(0x05, "DUPLICATE_KEY", "the Definition contains duplicate JSON keys")
            break

    return declared


def check_bindings(declared, cid, profiles, f):
    """Resolve every cid_binding against a v0.9 CID."""
    index, unresolved = cid_group_index(cid, profiles, f)
    primary = cid.get("power", {}).get("primary", {})

    for fid, d in sorted(declared.items()):
        cb = d.get("cid_binding")
        if not isinstance(cb, dict):
            continue

        if cb.get("cid_object") == "protocol_group":
            key = (cb.get("cid_connector"), cb.get("cid_group_name"))
            grp = index.get(key)
            if grp is None and key[0] in unresolved:
                f.add(0x10, "CONSTRAINT_CONFLICT",
                      "field %s binds into connector %s, whose protocol groups come "
                      "from profile %r; supply --profiles pointing at the directory "
                      "holding it, or this binding cannot be checked"
                      % (fid, key[0], unresolved[key[0]]))
                continue
            if grp is None:
                f.add(0x04, "UNKNOWN_FIELD_ID",
                      "field %s binds to connector %r group %r, which the CID does not "
                      "declare; resolving either half alone is not sufficient"
                      % (fid, key[0], key[1]))
                continue
            total = grp.get("total_lanes")
            if _is_int(total):
                for v in (d.get("values") or []):
                    segs = mode_segments(v.get("value")) if isinstance(v, dict) else None
                    if segs is not None and sum(segs) != total:
                        f.add(0x10, "CONSTRAINT_CONFLICT",
                              "field %s declares mode %r summing to %d lanes, but CID "
                              "%s group %s declares total_lanes %d"
                              % (fid, v.get("value"), sum(segs), key[0], key[1], total))
            if "link_subdivision" in grp:
                f.add(0x10, "CONSTRAINT_CONFLICT",
                      "CID %s group %s carries link_subdivision; the mode menu "
                      "belongs in the Definition" % (key[0], key[1]))

        elif cb.get("cid_object") == "power.primary":
            spec = POWER_REGISTRY.get(fid)
            if spec is None:
                continue
            lo_key, hi_key, def_key = spec
            for key, declared_key in ((lo_key, "min"), (hi_key, "max")):
                if key not in primary:
                    f.add(0x10, "CONSTRAINT_CONFLICT",
                          "field %s requires CID power.primary.%s, which is not declared"
                          % (fid, key))
                elif d.get(declared_key) != primary[key]:
                    f.add(0x07, "OUT_OF_RANGE",
                          "field %s declares %s %r but CID power.primary.%s is %r"
                          % (fid, declared_key, d.get(declared_key), key, primary[key]))
            if def_key and def_key in primary and d.get("default") != primary[def_key]:
                f.add(0x07, "OUT_OF_RANGE",
                      "field %s declares default %r but must default to CID "
                      "power.primary.%s (%r) so that an omitted budget throttles the "
                      "OAC rather than assuming one"
                      % (fid, d.get("default"), def_key, primary[def_key]))


def check_value(fid, d, value, f):
    ftype = d.get("type")
    if ftype == "integer":
        if not _is_int(value):
            f.add(0x06, "TYPE_MISMATCH",
                  "%s is %r; the Definition declares type integer and no coercion is "
                  "permitted" % (fid, value))
            return
        if d.get("sentinel_default") and value == d.get("default"):
            f.add(0x0A, "SENTINEL_ASSIGNED",
                  "%s assigns the sentinel value %r; the sentinel is a state the "
                  "OAC may hold, not a value the upstream management controller may choose"
                  % (fid, value))
            return
        if "min" in d and "max" in d and not d["min"] <= value <= d["max"]:
            f.add(0x07, "OUT_OF_RANGE",
                  "%s is %r; the Definition declares [%r, %r]"
                  % (fid, value, d["min"], d["max"]))
    elif ftype == "boolean":
        if not isinstance(value, bool):
            f.add(0x06, "TYPE_MISMATCH",
                  "%s is %r; the Definition declares type boolean" % (fid, value))
    elif ftype == "string":
        if not isinstance(value, str):
            f.add(0x06, "TYPE_MISMATCH",
                  "%s is %r; the Definition declares type string" % (fid, value))
        elif "max_length" in d and len(value) > d["max_length"]:
            f.add(0x08, "LENGTH_EXCEEDED",
                  "%s is %d characters; the Definition declares max_length %r"
                  % (fid, len(value), d["max_length"]))
    elif ftype == "enumeration":
        literals = [v.get("value") for v in (d.get("values") or [])
                    if isinstance(v, dict)]
        if value not in literals:
            f.add(0x09, "INVALID_ENUM_VALUE",
                  "%s is %r; the Definition declares %s. Matching is by value and "
                  "case-sensitive, never by array position" % (fid, value, literals))


def check_scda(scda, declared, scdd, f):
    md = scda.get("metadata")
    if not isinstance(md, dict):
        f.add(0x03, "MISSING_SECTION", "oac_scda.metadata is absent")
    else:
        if md.get("schema_version") not in SCHEMA_VERSIONS:
            f.add(0x0C, "UNSUPPORTED_SCHEMA_VERSION",
                  "metadata.schema_version is %r; recognized versions are %s"
                  % (md.get("schema_version"), sorted(SCHEMA_VERSIONS)))
        want = (scdd.get("metadata") or {}).get("definition_revision")
        got = md.get("definition_revision")
        if want is not None and got != want:
            f.add(0x0D, "DEFINITION_REVISION_MISMATCH",
                  "the Assignment echoes definition_revision %r but the Definition "
                  "publishes %r; the controller composed against a stale Definition "
                  "and must re-read and recompose" % (got, want))

    assignments = scda.get("assignments")
    if not isinstance(assignments, dict):
        f.add(0x03, "MISSING_SECTION",
              "oac_scda.assignments must be an object; it may be empty, but it must "
              "be present")
        return

    for dup in assignments.pop("__duplicate_keys__", []):
        f.add(0x05, "DUPLICATE_KEY",
              "%s appears more than once; ECMA-404 leaves duplicate resolution "
              "undefined, so it is rejected rather than silently resolved" % dup)

    for fid, value in assignments.items():
        d = declared.get(fid)
        if d is None:
            f.add(0x04, "UNKNOWN_FIELD_ID",
                  "%s matches no field declared in the Definition; a controller that "
                  "does not recognize a field omits it rather than inventing it" % fid)
            continue
        if value is None:
            f.add(0x0B, "NULL_VALUE",
                  "%s is null; absence and null are not equivalent" % fid)
            continue
        check_value(fid, d, value, f)


def validate(scdd_doc, scda_doc, cid_doc, profiles):
    f = Findings()

    scdd = scdd_doc.get("oac_scdd") if isinstance(scdd_doc, dict) else None
    if not isinstance(scdd, dict):
        f.add(0x02, "WRONG_ROOT_KEY", "Definition root key 'oac_scdd' is absent")
        return f

    find_nulls(scdd, f, "oac_scdd", 0x0B, "NULL_VALUE")
    declared = check_scdd(scdd, f)

    if cid_doc is not None:
        cid = cid_doc.get("oac_cid")
        if not isinstance(cid, dict):
            f.add(0x01, "MALFORMED_JSON", "CID root key 'oac_cid' is absent")
        else:
            check_bindings(declared, cid, profiles, f)

    if scda_doc is not None:
        scda = scda_doc.get("oac_scda") if isinstance(scda_doc, dict) else None
        if not isinstance(scda, dict):
            f.add(0x02, "WRONG_ROOT_KEY", "Assignment root key 'oac_scda' is absent")
        else:
            check_scda(scda, declared, scdd, f)

    return f


# ---------------------------------------------------------------------------

def _load(path, dup_aware=False):
    with open(path) as fh:
        if dup_aware:
            return json.load(fh, object_pairs_hook=_dup_key_hook)
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scdd", required=True, help="SCD Definition JSON document")
    ap.add_argument("--scda", default=None, help="SCD Assignment JSON document")
    ap.add_argument("--cid", default=None, help="path to the CID JSON document")
    ap.add_argument("--profiles", default=None,
                    help="directory of OCP-ratified OAC-PROF-*.json connector profiles")
    args = ap.parse_args()

    try:
        scdd_doc = _load(args.scdd, dup_aware=True)
        scda_doc = _load(args.scda, dup_aware=True) if args.scda else None
        cid_doc = _load(args.cid) if args.cid else None
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    findings = validate(scdd_doc, scda_doc, cid_doc, load_profiles(args.profiles))
    label = os.path.basename(args.scda or args.scdd)

    if not findings:
        print("ACCEPTED  0x00  %s" % label)
        return 0

    print("REJECTED        %s" % label)
    for code, name, detail in findings.items:
        print("  0x%02X  %-32s %s" % (code, name, detail))
    return 1


if __name__ == "__main__":
    sys.exit(main())
