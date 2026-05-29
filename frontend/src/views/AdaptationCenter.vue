<template>
  <AppLayout>
    <div class="page-header">
      <h1>平台适配</h1>
      <p>查看系统为不同平台生成的草稿。</p>
    </div>
    <el-empty v-if="!drafts.length" description="暂无平台草稿，请先在内容创作页生成" />
    <div v-else class="draft-grid">
      <el-card v-for="draft in drafts" :key="draft.id">
        <template #header>
          <strong>{{ platformName(draft.platform) }}</strong>
        </template>
        <h3>{{ draft.title }}</h3>
        <p class="muted">{{ draft.summary || '暂无摘要' }}</p>
        <div class="tag-row"><el-tag v-for="tag in draft.tags" :key="tag">{{ tag }}</el-tag></div>
        <el-alert v-for="w in draft.validation_warnings" :key="w" :title="w" type="warning" show-icon :closable="false" />
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { contentApi } from '../api/content'
import { platformName } from '../utils/platform'
import { useContentStore } from '../stores/content'

const store = useContentStore()
const drafts = ref([])

onMounted(async () => {
  store.restoreCurrentContentId()
  if (store.currentContentId) {
    drafts.value = (await contentApi.drafts(store.currentContentId)).data.data || []
    store.drafts = drafts.value
  }
})
</script>
