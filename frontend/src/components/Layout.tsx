import type { ReactNode } from 'react'
import { useAuth } from '../hooks/useAuth'

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b border-sentinel-border bg-sentinel-panel px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-sentinel-accent font-bold text-sentinel-bg">
            S
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight">SentinelAI</h1>
            <p className="text-xs text-slate-400">Autonomous AI SOC</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-300">
            {user?.full_name || user?.email}
            <span className="ml-2 rounded bg-sentinel-bg px-2 py-0.5 text-xs text-sentinel-accent">
              {user?.role}
            </span>
          </span>
          <button
            onClick={logout}
            className="rounded border border-sentinel-border px-3 py-1 text-slate-300 hover:border-sentinel-accent hover:text-sentinel-accent"
          >
            Logout
          </button>
        </div>
      </header>
      <main className="flex-1 p-6">{children}</main>
    </div>
  )
}
