CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS robot_state_samples (
  observed_at TIMESTAMPTZ NOT NULL,
  run_id TEXT NOT NULL,
  robot_id TEXT NOT NULL,
  sequence BIGINT NOT NULL CHECK (sequence > 0),
  simulation_time_ns BIGINT NOT NULL CHECK (simulation_time_ns >= 0),
  frame_id TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  PRIMARY KEY (observed_at, run_id, sequence)
);

SELECT create_hypertable('robot_state_samples', 'observed_at', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS robot_state_run_time_idx
  ON robot_state_samples (run_id, observed_at DESC);
