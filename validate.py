"""Validate every camera profile in profiles/. Run by CI on each pull request.

    python validate.py            # exit 1 on any error; warnings are informational

Standalone on purpose: contributors don't need the Gimballer app code.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "profiles"
FIELDS = ("latitude", "longitude", "gimbal_pitch", "serial_number", "date", "make", "model", "altitude")
REQUIRED = ("latitude", "longitude", "gimbal_pitch", "date")
# serial_number is optional (some cameras record none; Gimballer flags those rows) but, when set,
# must be the camera's own serial: never Make/Model or another stand-in, never the aircraft's.
NOT_CAMERA_SERIAL = ("drone", "aircraft")
KEYWORDS = {"latitude": "lat", "longitude": "lon", "gimbal_pitch": "pitch", "serial_number": "serial",
            "date": "date", "make": "make", "model": "model", "altitude": "alt"}
TAG_RE = re.compile(r"^[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+$")
ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def safe(name: str) -> str:
    cleaned = ILLEGAL.sub("_", name.strip()).rstrip(". ") or "_"
    return "_" + cleaned if cleaned.split(".")[0].upper() in RESERVED else cleaned


def check(path: Path, seen: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    raw = path.read_bytes()
    if b"\r\n" in raw:
        errors.append("use LF line endings")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"invalid JSON: {exc}"], []
    if not isinstance(data, dict):
        return ["profile must be a JSON object"], []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    make, model = data.get("make"), data.get("model")
    if not isinstance(make, str) or not make.strip() or not isinstance(model, str) or not model.strip():
        errors.append("make and model must be non-empty strings (exactly as ExifTool reports EXIF:Make / EXIF:Model)")
        return errors, warnings
    expected = f"{safe(make)}/{safe(model)}.json"
    actual = path.relative_to(ROOT).as_posix()
    if actual != expected:
        errors.append(f"file should be at profiles/{expected}")
    key = (" ".join(make.split()).casefold(), " ".join(model.split()).casefold())
    if key in seen:
        errors.append(f"duplicate of {seen[key]} (Make+Model must be unique)")
    seen[key] = actual
    fields = data.get("fields")
    if not isinstance(fields, dict):
        errors.append("'fields' must be an object")
        return errors, warnings
    for name in sorted(set(fields) - set(FIELDS)):
        errors.append(f"unknown field '{name}'")
    for name in REQUIRED:
        if not fields.get(name):
            errors.append(f"required field '{name}' is not mapped")
    for name, tag in fields.items():
        if tag is None:
            continue
        if not isinstance(tag, str) or not TAG_RE.match(tag):
            errors.append(f"field '{name}' must be a 'Group:Tag' string or null, got {tag!r}")
        elif name == "serial_number" and "serial" not in tag.split(":", 1)[1].casefold():
            errors.append(f"serial_number -> {tag}: must be a serial-number tag. If the camera records no "
                          "serial, use null (Gimballer flags those rows); never a stand-in such as the model")
        elif name == "serial_number" and any(w in tag.split(":", 1)[1].casefold() for w in NOT_CAMERA_SERIAL):
            errors.append(f"serial_number -> {tag}: must be the camera's serial, not the aircraft's")
        elif KEYWORDS.get(name, "") not in tag.split(":", 1)[1].casefold():
            warnings.append(f"{name} -> {tag}: tag name doesn't mention '{KEYWORDS[name]}' — double-check")
    for name in ("notes", "contributor", "updated"):
        if name in data and not isinstance(data[name], str):
            errors.append(f"'{name}' must be a string")
    return errors, warnings


def main() -> int:
    seen: dict = {}
    failed = 0
    files = sorted(ROOT.rglob("*.json"))
    for path in files:
        errors, warnings = check(path, seen)
        rel = path.relative_to(ROOT.parent).as_posix()
        for message in errors:
            print(f"::error file={rel}::{message}")
        for message in warnings:
            print(f"::warning file={rel}::{message}")
        failed += bool(errors)
    print(f"{len(files)} profiles checked, {failed} with errors")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
