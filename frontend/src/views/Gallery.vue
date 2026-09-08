<!--
  图库页：瀑布流展示本地图片（src/assets/gallery/ 自动扫描）。
  - 专辑筛选（全部 / 收藏 / 各专辑）、随机一张、收藏、灯箱查看
-->
<template>
  <div class="max-w-5xl mx-auto">
    <!-- 头部卡片 -->
    <div class="glass-card p-6 mb-6">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-2xl font-bold text-ink">🖼 图库</h1>
          <p class="text-xs text-sub mt-1">共 {{ gallery.items.length }} 张 · 已收藏 {{ gallery.favorites.length }} 张</p>
        </div>
        <button class="btn-ghost" :disabled="!visibleItems.length" @click="randomOpen">🎲 随机一张</button>
      </div>

      <!-- 专辑筛选 -->
      <div class="flex flex-wrap gap-2 mt-4">
        <button
          v-for="a in albums"
          :key="a"
          class="chip"
          :class="{ 'chip-active': gallery.currentAlbum === a }"
          @click="setAlbum(a)"
        >{{ a }}</button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!visibleItems.length" class="text-center text-sub py-16">
      <p class="text-3xl mb-2">📭</p>
      <p class="text-sm">
        {{ gallery.currentAlbum === '❤️ 收藏' ? '还没有收藏的图片，点图片上的 🤍 收藏吧' : '这个分类还没有图片' }}
      </p>
    </div>

    <!-- 瀑布流 -->
    <div v-else class="gallery-grid">
      <figure
        v-for="(item, i) in visibleItems"
        :key="item.id"
        class="gallery-item"
        @click="openAt(i)"
      >
        <img :src="item.url" :alt="item.title" loading="lazy" />
        <figcaption class="gallery-cap">
          <span class="gallery-title">{{ item.title }}</span>
          <button
            class="gallery-fav"
            :class="{ 'gallery-fav-on': isFav(item.id) }"
            :aria-label="isFav(item.id) ? '取消收藏' : '收藏'"
            @click.stop="toggleFavorite(item.id)"
          >{{ isFav(item.id) ? '❤️' : '🤍' }}</button>
        </figcaption>
      </figure>
    </div>

    <!-- 灯箱 -->
    <GalleryLightbox
      :items="visibleItems"
      :index="currentIndex"
      :fav="!!currentItem && isFav(currentItem.id)"
      @close="closeLightbox"
      @prev="prevImg"
      @next="nextImg"
      @toggle-favorite="toggleFavorite"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { gallery, albums, visibleItems, initGallery, setAlbum, toggleFavorite, isFavorite } from '../store/gallery'
import GalleryLightbox from '../components/GalleryLightbox.vue'

const currentIndex = ref(null)

const currentItem = computed(() =>
  currentIndex.value === null ? null : visibleItems.value[currentIndex.value],
)

function isFav(id) {
  return isFavorite(id)
}

function openAt(i) {
  currentIndex.value = i
}
function nextImg() {
  const n = visibleItems.value.length
  if (n) currentIndex.value = (currentIndex.value + 1) % n
}
function prevImg() {
  const n = visibleItems.value.length
  if (n) currentIndex.value = (currentIndex.value - 1 + n) % n
}
function closeLightbox() {
  currentIndex.value = null
}
function randomOpen() {
  const n = visibleItems.value.length
  if (!n) return
  currentIndex.value = Math.floor(Math.random() * n)
}

// 切换专辑时关闭灯箱，避免 index 越界
watch(() => gallery.currentAlbum, () => closeLightbox())

onMounted(() => initGallery())
</script>

<style scoped>
@reference "../style.css";

/* 瀑布流：CSS columns 自适应列数 */
.gallery-grid {
  columns: 4 220px;
  column-gap: 1rem;
}
.gallery-item {
  break-inside: avoid;
  margin-bottom: 1rem;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  cursor: zoom-in;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.gallery-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-glow);
  border-color: color-mix(in srgb, var(--c-primary) 45%, transparent);
}
.gallery-item img {
  display: block;
  width: 100%;
  height: auto;
}

.gallery-cap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.45rem 0.7rem;
}
.gallery-title {
  font-size: 0.78rem;
  color: var(--c-sub);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gallery-fav {
  font-size: 0.9rem;
  line-height: 1;
  background: none;
  border: none;
  cursor: pointer;
  filter: grayscale(0.4);
  transition: filter 0.2s, transform 0.2s;
}
.gallery-fav:hover { transform: scale(1.2); }
.gallery-fav-on { filter: none; }
</style>
