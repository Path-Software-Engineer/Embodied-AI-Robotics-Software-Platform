import { Canvas } from '@react-three/fiber'
import { Activity, AlertTriangle, Box, Clock3, Database, Radio, RotateCcw, ShieldCheck } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import type { LinkPose, LoopEvent, RobotState } from './state'
import { freshness, linksFromState, loopEventFromUnknown } from './state'

const parts: Record<string, { scale: [number, number, number]; color: string }> = {
  torso: { scale: [0.48, 0.28, 0.7], color: '#168ba0' },
  head: { scale: [0.3, 0.3, 0.3], color: '#d7ded6' },
  left_arm: { scale: [0.12, 0.52, 0.12], color: '#e8aa55' },
}

function RobotPart({ link }: { link: LinkPose }) {
  const part = parts[link.link_name]
  if (!part) return null
  const scale = part.scale
  const p = link.position_m
  const q = link.orientation
  return (
    <mesh position={[p.x, p.y, p.z]} quaternion={[q.x, q.y, q.z, q.w]}>
      {link.link_name === 'head' ? <sphereGeometry args={[0.15, 16, 16]} /> : <boxGeometry args={scale} />}
      <meshStandardMaterial color={part.color} roughness={0.42} metalness={0.25} />
    </mesh>
  )
}

function Twin({ state }: { state: RobotState | null }) {
  return (
    <Canvas camera={{ position: [2.4, -3.3, 2.3], fov: 42 }} gl={{ antialias: true }}>
      <color attach="background" args={['#081522']} />
      <ambientLight intensity={1.35} />
      <directionalLight position={[2, -1, 4]} intensity={2.2} />
      <gridHelper args={[4, 16, '#294a5c', '#173043']} rotation={[Math.PI / 2, 0, 0]} />
      {state?.links.map(link => <RobotPart key={link.link_name} link={link} />)}
    </Canvas>
  )
}

function useRobotState() {
  const [state, setState] = useState<RobotState | null>(null)
  const [connected, setConnected] = useState(false)
  const [degraded, setDegraded] = useState(false)
  const [message, setMessage] = useState('Esperando el primer estado ROS/Gazebo.')

  useEffect(() => {
    let active = true
    let socket: WebSocket | null = null
    let timer: number | undefined
    let lastSequence = 0
    let lastRun = ''
    const connect = () => {
      if (!active) return
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      socket = new WebSocket(`${protocol}//${location.host}/api/v1/robots/embodied_demo/stream`)
      socket.onopen = () => { setConnected(true); setMessage('Canal de observación conectado.') }
      socket.onmessage = event => {
        try {
          const envelope = JSON.parse(event.data) as { type?: string; state?: unknown; database_ready?: boolean; dropped_write_samples?: number }
          if (typeof envelope.database_ready === 'boolean') {
            setDegraded(!envelope.database_ready || (envelope.dropped_write_samples ?? 0) > 0)
          }
          const next = envelope.state
          if (envelope.type === 'robot-state' && linksFromState(next)) {
            if (lastRun === next.run_id && next.sequence <= lastSequence) return
            if (lastRun === next.run_id && next.sequence > lastSequence + 1) {
              setMessage(`Hueco de ${next.sequence - lastSequence - 1} muestras; sincronizado con snapshot completo.`)
            }
            lastRun = next.run_id
            lastSequence = next.sequence
            setState(next)
          }
        } catch { setMessage('Se rechazó un mensaje inválido del stream.') }
      }
      socket.onclose = () => {
        setConnected(false)
        setMessage('Canal desconectado. Reconectando…')
        if (active) timer = window.setTimeout(connect, 1500)
      }
      socket.onerror = () => setMessage('No se pudo recibir telemetría.')
    }
    connect()
    return () => { active = false; window.clearTimeout(timer); socket?.close() }
  }, [])

  return { state, connected, degraded, message }
}

function useLoopEvents() {
  const [events, setEvents] = useState<LoopEvent[]>([])
  useEffect(() => {
    let active = true
    let socket: WebSocket | null = null
    let timer: number | undefined
    const connect = () => {
      if (!active) return
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      socket = new WebSocket(`${protocol}//${location.host}/api/v1/robots/embodied_demo/loop-stream`)
      socket.onmessage = message => {
        try {
          const envelope = JSON.parse(message.data) as { type?: string; event?: unknown }
          if (envelope.type === 'loop-event' && loopEventFromUnknown(envelope.event)) {
            const event = envelope.event
            setEvents(previous => previous.some(item =>
              item.correlation_id === event.correlation_id && item.event_sequence === event.event_sequence
            ) ? previous : [...previous, event].slice(-64))
          }
        } catch { /* Invalid events are ignored, never rendered as evidence. */ }
      }
      socket.onclose = () => { if (active) timer = window.setTimeout(connect, 1500) }
    }
    connect()
    return () => { active = false; window.clearTimeout(timer); socket?.close() }
  }, [])
  return events
}

function webglAvailable(): boolean {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch { return false }
}

export function App() {
  const { state: liveState, connected, degraded, message } = useRobotState()
  const liveLoopEvents = useLoopEvents()
  const [now, setNow] = useState(Date.now())
  const [show3D, setShow3D] = useState(true)
  const [webglFailed] = useState(() => !webglAvailable())
  const [replaySamples, setReplaySamples] = useState<RobotState[] | null>(null)
  const [replayIndex, setReplayIndex] = useState(0)
  const [replayRunId, setReplayRunId] = useState('')
  const [availableRuns, setAvailableRuns] = useState<string[]>([])
  const [replayPlaying, setReplayPlaying] = useState(false)
  const [replaySpeed, setReplaySpeed] = useState(1)
  const [replayError, setReplayError] = useState('')
  const [replayLoopEvents, setReplayLoopEvents] = useState<LoopEvent[]>([])
  const state = replaySamples?.[replayIndex] ?? liveState
  const replaying = replaySamples !== null
  const loopEvents = (replaying ? replayLoopEvents : liveLoopEvents).filter(event => event.run_id === state?.run_id)
  const latestCorrelation = [...loopEvents].reverse().find(event => event.status === 'completed')?.correlation_id ?? loopEvents.at(-1)?.correlation_id
  const currentLoop = loopEvents.filter(event => event.correlation_id === latestCorrelation)
  useEffect(() => {
    if (!liveState) return
    let active = true
    fetch('/api/v1/simulation-runs?limit=30')
      .then(response => response.ok ? response.json() : Promise.reject(new Error('Runs unavailable')))
      .then((result: { runs?: { run_id: string }[] }) => {
        if (!active) return
        const ids = (result.runs ?? []).map(run => run.run_id)
        setAvailableRuns(ids)
        setReplayRunId(previous => previous || ids[0] || liveState.run_id)
      })
      .catch(() => { if (active) setReplayRunId(previous => previous || liveState.run_id) })
    return () => { active = false }
  }, [liveState?.run_id])
  useEffect(() => {
    if (!replayPlaying || !replaySamples) return
    const timer = window.setInterval(() => {
      setReplayIndex(previous => {
        if (previous >= replaySamples.length - 1) {
          setReplayPlaying(false)
          return previous
        }
        return previous + 1
      })
    }, 500 / replaySpeed)
    return () => window.clearInterval(timer)
  }, [replayPlaying, replaySamples, replaySpeed])
  const loadReplay = async () => {
    if (!liveState) return
    setReplayError('')
    try {
      const selectedRunId = replayRunId || liveState.run_id
      const response = await fetch(`/api/v1/simulation-runs/${encodeURIComponent(selectedRunId)}/samples?limit=500`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const result = await response.json() as { read_only?: boolean; samples?: unknown[] }
      const samples = result.samples?.filter(linksFromState) ?? []
      if (!result.read_only || samples.length === 0) throw new Error('No hay muestras verificadas.')
      setReplaySamples(samples)
      setReplayIndex(0)
      setReplayPlaying(false)
      const eventResponse = await fetch(`/api/v1/simulation-runs/${encodeURIComponent(selectedRunId)}/loop-events?limit=100`)
      if (eventResponse.ok) {
        const payload = await eventResponse.json() as { events?: unknown[] }
        setReplayLoopEvents(payload.events?.filter(loopEventFromUnknown) ?? [])
      } else setReplayLoopEvents([])
    } catch (error) {
      setReplayError(error instanceof Error ? error.message : 'No se pudo cargar el replay.')
    }
  }
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 250)
    return () => window.clearInterval(timer)
  }, [])
  const freshnessStatus = connected ? freshness(state, now) : 'disconnected'
  const status = replaying ? 'replay' : freshnessStatus === 'live' && degraded ? 'degraded' : freshnessStatus
  const age = state ? Math.max(0, Math.round(now - state.observed_wall_time_ns / 1_000_000)) : null
  const simSeconds = state ? (state.simulation_time_ns / 1_000_000_000).toFixed(2) : '—'
  const links = useMemo(() => state?.links ?? [], [state])

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Navegación de la plataforma">
        <div className="brand"><Box size={22} aria-hidden="true" /><span>EMBODIED<span className="brand-accent">/</span>LAB</span></div>
        <div className="sidebar-caption">SIMULATION CONTROL PLATFORM</div>
        <nav aria-label="Módulos"><a className="nav-item active" href="#observatory"><Activity size={18} aria-hidden="true" />Observatorio<span>01</span></a></nav>
        <div className="sidebar-bottom"><ShieldCheck size={18} aria-hidden="true" /><p>Entorno de simulación.<br />Sin actuadores físicos.</p></div>
      </aside>
      <main id="observatory">
        <header className="topbar"><span className="eyebrow">PATH SOFTWARE ENGINEER / PROJECT 11</span><span className="topbar-label"><Radio size={15} aria-hidden="true" /> GAZEBO + ROS 2</span></header>
        <section className="intro"><div><p className="section-kicker">SPRINT 01 · EMBODIED AGENT LOOP</p><h1>Simulation<br /><em>Observatory</em></h1><p className="intro-copy">Estado del robot obtenido del simulador y transportado por ROS 2. Cada dato conserva reloj, frame y procedencia.</p></div><div className={`status-pill ${status}`} role="status"><span className="status-dot" />{status === 'replay' ? 'READ-ONLY REPLAY' : status === 'live' ? 'LIVE SIMULATION' : status === 'degraded' ? 'DEGRADED TELEMETRY' : status === 'stale' ? 'STALE DATA' : 'DISCONNECTED'}</div></section>
        <section className="replay-controls" aria-label="Replay de muestras persistidas">
          <div><strong>Timeline</strong><span>{replaying ? `${replayIndex + 1} / ${replaySamples.length} muestras persistidas` : 'La vista en vivo no envía comandos.'}</span></div>
          {replaying ? <>
            <label htmlFor="replay-position">Muestra</label>
            <input id="replay-position" type="range" min="0" max={replaySamples.length - 1} value={replayIndex} onChange={event => setReplayIndex(Number(event.target.value))} />
            <button className="text-button" onClick={() => setReplayPlaying(value => !value)}>{replayPlaying ? 'Pausar' : 'Reproducir'}</button>
            <label htmlFor="replay-speed">Velocidad</label>
            <select id="replay-speed" value={replaySpeed} onChange={event => setReplaySpeed(Number(event.target.value))}><option value={1}>1×</option><option value={2}>2×</option><option value={4}>4×</option></select>
            <button className="text-button" onClick={() => { setReplayPlaying(false); setReplaySamples(null) }}>Volver a vivo</button>
          </> : <>
            <label htmlFor="replay-run">Run persistido</label>
            <select id="replay-run" value={replayRunId} onChange={event => setReplayRunId(event.target.value)} disabled={!liveState}>
              {(availableRuns.includes(replayRunId) ? availableRuns : [replayRunId, ...availableRuns]).filter(Boolean).map(id => <option key={id} value={id}>{id}</option>)}
            </select>
            <button className="text-button" onClick={loadReplay} disabled={!liveState}>Cargar replay</button>
          </>}
          {replayError && <p role="alert">{replayError}</p>}
        </section>
        <section className="metrics" aria-label="Estado de la evidencia"><div className="metric"><span><Clock3 size={15} aria-hidden="true" /> SIM CLOCK</span><strong>{simSeconds}<small> s</small></strong><p>Gazebo simulation time</p></div><div className="metric"><span><Activity size={15} aria-hidden="true" /> SEQUENCE</span><strong>{state?.sequence ?? '—'}</strong><p>Monotonic state sample</p></div><div className="metric"><span><Radio size={15} aria-hidden="true" /> SAMPLE AGE</span><strong>{age ?? '—'}<small> ms</small></strong><p>{status === 'live' ? 'Current observation' : 'Not valid for live decisions'}</p></div><div className="metric"><span><Database size={15} aria-hidden="true" /> SOURCE</span><strong className="metric-source">{state ? 'ROS 2' : '—'}</strong><p>Gazebo via ros_gz_bridge</p></div></section>
        <div className="content-grid"><section className="panel twin-panel" aria-label="Gemelo digital"><div className="panel-heading"><div><p className="panel-kicker">DIGITAL TWIN / WORLD FRAME</p><h2>Robot state</h2></div><button className="text-button" onClick={() => setShow3D(value => !value)}>{show3D ? 'Vista tabular' : 'Vista 3D'}</button></div><div className="viewport">{show3D && !webglFailed ? <div className="canvas-wrap"><Twin state={state} /></div> : <div className="fallback"><Box size={36} aria-hidden="true" /><p>{webglFailed ? 'WebGL no disponible; datos accesibles en tabla.' : 'Vista tabular activa'}</p></div>}{!state && <div className="viewport-overlay"><RotateCcw size={22} aria-hidden="true" /><strong>Esperando pose verificada</strong><span>No se dibuja un robot ficticio mientras Gazebo/ROS no entregue estado.</span></div>}{status === 'stale' && <div className="stale-overlay"><AlertTriangle size={17} aria-hidden="true" /> La última pose está desactualizada.</div>}</div><div className="frame-meta"><span>FRAME <b>{state?.frame_id ?? '—'}</b></span><span>ROBOT <b>{state?.robot_id ?? '—'}</b></span><span>LINKS <b>{links.length}</b></span></div></section><section className="panel trace-panel"><div className="panel-heading"><div><p className="panel-kicker">EVIDENCE STREAM</p><h2>Trace &amp; provenance</h2></div><span className="read-only">READ ONLY</span></div><p className="stream-message">{message}</p><dl className="trace-list"><div><dt>Run ID</dt><dd>{state?.run_id ?? '—'}</dd></div><div><dt>Source</dt><dd>{state?.source ?? '—'}</dd></div><div><dt>Clock domain</dt><dd>{state?.clock_domain ?? '—'}</dd></div><div><dt>Correlation</dt><dd className="truncate" title={state?.correlation_id}>{state?.correlation_id ?? '—'}</dd></div></dl><div className="safety-note"><ShieldCheck size={19} aria-hidden="true" /><p>Esta pantalla observa. No autoriza movimientos ni sustituye una parada física de emergencia.</p></div></section></div>
        <section className="panel loop-panel" aria-label="Ciclo embodied observado"><div className="panel-heading"><div><p className="panel-kicker">PERCEPTION → FEEDBACK / ROS EVIDENCE</p><h2>Agent loop</h2></div><span className="read-only">{replaying ? 'REPLAY' : 'OBSERVATION'}</span></div><div className="loop-grid">{(['perception', 'state', 'memory', 'intent', 'safety', 'action', 'feedback'] as const).map((stage, index) => { const event = [...currentLoop].reverse().find(item => item.stage === stage); return <div className={`loop-stage ${event ? 'observed' : ''}`} key={stage}><span className="loop-number">{String(index + 1).padStart(2, '0')}</span><h3>{stage}</h3><strong>{event?.status ?? 'Sin evidencia'}</strong><p>{event?.detail ?? 'Esperando evento ROS del run.'}</p>{event && <small>seq {event.event_sequence} · {event.observed_joint_radians.toFixed(3)} rad</small>}</div> })}</div><div className="loop-footer">Correlation ID: <code>{latestCorrelation ?? '—'}</code> · {currentLoop.length} eventos observados</div></section>
        <section className="panel table-panel"><div className="panel-heading"><div><p className="panel-kicker">ACCESSIBLE STATE / SI UNITS</p><h2>Link positions</h2></div><span className="table-count">{links.length} records</span></div><div className="table-scroll"><table><thead><tr><th scope="col">Link</th><th scope="col">X (m)</th><th scope="col">Y (m)</th><th scope="col">Z (m)</th><th scope="col">Status</th></tr></thead><tbody>{links.length === 0 ? <tr><td colSpan={5}>Sin muestras verificadas. La tabla se actualizará al recibir ROS/Gazebo.</td></tr> : links.map(link => <tr key={link.link_name}><th scope="row">{link.link_name}</th><td>{link.position_m.x.toFixed(3)}</td><td>{link.position_m.y.toFixed(3)}</td><td>{link.position_m.z.toFixed(3)}</td><td>{status === 'live' ? 'Actual' : 'No actual'}</td></tr>)}</tbody></table></div></section>
      </main>
    </div>
  )
}
