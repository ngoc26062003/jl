<script setup lang="ts">
import axios from 'axios'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  changePassword,
  fetchMyAvatar,
  fetchPracticeHistory,
  fetchPracticeSummary,
  logoutAccount,
  updateMyAvatar,
  type PracticeHistory,
  type PracticeSummary,
} from '@/api/auth'
import { authState } from '@/auth/session'

const router = useRouter()
const root = ref<HTMLElement | null>(null)
const avatarInput = ref<HTMLInputElement | null>(null)
const open = ref(false)
const history = ref<PracticeHistory | null>(null)
const summary = ref<PracticeSummary | null>(null)
const loading = ref(false)
const busyAvatar = ref(false)
const busyPassword = ref(false)
const error = ref('')
const notice = ref('')
const avatarUrl = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const username = computed(() => authState.user?.username || authState.user?.email || 'Học viên')
const initials = computed(() => username.value.slice(0, 1).toLocaleUpperCase())
const activeDays = computed(() => new Set(history.value?.practice_days ?? []))
const chartRuns = computed(() => [...(history.value?.runs ?? [])].reverse())
const chartPoints = computed(() =>
  chartRuns.value
    .map((run, index) => {
      const score = run.total_questions ? run.correct_count / run.total_questions : 0
      return `${chartRuns.value.length < 2 ? 150 : 10 + (index * 280) / (chartRuns.value.length - 1)},${90 - score * 78}`
    })
    .join(' '),
)

function dateKey(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const calendarCells = computed(() => {
  const today = new Date()
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 34)
  const leadingDays = (start.getDay() + 6) % 7
  const cells: Array<{ key: string; date: Date | null }> = Array.from(
    { length: leadingDays },
    (_, index) => ({ key: `blank-${index}`, date: null }),
  )
  for (let index = 0; index < 35; index += 1) {
    const date = new Date(start.getFullYear(), start.getMonth(), start.getDate() + index)
    cells.push({ key: dateKey(date), date })
  }
  return cells
})

function errorText(errorValue: unknown): string {
  if (axios.isAxiosError(errorValue)) {
    const detail = errorValue.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') return detail[0].msg
  }
  return errorValue instanceof Error ? errorValue.message : 'Có lỗi xảy ra. Vui lòng thử lại.'
}

function revokeAvatarUrl() {
  if (avatarUrl.value) URL.revokeObjectURL(avatarUrl.value)
  avatarUrl.value = ''
}

async function loadAvatar() {
  try {
    const blob = await fetchMyAvatar()
    revokeAvatarUrl()
    avatarUrl.value = URL.createObjectURL(blob)
  } catch (reason) {
    if (!axios.isAxiosError(reason) || reason.response?.status !== 404) {
      error.value = errorText(reason)
    }
  }
}

async function loadActivity() {
  loading.value = true
  error.value = ''
  try {
    const [activity, totals] = await Promise.all([fetchPracticeHistory(), fetchPracticeSummary()])
    history.value = activity
    summary.value = totals
  } catch (reason) {
    error.value = errorText(reason)
  } finally {
    loading.value = false
  }
}

function toggleMenu() {
  open.value = !open.value
  notice.value = ''
  error.value = ''
  if (open.value) {
    void loadActivity()
    void loadAvatar()
  }
}

function closeMenu() {
  open.value = false
}

function handleOutsideClick(event: MouseEvent) {
  if (event.target instanceof Node && !root.value?.contains(event.target)) closeMenu()
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape') closeMenu()
}

function chooseAvatar() {
  avatarInput.value?.click()
}

async function onAvatarSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    error.value = 'Chỉ chọn ảnh JPEG, PNG hoặc WebP.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Ảnh tải lên tối đa 5 MB.'
    return
  }
  busyAvatar.value = true
  error.value = ''
  notice.value = ''
  try {
    await updateMyAvatar(file)
    revokeAvatarUrl()
    avatarUrl.value = URL.createObjectURL(file)
    notice.value = 'Đã cập nhật ảnh đại diện.'
  } catch (reason) {
    error.value = errorText(reason)
  } finally {
    busyAvatar.value = false
  }
}

async function submitPassword() {
  error.value = ''
  notice.value = ''
  if (!currentPassword.value) {
    error.value = 'Vui lòng nhập mật khẩu hiện tại.'
    return
  }
  if (newPassword.value.length < 8) {
    error.value = 'Mật khẩu mới cần có ít nhất 8 ký tự.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Mật khẩu xác nhận chưa trùng khớp.'
    return
  }
  busyPassword.value = true
  try {
    await changePassword(currentPassword.value, newPassword.value)
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    notice.value = 'Đã đổi mật khẩu.'
  } catch (reason) {
    error.value = errorText(reason)
  } finally {
    busyPassword.value = false
  }
}

function logout() {
  logoutAccount()
  closeMenu()
  void router.replace('/')
}

function score(run: { correct_count: number; total_questions: number }): number {
  return run.total_questions ? Math.round((run.correct_count / run.total_questions) * 100) : 0
}

function modeLabel(mode: string): string {
  return mode === 'flashcard' ? 'Thẻ ghi nhớ' : mode === 'typing' ? 'Gõ đáp án' : 'Trắc nghiệm'
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
}

watch(
  () => authState.user?.id,
  () => {
    history.value = null
    summary.value = null
    revokeAvatarUrl()
  },
)

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  document.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleEscape)
  revokeAvatarUrl()
})
</script>

<template>
  <div ref="root" class="profile-menu">
    <button
      class="profile-trigger"
      type="button"
      :aria-expanded="open"
      aria-label="Mở hồ sơ tài khoản"
      @click.stop="toggleMenu"
    >
      <img v-if="avatarUrl" :src="avatarUrl" alt="" class="trigger-avatar" />
      <span v-else class="trigger-initial">{{ initials }}</span>
    </button>

    <section v-if="open" class="profile-popover" aria-label="Hồ sơ và hoạt động">
      <div class="popover-heading">
        <div>
          <strong>Hồ sơ của tôi</strong>
          <span>{{ username }}</span>
        </div>
        <button class="close-button" type="button" aria-label="Đóng" @click="closeMenu">×</button>
      </div>

      <p v-if="error" class="profile-error" role="alert">{{ error }}</p>
      <p v-if="notice" class="profile-notice" role="status">{{ notice }}</p>

      <section class="profile-section">
        <div class="identity-row">
          <div class="large-avatar">
            <img v-if="avatarUrl" :src="avatarUrl" alt="Ảnh đại diện" />
            <span v-else>{{ initials }}</span>
          </div>
          <div class="identity-details">
            <strong>{{ username }}</strong>
            <span>{{ authState.user?.email }}</span>
            <span class="role-badge">{{ authState.user?.role === 'admin' ? 'Quản trị viên' : 'Học viên' }}</span>
          </div>
        </div>
        <input
          ref="avatarInput"
          class="visually-hidden"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          @change="onAvatarSelected"
        />
        <button class="secondary-button" type="button" :disabled="busyAvatar" @click="chooseAvatar">
          {{ busyAvatar ? 'Đang tải ảnh…' : 'Thay đổi ảnh đại diện' }}
        </button>
      </section>

      <section class="profile-section">
        <h3>Luyện tập</h3>
        <p v-if="loading">Đang tải lịch sử…</p>
        <template v-else-if="summary && history">
          <div class="activity-stats">
            <span><b>{{ summary.total_runs }}</b> lượt luyện</span>
            <span><b>{{ summary.current_streak }}</b> ngày streak</span>
            <span><b>{{ summary.total_stars }}</b> sao</span>
          </div>
          <div class="chart-heading">
            <strong>Diễn tiến điểm</strong>
            <small>Điểm đúng theo từng lượt gần đây</small>
          </div>
          <div v-if="chartRuns.length" class="chart-wrap">
            <svg viewBox="0 0 300 100" role="img" aria-label="Biểu đồ tỷ lệ trả lời đúng">
              <line x1="10" y1="12" x2="290" y2="12" class="chart-grid" />
              <line x1="10" y1="51" x2="290" y2="51" class="chart-grid" />
              <line x1="10" y1="90" x2="290" y2="90" class="chart-grid" />
              <polyline :points="chartPoints" class="chart-line" />
              <circle
                v-for="(run, index) in chartRuns"
                :key="run.id"
                :cx="chartRuns.length < 2 ? 150 : 10 + (index * 280) / (chartRuns.length - 1)"
                :cy="90 - (score(run) / 100) * 78"
                r="3"
                class="chart-dot"
              />
            </svg>
            <div class="chart-axis"><span>0%</span><span>100%</span></div>
          </div>
          <p v-else class="muted">Chưa có lượt luyện được lưu.</p>

          <strong class="calendar-title">Ngày đã luyện trong 35 ngày gần đây</strong>
          <div class="calendar-weekdays" aria-hidden="true">
            <span>T2</span><span>T3</span><span>T4</span><span>T5</span><span>T6</span><span>T7</span><span>CN</span>
          </div>
          <div class="streak-calendar" aria-label="Lịch luyện tập 35 ngày">
            <span v-for="cell in calendarCells" :key="cell.key" class="calendar-cell">
              <span
                v-if="cell.date"
                class="day-dot"
                :class="{
                  practiced: activeDays.has(cell.key),
                  today: cell.key === dateKey(new Date()),
                }"
                :title="`${cell.key}${activeDays.has(cell.key) ? ' · Đã luyện tập' : ''}`"
                :aria-label="`${cell.key}${activeDays.has(cell.key) ? ', đã luyện tập' : ', chưa luyện tập'}`"
              >{{ cell.date.getDate() }}</span>
            </span>
          </div>

          <strong class="history-title">Lịch sử gần đây</strong>
          <p v-if="!history.runs.length" class="muted">Chưa có lịch sử luyện tập.</p>
          <ol v-else class="history-list">
            <li v-for="run in history.runs.slice(0, 8)" :key="run.id">
              <span><b>{{ modeLabel(run.mode) }}</b><small>{{ formatDate(run.created_at) }}</small></span>
              <strong>{{ score(run) }}%<small>{{ run.correct_count }}/{{ run.total_questions }} đúng</small></strong>
            </li>
          </ol>
        </template>
      </section>

      <section class="profile-section password-section">
        <h3>Đổi mật khẩu</h3>
        <p class="muted">Tài khoản chỉ đăng nhập bằng Google chưa có mật khẩu để đổi.</p>
        <form @submit.prevent="submitPassword">
          <label>Mật khẩu hiện tại<input v-model="currentPassword" type="password" autocomplete="current-password" /></label>
          <label>Mật khẩu mới<input v-model="newPassword" type="password" minlength="8" autocomplete="new-password" /></label>
          <label>Nhập lại mật khẩu mới<input v-model="confirmPassword" type="password" minlength="8" autocomplete="new-password" /></label>
          <button class="secondary-button" type="submit" :disabled="busyPassword">
            {{ busyPassword ? 'Đang cập nhật…' : 'Cập nhật mật khẩu' }}
          </button>
        </form>
      </section>

      <RouterLink v-if="authState.user?.role === 'admin'" class="admin-link" to="/admin" @click="closeMenu">
        Mở trang quản trị
      </RouterLink>
      <button class="logout-button" type="button" @click="logout">Đăng xuất</button>
    </section>
  </div>
</template>

<style scoped>
.profile-menu { position: relative; flex: 0 0 auto; }
.profile-trigger, .large-avatar {
  display: grid;
  place-items: center;
  overflow: hidden;
  padding: 0;
  border: 2px solid var(--pink-deep);
  border-radius: 50%;
  color: #fff;
  background: #e85a9e;
  font-weight: 700;
}
.profile-trigger { width: 44px; height: 44px; cursor: pointer; }
.trigger-avatar, .large-avatar img { width: 100%; height: 100%; object-fit: cover; }
.trigger-initial { font-size: 1.15rem; }
.profile-popover {
  position: absolute;
  z-index: 20;
  top: calc(100% + 10px);
  right: 0;
  display: grid;
  gap: 0.8rem;
  width: min(390px, calc(100vw - 24px));
  max-height: min(78vh, 760px);
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: #fffafd;
  box-shadow: 0 12px 36px #541b3930;
  color: var(--text);
}
.popover-heading { display: flex; justify-content: space-between; align-items: flex-start; }
.popover-heading > div, .identity-details { display: grid; gap: 0.2rem; }
.popover-heading > div > strong { color: var(--pink-link); font-size: 1.05rem; }
.popover-heading span, .identity-details span { overflow-wrap: anywhere; font-size: 0.84rem; }
.close-button { border: 0; background: transparent; color: var(--text); font-size: 1.4rem; cursor: pointer; }
.profile-section { display: grid; gap: 0.65rem; padding-top: 0.75rem; border-top: 1px solid #f5c2d8; }
.profile-section h3 { margin: 0; color: var(--pink-link); font-size: 0.98rem; }
.identity-row { display: flex; align-items: center; gap: 0.7rem; }
.large-avatar { flex: 0 0 58px; width: 58px; height: 58px; font-size: 1.5rem; }
.identity-details { min-width: 0; }
.identity-details > strong { overflow-wrap: anywhere; }
.role-badge { width: max-content; padding: 0.1rem 0.45rem; border-radius: 999px; background: #ffe3f0; color: var(--pink-link); }
.secondary-button, .logout-button {
  width: 100%;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--pink-deep);
  border-radius: 9px;
  color: var(--pink-link);
  background: white;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.secondary-button:disabled { opacity: 0.6; cursor: wait; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%); }
.activity-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem; text-align: center; }
.activity-stats span { display: grid; gap: 0.1rem; padding: 0.4rem 0.15rem; border-radius: 8px; background: #fff0f7; font-size: 0.75rem; }
.activity-stats b { color: var(--pink-link); font-size: 1rem; }
.chart-heading { display: grid; gap: 0.1rem; }
.chart-heading small, .history-list small { display: block; color: #806477; font-size: 0.72rem; }
.chart-wrap { padding: 0.3rem 0.2rem 0; }
.chart-wrap svg { display: block; width: 100%; height: 105px; overflow: visible; }
.chart-grid { stroke: #f1d8e4; stroke-width: 1; }
.chart-line { fill: none; stroke: var(--pink-deep); stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
.chart-dot { fill: white; stroke: var(--pink-deep); stroke-width: 2; }
.chart-axis { display: flex; justify-content: space-between; color: #806477; font-size: 0.7rem; }
.calendar-title, .history-title { margin-top: 0.2rem; }
.calendar-weekdays, .streak-calendar { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 0.3rem; text-align: center; }
.calendar-weekdays { color: #806477; font-size: 0.68rem; }
.calendar-cell { display: grid; place-items: center; min-height: 31px; }
.day-dot { display: grid; place-items: center; width: 28px; height: 28px; border-radius: 50%; color: #947889; background: #f8eef3; font-size: 0.69rem; }
.day-dot.practiced { color: #fff; background: var(--pink-deep); box-shadow: 0 0 0 3px #ffd0e4; }
.day-dot.today { outline: 2px solid #71234c; outline-offset: 2px; }
.history-list { display: grid; gap: 0.35rem; max-height: 190px; overflow: auto; margin: 0; padding: 0; list-style: none; }
.history-list li { display: flex; justify-content: space-between; gap: 0.7rem; padding: 0.45rem 0.55rem; border-radius: 8px; background: #fff0f7; font-size: 0.78rem; }
.history-list li > span, .history-list li > strong { display: grid; gap: 0.1rem; }
.history-list li > strong { text-align: right; color: var(--pink-link); }
.password-section form, .password-section label { display: grid; gap: 0.4rem; }
.password-section form { gap: 0.6rem; }
.password-section label { font-size: 0.78rem; font-weight: 600; }
.password-section input { width: 100%; padding: 0.55rem; border: 1px solid var(--border); border-radius: 8px; font: inherit; }
.muted { margin: 0; color: #806477; font-size: 0.78rem; line-height: 1.4; }
.profile-error, .profile-notice { margin: 0; padding: 0.5rem; border-radius: 8px; font-size: 0.8rem; }
.profile-error { color: #a20d2b; background: #fff0f0; }
.profile-notice { color: #17653a; background: #eaf8ef; }
.admin-link { display: block; padding: 0.6rem; border-radius: 9px; background: #fff0f7; text-align: center; font-weight: 700; }
.logout-button { color: #a20d2b; border-color: #e5a1ad; }
</style>
