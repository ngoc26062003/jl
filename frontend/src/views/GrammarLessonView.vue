<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  fetchGrammarLesson,
  fetchGrammarQuestions,
  submitGrammarAnswer,
  type GrammarAnswer,
  type GrammarLesson,
  type GrammarQuestion,
} from '@/api/grammar'

const route = useRoute()
const lessonId = String(route.params.id)

const lesson = ref<GrammarLesson | null>(null)
const questions = ref<GrammarQuestion[]>([])
const currentIndex = ref(0)
const selectedOptionId = ref<string | null>(null)
const answer = ref<GrammarAnswer | null>(null)
const score = ref(0)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

const currentQuestion = computed(() => questions.value[currentIndex.value])
const finished = computed(
  () => !loading.value && questions.value.length > 0 && currentIndex.value >= questions.value.length,
)

onMounted(async () => {
  try {
    const [lessonData, questionData] = await Promise.all([
      fetchGrammarLesson(lessonId),
      fetchGrammarQuestions(lessonId),
    ])
    lesson.value = lessonData
    questions.value = questionData
    if (questionData.length === 0) error.value = 'Bài học chưa có câu hỏi luyện tập.'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Không tải được bài học'
  } finally {
    loading.value = false
  }
})

async function checkAnswer(optionId: string) {
  if (submitting.value || answer.value || !currentQuestion.value) return
  selectedOptionId.value = optionId
  submitting.value = true
  error.value = ''
  try {
    answer.value = await submitGrammarAnswer(lessonId, currentQuestion.value.id, optionId)
    if (answer.value.correct) score.value++
  } catch (e) {
    selectedOptionId.value = null
    error.value = e instanceof Error ? e.message : 'Không chấm được câu trả lời'
  } finally {
    submitting.value = false
  }
}

function nextQuestion() {
  currentIndex.value++
  answer.value = null
  selectedOptionId.value = null
  error.value = ''
}

function restartQuiz() {
  currentIndex.value = 0
  selectedOptionId.value = null
  answer.value = null
  score.value = 0
  error.value = ''
}
</script>

<template>
  <main class="grammar-page">
    <RouterLink to="/lessons" class="back-link">← Danh sách bài học</RouterLink>

    <p v-if="loading">Đang tải bài học…</p>
    <p v-else-if="error && !lesson" class="error">Lỗi: {{ error }}</p>

    <template v-else-if="lesson">
      <header class="grammar-heading">
        <p class="grammar-level">{{ lesson.level }} · BÀI {{ lesson.position }}</p>
        <h1>{{ lesson.title }}</h1>
        <p v-if="lesson.objective" class="objective">{{ lesson.objective }}</p>
      </header>

      <section v-if="lesson.content" class="grammar-content card">
        <h2>Cách dùng</h2>
        <p class="grammar-summary">{{ lesson.content.summary }}</p>
        <ul class="usage-list">
          <li v-for="(item, index) in lesson.content.usage" :key="index">{{ item }}</li>
        </ul>

        <h2>Ví dụ thực tế</h2>
        <article
          v-for="(example, index) in lesson.content.examples"
          :key="index"
          class="grammar-example"
        >
          <p class="example-japanese">{{ example.japanese }}</p>
          <p class="example-reading">{{ example.reading }}</p>
          <p class="example-meaning">{{ example.meaning }}</p>
        </article>
      </section>

      <section v-if="questions.length" class="exercise-section card">
        <template v-if="finished">
          <h2>Hoàn thành bài luyện tập</h2>
          <p class="quiz-score">Bạn trả lời đúng {{ score }} / {{ questions.length }} câu.</p>
          <div class="exercise-actions">
            <button class="primary-button" @click="restartQuiz">Làm lại</button>
            <RouterLink class="secondary-button" to="/lessons">Chọn bài khác</RouterLink>
          </div>
        </template>

        <template v-else-if="currentQuestion">
          <h2>Luyện tập: chọn trợ từ phù hợp</h2>
          <p class="question-progress">Câu {{ currentIndex + 1 }} / {{ questions.length }}</p>
          <p class="question-sentence">{{ currentQuestion.prompt.sentence }}</p>
          <p class="question-translation">{{ currentQuestion.prompt.translation }}</p>

          <div class="answer-options">
            <button
              v-for="option in currentQuestion.options"
              :key="option.id"
              class="answer-option"
              :class="{
                correct: answer && option.text === answer.correct_answer,
                incorrect: answer && option.id === selectedOptionId && !answer.correct,
              }"
              :disabled="!!answer || submitting"
              @click="checkAnswer(option.id)"
            >
              {{ option.text }}
            </button>
          </div>

          <div v-if="answer" class="answer-feedback" :class="{ good: answer.correct, bad: !answer.correct }">
            <p>{{ answer.correct ? 'Chính xác!' : `Chưa đúng. Đáp án là「${answer.correct_answer}」.` }}</p>
            <p v-if="answer.explanation">{{ answer.explanation }}</p>
            <button class="primary-button" @click="nextQuestion">
              {{ currentIndex + 1 < questions.length ? 'Câu tiếp theo' : 'Xem kết quả' }}
            </button>
          </div>
          <p v-if="error" class="error">{{ error }}</p>
        </template>
      </section>
    </template>
  </main>
</template>

<style scoped>
.grammar-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 1rem 0 3rem;
}

.back-link {
  display: inline-block;
  margin-bottom: 1rem;
}

.grammar-heading {
  margin-bottom: 1.5rem;
}

.grammar-heading h1 {
  margin: 0.3rem 0;
  font-size: clamp(1.7rem, 5vw, 2.4rem);
}

.grammar-level,
.question-progress {
  color: #8b315b;
  font-size: 0.85rem;
  font-weight: 700;
}

.objective,
.grammar-summary,
.usage-list,
.grammar-example,
.exercise-section {
  line-height: 1.75;
}

.grammar-content,
.exercise-section {
  margin: 1rem 0;
}

.grammar-content h2,
.exercise-section h2 {
  margin-top: 0;
  font-size: 1.3rem;
}

.grammar-content h2:not(:first-child) {
  margin-top: 1.75rem;
}

.usage-list {
  padding-left: 1.4rem;
}

.usage-list li + li {
  margin-top: 0.6rem;
}

.grammar-example {
  padding: 0.8rem 1rem;
  border-left: 3px solid var(--pink-deep);
  background: rgba(255, 255, 255, 0.65);
}

.grammar-example + .grammar-example {
  margin-top: 0.75rem;
}

.grammar-example p {
  margin: 0.15rem 0;
}

.example-japanese,
.question-sentence {
  font-family: "Avo", "Noto Sans JP", "Yu Gothic", sans-serif;
  font-size: 1.25rem;
}

.example-reading,
.question-translation {
  color: #66525e;
}

.question-sentence {
  margin: 1rem 0 0.25rem;
  font-size: clamp(1.5rem, 5vw, 2rem);
  text-align: center;
}

.question-translation {
  margin: 0 0 1rem;
  text-align: center;
}

.answer-options,
.exercise-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
}

.answer-option,
.primary-button,
.secondary-button {
  padding: 0.65rem 1.25rem;
  border: 1px solid var(--border);
  border-radius: 0.65rem;
  background: #fff;
  color: var(--text);
  cursor: pointer;
  font: inherit;
}

.answer-option {
  min-width: 4.5rem;
  font-family: "Avo", "Noto Sans JP", sans-serif;
  font-size: 1.2rem;
}

.answer-option:hover:not(:disabled) {
  border-color: var(--pink-deep);
}

.answer-option.correct {
  border-color: #278449;
  background: #e7f6ec;
}

.answer-option.incorrect {
  border-color: #c62828;
  background: #fdeaea;
}

.answer-option:disabled {
  cursor: default;
}

.answer-feedback,
.quiz-score {
  margin-top: 1rem;
  text-align: center;
}

.answer-feedback.good {
  color: #176f38;
}

.answer-feedback.bad,
.error {
  color: #b42332;
}

.primary-button {
  border-color: var(--pink-deep);
  background: var(--pink-deep);
  color: white;
  font-weight: 700;
}

.secondary-button {
  text-decoration: none;
}
</style>
