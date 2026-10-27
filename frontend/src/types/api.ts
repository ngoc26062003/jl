export interface Lesson {
  id: number | string
  title?: string
  [key: string]: unknown
}

export interface LessonPage {
  items: Lesson[]
  total: number
  limit: number
  offset: number
}

export interface LessonQuery {
  limit?: number
  offset?: number
  category?: string
  level?: string
  lesson_type?: string
}

export async function fetchLessons(params: LessonQuery = {}): Promise<LessonPage> {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value))
  }
  const res = await fetch(`/api/v1/lessons?${query}`)
  if (!res.ok) throw new Error(`API lỗi ${res.status}`)
  return res.json()
}