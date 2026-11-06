import type { StudyItem } from '../api/practice'

export type Mode = 'flashcard' | 'choice' | 'typing'
export type Direction = 'term_to_romaji' | 'romaji_to_term' | 'term_to_meaning'
export interface Result { item: StudyItem; correct: boolean; given?: string }

export function shuffle<T>(arr: readonly T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export const promptOf = (it: StudyItem, dir: Direction) => (dir === 'romaji_to_term' ? it.romaji : it.term)

export const answerOf = (it: StudyItem, dir: Direction) =>
  dir === 'term_to_romaji' ? it.romaji : dir === 'romaji_to_term' ? it.term : (it.meaning_vi ?? '')

/** 1 đáp án đúng + tối đa n-1 đáp án nhiễu khác nhau, không trùng romaji với đáp án đúng. */
export function buildChoices(correct: StudyItem, pool: StudyItem[], dir: Direction, n = 4): string[] {
  const right = answerOf(correct, dir)
  const seen = new Set([right])
  const wrong: string[] = []
  for (const d of shuffle(pool)) {
    if (d.id === correct.id || d.romaji === correct.romaji) continue
    const text = answerOf(d, dir)
    if (!text || seen.has(text)) continue
    seen.add(text)
    wrong.push(text)
    if (wrong.length === n - 1) break
  }
  return shuffle([right, ...wrong])
}

// So romaji theo dạng chuẩn hóa để chấp nhận cả si/shi, tu/tsu, hu/fu, zi/ji...
const CANON: [string, string][] = [
  ['sha', 'sya'], ['shu', 'syu'], ['sho', 'syo'], ['shi', 'si'],
  ['cha', 'tya'], ['chu', 'tyu'], ['cho', 'tyo'], ['chi', 'ti'],
  ['tsu', 'tu'], ['fu', 'hu'],
  ['ja', 'zya'], ['ju', 'zyu'], ['jo', 'zyo'], ['ji', 'zi'],
]

export function canonRomaji(s: string): string {
  let r = s.normalize('NFKC').toLowerCase().replace(/[\s'’\-.]/g, '')
  for (const [from, to] of CANON) r = r.split(from).join(to)
  return r
}

export function isRomajiCorrect(item: StudyItem, input: string): boolean {
  const a = canonRomaji(input)
  return a !== '' && [item.romaji, ...item.romaji_alt].some((x) => canonRomaji(x) === a)
}