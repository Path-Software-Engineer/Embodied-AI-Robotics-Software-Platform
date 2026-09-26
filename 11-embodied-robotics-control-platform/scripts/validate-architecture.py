"""Formal schema and source-link validation for the architecture manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from services.architecture import ROOT, android_evidence_contract, architecture_catalog

    manifest_path = ROOT / "architecture/manifest.v1.json"
    schema_path = ROOT / "contracts/schemas/architecture-manifest.v1.schema.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(manifest, schema)
    catalog = architecture_catalog()
    android_contract = json.loads((ROOT / "architecture/android-evidence.v1.json").read_text())
    android_schema = json.loads(
        (ROOT / "contracts/schemas/android-architecture-evidence.v1.schema.json").read_text()
    )
    jsonschema.Draft202012Validator.check_schema(android_schema)
    jsonschema.validate(android_contract, android_schema)
    android_evidence_contract()
    print(
        "OK - ArchitectureManifest v1: "
        f"{len(catalog['components'])} components, "
        f"{len(catalog['interfaces'])} interfaces, "
        f"{len(catalog['hazards'])} traced hazards, "
        f"{len(catalog['evidence_sha256'])} hashed source references"
    )


if __name__ == "__main__":
    main()
