<template>
  <AppLayout>
    <div class="page-header">
      <h1>平台适配</h1>
      <p>查看系统为不同平台生成的草稿。每个平台会根据其特点调整标题、正文风格和标签。</p>
    </div>
    <el-empty v-if="!drafts.length" description="暂无平台草稿，请先在内容创作页生成">
      <el-button type="primary" @click="router.push('/content-editor')">
        <el-icon style="margin-right:6px"><EditPen /></el-icon> 前往内容创作
      </el-button>
    </el-empty>
    <div v-else class="draft-grid">
      <el-card v-for="draft in drafts" :key="draft.id" class="adapt-card">
        <template #header>
          <div class="card-header">
            <span class="platform-pill">{{ platformName(draft.platform) }}</span>
            <el-tag
              size="small"
              :type="draft.platform === 'wechat_official' ? 'success' : draft.platform === 'zhihu' ? '' : 'primary'"
              effect="light"
              round
            >
              {{ draft.platform === 'wechat_official' ? '长文' : draft.platform === 'zhihu' ? '理性分析' : draft.platform === 'bilibili' ? '视频' : draft.platform === 'xiaohongshu' ? '种草' : draft.platform === 'douyin' ? '短视频' : '短视频' }}
            </el-tag>
          </div>
        </template>
        <h3>{{ draft.title }}</h3>
        <p class="muted">{{ draft.summary || '暂无摘要' }}</p>
        <div class="tag-row">
          <el-tag v-for="tag in draft.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
        </div>
        <div class="adapt-card-actions">
          <el-button size="small" type="primary" plain @click="goPreview(draft)">预览编辑</el-button>
        </div>
        <el-alert
          v-for="(w, idx) in draft.validation_warnings"
          :key="idx"
          :title="w"
          type="warning"
          show-icon
          :closable="false"
          style="margin-top:12px"
        />
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { EditPen } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'
import { contentApi } from '../api/content'
import { platformName } from '../utils/platform'
import { useContentStore } from '../stores/content'

const router = useRouter()
const store = useContentStore()
const drafts = ref([])

onMounted(async () => {
  store.restoreCurrentContentId()
  if (store.currentContentId) {
    drafts.value = (await contentApi.drafts(store.currentContentId)).data.data || []
    store.drafts = drafts.value
  }
})

function goPreview(draft) {
  store.setCurrentContentId(draft.content_id)
  store.drafts = drafts.value
  router.push('/preview-center')
}
</script>

<style scoped>
.adapt-card {
  transition: all var(--transition-base);
}

.adapt-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md) !important;
}

.adapt-card h3 {
  font-size: var(--text-lg);
  margin: 0 0 var(--space-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.adapt-card-actions {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border-light);
}
</style>
