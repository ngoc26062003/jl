<script setup lang="ts">
import { computed } from 'vue'
import { COLUMN_HEADERS, KANA_ROWS, type Script } from '../data/kana'
import { useSpeech } from '../composables/useSpeech'

const props = defineProps<{ script: Script }>()
const { supported, hasJapaneseVoice, playingKey, speak } = useSpeech()

const rows = computed(() =>
  KANA_ROWS.map((row, ri) => ({
    consonant: row.consonant,
    cells: row.romaji.map((romaji, ci) => ({
      key: `${props.script}-${ri}-${ci}`,
      char: row[props.script][ci],
      romaji,
    })),
  })),
)
</script>

<template>
  <div>
    <p v-if="!supported" class="warn">Trình duyệt này không hỗ trợ phát âm.</p>
    <p v-else-if="!hasJapaneseVoice" class="warn">
      Máy chưa có giọng đọc tiếng Nhật. Hãy cài gói ngôn ngữ Nhật (Windows: Cài đặt → Thời gian &amp;
      ngôn ngữ → Ngôn ngữ &amp; khu vực → Thêm ngôn ngữ → 日本語) rồi tải lại trang.
    </p>

    <div class="grid">
      <div class="corner"></div>
      <div v-for="h in COLUMN_HEADERS" :key="h" class="head">{{ h }}</div>

      <template v-for="(row, ri) in rows" :key="ri">
        <div class="head side">{{ row.consonant }}</div>
        <template v-for="c in row.cells" :key="c.key">
          <button
            v-if="c.char && c.romaji"
            class="cell"
            :class="{ playing: playingKey === c.key }"
            :aria-label="`Phát âm ${c.romaji}`"
            @click="speak(c.char, c.key)"
          >
            <span class="char">{{ c.char }}</span>
            <span class="romaji">{{ c.romaji }}</span>
            <svg class="spk" viewBox="0 0 24 24" width="16" height="16" fill="none"
                 stroke="currentColor" stroke-width="2" stroke-linecap="round"
                 stroke-linejoin="round" aria-hidden="true">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
            </svg>
          </button>
          <div v-else class="empty"></div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 2rem repeat(5, minmax(0, 1fr));
  gap: 0.5rem;
  max-width: 560px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b949e;
  font-size: 0.85rem;
  text-transform: uppercase;
}
.cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.6rem 0.25rem 0.5rem;
  background: var(--card, #161b22);
  color: inherit;
  border: 1px solid var(--border, #30363d);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.1s;
}
.cell:hover { border-color: #e5484d; }
.cell:active { transform: scale(0.97); }
.cell.playing { border-color: #e5484d; background: rgba(229, 72, 77, 0.12); }
.char { font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif; font-size: clamp(1.4rem, 4vw, 2rem); line-height: 1.2; }
.romaji { font-size: 0.8rem; color: #8b949e; }
.spk { position: absolute; top: 4px; right: 4px; opacity: 0.55; }
.cell:hover .spk, .cell.playing .spk { opacity: 1; color: #e5484d; }
.warn { padding: 0.6rem 0.8rem; margin-bottom: 1rem; border: 1px solid #9e6a03; border-radius: 6px; background: rgba(158, 106, 3, 0.15); font-size: 0.9rem; }
</style>