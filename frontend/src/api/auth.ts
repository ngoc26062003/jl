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

export interface PracticeHistoryEntry {
  id: string
  mode: string
  direction: string
  total_questions: number
  correct_count: number
  created_at: string
}

export interface PracticeHistory {
  runs: PracticeHistoryEntry[]
  practice_days: string[]
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

export async function fetchPracticeHistory(): Promise<PracticeHistory> {
  const { data } = await api.get<PracticeHistory>('/auth/history')
  return data
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await api.put('/auth/password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
}

export async function fetchMyAvatar(): Promise<Blob> {
  const { data } = await api.get<Blob>('/auth/me/avatar', { responseType: 'blob' })
  return data
}

export async function updateMyAvatar(file: File): Promise<void> {
  const form = new FormData()
  form.append('file', file)
  await api.put('/auth/me/avatar', form)
}

export function logoutAccount(): void {
  clearSession()
}
