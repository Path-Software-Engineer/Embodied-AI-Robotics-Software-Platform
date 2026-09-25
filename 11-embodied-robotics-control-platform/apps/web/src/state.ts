export interface Vector3 { x: number; y: number; z: number }
export interface Quaternion { x: number; y: number; z: number; w: number }
export interface LinkPose {
  link_name: string
  position_m: Vector3
  orientation: Quaternion
}
export interface RobotState {
  schema_version: 'robot-state.v1'
  run_id: string
  robot_id: string
  frame_id: string
  clock_domain: 'gazebo_sim'
  simulation_time_ns: number
  observed_wall_time_ns: number
  sequence: number
  source: 'gazebo/ros_gz_bridge'
  correlation_id: string
  links: LinkPose[]
}
export interface StateEnvelope {
  mode: 'simulation'
  age_ms: number
  stale: boolean
  state: RobotState
}
export interface LoopEvent {
  schema_version: 'embodied-loop-event.v1'
  run_id: string
  robot_id: string
  correlation_id: string
  clock_domain: 'gazebo_sim'
  simulation_time_ns: number
  stage: 'perception' | 'state' | 'memory' | 'intent' | 'safety' | 'action' | 'feedback'
  status: string
  event_sequence: number
  observed_wall_time_ns: number
  observed_joint_radians: number
  target_joint_radians: number
  detail: string
}

export function loopEventFromUnknown(value: unknown): value is LoopEvent {
  if (!value || typeof value !== 'object') return false
  const event = value as Partial<LoopEvent>
  return event.schema_version === 'embodied-loop-event.v1'
    && event.clock_domain === 'gazebo_sim'
    && typeof event.simulation_time_ns === 'number'
    && typeof event.run_id === 'string'
    && typeof event.correlation_id === 'string'
    && ['perception', 'state', 'memory', 'intent', 'safety', 'action', 'feedback'].includes(event.stage ?? '')
    && typeof event.event_sequence === 'number'
    && typeof event.observed_wall_time_ns === 'number'
}

export function freshness(state: RobotState | null, nowMs: number): 'live' | 'stale' | 'disconnected' {
  if (!state) return 'disconnected'
  return nowMs - state.observed_wall_time_ns / 1_000_000 > 1000 ? 'stale' : 'live'
}

export function linksFromState(value: unknown): value is RobotState {
  if (!value || typeof value !== 'object') return false
  const state = value as Partial<RobotState>
  return state.schema_version === 'robot-state.v1'
    && state.clock_domain === 'gazebo_sim'
    && state.source === 'gazebo/ros_gz_bridge'
    && typeof state.sequence === 'number'
    && state.sequence > 0
    && typeof state.observed_wall_time_ns === 'number'
    && Array.isArray(state.links)
    && state.links.length > 0
}
