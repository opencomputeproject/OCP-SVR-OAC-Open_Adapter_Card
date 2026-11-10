#!/usr/bin/env python3
"""Validate OAC Metadata documents against the OAC Metadata JSON Schema.

The schema is located alongside this tool by default, so the common case is:

    python validate-metadata.py ../examples/OAC-METADATA-0.9-ExampleA-Minimal.json

Beyond JSON Schema validation this tool applies the semantic rules of the OAC
Metadata Specification that JSON Schema cannot express, and -- when given a
directory with --resolve -- checks that the file names the document advertises
actually correspond to artifacts present.

Exit codes:
    0  schema and all instances valid
    1  at least one instance failed validation
    2  schema or input JSON could not be processed
    3  the jsonschema dependency is missing
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    print(
        "ERROR: Missing dependency 'jsonschema'. "
        "Install it with: python -m pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(3)


DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent / "OAC-Metadata-v0.9.schema.json"

# The revision of the OAC Metadata Specification this tool implements. A
# document is accepted when its major component matches; see Section 5.2 of the
# specification for why metadata deliberately diverges from the SCD's strict
# exact-match rule.
SUPPORTED_MAJOR = "0"

# Table 7.4-2. Fixed for the OCP-defined roles; a vendor role may use any name.
CANONICAL_FILE_NAMES = {
    "cid": "OAC_CID.json",
    "scdd": "OAC_SCDD.json",
    "scda": "OAC_SCDA.json",
}

# Section 6.3. The one reserved name in the OAC management model.
RESERVED_METADATA_FILE_NAME = "OAC_METADATA.json"


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except PermissionError:
        raise ValueError(f"Permission denied: {path}")
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {path}: line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error


def format_json_path(parts):
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        elif str(part).isidentifier():
            path += f".{part}"
        else:
            path += f"[{json.dumps(str(part))}]"
    return path


def semantic_errors(instance, resolve_dir: Path = None):
    """Rules from the specification that JSON Schema cannot express.

    Returned as (json_path, message) pairs so they print like schema errors.
    """
    errors = []
    root = instance.get("oac_metadata")
    if not isinstance(root, dict):
        return errors

    version = root.get("schema_version")
    if isinstance(version, str) and "." in version:
        major = version.split(".", 1)[0]
        if major != SUPPORTED_MAJOR:
            errors.append(
                (
                    "$.oac_metadata.schema_version",
                    f"major version {major!r} is not supported by this tool "
                    f"(supports major {SUPPORTED_MAJOR!r}); see Specification Section 5.2",
                )
            )

    files = root.get("files")
    if not isinstance(files, dict):
        return errors

    # Table 7.4-2 -- the OCP-defined roles carry fixed names. A vendor role may
    # name its file anything, so only the three defined roles are checked.
    for role, expected in CANONICAL_FILE_NAMES.items():
        entry = files.get(role)
        if isinstance(entry, dict):
            actual = entry.get("file_name")
            if actual is not None and actual != expected:
                errors.append(
                    (
                        f'$.oac_metadata.files["{role}"].file_name',
                        f"shall be {expected!r} for the {role} role, found {actual!r} "
                        f"(Specification Table 7.4-2)",
                    )
                )

    # Section 6.3 -- the metadata file is located by a reserved name and is not
    # one of its own entries. A self-reference is a bootstrap loop.
    for role, entry in files.items():
        if isinstance(entry, dict) and entry.get("file_name") == RESERVED_METADATA_FILE_NAME:
            errors.append(
                (
                    f'$.oac_metadata.files["{role}"].file_name',
                    f"{RESERVED_METADATA_FILE_NAME!r} is reserved for the metadata file "
                    f"itself and shall not appear as an entry (Specification Section 7.4)",
                )
            )

    # Section 7.4 -- FileIdentifier is unique relative to the PLDM Terminus ID,
    # so two roles cannot share one. This is the error that silently sends a
    # controller to the wrong file, and no schema keyword catches it.
    seen = {}
    for role, entry in sorted(files.items()):
        if not isinstance(entry, dict):
            continue
        identifier = entry.get("file_identifier")
        if identifier is None:
            continue
        if identifier in seen:
            errors.append(
                (
                    f'$.oac_metadata.files["{role}"].file_identifier',
                    f"duplicate file_identifier {identifier}, already used by role "
                    f"{seen[identifier]!r}; identifiers are unique relative to the "
                    f"PLDM Terminus ID (Specification Section 7.4)",
                )
            )
        else:
            seen[identifier] = role

    # Duplicate file names are the same failure wearing a different hat.
    seen_names = {}
    for role, entry in sorted(files.items()):
        if not isinstance(entry, dict):
            continue
        name = entry.get("file_name")
        if name is None:
            continue
        if name in seen_names:
            errors.append(
                (
                    f'$.oac_metadata.files["{role}"].file_name',
                    f"duplicate file_name {name!r}, already used by role "
                    f"{seen_names[name]!r} (Specification Section 7.4)",
                )
            )
        else:
            seen_names[name] = role

    if resolve_dir is not None:
        for role, entry in sorted(files.items()):
            if not isinstance(entry, dict):
                continue
            name = entry.get("file_name")
            if name and not (resolve_dir / name).exists():
                errors.append(
                    (
                        f'$.oac_metadata.files["{role}"].file_name',
                        f"advertised file {name!r} not found in {resolve_dir}",
                    )
                )

    return errors


def validate_instance(validator, instance_path: Path, resolve_dir: Path = None):
    try:
        instance = load_json(instance_path)
    except ValueError as error:
        print(f"\nFILE: {instance_path}")
        print("INSTANCE: INVALID JSON")
        print(f"1. $: {error}")
        return False

    findings = [
        (format_json_path(list(error.absolute_path)), error.message)
        for error in validator.iter_errors(instance)
    ]
    findings.extend(semantic_errors(instance, resolve_dir))
    findings.sort()

    print(f"\nFILE: {instance_path}")
    if not findings:
        print("INSTANCE: VALID")
        print("ERROR COUNT: 0")
        return True

    print("INSTANCE: INVALID")
    print(f"ERROR COUNT: {len(findings)}")
    for index, (path, message) in enumerate(findings, 1):
        print(f"{index}. {path}: {message}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate OAC Metadata documents against the OAC Metadata JSON Schema."
    )
    parser.add_argument(
        "instances",
        type=Path,
        nargs="+",
        help="One or more OAC Metadata documents to validate",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"Path to the schema (default: {DEFAULT_SCHEMA.name} beside this tool)",
    )
    parser.add_argument(
        "--resolve",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Also check that every advertised file_name exists in DIR. Useful "
            "against a staged firmware image; meaningless against the repository, "
            "where the artifacts carry repository names rather than FileName values."
        ),
    )
    args = parser.parse_args()

    try:
        schema = load_json(args.schema)
    except ValueError as error:
        print(f"SCHEMA: INVALID JSON\n{error}", file=sys.stderr)
        return 2

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        print("SCHEMA: INVALID")
        print(error.message)
        return 2

    print("SCHEMA: VALID Draft 2020-12")
    validator = Draft202012Validator(schema)
    results = [validate_instance(validator, path, args.resolve) for path in args.instances]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
