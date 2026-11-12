<template>
  <header class="topbar">
    <RouterLink to="/" class="brand" aria-label="Nagoyaka - Trang chủ">
      <img class="brand-logo" src="/Nagoyaka.webp" alt="Nagoyaka" />
    </RouterLink>
    <nav>
      <RouterLink to="/">Trang chủ</RouterLink>
      <template v-if="authState.user">
        <RouterLink to="/alphabet">Bảng chữ cái</RouterLink>
        <RouterLink to="/lessons">Bài học</RouterLink>
        <RouterLink to="/practice">Luyện tập</RouterLink>
        <RouterLink v-if="authState.user.role === 'admin'" to="/admin">Quản trị</RouterLink>
        <span class="user-summary">
          {{ authState.user.username }} · {{ authState.user.current_streak }} ngày · {{ authState.user.total_stars }} sao
        </span>
        <button class="auth-link" @click="logout">Đăng xuất</button>
      </template>
      <template v-else>
        <RouterLink to="/login">Đăng nhập</RouterLink>
        <RouterLink to="/register">Đăng ký</RouterLink>
      </template>
    </nav>
  </header>
  <main class="container">
    <RouterView />
  </main>
  <footer class="data-attribution">
    Từ vựng N5 từ
    <a href="https://github.com/evanclan/OpenJLPT" target="_blank" rel="noreferrer">OpenJLPT 0.3.0</a>
    (<a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a>),
    dựa trên danh sách JLPT cộng đồng của Jonathan Waller và JMdict (EDRDG).
    Cấp độ N5 là ước tính không chính thức; nghĩa tiếng Việt được dịch máy từ tiếng Anh.
  </footer>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { authState } from '@/auth/session'
import { logoutAccount } from '@/api/auth'

const router = useRouter()

function logout() {
  logoutAccount()
  void router.replace('/')
}
</script>

<style scoped>
.brand {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  -webkit-text-stroke: 0;
  text-shadow: none;
}

.brand-logo {
  display: block;
  width: clamp(120px, 18vw, 190px);
  height: 64px;
  object-fit: contain;
}

.data-attribution {
  max-width: 960px;
  margin: 0 auto;
  padding: 1rem;
  color: #777;
  font-size: 0.8rem;
  line-height: 1.5;
  text-align: center;
}

.data-attribution a {
  color: inherit;
}

.user-summary {
  font-size: 0.8rem;
  white-space: nowrap;
}

.auth-link {
  padding: 0;
  color: var(--pink-link);
  background: transparent;
  border: 0;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 520px) {
  .brand-logo {
    width: 100px;
    height: 48px;
  }

  .topbar {
    gap: 12px;
    padding-inline: 12px;
  }

  .topbar nav {
    gap: 10px;
    font-size: 0.875rem;
    flex-wrap: wrap;
    justify-content: flex-end;
  }
}
</style>