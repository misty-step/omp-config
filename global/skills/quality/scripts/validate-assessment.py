#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


SUPPORTED_KEYWORDS = {
    "$schema",
    "$id",
    "$ref",
    "$defs",
    "title",
    "type",
    "const",
    "enum",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minItems",
    "minLength",
    "pattern",
    "anyOf",
    "oneOf",
    "allOf",
    "if",
    "then",
    "else",
}


class ValidationError(ValueError):
    pass


def resolve_reference(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValidationError(f"unsupported $ref {reference!r}")
    current: Any = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise ValidationError(f"unresolved $ref {reference!r}")
        current = current[part]
    if not isinstance(current, dict):
        raise ValidationError(f"$ref {reference!r} does not resolve to a schema")
    return current


def matches_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    raise ValidationError(f"unsupported JSON Schema type {expected!r}")


def validate_schema_vocabulary(
    schema: dict[str, Any],
    location: str = "$",
) -> None:
    unknown = sorted(set(schema) - SUPPORTED_KEYWORDS)
    if unknown:
        raise ValidationError(f"{location}: unsupported schema keywords {unknown}")

    for container in ("properties", "$defs"):
        for name, child in schema.get(container, {}).items():
            validate_schema_vocabulary(child, f"{location}/{container}/{name}")
    for container in ("allOf", "anyOf", "oneOf"):
        for index, child in enumerate(schema.get(container, [])):
            validate_schema_vocabulary(child, f"{location}/{container}/{index}")
    for key in ("items", "if", "then", "else"):
        if key in schema:
            validate_schema_vocabulary(schema[key], f"{location}/{key}")


def matches(instance: Any, schema: dict[str, Any], root: dict[str, Any]) -> bool:
    try:
        validate(instance, schema, root)
    except ValidationError:
        return False
    return True


def validate(
    instance: Any,
    schema: dict[str, Any],
    root: dict[str, Any],
    location: str = "$",
) -> None:

    if "$ref" in schema:
        validate(instance, resolve_reference(root, schema["$ref"]), root, location)

    for branch in schema.get("allOf", []):
        validate(instance, branch, root, location)

    if "anyOf" in schema:
        if not any(matches(instance, branch, root) for branch in schema["anyOf"]):
            raise ValidationError(f"{location}: anyOf matched no schema")

    if "oneOf" in schema:
        count = sum(matches(instance, branch, root) for branch in schema["oneOf"])
        if count != 1:
            raise ValidationError(f"{location}: oneOf matched {count} schemas")

    if "if" in schema:
        branch = schema.get("then") if matches(instance, schema["if"], root) else schema.get("else")
        if branch is not None:
            validate(instance, branch, root, location)

    if "const" in schema and instance != schema["const"]:
        raise ValidationError(f"{location}: value does not match const")
    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(f"{location}: value is not in enum")

    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not isinstance(expected_types, list) or not all(
            isinstance(item, str) for item in expected_types
        ):
            raise ValidationError(f"{location}: invalid type declaration")
        if not any(matches_type(instance, item) for item in expected_types):
            raise ValidationError(f"{location}: type must be {expected_types}")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            raise ValidationError(f"{location}: minLength failed")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            raise ValidationError(f"{location}: pattern failed")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            raise ValidationError(f"{location}: minItems failed")
        if "items" in schema:
            for index, item in enumerate(instance):
                validate(item, schema["items"], root, f"{location}/{index}")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                raise ValidationError(f"{location}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(instance) - set(properties))
            if extra:
                raise ValidationError(f"{location}: additional properties {extra}")
        for key, child_schema in properties.items():
            if key in instance:
                validate(instance[key], child_schema, root, f"{location}/{key}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-assessment.py <assessment.json>", file=sys.stderr)
        return 2

    assessment_path = Path(sys.argv[1])
    schema_path = Path(__file__).resolve().parent.parent / "references" / "assessment.schema.json"
    try:
        schema = json.loads(schema_path.read_text())
        assessment = json.loads(assessment_path.read_text())
        validate_schema_vocabulary(schema)
        validate(assessment, schema, schema)
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(error, file=sys.stderr)
        return 1

    print(f"quality assessment valid: {assessment_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
