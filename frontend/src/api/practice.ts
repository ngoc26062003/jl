import { api } from './client'

export type Category = 'hiragana' | 'katakana' | 'vocab' | 'kanji'

export interface Deck {
  id: number; category: Category; level: string | null
  slug: string; title_jp: string; title_vi: string; item_count: number
}
export interface StudyItem {
  id: number; deck_id: number; term: string; reading: string; romaji: string
  romaji_alt: string[]; meaning_vi: string | null; extra: Record<string, unknown> | null
}
export interface PracticeRunResult {
  id: string
  total_questions: number
  correct_count: number
  current_streak: number
  total_stars: number
  practiced_today: boolean
}

async function getJson<T>(url: string): Promise<T> {
  const { data } = await api.get<T>(url)
  return data
}

export function fetchDecks(categories: Category[], level?: string) {
  const p = new URLSearchParams()
  categories.forEach((c) => p.append('category', c))
  if (level) p.set('level', level)
  return getJson<Deck[]>(`/practice/decks?${p}`)
}

export function fetchItems(deckIds: number[], withDistractors: boolean) {
  const p = new URLSearchParams()
  deckIds.forEach((id) => p.append('deck_ids', String(id)))
  if (withDistractors) p.set('with_distractors', 'true')
  return getJson<{ items: StudyItem[]; distractors: StudyItem[] }>(`/practice/items?${p}`)
}

export async function savePracticeRun(input: {
  mode: 'choice' | 'typing' | 'flashcard'
  direction: 'term_to_romaji' | 'romaji_to_term' | 'term_to_meaning' | 'typing'
  answers: { item_id: number; given: string }[]
}): Promise<PracticeRunResult> {
  const { data } = await api.post<PracticeRunResult>('/practice/runs', input)
  return data
}