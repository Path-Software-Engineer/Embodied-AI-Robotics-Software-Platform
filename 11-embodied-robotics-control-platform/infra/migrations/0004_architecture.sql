CREATE TABLE IF NOT EXISTS architecture_manifest_snapshots (
    manifest_sha256 char(64) PRIMARY KEY,
    schema_version text NOT NULL CHECK (schema_version = 'architecture-manifest.v1'),
    recorded_at timestamptz NOT NULL DEFAULT now(),
    payload jsonb NOT NULL,
    CHECK (payload->>'scope' = 'simulation-only')
);
