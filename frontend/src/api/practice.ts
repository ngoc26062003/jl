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