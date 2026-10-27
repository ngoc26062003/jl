import { api } from './client'
import type { LessonPage, LessonQuery } from '@/types/api'

export async function fetchLessons(params: LessonQuery = {}): Promise<LessonPage> {
  // Bỏ các tham số rỗng để không gửi ?level= lên server
  const clean = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== ''),
  )
  const { data } = await api.get<LessonPage>('/lessons', { params: clean })
  return data
}
export interface Lesson {
  id: string
  slug: string
  title: string
  lesson_type: string
  level: string | null
  objective: string | null
  position: number
}
