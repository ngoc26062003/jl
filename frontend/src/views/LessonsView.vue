<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchLessons } from '@/api/lessons'
import type { Lesson } from '@/types/api'

const lessons = ref<Lesson[]>([])
const total = ref(0)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const page = await fetchLessons({ limit: 20 })
    lessons.value = page.items
    total.value = page.total
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Không tải được dữ liệu'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <h1>Bài học</h1>

  <p v-if="loading">Đang tải...</p>
  <p v-else-if="error" class="error">Lỗi: {{ error }}</p>
  <p v-else-if="lessons.length === 0">
    Kết nối backend và database thành công, nhưng chưa có bài học nào (total = {{ total }}).
  </p>

  <ul v-else class="cards">
    <li v-for="lesson in lessons" :key="lesson.id" class="card">
      <strong>{{ lesson.position }}. {{ lesson.title }}</strong>
      <span> ({{ lesson.lesson_type }}<template v-if="lesson.level">, {{ lesson.level }}</template>)</span>
      <div v-if="lesson.objective">{{ lesson.objective }}</div>
    </li>
  </ul>
</template>