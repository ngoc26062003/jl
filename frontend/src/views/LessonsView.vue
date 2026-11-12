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
    const page = await fetchLessons({ limit: 100, level: 'N5', lesson_type: 'grammar' })
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
    Chưa có bài học ngữ pháp N5 nào (total = {{ total }}).
  </p>

  <ul v-else class="cards">
    <li v-for="lesson in lessons" :key="lesson.id" class="card">
      <strong>{{ lesson.position }}. {{ lesson.title }}</strong>
      <div v-if="lesson.objective">{{ lesson.objective }}</div>
      <RouterLink :to="`/lessons/${lesson.id}`">Học bài và làm bài tập →</RouterLink>
    </li>
  </ul>
</template>