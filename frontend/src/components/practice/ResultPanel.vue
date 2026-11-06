<script setup lang="ts">
import { computed } from 'vue'
import type { Mode, Result } from '../../lib/practice'
import PageTitle from '../PageTitle.vue'

const props = defineProps<{ results: Result[]; mode: Mode }>()
defineEmits<{ retryWrong: []; restart: []; back: [] }>()

const flash = computed(() => props.mode === 'flashcard')
const good = computed(() => props.results.filter((r) => r.correct).length)
const bad = computed(() => props.results.filter((r) => !r.correct))
</script>

<template>
  <section>
    <PageTitle jp="結果" vi="Kết quả" />
    <p class="pr-prompt big-text">{{ good }} / {{ results.length }}</p>
    <p class="small pr-center">{{ flash ? 'Đã nhớ' : 'Trả lời đúng' }}: {{ good }} · {{ flash ? 'Chưa nhớ' : 'Cần ôn lại' }}: {{ bad.length }}</p>

    <ul v-if="bad.length" class="small">
      <li v-for="r in bad" :key="r.item.id">
        <b>{{ r.item.term }}</b> — {{ r.item.romaji }}<span v-if="r.item.meaning_vi"> ({{ r.item.meaning_vi }})</span>
        <span v-if="r.given"> · bạn trả lời: {{ r.given }}</span>
      </li>
    </ul>

    <div class="pr-actions">
      <button v-if="bad.length" class="pr-btn" @click="$emit('retryWrong')">Luyện lại {{ bad.length }} mục sai</button>
      <button class="pr-btn ghost" @click="$emit('restart')">Làm lại từ đầu</button>
      <button class="pr-btn ghost" @click="$emit('back')">Chọn nội dung khác</button>
    </div>
  </section>
</template>