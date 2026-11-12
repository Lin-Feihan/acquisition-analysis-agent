"""Manifest-driven input collection and validation."""
import json
import re
from datetime import date
from pathlib import Path


class SettingsValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Invalid task settings: " + "; ".join(f"{key}: {value}" for key, value in errors.items()))


def load_manifest(agent_root):
    return json.loads((Path(agent_root) / "manifest.json").read_text(encoding="utf-8"))


def validate_settings(agent_root, submitted):
    if not isinstance(submitted, dict):
        raise SettingsValidationError({"settings": "must be a JSON object"})
    fields = load_manifest(agent_root)["settings_schema"]["fields"]
    allowed = {field["id"] for field in fields}
    unknown = sorted(set(submitted) - allowed)
    if unknown:
        raise SettingsValidationError({key: "unknown field" for key in unknown})
    result, errors = {}, {}
    for field in fields:
        key = field["id"]
        value = submitted.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            value = field.get("default")
        if value is None:
            if field.get("required"):
                errors[key] = "required"
            result[key] = None
            continue
        if not isinstance(value, str):
            errors[key] = "must be text"
            continue
        value = value.strip()
        if field["type"] == "date":
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    raise ValueError()
                date.fromisoformat(value)
            except ValueError:
                errors[key] = "use a valid YYYY-MM-DD date"
        result[key] = value
    if errors:
        raise SettingsValidationError(errors)
    result["valuation_date"] = result.get("valuation_date") or result["research_cutoff_date"]
    return result


def collect_settings(agent_root):
    manifest = load_manifest(agent_root)
    print(manifest["name"])
    print("Optional answers may be left blank. Documents listed here are not uploaded.")
    submitted = {}
    for field in manifest["settings_schema"]["fields"]:
        default = field.get("default")
        suffix = f" [{default}]" if default is not None else ""
        while True:
            print("\n" + field["description"])
            value = input(field["label"] + suffix + ": ").strip()
            if value or not field.get("required"):
                break
            print("This field is required.")
        if value:
            submitted[field["id"]] = value
    return validate_settings(agent_root, submitted)
