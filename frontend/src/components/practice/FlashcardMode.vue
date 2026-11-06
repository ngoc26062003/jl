<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import type { StudyItem } from '../../api/practice'
import { useSpeech } from '../../composables/useSpeech'
import type { Direction, Result } from '../../lib/practice'

const props = defineProps<{ items: StudyItem[]; dir: Direction }>()
const emit = defineEmits<{ finish: [results: Result[]] }>()

const { speak } = useSpeech()
const index = ref(0)
const flipped = ref(false)
const results: Result[] = []

const current = computed(() => props.items[index.value])
const reverse = computed(() => props.dir === 'romaji_to_term') // mặt trước là phiên âm/nghĩa

function mark(known: boolean) {
  ;(document.activeElement as HTMLElement | null)?.blur()
  results.push({ item: current.value, correct: known })
  flipped.value = false
  if (index.value + 1 >= props.items.length) emit('finish', results)
  else index.value++
}

function onKey(e: KeyboardEvent) {
  if (e.key === ' ') { e.preventDefault(); flipped.value = !flipped.value }
  else if (e.key === 'ArrowRight') mark(true)
  else if (e.key === 'ArrowLeft') mark(false)
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <section>
    <div class="pr-bar"><span :style="{ width: `${(index / items.length) * 100}%` }"></span></div>
    <p class="small">Thẻ {{ index + 1 }} / {{ items.length }}</p>

    <div class="pr-card" @click="flipped = !flipped">
      <template v-if="!flipped">
        <div v-if="!reverse" class="pr-prompt big-text">{{ current.term }}</div>
        <template v-else>
          <div class="pr-prompt big-text">{{ current.romaji }}</div>
          <p v-if="current.meaning_vi" class="small">{{ current.meaning_vi }}</p>
        </template>
        <p class="small">Nhấn để lật (Space)</p>
      </template>
      <template v-else>
        <div class="pr-prompt big-text">{{ current.term }}</div>
        <p v-if="current.reading !== current.term" class="small">{{ current.reading }}</p>
        <p class="small"><b>{{ current.romaji }}</b></p>
        <p v-if="current.meaning_vi" class="small">{{ current.meaning_vi }}</p>
        <button class="pr-btn ghost" @click.stop="speak(current.reading, String(current.id))">🔊 Nghe</button>
      </template>
    </div>

    <div class="pr-actions">
      <button class="pr-btn ghost" @click="mark(false)">← Chưa nhớ</button>
      <button class="pr-btn" @click="mark(true)">Đã nhớ →</button>
    </div>
  </section>
</template>