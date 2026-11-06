<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import type { StudyItem } from '../../api/practice'
import { answerOf, buildChoices, promptOf, type Direction, type Result } from '../../lib/practice'

const props = defineProps<{ items: StudyItem[]; pool: StudyItem[]; dir: Direction }>()
const emit = defineEmits<{ finish: [results: Result[]] }>()

const index = ref(0)
const options = ref<string[]>([])
const picked = ref<string | null>(null)
const results: Result[] = []

const current = computed(() => props.items[index.value])
const right = computed(() => answerOf(current.value, props.dir))
const answered = computed(() => picked.value !== null)
const last = computed(() => index.value + 1 >= props.items.length)

watch(index, () => (options.value = buildChoices(current.value, props.pool, props.dir)), { immediate: true })

function pick(opt: string) {
  if (answered.value) return
  picked.value = opt
  results.push({ item: current.value, correct: opt === right.value, given: opt })
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
</script>

<template>
  <section>
    <div class="pr-bar"><span :style="{ width: `${(index / items.length) * 100}%` }"></span></div>
    <p class="small">Câu {{ index + 1 }} / {{ items.length }}</p>
    <div class="pr-prompt big-text">{{ promptOf(current, dir) }}</div>

    <div class="pr-options">
      <button v-for="(o, i) in options" :key="o" class="pr-opt" :disabled="answered"
        :class="{ ok: answered && o === right, bad: answered && o === picked && o !== right }" @click="pick(o)">
        <kbd>{{ i + 1 }}</kbd>{{ o }}
      </button>
    </div>

    <div v-if="answered" class="pr-fb">
      <p class="small">{{ picked === right ? '✅ Chính xác!' : `❌ Đáp án đúng: ${right}` }}</p>
      <button class="pr-btn" @click="next">{{ last ? 'Xem kết quả (Enter)' : 'Câu tiếp (Enter)' }}</button>
    </div>
  </section>
</template>