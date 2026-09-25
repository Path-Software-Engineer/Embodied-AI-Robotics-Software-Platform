CREATE TABLE IF NOT EXISTS control_plans (
  plan_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN
    ('proposed', 'approved', 'running', 'completed', 'failed', 'cancelled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at TIMESTAMPTZ,
  plan_payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS control_plans_run_created_idx
  ON control_plans (run_id, created_at DESC);

CREATE TABLE IF NOT EXISTS control_events (
  id BIGSERIAL PRIMARY KEY,
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  run_id TEXT NOT NULL,
  plan_id TEXT,
  actor_id TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS control_events_run_time_idx
  ON control_events (run_id, observed_at, id);
