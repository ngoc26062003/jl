<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { loginAccount, loginWithGoogle, registerAccount } from '@/api/auth'

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (options: {
            client_id: string
            callback: (response: { credential: string }) => void
            auto_select: false
          }) => void
          renderButton: (
            element: HTMLElement,
            options: { theme: string; size: string; shape: string; width: number },
          ) => void
        }
      }
    }
  }
}

const route = useRoute()
const router = useRouter()
const isRegister = computed(() => route.name === 'register')
const username = ref('')
const email = ref('')
const identifier = ref('')
const password = ref('')
const confirmPassword = ref('')
const busy = ref(false)
const message = ref('')
const googleError = ref('')
const googleButton = ref<HTMLElement | null>(null)
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim() ?? ''

function errorText(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') return detail[0].msg
  }
  return error instanceof Error ? error.message : 'Có lỗi xảy ra. Vui lòng thử lại.'
}

function destination(): string {
  const redirect = route.query.redirect
  return typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
    ? redirect
    : '/'
}

async function submit() {
  message.value = ''
  if (!isRegister.value) {
    if (!identifier.value.trim()) {
      message.value = 'Bạn chưa nhập tên đăng nhập hoặc email.'
      return
    }
    if (!password.value) {
      message.value = 'Bạn chưa nhập mật khẩu.'
      return
    }
  } else {
    if (!username.value.trim()) {
      message.value = 'Bạn chưa nhập tên đăng nhập.'
      return
    }
    if (!email.value.trim()) {
      message.value = 'Bạn chưa nhập email.'
      return
    }
    if (!password.value) {
      message.value = 'Bạn chưa nhập mật khẩu.'
      return
    }
    if (password.value.length < 8) {
      message.value = 'Mật khẩu cần có ít nhất 8 ký tự.'
      return
    }
    if (password.value !== confirmPassword.value) {
      message.value = 'Mật khẩu xác nhận chưa trùng khớp.'
      return
    }
  }

  busy.value = true
  try {
    if (isRegister.value) {
      await registerAccount({
        username: username.value.trim(),
        email: email.value.trim(),
        password: password.value,
      })
    } else {
      await loginAccount(identifier.value.trim(), password.value)
    }
    await router.replace(destination())
  } catch (error) {
    message.value = errorText(error)
  } finally {
    busy.value = false
  }
}

async function handleGoogleCredential(credential: string) {
  message.value = ''
  busy.value = true
  try {
    await loginWithGoogle(credential)
    await router.replace(destination())
  } catch (error) {
    message.value = errorText(error)
  } finally {
    busy.value = false
  }
}

function initializeGoogleButton() {
  if (!googleClientId || !googleButton.value || !window.google) return
  googleButton.value.replaceChildren()
  window.google.accounts.id.initialize({
    client_id: googleClientId,
    callback: ({ credential }) => void handleGoogleCredential(credential),
    auto_select: false,
  })
  window.google.accounts.id.renderButton(googleButton.value, {
    theme: 'outline',
    size: 'large',
    shape: 'pill',
    width: 320,
  })
}

onMounted(() => {
  if (!googleClientId || window.google) {
    initializeGoogleButton()
    return
  }
  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  script.onload = initializeGoogleButton
  script.onerror = () => {
    googleError.value = 'Không tải được dịch vụ đăng nhập Google.'
  }
  document.head.append(script)
})
</script>

<template>
  <main class="auth-page card">
    <h1>{{ isRegister ? 'Tạo tài khoản' : 'Đăng nhập' }}</h1>
    <p v-if="isRegister" class="auth-note">Tài khoản mới mặc định chỉ có quyền học viên.</p>

    <form class="auth-form" @submit.prevent="submit">
      <label v-if="isRegister">
        Tên đăng nhập
        <input v-model="username" autocomplete="username" minlength="3" maxlength="32" />
      </label>
      <label v-if="isRegister">
        Email
        <input v-model="email" type="email" autocomplete="email" />
      </label>
      <label v-else>
        Tên đăng nhập hoặc email
        <input v-model="identifier" autocomplete="username" />
      </label>
      <label>
        Mật khẩu
        <input
          v-model="password"
          type="password"
          :autocomplete="isRegister ? 'new-password' : 'current-password'"
        />
      </label>
      <label v-if="isRegister">
        Nhập lại mật khẩu
        <input v-model="confirmPassword" type="password" autocomplete="new-password" />
      </label>
      <p v-if="message" class="error" role="alert">{{ message }}</p>
      <button class="auth-submit" type="submit" :disabled="busy">
        {{ busy ? 'Đang xử lý…' : isRegister ? 'Đăng ký' : 'Đăng nhập' }}
      </button>
    </form>

    <div class="auth-divider"><span>hoặc</span></div>
    <div v-if="googleClientId" ref="googleButton" class="google-button"></div>
    <p v-else class="auth-note">Đăng nhập Google chưa được cấu hình.</p>
    <p v-if="googleError" class="error" role="alert">{{ googleError }}</p>

    <p class="auth-switch">
      <template v-if="isRegister">Đã có tài khoản? <RouterLink to="/login">Đăng nhập</RouterLink></template>
      <template v-else>Chưa có tài khoản? <RouterLink to="/register">Đăng ký</RouterLink></template>
    </p>
  </main>
</template>

<style scoped>
.auth-page {
  width: min(100%, 460px);
  margin: 2rem auto;
}

.auth-page h1 {
  margin-top: 0;
  text-align: center;
}

.auth-note,
.auth-switch {
  text-align: center;
}

.auth-form,
.auth-form label {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.auth-form {
  gap: 1rem;
}

.auth-form input {
  width: 100%;
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 0.6rem;
  font: inherit;
}

.auth-submit {
  padding: 0.75rem 1rem;
  color: #fff;
  background: var(--pink-deep);
  border: 0;
  border-radius: 0.6rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.auth-submit:disabled {
  opacity: 0.6;
}

.auth-divider {
  margin: 1.3rem 0;
  text-align: center;
  border-bottom: 1px solid var(--border);
  line-height: 0.1rem;
}

.auth-divider span {
  padding: 0 0.6rem;
  background: var(--card);
}

.google-button {
  display: flex;
  justify-content: center;
  min-height: 42px;
}
</style>
