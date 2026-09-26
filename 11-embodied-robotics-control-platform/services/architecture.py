"""Validated, read-only architecture catalog backed by versioned source files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("architecture/manifest.v1.json")
ANDROID_CONTRACT = Path("architecture/android-evidence.v1.json")


class ArchitectureRejected(ValueError):
    """Raised when architecture evidence is absent, unsafe or disconnected."""


def evidence_file(root: Path, relative: str) -> Path:
    if not relative or "\\" in relative or ".." in Path(relative).parts:
        raise ArchitectureRejected(f"unsafe evidence path: {relative}")
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()) or not candidate.is_file():
        raise ArchitectureRejected(f"missing or out-of-root evidence: {relative}")
    return candidate


def architecture_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = evidence_file(root, MANIFEST.as_posix())
    raw = source.read_bytes()
    manifest: dict[str, Any] = json.loads(raw)
    if manifest.get("schema_version") != "architecture-manifest.v1":
        raise ArchitectureRejected("unsupported architecture manifest version")
    components = manifest["components"]
    interfaces = manifest["interfaces"]
    hazards = manifest["hazards"]
    component_ids = {item["id"] for item in components}
    if len(component_ids) != len(components):
        raise ArchitectureRejected("duplicate component ID")
    if len({item["id"] for item in interfaces}) != len(interfaces):
        raise ArchitectureRejected("duplicate interface ID")
    attached: set[str] = set()
    references: set[str] = set()
    for component in components:
        for target in component["depends_on"]:
            if target not in component_ids or target == component["id"]:
                raise ArchitectureRejected(f"invalid dependency: {component['id']} -> {target}")
        references.update(component["evidence_paths"])
    for interface in interfaces:
        if interface["from"] not in component_ids or interface["to"] not in component_ids:
            raise ArchitectureRejected(f"orphan interface: {interface['id']}")
        attached.update((interface["from"], interface["to"]))
        references.add(interface["contract_path"])
    if attached != component_ids:
        raise ArchitectureRejected(f"orphan components: {sorted(component_ids - attached)}")
    for hazard in hazards:
        if not set(hazard["control_component_ids"]) <= component_ids:
            raise ArchitectureRejected(f"orphan hazard control: {hazard['id']}")
        references.update(hazard["test_paths"])
    for profile in manifest["edge_profiles"]:
        if profile["status"] == "measured":
            raise ArchitectureRejected(
                f"edge measurements have no verified importer: {profile['id']}"
            )
        if profile["measurement_path"]:
            references.add(profile["measurement_path"])
    for external in manifest["external_evidence"]:
        if external["status"] != "unavailable":
            raise ArchitectureRejected(
                f"external evidence has no verified importer: {external['id']}"
            )
    checksums = {
        path: hashlib.sha256(evidence_file(root, path).read_bytes()).hexdigest()
        for path in sorted(references)
    }
    return {
        **manifest,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "evidence_sha256": checksums,
        "validation": "source-linked",
    }


def android_evidence_contract(root: Path = ROOT) -> dict[str, Any]:
    source = evidence_file(root, ANDROID_CONTRACT.as_posix())
    raw = source.read_bytes()
    contract: dict[str, Any] = json.loads(raw)
    catalog = architecture_catalog(root)
    if contract.get("schema_version") != "android-architecture-evidence.v1":
        raise ArchitectureRejected("unsupported Android evidence contract")
    if contract.get("architecture_manifest") != MANIFEST.as_posix():
        raise ArchitectureRejected("Android contract references another manifest")
    if set(contract["exported_component_ids"]) != {item["id"] for item in catalog["components"]}:
        raise ArchitectureRejected("Android component references are incomplete")
    if set(contract["interface_ids"]) != {item["id"] for item in catalog["interfaces"]}:
        raise ArchitectureRejected("Android interface references are incomplete")
    return {
        **contract,
        "contract_sha256": hashlib.sha256(raw).hexdigest(),
        "manifest_sha256": catalog["manifest_sha256"],
        "evidence_sha256": catalog["evidence_sha256"],
    }
