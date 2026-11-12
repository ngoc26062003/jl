export interface Lesson {
  id: number | string
  slug?: string
  title?: string
  lesson_type?: string
  level?: string | null
  objective?: string | null
  position?: number
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