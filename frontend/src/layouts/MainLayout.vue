<template>
  <header class="topbar">
    <RouterLink to="/" class="brand">JL 日本語</RouterLink>
    <nav>
      <RouterLink to="/">Trang chủ</RouterLink>
      <RouterLink to="/lessons">Bài học</RouterLink>
    </nav>
  </header>
  <main class="container">
    <RouterView />
  </main>
</template>