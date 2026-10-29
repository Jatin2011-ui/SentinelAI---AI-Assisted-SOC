// Minimal API client
import type { HealthStatus, TokenPair, UserOut } from '../types'

const ACCESS_KEY = 'sentinel.access_token'
const REFRESH_KEY = 'sentinel.refresh_token'

export function getAccessToken(): string | null { return localStorage.getItem(ACCESS_KEY) }
export function saveTokens(tokens: TokenPair): void { localStorage.setItem(ACCESS_KEY, tokens.access_token); localStorage.setItem(REFRESH_KEY, tokens.refresh_token) }
export function clearTokens(): void { localStorage.removeItem(ACCESS_KEY); localStorage.removeItem(REFRESH_KEY) }

async function rawFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  headers.set('Content-Type','application/json')
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  return fetch(path, {...init, headers})
}
async function tryRefresh(): Promise<boolean> {
  const refreshToken = localStorage.getItem(REFRESH_KEY)
  if (!refreshToken) return false
  const resp = await fetch('/api/v1/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:refreshToken})})
  if (!resp.ok){clearTokens();return false}
  saveTokens((await resp.json()) as TokenPair)
  return true
}
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let resp = await rawFetch(path, init)
  if (resp.status===401){ if (await tryRefresh()) { resp = await rawFetch(path, init) } }
  if (!resp.ok){ const body = await resp.text().catch(()=> ''); throw new ApiError(resp.status, body||resp.statusText) }
  return (await resp.json()) as T
}
export class ApiError extends Error { constructor(public status:number,message:string){super(message);this.name='ApiError'} }
export async function login(email:string,password:string):Promise<UserOut>{ const resp=await fetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})}); if(!resp.ok) throw new ApiError(resp.status,'Invalid'); saveTokens((await resp.json()) as TokenPair); return fetchMe() }
export function logout():void{clearTokens()}
export async function fetchMe():Promise<UserOut>{return request<UserOut>('/api/v1/auth/me')}
export async function fetchHealth():Promise<HealthStatus>{return request<HealthStatus>('/health')}
export async function fetchIncidents(){return request<any[]>('/api/v1/incidents')}
