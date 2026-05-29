<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">Creator Publisher</div>
      <router-link v-for="item in nav" :key="item.path" :to="item.path">{{ item.label }}</router-link>
    </aside>
    <main class="main">
      <slot />
    </main>
  </div>
</template>

<script setup>
const nav = [
  { path: '/dashboard', label: '仪表盘' },
  { path: '/content-editor', label: '内容创作' },
  { path: '/adaptation-center', label: '平台适配' },
  { path: '/preview-center', label: '预览中心' },
  { path: '/publish-center', label: '发布中心' },
  { path: '/publish-history', label: '发布历史' },
  { path: '/settings', label: '系统设置' },
]
</script>
