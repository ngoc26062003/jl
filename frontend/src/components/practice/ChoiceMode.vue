<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import type { StudyItem } from '../../api/practice'
import { useSpeech } from '../../composables/useSpeech'
import { answerOf, buildChoices, promptOf, type Direction, type Result } from '../../lib/practice'

const props = defineProps<{ items: StudyItem[]; pool: StudyItem[]; dir: Direction }>()
const emit = defineEmits<{ finish: [results: Result[]] }>()

const index = ref(0)
const { supported, playingKey, speak } = useSpeech()
const options = ref<StudyItem[]>([])
const picked = ref<StudyItem | null>(null)
const results: Result[] = []

const current = computed(() => props.items[index.value])
const right = computed(() => answerOf(current.value, props.dir))
const answered = computed(() => picked.value !== null)
const last = computed(() => index.value + 1 >= props.items.length)
const isMeaningQuestion = computed(() => props.dir === 'term_to_meaning')

watch(index, () => (options.value = buildChoices(current.value, props.pool, props.dir)), { immediate: true })

function pick(opt: StudyItem) {
  if (answered.value) return
  picked.value = opt
  const given = answerOf(opt, props.dir)
  results.push({ item: current.value, correct: opt.id === current.value.id, given })
}

function next() {
  if (!answered.value) return
  picked.value = null
  if (last.value) emit('finish', results)
  else index.value++
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    if (answered.value) { e.preventDefault(); next() }
    return
  }
  const n = Number(e.key)
  if (n >= 1 && n <= options.value.length) pick(options.value[n - 1])
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))

function meaningEnglish(item: StudyItem): string {
  const value = item.extra?.meaning_en
  return typeof value === 'string' ? value : ''
}
</script>

<template>
  <section>
    <div class="pr-bar"><span :style="{ width: `${(index / items.length) * 100}%` }"></span></div>
    <p class="small">Câu {{ index + 1 }} / {{ items.length }}</p>
    <template v-if="isMeaningQuestion">
      <div class="pr-prompt big-text vocab-term">{{ current.term }}</div>
      <div class="reading-row">
        <span>{{ current.reading }}</span>
        <button
          v-if="supported"
          class="pr-btn ghost speech-button"
          :class="{ playing: playingKey === String(current.id) }"
          :aria-label="`Nghe cách đọc ${current.term}`"
          @click="speak(current.reading, String(current.id))"
        >🔊 Nghe</button>
      </div>
    </template>
    <div v-else class="pr-prompt big-text">{{ promptOf(current, dir) }}</div>

    <div class="pr-options">
      <button
        v-for="(option, i) in options"
        :key="option.id"
        class="pr-opt"
        :disabled="answered"
        :class="{
          ok: answered && option.id === current.id,
          bad: answered && option.id === picked?.id && option.id !== current.id,
          bilingual: isMeaningQuestion,
        }"
        @click="pick(option)"
      >
        <kbd>{{ i + 1 }}</kbd>
        <span>{{ answerOf(option, dir) }}</span>
        <span v-if="isMeaningQuestion && meaningEnglish(option)" class="meaning-en">
          {{ meaningEnglish(option) }}
        </span>
      </button>
    </div>

    <div v-if="answered" class="pr-fb">
      <p class="small">{{ picked?.id === current.id ? '✅ Chính xác!' : `❌ Đáp án đúng: ${right}` }}</p>
      <button class="pr-btn" @click="next">{{ last ? 'Xem kết quả (Enter)' : 'Câu tiếp (Enter)' }}</button>
    </div>
  </section>
</template>

<style scoped>
.vocab-term {
  margin-bottom: 0.25rem;
}

.reading-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.65rem;
  margin: 0 0 1.5rem;
  color: var(--ink);
  font-size: 1.35rem;
  font-weight: 700;
}

.speech-button {
  padding: 0.35rem 0.75rem;
  font-size: 0.9rem;
}

.speech-button.playing {
  background: var(--pink-soft);
}

.pr-opt.bilingual {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  min-height: 5rem;
}

.meaning-en {
  font-size: 0.9rem;
  font-weight: 400;
  color: #66525e;
}
</style>