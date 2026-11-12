import { reactive } from 'vue'

export interface AuthUser {
  id: string
  username: string | null
  email: string
  role: 'learner' | 'admin'
  total_stars: number
  current_streak: number
  last_practiced_on: string | null
}

let accessToken: string | null = null

export const authState = reactive({
  user: null as AuthUser | null,
  initialized: false,
})

export function getAccessToken(): string | null {
  return accessToken
}

export function setSession(token: string, user: AuthUser): void {
  accessToken = token
  authState.user = user
  authState.initialized = true
}

export function updatePracticeProgress(currentStreak: number, totalStars: number): void {
  if (!authState.user) return
  authState.user.current_streak = currentStreak
  authState.user.total_stars = totalStars
}

export function clearSession(): void {
  accessToken = null
  authState.user = null
  authState.initialized = true
}
