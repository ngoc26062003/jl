<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchPublicImageSlots, resolveMediaUrl } from '@/api/admin'
import type { PublicImageSlot } from '@/api/admin'
import BilingualTitle from '@/components/BilingualTitle.vue'
import ImageFrame from '@/components/ImageFrame.vue'

const images = ref<Record<string, string>>({})
const imageError = ref('')
const heroImage = () => images.value['home-hero'] ?? ''

const steps = [
  { ja: '文字', vi: 'Chữ cái', desc: 'Làm quen Hiragana và Katakana.' },
  { ja: '文法', vi: 'Ngữ pháp', desc: 'Học cấu trúc câu cơ bản qua từng bài.' },
  { ja: '練習', vi: 'Luyện tập', desc: 'Làm trắc nghiệm, gõ romaji để ghi nhớ.' },
]

const activities = [
  { ja: 'ひらがな', vi: 'Bảng chữ Hiragana', desc: 'Xem ký tự, romaji và nghe phát âm.', to: '/alphabet', slot: 'activity-hiragana', label: 'Ảnh minh họa Hiragana' },
  { ja: 'カタカナ', vi: 'Bảng chữ Katakana', desc: 'Dùng cho từ mượn và tên nước ngoài.', to: '/alphabet', slot: 'activity-katakana', label: 'Ảnh minh họa Katakana' },
  { ja: '文法', vi: 'Bài học ngữ pháp', desc: 'Các bài học sắp xếp theo thứ tự.', to: '/lessons', slot: 'activity-grammar', label: 'Ảnh minh họa bài học' },
  { ja: 'クイズ', vi: 'Trắc nghiệm', desc: 'Kiểm tra nhanh những gì đã học.', to: '/practice', slot: 'activity-quiz', label: 'Ảnh minh họa trắc nghiệm' },
]

onMounted(async () => {
  try {
    const slots: PublicImageSlot[] = await fetchPublicImageSlots()
    images.value = Object.fromEntries(
      slots.filter((slot) => slot.url).map((slot) => [slot.slot, resolveMediaUrl(slot.url!)]),
    )
  } catch (error) {
    imageError.value = error instanceof Error ? error.message : 'Không tải được hình ảnh trang chủ.'
  }
})
</script>

<template>
  <p v-if="imageError" class="error" role="status">{{ imageError }}</p>
  <!-- 1. HERO -->
  <section class="hero">
    <div class="hero__text">
      <BilingualTitle tag="h1" ja="日本語を学ぼう" vi="Cùng học tiếng Nhật" />
      <p class="lead">Bắt đầu với Hiragana, Katakana và ngữ pháp cơ bản, học từng bước và có chỗ để luyện tập.</p>
      <div class="actions">
        <RouterLink to="/alphabet" class="btn btn--primary">Bắt đầu học</RouterLink>
        <RouterLink to="/lessons" class="btn">Xem bài học</RouterLink>
        <RouterLink to="/practice" class="btn">Luyện tập</RouterLink>
      </div>
    </div>
    <ImageFrame :src="heroImage()" ratio="4 / 3" alt="Học tiếng Nhật" label="Ảnh chính trang chủ" />
  </section>

  <!-- 2. LỘ TRÌNH -->
  <section class="section">
    <BilingualTitle ja="学習ロードマップ" vi="Lộ trình học tập" />
    <ol class="steps">
      <li v-for="(s, i) in steps" :key="s.ja" class="step">
        <span class="step__no">{{ i + 1 }}</span>
        <BilingualTitle tag="h3" :ja="s.ja" :vi="s.vi" />
        <p>{{ s.desc }}</p>
      </li>
    </ol>
  </section>

  <!-- 3. HOẠT ĐỘNG -->
  <section class="section">
    <BilingualTitle ja="学習アクティビティ" vi="Hoạt động học tập" />
    <div class="grid">
      <article v-for="a in activities" :key="a.ja" class="act">
        <ImageFrame :src="images[a.slot] ?? ''" ratio="16 / 10" :alt="a.vi" :label="a.label" />
        <BilingualTitle tag="h3" :ja="a.ja" :vi="a.vi" />
        <p>{{ a.desc }}</p>
        <RouterLink v-if="a.to" :to="a.to" class="more">Vào học →</RouterLink>
        <span v-else class="soon">Sắp ra mắt</span>
      </article>
    </div>
  </section>
</template>

<style scoped>
.section { margin-top: 48px; }

.hero {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 32px;
  align-items: center;
}
.lead { font-size: 1.1rem; line-height: 1.6; margin: 0 0 20px; }
.actions { display: flex; gap: 12px; flex-wrap: wrap; }

.btn {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 999px;
  border: 2px solid var(--pink-deep);
  background: #fff;
  color: var(--pink-link);
  font-weight: 700;
}
.btn:hover { text-decoration: none; background: #ffe3f0; }
.btn--primary { background: var(--pink-deep); color: #fff; }
.btn--primary:hover { background: #b0125f; }

.steps {
  list-style: none; padding: 0; margin: 0;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;
}
.step {
  position: relative;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 4px 14px rgba(216, 27, 122, 0.12);
}
.step__no {
  position: absolute; top: -12px; right: 14px;
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--pink-deep); color: #fff; font-weight: 800;
  display: grid; place-items: center;
}
.step p, .act p { margin: 0; line-height: 1.5; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.act {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  display: flex; flex-direction: column; gap: 10px;
  box-shadow: 0 4px 14px rgba(216, 27, 122, 0.12);
}
.act :deep(.bi) { margin: 0; }
.more { font-weight: 700; margin-top: auto; }
.soon { margin-top: auto; font-weight: 600; color: #8a5a73; }

@media (max-width: 720px) {
  .hero { grid-template-columns: 1fr; }
}
</style>