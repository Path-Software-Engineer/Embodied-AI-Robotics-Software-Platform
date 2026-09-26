"""Architecture cards must remain connected to real source and control evidence."""

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient

from services.architecture import (
    ArchitectureRejected,
    android_evidence_contract,
    architecture_catalog,
)
from services.gateway import app


def test_manifest_schema_references_and_sha256() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "architecture/manifest.v1.json").read_text())
    schema = json.loads(
        (root / "contracts/schemas/architecture-manifest.v1.schema.json").read_text()
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(manifest, schema)
    catalog = architecture_catalog(root)
    assert catalog["scope"] == "simulation-only"
    assert {item["protocol"] for item in catalog["interfaces"]} >= {
        "HTTP",
        "WebSocket",
        "gRPC",
        "ROS2-Action",
        "ROS2-Service",
        "ROS2-Topic",
    }
    assert all(item["status"] == "unavailable" for item in catalog["external_evidence"])
    for path, digest in catalog["evidence_sha256"].items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest


def test_orphan_interface_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(architecture_catalog())
    for field in ("manifest_sha256", "evidence_sha256", "validation"):
        manifest.pop(field)
    manifest["interfaces"][0]["to"] = "phantom"
    location = tmp_path / "architecture"
    location.mkdir()
    (location / "manifest.v1.json").write_text(json.dumps(manifest))
    with pytest.raises(ArchitectureRejected, match="orphan interface"):
        architecture_catalog(tmp_path)


def test_unsafe_evidence_path_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(architecture_catalog())
    for field in ("manifest_sha256", "evidence_sha256", "validation"):
        manifest.pop(field)
    manifest["components"][0]["evidence_paths"] = ["../outside.txt"]
    location = tmp_path / "architecture"
    location.mkdir()
    (location / "manifest.v1.json").write_text(json.dumps(manifest))
    with pytest.raises(ArchitectureRejected, match="unsafe evidence path"):
        architecture_catalog(tmp_path)


def test_unverified_external_and_edge_claims_are_rejected(tmp_path: Path) -> None:
    baseline = copy.deepcopy(architecture_catalog())
    for field in ("manifest_sha256", "evidence_sha256", "validation"):
        baseline.pop(field)
    location = tmp_path / "architecture"
    location.mkdir()
    baseline["external_evidence"][0]["status"] = "verified"
    (location / "manifest.v1.json").write_text(json.dumps(baseline))
    with pytest.raises(ArchitectureRejected, match="external evidence"):
        architecture_catalog(tmp_path)
    baseline["external_evidence"][0]["status"] = "unavailable"
    baseline["edge_profiles"][1]["status"] = "measured"
    (location / "manifest.v1.json").write_text(json.dumps(baseline))
    with pytest.raises(ArchitectureRejected, match="edge measurements"):
        architecture_catalog(tmp_path)


def test_public_architecture_api_is_read_only_and_does_not_claim_edge_readiness() -> None:
    client = TestClient(app)
    catalog = client.get("/api/v3/architecture/manifest")
    assert catalog.status_code == 200
    assert catalog.json()["edge_profiles"][1]["status"] == "not-measured"
    assert client.post("/api/v3/architecture/manifest").status_code == 405
    health = client.get("/api/v3/architecture/health")
    assert health.status_code == 200
    assert health.json()["schema_version"] == "architecture-health.v1"
    assert "/api/v3/architecture/manifest" in app.openapi()["paths"]


def test_android_contract_is_a_versioned_read_only_export() -> None:
    contract = android_evidence_contract()
    assert contract["scope"] == "simulation-only"
    assert len(contract["contract_sha256"]) == 64
    assert contract["manifest_sha256"] == architecture_catalog()["manifest_sha256"]
    client = TestClient(app)
    assert client.get("/api/v3/architecture/android-evidence").status_code == 200
    assert client.post("/api/v3/architecture/android-evidence").status_code == 405
