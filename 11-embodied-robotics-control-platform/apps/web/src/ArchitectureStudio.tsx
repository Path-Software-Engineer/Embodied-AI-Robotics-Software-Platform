import { useEffect, useState } from 'react'
import { Activity, Boxes, GitBranch, ShieldAlert } from 'lucide-react'

type Component = {
  id: string
  name: string
  kind: string
  owner: string
  evidence_paths: string[]
  depends_on: string[]
}
type Interface = {
  id: string
  protocol: string
  from: string
  to: string
  contract_path: string
  authority: string
  timing: string
}
type Hazard = {
  id: string
  name: string
  control_component_ids: string[]
  test_paths: string[]
  residual_risk: string
}
type Catalog = {
  schema_version: string
  scope: string
  manifest_sha256: string
  components: Component[]
  interfaces: Interface[]
  hazards: Hazard[]
  edge_profiles: { id: string; target: string; status: string; note: string }[]
  external_evidence: { id: string; status: string; reason: string }[]
  evidence_sha256: Record<string, string>
}
type Health = {
  run_id: string | null
  state_age_ms: number | null
  simulation_state: string
  telemetry_database: string
  dropped_write_samples: number
}

export function ArchitectureStudio() {
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [health, setHealth] = useState<Health | null>(null)
  const [selectedId, setSelectedId] = useState('gateway')
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/v3/architecture/manifest', { signal: controller.signal })
      .then(response => response.ok ? response.json() as Promise<Catalog> : Promise.reject(new Error(`HTTP ${response.status}`)))
      .then(setCatalog)
      .catch(reason => { if (!controller.signal.aborted) setError(`Catálogo no disponible: ${String(reason)}`) })
    return () => controller.abort()
  }, [])
  useEffect(() => {
    let active = true
    const refresh = () => fetch('/api/v3/architecture/health')
      .then(response => response.ok ? response.json() as Promise<Health> : Promise.reject())
      .then(result => { if (active) setHealth(result) })
      .catch(() => { if (active) setHealth(null) })
    refresh()
    const interval = window.setInterval(refresh, 5000)
    return () => { active = false; window.clearInterval(interval) }
  }, [])

  const selected = catalog?.components.find(item => item.id === selectedId) ?? catalog?.components[0]
  const linked = catalog?.interfaces.filter(item => item.from === selected?.id || item.to === selected?.id) ?? []

  return (
    <section className="panel architecture-studio" id="architecture" aria-label="Estudio de arquitectura">
      <div className="panel-heading">
        <div><p className="panel-kicker">SPRINT 03 / SOURCE-LINKED ARCHITECTURE</p><h2>Architecture studio</h2></div>
        <span className="read-only">SIMULATION ONLY</span>
      </div>
      <p className="architecture-intro">Las tarjetas se derivan del manifest versionado y enlazan código, contratos y pruebas con SHA-256. Un archivo existente no equivale a un test aprobado ni a hardware validado.</p>
      {error && <p className="architecture-error" role="alert">{error}</p>}
      {!catalog && !error && <p className="architecture-intro" role="status">Validando catálogo de arquitectura…</p>}
      {catalog && <>
        <div className="architecture-summary" aria-label="Resumen del manifest">
          <div><Boxes size={19} aria-hidden="true" /><strong>{catalog.components.length}</strong><span>Componentes enlazados</span></div>
          <div><GitBranch size={19} aria-hidden="true" /><strong>{catalog.interfaces.length}</strong><span>Interfaces trazadas</span></div>
          <div><ShieldAlert size={19} aria-hidden="true" /><strong>{catalog.hazards.length}</strong><span>Hazards con controles</span></div>
          <div><Activity size={19} aria-hidden="true" /><strong>{health?.simulation_state ?? 'unknown'}</strong><span>Estado observado, no certificado</span></div>
        </div>
        <div className="architecture-columns">
          <div>
            <h3>Componentes</h3>
            <div className="architecture-card-list">
              {catalog.components.map(item => <button key={item.id} type="button" className={`architecture-card ${selected?.id === item.id ? 'selected' : ''}`} onClick={() => setSelectedId(item.id)} aria-pressed={selected?.id === item.id}>
                <span>{item.kind}</span><strong>{item.name}</strong><small>{item.id}</small>
              </button>)}
            </div>
          </div>
          <div className="architecture-detail" aria-live="polite">
            <h3>{selected?.name ?? 'Selecciona un componente'}</h3>
            {selected && <>
              <dl><div><dt>Owner</dt><dd>{selected.owner}</dd></div><div><dt>Depende de</dt><dd>{selected.depends_on.join(', ') || 'Ninguno'}</dd></div></dl>
              <h4>Interfaces y autoridad</h4>
              <ul>{linked.map(item => <li key={item.id}><strong>{item.protocol}: {item.from} → {item.to}</strong><span>{item.authority} · {item.timing}</span><code>{item.contract_path}</code></li>)}</ul>
              <a className="architecture-drill" href="#control">Abrir control board y feedback ROS</a>
              <h4>Evidencia de fuente</h4>
              <ul>{selected.evidence_paths.map(path => <li key={path}><code>{path}</code><span>SHA-256 {catalog.evidence_sha256[path]?.slice(0, 16)}…</span></li>)}</ul>
            </>}
          </div>
        </div>
        <div className="architecture-bottom">
          <div><h3>Seguridad y riesgo residual</h3><ul>{catalog.hazards.map(item => <li key={item.id}><strong>{item.id} · {item.name}</strong><span>Controles: {item.control_component_ids.join(', ')}</span><span>Pruebas: {item.test_paths.join(', ')}</span><em>{item.residual_risk}</em></li>)}</ul></div>
          <div><h3>Edge y evidencia externa</h3><ul>{catalog.edge_profiles.map(item => <li key={item.id}><strong>{item.target} · {item.status}</strong><span>{item.note}</span></li>)}{catalog.external_evidence.map(item => <li key={item.id}><strong>{item.id} · {item.status}</strong><span>{item.reason}</span></li>)}</ul></div>
        </div>
        <footer className="architecture-footer">Manifest SHA-256: <code>{catalog.manifest_sha256}</code> · Run: <code>{health?.run_id ?? 'sin estado'}</code> · DB: {health?.telemetry_database ?? 'unknown'} · Pérdidas de escritura: {health?.dropped_write_samples ?? '—'} · <a href="/api/v3/architecture/android-evidence">Contrato Android P66</a> · <a href="/api/v3/architecture/snapshots">Historial de manifests</a></footer>
      </>}
    </section>
  )
}
