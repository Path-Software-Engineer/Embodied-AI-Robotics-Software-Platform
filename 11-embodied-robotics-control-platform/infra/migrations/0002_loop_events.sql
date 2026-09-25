CREATE TABLE IF NOT EXISTS loop_events (
  observed_at TIMESTAMPTZ NOT NULL,
  run_id TEXT NOT NULL,
  robot_id TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  event_sequence BIGINT NOT NULL CHECK (event_sequence > 0),
  stage TEXT NOT NULL CHECK (stage IN
    ('perception', 'state', 'memory', 'intent', 'safety', 'action', 'feedback')),
  status TEXT NOT NULL,
  payload JSONB NOT NULL,
  PRIMARY KEY (observed_at, run_id, event_sequence)
);

SELECT create_hypertable('loop_events', 'observed_at', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS loop_events_run_correlation_time_idx
  ON loop_events (run_id, correlation_id, observed_at DESC);
