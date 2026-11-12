<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { checkAnswer, fetchQuiz, type CheckResult, type QuizMode, type Question } from '../api/quiz'

const route = useRoute()
const lessonId = Number(route.params.id)
const mode = ref<QuizMode>((route.query.mode as QuizMode) === 'typing' ? 'typing' : 'choice')

const questions = ref<Question[]>([])
const index = ref(0)
const typed = ref('')
const feedback = ref<CheckResult | null>(null)
const picked = ref<string | null>(null)
const wrong = ref<{ char: string; correct: string; given: string }[]>([])
const score = ref(0)
const loading = ref(true)
const error = ref('')
const inputEl = ref<HTMLInputElement | null>(null)

const current = computed(() => questions.value[index.value])
const finished = computed(() => !loading.value && index.value >= questions.value.length)

async function start() {
  loading.value = true; error.value = ''
  index.value = 0; score.value = 0; wrong.value = []; feedback.value = null; typed.value = ''
  try {
    questions.value = await fetchQuiz(lessonId, mode.value)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
    await nextTick(); inputEl.value?.focus()
  }
}

async function submit(answer: string) {
  if (feedback.value || !answer.trim()) return
  picked.value = answer
  try {
    feedback.value = await checkAnswer(current.value.character_id, answer)
  } catch (e) {
    error.value = (e as Error).message
    return
  }
  if (feedback.value.correct) score.value++
  else wrong.value.push({ char: current.value.char, correct: feedback.value.correct_answer, given: answer })
}

async function next() {
  feedback.value = null; picked.value = null; typed.value = ''
  index.value++
  await nextTick(); inputEl.value?.focus()
}

onMounted(start)
</script>

<template>
  <main class="quiz">
    <h1>Kiểm tra – {{ mode === 'choice' ? 'Trắc nghiệm' : 'Nhập phiên âm' }}</h1>
    <p v-if="loading">Đang tải…</p>
    <p v-else-if="error" class="err">{{ error }}</p>

    <section v-else-if="finished">
      <h2>Kết quả: {{ score }} / {{ questions.length }}</h2>
      <ul v-if="wrong.length">
        <li v-for="(w, i) in wrong" :key="i">
          <span class="jp">{{ w.char }}</span> đúng là <b>{{ w.correct }}</b> (bạn chọn: {{ w.given }})
        </li>
      </ul>
      <button @click="start">Làm lại</button>
      <router-link to="/lessons"> Về danh sách bài</router-link>
    </section>

    <section v-else-if="current">
      <p>Câu {{ index + 1 }} / {{ questions.length }}</p>
      <div class="jp big">{{ current.char }}</div>

      <div v-if="mode === 'choice'" class="options">
        <button
          v-for="o in current.options"
          :key="o"
          :disabled="!!feedback"
          :class="{
            ok: feedback && o === feedback.correct_answer,
            bad: feedback && o === picked && !feedback.correct,
          }"
          @click="submit(o)"
        >{{ o }}</button>
      </div>

      <form v-else @submit.prevent="submit(typed)">
        <input
          ref="inputEl" v-model="typed" :disabled="!!feedback"
          autocomplete="off" autocapitalize="off" spellcheck="false"
          placeholder="Gõ phiên âm, ví dụ: ka"
        />
        <button type="submit" :disabled="!!feedback">Kiểm tra</button>
      </form>

      <div v-if="feedback" class="fb">
        <p v-if="feedback.correct">Chính xác!</p>
        <p v-else>Đáp án đúng: <b>{{ feedback.correct_answer }}</b></p>
        <button autofocus @click="next">
          {{ index + 1 < questions.length ? 'Câu tiếp' : 'Xem kết quả' }}
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.jp { font-family: 'Avo', 'Noto Sans JP', sans-serif; }
.big { font-size: 6rem; text-align: center; margin: 1rem 0; }
.options { display: grid; grid-template-columns: repeat(2, 1fr); gap: .75rem; }
.ok { outline: 2px solid #3fb950; }
.bad { outline: 2px solid #f85149; }
.err { color: #f85149; }
</style>