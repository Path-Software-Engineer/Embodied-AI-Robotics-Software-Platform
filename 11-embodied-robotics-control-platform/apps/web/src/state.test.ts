import { describe, expect, it } from 'vitest'
import { freshness, linksFromState, type RobotState } from './state'

const observed: RobotState = {
  schema_version: 'robot-state.v1', run_id: 'test-run', robot_id: 'embodied_demo',
  frame_id: 'world/studio', clock_domain: 'gazebo_sim', simulation_time_ns: 100,
  observed_wall_time_ns: 2_000_000_000, sequence: 1,
  source: 'gazebo/ros_gz_bridge', correlation_id: 'fixture',
  links: [{ link_name: 'torso', position_m: { x: 0, y: 0, z: 1 },
    orientation: { x: 0, y: 0, z: 0, w: 1 } }],
}

describe('state provenance and freshness', () => {
  it('does not present missing or aged evidence as live', () => {
    expect(freshness(null, 2000)).toBe('disconnected')
    expect(freshness(observed, 2500)).toBe('live')
    expect(freshness(observed, 3500)).toBe('stale')
  })
  it('rejects an unversioned or invented payload', () => {
    expect(linksFromState({ ...observed, source: 'sample-data' })).toBe(false)
    expect(linksFromState(observed)).toBe(true)
  })
})
