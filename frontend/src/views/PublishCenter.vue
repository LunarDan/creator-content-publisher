<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布中心</h1>
      <p>当前版本支持模拟发布，真实发布将在平台 Publisher 稳定后接入。</p>
    </div>
    <el-empty v-if="!store.drafts.length" description="暂无可发布草稿" />
    <div v-else class="draft-grid">
      <el-card v-for="draft in store.drafts" :key="draft.id">
        <h3>{{ draft.title }}</h3>
        <p>{{ draft.platform }}</p>
        <el-button type="primary" @click="simulate(draft.id)">模拟发布</el-button>
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'
import { useContentStore } from '../stores/content'

const store = useContentStore()

async function simulate(draftId) {
  await publishApi.simulate(draftId)
  ElMessage.success('模拟发布成功')
}
</script>
