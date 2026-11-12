import { api } from './client'

export interface AdminUser {
  id: string
  username: string | null
  email: string
  role: 'learner' | 'admin'
  is_active: boolean
  total_stars: number
  current_streak: number
  last_practiced_on: string | null
}

export interface QuestionStat {
  id: number
  term: string
  reading: string
  meaning_vi: string | null
  attempts: number
  correct: number
  incorrect: number
}

export interface LeaderboardEntry {
  id: string
  username: string | null
  email: string
  total_stars: number
  current_streak: number
  correct_answers: number
}

export interface AdminDashboard {
  total_users: number
  active_learners: number
  total_runs: number
  most_correct: QuestionStat[]
  most_incorrect: QuestionStat[]
  leaderboard: LeaderboardEntry[]
  users: AdminUser[]
}

export interface ImageSlot {
  slot: string
  label: string
  url: string
  updated_at: string | null
}

export interface PublicImageSlot {
  slot: string
  url: string | null
}

export async function fetchAdminDashboard(): Promise<AdminDashboard> {
  const { data } = await api.get<AdminDashboard>('/admin/dashboard')
  return data
}

export async function updateUserRole(userId: string, role: 'learner' | 'admin'): Promise<void> {
  await api.patch(`/admin/users/${userId}/role`, { role })
}

export async function fetchImageSlots(): Promise<ImageSlot[]> {
  const { data } = await api.get<ImageSlot[]>('/media')
  return data
}

export async function fetchPublicImageSlots(): Promise<PublicImageSlot[]> {
  const { data } = await api.get<PublicImageSlot[]>('/media/slots')
  return data
}

export async function replaceImage(slot: string, file: File): Promise<ImageSlot> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.put<ImageSlot>(`/media/${slot}`, form)
  return data
}

export function resolveMediaUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
  return `${base}${path}`
}
