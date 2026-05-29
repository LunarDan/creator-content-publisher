<template>
  <AppLayout>
    <div class="page-header">
      <h1>预览中心</h1>
      <p>以卡片方式预览各平台草稿效果。</p>
    </div>
    <el-empty v-if="!store.drafts.length" description="暂无预览内容" />
    <div v-else class="preview-grid">
      <el-card v-for="draft in store.drafts" :key="draft.id" class="preview-card">
        <div class="platform-pill">{{ draft.platform }}</div>
        <h2>{{ draft.title }}</h2>
        <p class="preview-body">{{ draft.body }}</p>
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '../components/AppLayout.vue'
import { useContentStore } from '../stores/content'

const store = useContentStore()
</script>
