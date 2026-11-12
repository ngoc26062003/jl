<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchItems, savePracticeRun, type StudyItem } from '../api/practice'
import { updatePracticeProgress } from '@/auth/session'
import ChoiceMode from '../components/practice/ChoiceMode.vue'
import FlashcardMode from '../components/practice/FlashcardMode.vue'
import ResultPanel from '../components/practice/ResultPanel.vue'
import TypingMode from '../components/practice/TypingMode.vue'
import { shuffle, type Direction, type Mode, type Result } from '../lib/practice'

const route = useRoute()
const router = useRouter()

const MODES: Mode[] = ['flashcard', 'choice', 'typing']
const DIRS: Direction[] = ['term_to_romaji', 'romaji_to_term', 'term_to_meaning']
const deckIds = String(route.query.decks ?? '').split(',').map(Number).filter((n) => Number.isInteger(n) && n > 0)
const mode = (MODES.includes(route.query.mode as Mode) ? route.query.mode : 'choice') as Mode
const dir = (DIRS.includes(route.query.dir as Direction) ? route.query.dir : 'term_to_romaji') as Direction
const limit = Number(route.query.limit ?? 0) || 0
const doShuffle = route.query.shuffle !== '0'

const loading = ref(true)
const error = ref('')
const scope = ref<StudyItem[]>([])
const pool = ref<StudyItem[]>([])
const queue = ref<StudyItem[]>([])
const results = ref<Result[] | null>(null)
const round = ref(0)
const saveError = ref('')

function begin(source: StudyItem[], applyLimit: boolean) {
  let q = source.filter((i) => !(mode === 'choice' && dir === 'term_to_meaning') || !!i.meaning_vi)
  if (doShuffle) q = shuffle(q)
  if (applyLimit && limit > 0) q = q.slice(0, limit)
  if (q.length === 0) {
    error.value = 'Không có mục nào phù hợp để luyện tập (ví dụ chữ cái không có nghĩa tiếng Việt).'
    return
  }
  queue.value = q
  results.value = null
  round.value++
}

const retryWrong = () => begin(results.value!.filter((r) => !r.correct).map((r) => r.item), false)

async function completeRun(completed: Result[]) {
  results.value = completed
  saveError.value = ''
  try {
    const saved = await savePracticeRun({
      mode,
      direction: mode === 'typing' ? 'typing' : dir,
      answers: completed.map((result) => ({
        item_id: result.item.id,
        given: mode === 'flashcard'
          ? result.correct ? 'remembered' : 'forgotten'
          : result.given ?? '',
      })),
    })
    updatePracticeProgress(saved.current_streak, saved.total_stars)
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : 'Không lưu được kết quả luyện tập.'
  }
}

onMounted(async () => {
  try {
    if (deckIds.length === 0) throw new Error('Chưa chọn nội dung luyện tập')
    const res = await fetchItems(deckIds, mode === 'choice')
    scope.value = res.items
    const merged = new Map<number, StudyItem>()
    for (const i of [...res.items, ...res.distractors]) merged.set(i.id, i)
    pool.value = [...merged.values()]
    begin(scope.value, true)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="pr-page">
    <button class="pr-btn ghost" @click="router.push('/practice')">← Chọn lại</button>

    <p v-if="loading" class="small">Đang tải…</p>
    <p v-else-if="error" class="pr-err">{{ error }}</p>
    <ResultPanel v-if="!loading && !error && results" :results="results" :mode="mode"
      @retry-wrong="retryWrong" @restart="begin(scope, true)" @back="router.push('/practice')" />
    <p v-if="results && saveError" class="pr-err" role="alert">{{ saveError }}</p>

    <div v-if="!loading && !error && !results" :key="round">
      <FlashcardMode v-if="mode === 'flashcard'" :items="queue" :dir="dir" @finish="completeRun" />
      <ChoiceMode v-else-if="mode === 'choice'" :items="queue" :pool="pool" :dir="dir" @finish="completeRun" />
      <TypingMode v-else :items="queue" @finish="completeRun" />
    </div>
  </main>
</template>