// Shared API types. Keep aligned with backend/app/schemas (Phase 1: auth only).

export type RoleName = 'ADMIN' | 'SOC_ANALYST' | 'VIEWER'

export interface UserOut {
  id: string
  email: string
  full_name: string
  role: RoleName
  is_active: boolean
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface HealthStatus {
  status: string
  service: string
  environment: string
  simulation_mode: boolean
}
