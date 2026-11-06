export type QuizMode = 'choice' | 'typing'
export interface Question { character_id: number; char: string; options: string[] | null }
export interface CheckResult { correct: boolean; correct_answer: string }

export async function fetchQuiz(lessonId: number, mode: QuizMode, count = 10): Promise<Question[]> {
  const res = await fetch(`/api/v1/lessons/${lessonId}/quiz?mode=${mode}&count=${count}`)
  if (!res.ok) throw new Error('Không tải được bài kiểm tra')
  return res.json()
}

export async function checkAnswer(characterId: number, answer: string): Promise<CheckResult> {
  const res = await fetch('/api/v1/quiz/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ character_id: characterId, answer }),
  })
  if (!res.ok) throw new Error('Không chấm được câu trả lời')
  return res.json()
}