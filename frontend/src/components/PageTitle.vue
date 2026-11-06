<script setup lang="ts">
defineProps<{ jp: string; vi: string }>()
</script>

<template>
  <header class="title">
    <h1 class="jp">{{ jp }}</h1>
    <p class="vi">{{ vi }}</p>
  </header>
</template>

<style scoped>
.title { margin: 0.5rem 0 1.5rem; }
.jp, .vi {
  margin: 0; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em;
  color: #fff; paint-order: stroke fill; text-shadow: 3px 3px 0 rgba(90, 90, 90, 0.4);
  font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif;
}
.jp { font-size: 2.75rem; line-height: 1.1; -webkit-text-stroke: 7px #c2185b; }
.vi { font-size: 1.375rem; margin-top: 0.35rem; -webkit-text-stroke: 4px #c2185b; }
</style>