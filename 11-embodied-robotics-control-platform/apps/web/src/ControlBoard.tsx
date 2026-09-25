import { AlertOctagon, CheckCircle2, CirclePause, LockKeyhole, Play, ShieldAlert, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import type { LoopEvent, RobotState } from './state'

type ControlStatus = {
  run_id: string
  mode: 'Disarmed' | 'Manual' | 'Assisted' | 'AutonomousSim'
  estop_latched: boolean
  lease_owner: string
  lease_expires_at_wall_ms: number
  state_sequence: number
  state_stale: boolean
}

type PlanNode = { node_id: string; action: string; target_radians: number; dependencies: string[]; requires_approval: boolean }
type Plan = { plan_id: string; run_id: string; snapshot_sequence: number; snapshot_hash: string; nodes: PlanNode[] }
type PlanRecord = { plan_id: string; actor_id: string; status: string; plan_payload: Plan }
type AuditEvent = { observed_at: string; plan_id: string | null; actor_id: string; event_type: string; status: string; payload: Record<string, unknown> }

async function readJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) throw new Error(`Lectura no disponible (HTTP ${response.status}).`)
  return response.json() as Promise<T>
}

async function command<T>(path: string, token: string, actor: string, lease: string, body: unknown = {}): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      'X-Actor-Id': actor,
      ...(lease ? { 'X-Control-Lease': lease } : {}),
    },
    body: JSON.stringify(body),
  })
  const payload = await response.json() as { detail?: string } & T
  if (!response.ok) throw new Error(payload.detail ?? `Comando rechazado (HTTP ${response.status}).`)
  return payload
}

export function ControlBoard({ liveState, replaying, loopEvents }: {
  liveState: RobotState | null
  replaying: boolean
  loopEvents: LoopEvent[]
}) {
  const [token, setToken] = useState('')
  const [actor, setActor] = useState('local-operator')
  const [lease, setLease] = useState('')
  const [status, setStatus] = useState<ControlStatus | null>(null)
  const [plans, setPlans] = useState<PlanRecord[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [audit, setAudit] = useState<AuditEvent[]>([])
  const [target, setTarget] = useState('0.15')
  const [reason, setReason] = useState('Movimiento simulado revisado por operador')
  const [confirmed, setConfirmed] = useState(false)
  const [working, setWorking] = useState('')
  const [message, setMessage] = useState('Sin autoridad de control. Observación únicamente.')
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    if (!liveState) return
    try {
      const [nextStatus, nextPlans, nextAudit] = await Promise.all([
        readJson<ControlStatus>('/api/v2/control/status'),
        readJson<{ plans: PlanRecord[] }>('/api/v2/plans?limit=30'),
        readJson<{ events: AuditEvent[] }>(`/api/v2/simulation-runs/${encodeURIComponent(liveState.run_id)}/control-events?limit=100`),
      ])
      if (nextStatus.run_id !== liveState.run_id) return
      setStatus(nextStatus)
      setPlans(nextPlans.plans)
      setAudit(nextAudit.events)
    } catch {
      setStatus(null)
    }
  }, [liveState?.run_id])

  useEffect(() => {
    void refresh()
    const timer = window.setInterval(() => { void refresh() }, 2000)
    return () => window.clearInterval(timer)
  }, [refresh])

  useEffect(() => {
    if (!lease || !token || !liveState) return
    const timer = window.setInterval(() => {
      void command('/api/v2/control/leases/heartbeat', token, actor, lease)
        .catch(() => { setLease(''); setError('Lease expirada o revocada. El control volvió a estado seguro.') })
    }, 10_000)
    return () => window.clearInterval(timer)
  }, [lease, token, actor, liveState?.run_id])

  const selected = plans.find(plan => plan.plan_id === selectedId) ?? plans[0]
  const selectedPlanId = selected?.plan_id ?? ''
  const missionEvents = useMemo(() => audit.filter(event => event.plan_id === selectedPlanId).slice(-12), [audit, selectedPlanId])
  const actionFeedback = useMemo(() => loopEvents.filter(event => event.correlation_id === selectedPlanId).slice(-8), [loopEvents, selectedPlanId])
  const latestFeedback = actionFeedback.at(-1)
  const feedbackError = latestFeedback ? Math.abs(latestFeedback.target_joint_radians - latestFeedback.observed_joint_radians) : null
  const enabled = Boolean(liveState && !replaying && token.length >= 32 && /^[A-Za-z0-9_-]{3,64}$/.test(actor))
  const armed = Boolean(status && status.mode !== 'Disarmed' && !status.estop_latched && lease && status.lease_owner === actor)

  async function run(label: string, operation: () => Promise<unknown>) {
    setError('')
    setWorking(label)
    try {
      const result = await operation()
      setMessage(`${label} confirmado por el sistema de simulación.`)
      await refresh()
      return result
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : `${label} no se completó.`)
      return null
    } finally {
      setWorking('')
    }
  }

  const needsReview = enabled && confirmed && reason.trim().length >= 5

  return (
    <section className="panel control-board" aria-label="Control board supervisado">
      <div className="panel-heading">
        <div><p className="panel-kicker">SPRINT 02 / HUMAN AUTHORITY</p><h2>Robot task planning</h2></div>
        <span className="read-only">{replaying ? 'REPLAY: CONTROL BLOQUEADO' : 'SIMULATION ONLY'}</span>
      </div>
      <p className="control-explainer">Las propuestas no mueven el robot. Cada acción exige token local, lease exclusivo, modo armado, aprobación humana y autorización del supervisor ROS independiente.</p>
      <div className="control-status" role="status" aria-label="Estado del supervisor">
        {status?.estop_latched ? <ShieldAlert aria-hidden="true" /> : <ShieldCheck aria-hidden="true" />}
        <strong>{status ? `${status.mode}${status.estop_latched ? ' · E-STOP ENCLAVADO' : ''}` : 'SUPERVISOR NO DISPONIBLE'}</strong>
        <span>{status?.state_stale ? 'Pose desactualizada: no ejecutar' : status?.lease_owner ? `Lease: ${status.lease_owner}` : 'Sin lease activa'}</span>
      </div>
      <div className="control-grid">
        <div className="control-column">
          <h3><LockKeyhole size={17} aria-hidden="true" /> 01 · Operador y autoridad</h3>
          <label htmlFor="operator-id">Identificador del operador</label>
          <input id="operator-id" value={actor} maxLength={64} onChange={event => setActor(event.target.value)} autoComplete="off" />
          <label htmlFor="operator-token">Token de operador local</label>
          <input id="operator-token" type="password" value={token} onChange={event => setToken(event.target.value)} autoComplete="off" placeholder="No se publica en la interfaz" />
          <p className="control-help">El token permanece solo en memoria de esta pestaña; nunca forma parte del bundle web.</p>
          <div className="control-actions">
            <button onClick={() => void run('Lease', async () => {
              const result = await command<{ lease_id: string }>('/api/v2/control/leases', token, actor, '')
              setLease(result.lease_id)
              return result
            })} disabled={!enabled || Boolean(lease) || Boolean(working)}>Tomar lease</button>
            <button className="quiet" onClick={() => void run('Revocación', async () => {
              const result = await command('/api/v2/control/revoke', token, actor, lease, { confirmed: true, reason })
              setLease('')
              return result
            })} disabled={!enabled || !lease || !needsReview}>Liberar</button>
          </div>
          <p className="control-help">{lease ? `Lease temporal activa hasta ${status?.lease_expires_at_wall_ms ? new Date(status.lease_expires_at_wall_ms).toLocaleTimeString() : 'confirmación pendiente'}.` : 'La lease vence si esta pestaña deja de renovarla.'}</p>
          <div className="mode-actions" aria-label="Cambios de modo con confirmación">
            {(['Disarmed', 'Manual', 'Assisted', 'AutonomousSim'] as const).map(mode =>
              <button key={mode} className={status?.mode === mode ? 'selected' : 'quiet'} disabled={!needsReview || !lease || Boolean(working) || status?.mode === mode}
                onClick={() => void run(`Modo ${mode}`, () => command('/api/v2/control/mode', token, actor, lease, { requested_mode: mode, confirmed: true, reason }))}>{mode}</button>
            )}
          </div>
          <p className="control-help">Transiciones progresivas; Disarmed → AutonomousSim directo se rechaza.</p>
        </div>
        <div className="control-column">
          <h3><Play size={17} aria-hidden="true" /> 02 · Plan y ejecución</h3>
          <label htmlFor="goal-target">Meta: hombro izquierdo (rad)</label>
          <input id="goal-target" type="number" min="-0.8" max="0.8" step="0.05" value={target} onChange={event => setTarget(event.target.value)} />
          <button onClick={() => void run('Propuesta', async () => {
            const result = await command<{ plan: Plan }>('/api/v2/plans', token, actor, '', { target_radians: Number(target) })
            setSelectedId(result.plan.plan_id)
            return result
          })} disabled={!enabled || Boolean(working)}>Proponer plan</button>
          <label htmlFor="mission-queue">Cola de misiones del run</label>
          <select id="mission-queue" value={selectedPlanId} onChange={event => setSelectedId(event.target.value)}>
            {plans.length === 0 ? <option value="">Sin planes persistidos</option> : plans.map(plan => <option key={plan.plan_id} value={plan.plan_id}>{plan.plan_id.slice(0, 16)} · {plan.status}</option>)}
          </select>
          {selected && <div className="plan-card">
            <p><strong>Estado:</strong> {selected.status} · <strong>Owner:</strong> {selected.actor_id}</p>
            <p><strong>Snapshot:</strong> seq {selected.plan_payload.snapshot_sequence} · <code>{selected.plan_payload.snapshot_hash.slice(0, 12)}</code></p>
            <ol>{selected.plan_payload.nodes.map(node => <li key={node.node_id}><strong>{node.node_id}</strong> → {node.target_radians.toFixed(2)} rad · aprobación {node.requires_approval ? 'requerida' : 'ausente'} · depende de {node.dependencies.length ? node.dependencies.join(', ') : 'ninguno'}</li>)}</ol>
          </div>}
          <label htmlFor="operator-reason">Motivo de autorización</label>
          <input id="operator-reason" value={reason} maxLength={300} onChange={event => setReason(event.target.value)} />
          <label className="confirm-line"><input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} /> Confirmo que revisé el plan, la pose y el modo de simulación.</label>
          <div className="control-actions">
            <button onClick={() => void run('Aprobación', () => command(`/api/v2/plans/${selectedPlanId}/approve`, token, actor, lease, { confirmed: true, reason }))} disabled={!needsReview || !armed || selected?.status !== 'proposed' || Boolean(working)}><CheckCircle2 size={16} aria-hidden="true" /> Aprobar</button>
            <button onClick={() => void run('Ejecución', () => command(`/api/v2/plans/${selectedPlanId}/execute`, token, actor, lease))} disabled={!needsReview || !armed || selected?.status !== 'approved' || Boolean(working)}><Play size={16} aria-hidden="true" /> Ejecutar</button>
          </div>
        </div>
        <div className="control-column emergency-column">
          <h3><ShieldAlert size={17} aria-hidden="true" /> 03 · Interrupción segura</h3>
          <p>Cancelar termina la ROS Action activa. Stop desarma y solicita cancelación. E‑Stop queda enclavado y requiere reset explícito; no equivale a una parada física certificada.</p>
          <button className="quiet" onClick={() => void run('Cancelación', () => command(`/api/v2/plans/${selectedPlanId}/cancel`, token, actor, lease))} disabled={!needsReview || !lease || selected?.status !== 'running'}><CirclePause size={16} aria-hidden="true" /> Cancelar acción</button>
          <button className="quiet" onClick={() => void run('Stop', () => command('/api/v2/control/stop', token, actor, lease, { confirmed: true, reason }))} disabled={!needsReview || !lease}>Solicitar stop</button>
          <button className="danger" onClick={() => void run('E‑Stop', () => command('/api/v2/control/estop', token, actor, '', { confirmed: true, reason }))} disabled={!needsReview}><AlertOctagon size={16} aria-hidden="true" /> E‑Stop simulado</button>
          <button className="quiet" onClick={() => void run('Reset E‑Stop', () => command('/api/v2/control/reset_estop', token, actor, '', { confirmed: true, reason }))} disabled={!needsReview || !status?.estop_latched}>Reset · permanece Disarmed</button>
          <div className="control-feedback" aria-live="polite"><strong>{working ? `${working} en curso…` : message}</strong>{error && <p role="alert">{error}</p>}</div>
        </div>
      </div>
      <div className="mission-evidence">
        <div><h3>Eventos auditados</h3><ul tabIndex={0} aria-label="Lista desplazable de eventos auditados">{missionEvents.length ? missionEvents.map((event, index) => <li key={`${event.observed_at}-${index}`}><time>{new Date(event.observed_at).toLocaleTimeString()}</time> {event.event_type} · {event.status} · {event.actor_id}</li>) : <li>Sin eventos auditados para el plan seleccionado.</li>}</ul></div>
        <div><h3>Feedback ROS correlacionado</h3>{latestFeedback && <p className="control-signal">Target {latestFeedback.target_joint_radians.toFixed(3)} rad · actual {latestFeedback.observed_joint_radians.toFixed(3)} rad · error {feedbackError?.toFixed(3)} rad · {latestFeedback.status}</p>}<ul tabIndex={0} aria-label="Lista desplazable de feedback ROS">{actionFeedback.length ? actionFeedback.map(event => <li key={event.event_sequence}>{event.stage} · {event.status} · {event.observed_joint_radians.toFixed(3)} rad</li>) : <li>Esperando feedback del ROS Action.</li>}</ul></div>
      </div>
    </section>
  )
}
