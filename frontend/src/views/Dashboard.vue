<template>
  <AppLayout>
    <div class="page-header">
      <h1>创作者多平台内容发布助手</h1>
      <p>从一份内容开始，生成多平台草稿、预览并模拟发布。</p>
    </div>

    <div class="dashboard-actions">
      <el-button type="primary" @click="router.push('/content-editor')">新建内容</el-button>
      <el-button @click="router.push('/publish-center')">发布中心</el-button>
      <el-button @click="router.push('/publish-history')">发布历史</el-button>
      <el-button :loading="loading" @click="loadDashboard">刷新数据</el-button>
    </div>

    <div class="stats-grid" v-loading="loading">
      <el-card><div class="stat-num">{{ contents.length }}</div><div>内容总数</div></el-card>
      <el-card><div class="stat-num">{{ platforms.length }}</div><div>适配平台</div></el-card>
      <el-card><div class="stat-num">{{ tasks.length }}</div><div>发布任务</div></el-card>
      <el-card><div class="stat-num">{{ simulatedCount }}</div><div>模拟成功</div></el-card>
    </div>

    <el-card class="content-card">
      <template #header>
        <div class="card-header">
          <strong>最近内容</strong>
          <span class="muted">管理已创建内容，快速进入预览或发布流程</span>
        </div>
      </template>

      <el-empty v-if="!contents.length" description="暂无内容，请先新建一篇内容" />
      <el-table v-else :data="contents" border>
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column label="摘要" min-width="220">
          <template #default="{ row }">
            <span>{{ row.summary || '暂无摘要' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="180">
          <template #default="{ row }">
            <div class="tag-row">
              <el-tag v-for="tag in row.tags" :key="tag" size="small">{{ tag }}</el-tag>
              <span v-if="!row.tags?.length" class="muted">无标签</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDrafts(row, '/preview-center')">预览</el-button>
            <el-button size="small" type="primary" @click="openDrafts(row, '/publish-center')">发布</el-button>
            <el-button size="small" type="danger" @click="deleteContent(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { contentApi } from '../api/content'
import { platformApi } from '../api/platform'
import { publishApi } from '../api/publish'
import { useContentStore } from '../stores/content'

const router = useRouter()
const store = useContentStore()
const loading = ref(false)
const contents = ref([])
const platforms = ref([])
const tasks = ref([])

const simulatedCount = computed(() => tasks.value.filter(task => ['simulated', 'success'].includes(task.status)).length)

onMounted(() => {
  loadDashboard()
})

async function loadDashboard() {
  loading.value = true
  try {
    const [contentRes, platformRes, taskRes] = await Promise.all([
      contentApi.list(),
      platformApi.list(),
      publishApi.tasks(),
    ])
    contents.value = contentRes.data.data || []
    platforms.value = platformRes.data.data || []
    tasks.value = taskRes.data.data || []
    store.contents = contents.value
  } finally {
    loading.value = false
  }
}

async function openDrafts(content, path) {
  store.currentContentId = content.id
  const res = await contentApi.drafts(content.id)
  store.drafts = res.data.data || []
  router.push(path)
}

async function deleteContent(content) {
  try {
    await ElMessageBox.confirm(
      `确定要删除「${content.title}」吗？删除后该内容不会再出现在首页列表中。`,
      '删除内容',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
    await contentApi.delete(content.id)
    if (store.currentContentId === content.id) {
      store.currentContentId = null
      store.drafts = []
    }
    ElMessage.success('内容已删除')
    await loadDashboard()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}
</script>
