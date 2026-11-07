<script setup lang="ts">
withDefaults(
  defineProps<{
    ja: string
    vi: string
    tag?: 'h1' | 'h2' | 'h3'
    align?: 'left' | 'center'
  }>(),
  { tag: 'h2', align: 'left' },
)

</script>

<template>
  <div class="bi" :class="[`bi--${tag}`, `bi--${align}`]">
    <component :is="tag" class="bi__ja">{{ ja }}</component>
    <p class="bi__vi">{{ vi }}</p>
  </div>
</template>

<style scoped>
.bi { --size: 2rem; margin: 0 0 14px; }
.bi--h1 { --size: 3rem; }
.bi--h3 { --size: 1.6rem; }
.bi--center { text-align: center; }

.bi__ja {
  margin: 0;
  font-size: var(--size);
  line-height: 1.2;
  text-transform: uppercase;
}
.bi--h3 .bi__ja { -webkit-text-stroke: 1.5px var(--pink-deep); } /* chữ nhỏ hơn nên viền mỏng hơn */

.bi__vi {
  margin: 4px 0 0;
  font-size: calc(var(--size) / 2);   /* đúng 1/2 cỡ tiêu đề */
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--pink-link);
  -webkit-text-stroke: 0;
  text-shadow: none;
}
</style>