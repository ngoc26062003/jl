export type Script = 'hiragana' | 'katakana'

export interface KanaRow {
  consonant: string
  romaji: (string | null)[]
  hiragana: (string | null)[]
  katakana: (string | null)[]
}

export const COLUMN_HEADERS = ['a', 'i', 'u', 'e', 'o'] as const

const _ = null

export const KANA_ROWS: KanaRow[] = [
  { consonant: '', romaji: ['a', 'i', 'u', 'e', 'o'],
    hiragana: ['あ', 'い', 'う', 'え', 'お'], katakana: ['ア', 'イ', 'ウ', 'エ', 'オ'] },
  { consonant: 'k', romaji: ['ka', 'ki', 'ku', 'ke', 'ko'],
    hiragana: ['か', 'き', 'く', 'け', 'こ'], katakana: ['カ', 'キ', 'ク', 'ケ', 'コ'] },
  { consonant: 's', romaji: ['sa', 'shi', 'su', 'se', 'so'],
    hiragana: ['さ', 'し', 'す', 'せ', 'そ'], katakana: ['サ', 'シ', 'ス', 'セ', 'ソ'] },
  { consonant: 't', romaji: ['ta', 'chi', 'tsu', 'te', 'to'],
    hiragana: ['た', 'ち', 'つ', 'て', 'と'], katakana: ['タ', 'チ', 'ツ', 'テ', 'ト'] },
  { consonant: 'n', romaji: ['na', 'ni', 'nu', 'ne', 'no'],
    hiragana: ['な', 'に', 'ぬ', 'ね', 'の'], katakana: ['ナ', 'ニ', 'ヌ', 'ネ', 'ノ'] },
  { consonant: 'h', romaji: ['ha', 'hi', 'fu', 'he', 'ho'],
    hiragana: ['は', 'ひ', 'ふ', 'へ', 'ほ'], katakana: ['ハ', 'ヒ', 'フ', 'ヘ', 'ホ'] },
  { consonant: 'm', romaji: ['ma', 'mi', 'mu', 'me', 'mo'],
    hiragana: ['ま', 'み', 'む', 'め', 'も'], katakana: ['マ', 'ミ', 'ム', 'メ', 'モ'] },
  { consonant: 'y', romaji: ['ya', _, 'yu', _, 'yo'],
    hiragana: ['や', _, 'ゆ', _, 'よ'], katakana: ['ヤ', _, 'ユ', _, 'ヨ'] },
  { consonant: 'r', romaji: ['ra', 'ri', 'ru', 're', 'ro'],
    hiragana: ['ら', 'り', 'る', 'れ', 'ろ'], katakana: ['ラ', 'リ', 'ル', 'レ', 'ロ'] },
  { consonant: 'w', romaji: ['wa', _, _, _, 'wo'],
    hiragana: ['わ', _, _, _, 'を'], katakana: ['ワ', _, _, _, 'ヲ'] },
  { consonant: '', romaji: ['n', _, _, _, _],
    hiragana: ['ん', _, _, _, _], katakana: ['ン', _, _, _, _] },
]