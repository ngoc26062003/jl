import { api } from './client'

export interface GrammarExample {
  japanese: string
  reading: string
  meaning: string
}

export interface GrammarContent {
  summary: string
  usage: string[]
  examples: GrammarExample[]
}

export interface GrammarLesson {
  id: string
  slug: string
  title: string
  lesson_type: string
  level: string | null
  objective: string | null
  position: number
  content: GrammarContent | null
}

export interface GrammarOption {
  id: string
  text: string
}

export interface GrammarQuestion {
  id: string
  question_type: string
  prompt: {
    sentence: string
    translation: string
  }
  position: number
  difficulty: number
  options: GrammarOption[]
}

export interface GrammarAnswer {
  correct: boolean
  correct_answer: string
  explanation: string | null
}

export async function fetchGrammarLesson(lessonId: string): Promise<GrammarLesson> {
  const { data } = await api.get<GrammarLesson>(`/lessons/${lessonId}`)
  return data
}

export async function fetchGrammarQuestions(lessonId: string): Promise<GrammarQuestion[]> {
  const { data } = await api.get<GrammarQuestion[]>(`/lessons/${lessonId}/questions`, {
    params: { mode: 'multiple_choice' },
  })
  return data
}

export async function submitGrammarAnswer(
  lessonId: string,
  questionId: string,
  optionId: string,
): Promise<GrammarAnswer> {
  const { data } = await api.post<GrammarAnswer>(
    `/lessons/${lessonId}/questions/${questionId}/answer`,
    { option_id: optionId },
  )
  return data
}
