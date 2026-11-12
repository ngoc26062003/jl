<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'
import {
  fetchAdminDashboard,
  fetchImageSlots,
  replaceImage,
  resolveMediaUrl,
  updateUserRole,
  type AdminDashboard,
  type ImageSlot,
} from '@/api/admin'
import { authState } from '@/auth/session'

const dashboard = ref<AdminDashboard | null>(null)
const images = ref<ImageSlot[]>([])
const loading = ref(true)
const busySlot = ref('')
const selectedSlot = ref<ImageSlot | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const failedPreviews = ref(new Set<string>())
const error = ref('')
const message = ref('')

function getError(errorValue: unknown): string {
  if (axios.isAxiosError(errorValue) && typeof errorValue.response?.data?.detail === 'string') {
    return errorValue.response.data.detail
  }
  return errorValue instanceof Error ? errorValue.message : 'Có lỗi xảy ra.'
}

async function load() {
  loading.value = true
  error.value = ''
  const [statsResult, slotsResult] = await Promise.allSettled([
    fetchAdminDashboard(),
    fetchImageSlots(),
  ])
  if (statsResult.status === 'fulfilled') dashboard.value = statsResult.value
  else error.value = `Không tải được thống kê: ${getError(statsResult.reason)}`
  if (slotsResult.status === 'fulfilled') images.value = slotsResult.value
  else error.value = [error.value, `Không tải được danh sách ảnh: ${getError(slotsResult.reason)}`]
    .filter(Boolean)
    .join(' ')
  loading.value = false
}

async function toggleRole(userId: string, currentRole: 'learner' | 'admin') {
  message.value = ''
  error.value = ''
  try {
    await updateUserRole(userId, currentRole === 'admin' ? 'learner' : 'admin')
    message.value = 'Đã cập nhật quyền tài khoản.'
    await load()
  } catch (reason) {
    error.value = getError(reason)
  }
}

function chooseImage(slot: ImageSlot) {
  selectedSlot.value = slot
  fileInput.value?.click()
}

function previewFailed(slot: string) {
  failedPreviews.value = new Set(failedPreviews.value).add(slot)
}

async function uploadImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  const slot = selectedSlot.value
  selectedSlot.value = null
  if (!file || !slot) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    error.value = 'Chỉ chọn ảnh JPEG, PNG hoặc WebP.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Ảnh tải lên tối đa 5 MB.'
    return
  }
  busySlot.value = slot.slot
  error.value = ''
  message.value = ''
  try {
    const updated = await replaceImage(slot.slot, file)
    images.value = images.value.map((image) => image.slot === slot.slot ? updated : image)
    failedPreviews.value.delete(slot.slot)
    message.value = `Đã thay ảnh: ${slot.label}.`
  } catch (reason) {
    error.value = getError(reason)
  } finally {
    busySlot.value = ''
  }
}

onMounted(load)
</script>

<template>
  <main class="admin-page">
    <h1>Quản trị hệ thống</h1>
    <p v-if="loading">Đang tải dữ liệu…</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="message" class="success" role="status">{{ message }}</p>

    <template v-if="dashboard">
      <section class="summary-grid">
        <article class="card"><strong>{{ dashboard.total_users }}</strong><span>Tài khoản</span></article>
        <article class="card"><strong>{{ dashboard.active_learners }}</strong><span>Người đã luyện tập</span></article>
        <article class="card"><strong>{{ dashboard.total_runs }}</strong><span>Lượt luyện tập</span></article>
      </section>

      <section class="card">
        <h2>Top câu đúng nhiều</h2>
        <p v-if="dashboard.most_correct.length === 0">Chưa có lượt luyện tập.</p>
        <ol v-else>
          <li v-for="item in dashboard.most_correct" :key="item.id">
            <b>{{ item.term }}</b> ({{ item.reading }}) — {{ item.correct }} đúng / {{ item.attempts }} lượt
            <span v-if="item.meaning_vi"> · {{ item.meaning_vi }}</span>
          </li>
        </ol>
      </section>

      <section class="card">
        <h2>Top câu sai nhiều</h2>
        <p v-if="dashboard.most_incorrect.length === 0">Chưa có lượt luyện tập.</p>
        <ol v-else>
          <li v-for="item in dashboard.most_incorrect" :key="item.id">
            <b>{{ item.term }}</b> ({{ item.reading }}) — {{ item.incorrect }} sai / {{ item.attempts }} lượt
            <span v-if="item.meaning_vi"> · {{ item.meaning_vi }}</span>
          </li>
        </ol>
      </section>

      <section class="card">
        <h2>Người dùng điểm cao</h2>
        <p v-if="dashboard.leaderboard.length === 0">Chưa có dữ liệu.</p>
        <ol v-else>
          <li v-for="person in dashboard.leaderboard" :key="person.id">
            <b>{{ person.username || person.email }}</b>
            — {{ person.correct_answers }} câu đúng · {{ person.total_stars }} sao · chuỗi {{ person.current_streak }} ngày
          </li>
        </ol>
      </section>

      <section class="card">
        <h2>Tài khoản và quyền</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Tên</th><th>Email</th><th>Vai trò</th><th>Sao</th><th>Chuỗi</th><th>Thao tác</th></tr></thead>
            <tbody>
              <tr v-for="person in dashboard.users" :key="person.id">
                <td>{{ person.username || '—' }}</td>
                <td>{{ person.email }}</td>
                <td>{{ person.role }}</td>
                <td>{{ person.total_stars }}</td>
                <td>{{ person.current_streak }}</td>
                <td>
                  <button
                    v-if="person.id !== authState.user?.id"
                    class="role-button"
                    @click="toggleRole(person.id, person.role)"
                  >{{ person.role === 'admin' ? 'Hạ quyền' : 'Cấp admin' }}</button>
                  <span v-else>Đang đăng nhập</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </template>

    <section v-if="images.length" class="card">
      <h2>Hình ảnh trang chủ</h2>
      <p>Chọn ảnh mới để thay thế; ảnh sẽ được kiểm tra và lưu trên máy chủ.</p>
      <div class="image-grid">
        <article v-for="slot in images" :key="slot.slot" class="image-card">
          <strong>{{ slot.label }}</strong>
          <img
            v-if="slot.updated_at && !failedPreviews.has(slot.slot)"
            :key="slot.updated_at"
            :src="resolveMediaUrl(slot.url)"
            :alt="slot.label"
            @error="previewFailed(slot.slot)"
          />
          <div v-else class="image-placeholder">{{ slot.updated_at ? 'Không tải được ảnh xem trước' : 'Chưa có ảnh' }}</div>
          <button
            class="role-button"
            type="button"
            :disabled="!!busySlot"
            @click="chooseImage(slot)"
          >{{ busySlot === slot.slot ? 'Đang tải…' : 'Chọn ảnh thay thế' }}</button>
        </article>
      </div>
      <input
        ref="fileInput"
        class="file-input"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        :disabled="!!busySlot"
        @change="uploadImage"
      />
    </section>
  </main>
</template>

<style scoped>
.admin-page { display: grid; gap: 1rem; }
.admin-page h1, .admin-page h2 { margin-top: 0; }
.summary-grid, .image-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.8rem; }
.summary-grid article { display: flex; flex-direction: column; align-items: center; gap: 0.3rem; }
.summary-grid strong { font-size: 1.8rem; color: var(--pink-deep); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.55rem; border-bottom: 1px solid var(--border); text-align: left; }
.role-button { display: inline-block; padding: 0.4rem 0.65rem; background: #fff; border: 1px solid var(--pink-deep); border-radius: 0.5rem; color: var(--pink-link); cursor: pointer; font: inherit; }
.role-button:disabled { opacity: 0.6; cursor: wait; }
.file-input { display: none; }
.image-card { display: flex; flex-direction: column; gap: 0.6rem; }
.image-card img, .image-placeholder { width: 100%; aspect-ratio: 16 / 10; object-fit: cover; border-radius: 0.6rem; background: #fff3f8; }
.image-placeholder { display: grid; place-items: center; color: var(--text); }
.success { color: #16743d; font-weight: 700; }
</style>
