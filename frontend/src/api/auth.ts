import { api } from './client'
import { authState, clearSession, getAccessToken, setSession, type AuthUser } from '@/auth/session'

interface AuthResponse {
  access_token: string
  token_type: 'bearer'
  user: AuthUser
}

export interface PracticeSummary {
  total_runs: number
  total_correct: number
  current_streak: number
  total_stars: number
  last_practiced_on: string | null
}

export async function registerAccount(input: {
  username: string
  email: string
  password: string
}): Promise<AuthUser> {
  const { data } = await api.post<AuthResponse>('/auth/register', input)
  setSession(data.access_token, data.user)
  return data.user
}

export async function loginAccount(identifier: string, password: string): Promise<AuthUser> {
  const { data } = await api.post<AuthResponse>('/auth/login', { identifier, password })
  setSession(data.access_token, data.user)
  return data.user
}

export async function loginWithGoogle(credential: string): Promise<AuthUser> {
  const { data } = await api.post<AuthResponse>('/auth/google', { credential })
  setSession(data.access_token, data.user)
  return data.user
}

export function initializeSession(): AuthUser | null {
  if (!getAccessToken()) clearSession()
  return authState.user
}

export async function fetchPracticeSummary(): Promise<PracticeSummary> {
  const { data } = await api.get<PracticeSummary>('/auth/summary')
  return data
}

export function logoutAccount(): void {
  clearSession()
}
