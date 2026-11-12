import { api } from './client'

export type QuizMode = 'choice' | 'typing'
export interface Question { character_id: number; char: string; options: string[] | null }
export interface CheckResult { correct: boolean; correct_answer: string }

export async function fetchQuiz(lessonId: number, mode: QuizMode, count = 10): Promise<Question[]> {
  const { data } = await api.get<Question[]>(`/lessons/${lessonId}/quiz`, {
    params: { mode, count },
  })
  return data
}

export async function checkAnswer(characterId: number, answer: string): Promise<CheckResult> {
  const { data } = await api.post<CheckResult>('/quiz/check', {
    character_id: characterId,
    answer,
  })
  return data
}