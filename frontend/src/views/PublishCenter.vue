<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布中心</h1>
      <p>选择多个平台草稿，一键完成模拟发布。</p>
    </div>

    <el-empty v-if="!store.drafts.length" description="暂无可发布草稿，请先生成平台草稿" />
    <template v-else>
      <el-card class="publish-toolbar">
        <div class="toolbar-content">
          <div>
            <strong>待发布草稿：{{ store.drafts.length }} 个</strong>
            <p class="muted">已选择 {{ selectedDraftIds.length }} 个平台草稿</p>
          </div>
          <div class="toolbar-actions">
            <el-button @click="selectAll">全选</el-button>
            <el-button @click="clearSelection">清空</el-button>
            <el-button type="primary" :loading="publishing" @click="simulateBatch">一键模拟发布</el-button>
          </div>
        </div>
      </el-card>

      <el-checkbox-group v-model="selectedDraftIds" class="draft-grid">
        <el-card v-for="draft in store.drafts" :key="draft.id" class="publish-card">
          <div class="card-header">
            <el-checkbox :label="draft.id">{{ draft.platform }}</el-checkbox>
            <el-tag type="success">模拟发布</el-tag>
          </div>
          <h3>{{ draft.title }}</h3>
          <p class="muted">{{ draft.summary || '暂无摘要' }}</p>
          <p class="draft-body">{{ draft.body }}</p>
          <div class="tag-row">
            <el-tag v-for="tag in draft.tags" :key="tag">{{ tag }}</el-tag>
          </div>
        </el-card>
      </el-checkbox-group>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'
import { useContentStore } from '../stores/content'

const router = useRouter()
const store = useContentStore()
const selectedDraftIds = ref([])
const publishing = ref(false)

onMounted(() => {
  selectAll()
})

function selectAll() {
  selectedDraftIds.value = store.drafts.map(draft => draft.id)
}

function clearSelection() {
  selectedDraftIds.value = []
}

async function simulateBatch() {
  if (!selectedDraftIds.value.length) {
    ElMessage.warning('请先选择要发布的平台草稿')
    return
  }

  publishing.value = true
  try {
    const res = await publishApi.simulateBatch(selectedDraftIds.value)
    const results = res.data.data || []
    const failedCount = results.filter(item => item.status === 'failed').length
    if (failedCount) {
      ElMessage.warning(`模拟发布完成，其中 ${failedCount} 个草稿发布失败`)
    } else {
      ElMessage.success('一键模拟发布完成')
    }
    router.push('/publish-history')
  } finally {
    publishing.value = false
  }
}
</script>
