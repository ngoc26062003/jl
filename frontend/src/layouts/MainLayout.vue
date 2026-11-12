<template>
  <header class="topbar">
    <RouterLink to="/" class="brand">JL 日本語</RouterLink>
    <nav>
      <RouterLink to="/">Trang chủ</RouterLink>
      <RouterLink to="/alphabet">Bảng chữ cái</RouterLink>
      <RouterLink to="/lessons">Bài học</RouterLink>
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

<style scoped>
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
</style>