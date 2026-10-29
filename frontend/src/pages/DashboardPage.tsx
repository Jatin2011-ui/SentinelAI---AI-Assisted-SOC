import { useEffect, useState } from 'react'
import { fetchHealth, fetchIncidents } from '../services/api'
import type { HealthStatus } from '../types'

interface IncidentRow {
  id: string
  title?: string
  severity?: string
  status?: string
  risk_score?: number
}

const SEVERITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

function severityColor(sev: string): string {
  if (sev === 'CRITICAL') return 'text-red-400'
  if (sev === 'HIGH') return 'text-orange-400'
  if (sev === 'MEDIUM') return 'text-amber-300'
  return 'text-emerald-400'
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [incidents, setIncidents] = useState<IncidentRow[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    fetchHealth()
      .then((h) => !cancelled && setHealth(h))
      .catch(() => !cancelled && setError('Backend status unavailable'))
    fetchIncidents()
      .then((data) => !cancelled && setIncidents(data))
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  const severityCounts: Record<string, number> = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }
  for (const inc of incidents) {
    const sev = inc.severity ?? ''
    if (sev in severityCounts) severityCounts[sev] += 1
  }
  const active = incidents.filter(
    (inc) => inc.status !== 'RESOLVED' && inc.status !== 'FALSE_POSITIVE',
  )

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">SOC Overview</h2>
        <p className="text-sm text-slate-400">
          Live incidents, severity breakdown and system status.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatusCard label="Backend" value={health ? health.status : '...'} ok={health?.status === 'ok'} />
        <StatusCard label="Environment" value={health?.environment ?? '...'} ok={!!health?.environment} />
        <StatusCard
          label="Simulation"
          value={health ? (health.simulation_mode ? 'ON' : 'OFF') : '...'}
          ok={health?.simulation_mode === true}
        />
        <StatusCard label="Incidents" value={String(incidents.length)} ok={true} />
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {SEVERITIES.map((s) => (
          <div key={s} className="rounded-lg border border-sentinel-border bg-sentinel-panel p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">{s}</p>
            <p className={'mt-1 text-lg font-semibold ' + severityColor(s)}>{severityCounts[s]}</p>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-sentinel-border bg-sentinel-panel p-6">
        <h3 className="mb-2 font-semibold text-slate-200">Active Incidents</h3>
        <div className="space-y-2">
          {active.slice(0, 10).map((inc) => (
            <div
              key={inc.id}
              className="flex items-center justify-between border-b border-sentinel-border py-2 text-sm"
            >
              <span className="text-slate-200">{inc.title || inc.id}</span>
              <span className="text-slate-400">
                {inc.severity} - risk {Math.round(inc.risk_score ?? 0)} - {inc.status}
              </span>
            </div>
          ))}
          {error && <p className="text-sm text-red-400">Backend status unavailable - incident data may be stale.</p>}
          {!error && active.length === 0 && <p className="text-sm text-slate-400">No active incidents.</p>}
        </div>
      </div>
    </div>
  )
}

function StatusCard({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="rounded-lg border border-sentinel-border bg-sentinel-panel p-4">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className={'mt-1 text-lg font-semibold ' + (ok ? 'text-emerald-400' : 'text-red-400')}>
        {value}
      </p>
    </div>
  )
}
