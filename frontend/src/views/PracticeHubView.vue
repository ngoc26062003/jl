<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchDecks, type Deck } from '../api/practice'
import PageTitle from '../components/PageTitle.vue'
import type { Direction, Mode } from '../lib/practice'

type Tab = 'vocab' | 'kana' | 'kanji'
const router = useRouter()

const tab = ref<Tab>('vocab')
const level = ref('N5')
const decks = ref<Deck[]>([])
const loading = ref(false)
const error = ref('')
const selected = ref<Set<number>>(new Set())

const mode = ref<Mode>('choice')
const dir = ref<Direction>('term_to_romaji')
const limit = ref(0)
const shuffleOn = ref(true)

const MODES: { id: Mode; label: string }[] = [
  { id: 'flashcard', label: 'Flashcard' },
  { id: 'choice', label: 'Chọn đáp án' },
  { id: 'typing', label: 'Gõ romaji' },
]
const dirs = computed(() => {
  const base = [
    { id: 'term_to_romaji', label: 'Nhật → Phiên âm' },
    { id: 'romaji_to_term', label: 'Phiên âm → Nhật' },
  ] as { id: Direction; label: string }[]
  if (tab.value === 'vocab') base.push({ id: 'term_to_meaning', label: 'Nhật → Nghĩa' })
  return base
})

const groups = computed(() =>
  tab.value === 'kana'
    ? [
        { title_jp: 'ひらがな', title_vi: 'Hiragana', decks: decks.value.filter((d) => d.category === 'hiragana') },
        { title_jp: 'カタカナ', title_vi: 'Katakana', decks: decks.value.filter((d) => d.category === 'katakana') },
      ]
    : [{ title_jp: '', title_vi: '', decks: decks.value }],
)
const selectedCount = computed(() =>
  decks.value.filter((d) => selected.value.has(d.id)).reduce((s, d) => s + d.item_count, 0),
)

async function load() {
  selected.value = new Set()
  if (tab.value !== 'vocab' && dir.value === 'term_to_meaning') dir.value = 'term_to_romaji'
  if (tab.value === 'kanji') { decks.value = []; return }
  loading.value = true
  error.value = ''
  try {
    decks.value = tab.value === 'vocab'
      ? await fetchDecks(['vocab'], level.value)
      : await fetchDecks(['hiragana', 'katakana'])
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
watch([tab, level], load, { immediate: true })

function toggle(id: number) {
  const s = new Set(selected.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selected.value = s
}
function toggleGroup(list: Deck[]) {
  const s = new Set(selected.value)
  const all = list.every((d) => s.has(d.id))
  list.forEach((d) => (all ? s.delete(d.id) : s.add(d.id)))
  selected.value = s
}

function start() {
  router.push({
    path: '/practice/session',
    query: {
      decks: [...selected.value].join(','), mode: mode.value, dir: dir.value,
      limit: String(limit.value), shuffle: shuffleOn.value ? '1' : '0',
    },
  })
}
</script>

<template>
  <main class="pr-page">
    <PageTitle jp="練習" vi="Luyện tập" />

    <div class="pr-tabs">
      <button class="pr-chip" :class="{ on: tab === 'vocab' }" @click="tab = 'vocab'">Từ vựng</button>
      <button class="pr-chip" :class="{ on: tab === 'kana' }" @click="tab = 'kana'">Bảng chữ cái</button>
      <button class="pr-chip" disabled title="Sắp có">Hán tự (sắp có)</button>
    </div>

    <div v-if="tab === 'vocab'" class="pr-tabs">
      <button v-for="lv in ['N5', 'N4', 'N3', 'N2', 'N1']" :key="lv" class="pr-chip"
        :class="{ on: level === lv }" @click="level = lv">{{ lv }}</button>
    </div>

    <p v-if="loading" class="small">Đang tải…</p>
    <p v-else-if="error" class="pr-err">{{ error }}</p>
    <p v-else-if="decks.length === 0" class="small">
      Chưa có nội dung cho mục này. Ở local, hãy migrate database rồi chạy
      <code>python -m app.seed_practice</code> để nạp bảng chữ cái và
      <code>python -m app.seed_n5</code> để nạp từ vựng N5.
    </p>

    <section v-for="(g, gi) in groups" :key="gi">
      <div v-if="g.title_jp && g.decks.length" class="pr-group-title">
        <span>{{ g.title_jp }} · {{ g.title_vi }}</span>
        <button class="pr-chip" @click="toggleGroup(g.decks)">Chọn / bỏ chọn tất cả</button>
      </div>
      <div class="pr-grid">
        <label v-for="d in g.decks" :key="d.id" class="pr-deck" :class="{ on: selected.has(d.id) }">
          <input type="checkbox" :checked="selected.has(d.id)" @change="toggle(d.id)" />
          <span class="jp">{{ d.title_jp }}</span>
          <span class="vi">{{ d.title_vi }}</span>
          <span class="count">{{ d.item_count }} mục</span>
        </label>
      </div>
    </section>

    <div class="pr-panel">
      <div class="pr-row">
        <span class="pr-label">Chế độ</span>
        <button v-for="m in MODES" :key="m.id" class="pr-chip" :class="{ on: mode === m.id }" @click="mode = m.id">{{ m.label }}</button>
      </div>
      <div v-if="mode !== 'typing'" class="pr-row">
        <span class="pr-label">{{ mode === 'flashcard' ? 'Mặt trước' : 'Hướng hỏi' }}</span>
        <button v-for="d in dirs" :key="d.id" class="pr-chip" :class="{ on: dir === d.id }" @click="dir = d.id">{{ d.label }}</button>
      </div>
      <p v-else class="small">Hiện chữ Nhật, bạn gõ phiên âm romaji, lần lượt đến hết phạm vi đã chọn.</p>
      <div class="pr-row">
        <span class="pr-label">Số lượng</span>
        <select v-model.number="limit" class="pr-chip">
          <option :value="0">Tất cả</option><option :value="10">10</option><option :value="20">20</option><option :value="50">50</option>
        </select>
        <label class="small"><input v-model="shuffleOn" type="checkbox" /> Trộn ngẫu nhiên</label>
      </div>
      <div class="pr-row">
        <button class="pr-btn" :disabled="selected.size === 0 || selectedCount === 0" @click="start">Bắt đầu</button>
        <span class="small">Đã chọn {{ selected.size }} bộ · {{ selectedCount }} mục</span>
      </div>
    </div>
  </main>
</template>