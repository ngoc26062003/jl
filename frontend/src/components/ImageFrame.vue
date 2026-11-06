<script setup lang="ts">
defineProps<{
  src?: string      // đường dẫn ảnh, vd '/images/home/hero.jpg'
  alt?: string
  ratio?: string    // vd '16 / 9', '4 / 3', '1 / 1'
  label?: string    // gợi ý nội dung ảnh cần chèn
}>()
</script>

<template>
  <div class="frame" :style="{ aspectRatio: ratio ?? '16 / 9' }">
    <img v-if="src" :src="src" :alt="alt ?? ''" loading="lazy" />
    <div v-else class="ph">
      <span class="ph__icon">＋</span>
      <span>Chèn hình</span>
      <span v-if="label" class="ph__label">{{ label }}</span>
    </div>
  </div>
</template>

<style scoped>
.frame {
  width: 100%;
  overflow: hidden;
  border-radius: 16px;
  border: 3px solid #fff;
  outline: 2px solid var(--pink-deep);
  box-shadow: 0 6px 18px rgba(216, 27, 122, 0.2);
  background: rgba(255, 255, 255, 0.55);
}
.frame img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ph {
  height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 4px;
  border: 2px dashed var(--border);
  color: var(--pink-link);
  font-weight: 600;
  text-align: center;
  padding: 8px;
}
.ph__icon { font-size: 1.8rem; line-height: 1; }
.ph__label { font-weight: 400; font-size: 0.85rem; color: var(--text); }
</style>