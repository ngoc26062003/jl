<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import type { StudyItem } from '../../api/practice'
import { isRomajiCorrect, type Result } from '../../lib/practice'

const props = defineProps<{ items: StudyItem[] }>()
const emit = defineEmits<{ finish: [results: Result[]] }>()

const index = ref(0)
const input = ref('')
const verdict = ref<boolean | null>(null) // null = đang nhập
const inputEl = ref<HTMLInputElement | null>(null)
const results: Result[] = []
let timer: ReturnType<typeof setTimeout> | undefined

const current = computed(() => props.items[index.value])

function onSubmit() {
  if (verdict.value === null) check()
  else next()
}

function check() {
  if (!input.value.trim()) return
  const ok = isRomajiCorrect(current.value, input.value)
  verdict.value = ok
  results.push({ item: current.value, correct: ok, given: input.value.trim() })
  if (ok) timer = setTimeout(next, 500) // đúng thì tự sang chữ tiếp theo cho liền mạch
}

function next() {
  clearTimeout(timer)
  if (verdict.value === null) return
  input.value = ''
  verdict.value = null
  if (index.value + 1 >= props.items.length) {
    emit('finish', results)
    return
  }
  index.value++
  nextTick(() => inputEl.value?.focus())
}

onMounted(() => inputEl.value?.focus())
onUnmounted(() => clearTimeout(timer))
</script>

<template>
  <section class="pr-center">
    <div class="pr-bar"><span :style="{ width: `${(index / items.length) * 100}%` }"></span></div>
    <p class="small">{{ index + 1 }} / {{ items.length }}</p>
    <div class="pr-prompt big-text">{{ current.term }}</div>
    <p v-if="current.meaning_vi" class="small">{{ current.meaning_vi }}</p>

    <form @submit.prevent="onSubmit">
      <input ref="inputEl" v-model="input" class="pr-input"
        :class="{ ok: verdict === true, bad: verdict === false }" :readonly="verdict !== null"
        autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Gõ romaji rồi nhấn Enter" />
    </form>

    <div class="pr-fb">
      <p v-if="verdict === true" class="small">✅ Chính xác!</p>
      <template v-else-if="verdict === false">
        <p class="small">❌ Đáp án đúng: <b>{{ current.romaji }}</b></p>
        <p class="small">Nhấn Enter để tiếp tục</p>
      </template>
    </div>
  </section>
</template>