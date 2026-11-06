<script setup lang="ts">
import { ref } from 'vue'
import KanaTable from '../components/KanaTable.vue'
import type { Script } from '../data/kana'

const level = ref<'basic' | 'advanced'>('basic')
const script = ref<Script>('hiragana')
</script>

<template>
  <main class="page">
    <h1>BẢNG CHỮ CÁI</h1>

    <div class="tabs" role="tablist">
      <button role="tab" :aria-selected="level === 'basic'" :class="{ on: level === 'basic' }" @click="level = 'basic'">Cơ bản</button>
      <button role="tab" :aria-selected="level === 'advanced'" :class="{ on: level === 'advanced' }" @click="level = 'advanced'">Nâng cao</button>
    </div>

    <section v-if="level === 'basic'">
      <div class="tabs small" role="tablist">
        <button role="tab" :aria-selected="script === 'hiragana'" :class="{ on: script === 'hiragana' }" @click="script = 'hiragana'">Hiragana ひらがな</button>
        <button role="tab" :aria-selected="script === 'katakana'" :class="{ on: script === 'katakana' }" @click="script = 'katakana'">Katakana カタカナ</button>
      </div>
      <KanaTable :script="script" :key="script" />
    </section>

    <section v-else class="soon">
      <p>Phần nâng cao đang được phát triển, sẽ có trong thời gian tới.</p>
    </section>
  </main>
</template>

<style scoped>
.page { max-width: 1140px; margin: 0 auto; padding: 2rem 1rem; }
.tabs { display: flex; gap: 0.5rem; margin: 1rem 0; }
.tabs button {
  padding: 0.5rem 1rem; background: transparent; color: inherit;
  border: 1px solid var(--border, #30363d); border-radius: 999px; cursor: pointer;
}
.tabs button.on { background: #e5484d; border-color: #e5484d; color: #fff; }
.tabs.small button { font-size: 0.9rem; padding: 0.35rem 0.8rem; }
.soon { padding: 2rem; border: 1px dashed var(--border, #30363d); border-radius: 8px; color: #8b949e; }
</style>