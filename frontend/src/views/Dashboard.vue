<template>
  <AppLayout>
    <div class="page-header">
      <h1>创作者多平台内容发布助手</h1>
      <p>从一份内容开始，生成多平台草稿、预览并模拟发布。</p>
    </div>

    <div class="dashboard-actions">
      <el-button type="primary" size="large" @click="router.push('/content-editor')">
        <el-icon style="margin-right:6px"><Plus /></el-icon> 新建内容
      </el-button>
      <el-button size="large" @click="router.push('/publish-center')">
        <el-icon style="margin-right:6px"><Promotion /></el-icon> 发布中心
      </el-button>
      <el-button size="large" @click="router.push('/publish-history')">
        <el-icon style="margin-right:6px"><Clock /></el-icon> 发布历史
      </el-button>
      <el-button size="large" :loading="loading" @click="loadDashboard">
        <el-icon style="margin-right:6px"><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <div class="stats-grid" v-loading="loading">
      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon blue">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-num">{{ contents.length }}</div>
          <div class="stat-label">内容总数</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon green">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-num">{{ platforms.length }}</div>
          <div class="stat-label">适配平台</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon amber">
            <el-icon><Promotion /></el-icon>
          </div>
          <div class="stat-num">{{ tasks.length }}</div>
          <div class="stat-label">发布任务</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon red">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <div class="stat-num">{{ simulatedCount }}</div>
          <div class="stat-label">发布成功</div>
        </div>
      </el-card>
    </div>

    <el-card class="content-card">
      <template #header>
        <div class="card-header">
          <strong>最近内容</strong>
          <span class="muted">管理已创建内容，快速进入预览或发布流程</span>
        </div>
      </template>

      <el-empty v-if="!contents.length" description="暂无内容，请先新建一篇内容">
        <el-button type="primary" @click="router.push('/content-editor')">前往内容创作</el-button>
      </el-empty>

      <el-table v-else :data="contents" border style="width:100%">
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="摘要" min-width="240">
          <template #default="{ row }">
            <span class="muted">{{ row.summary || '暂无摘要' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="200">
          <template #default="{ row }">
            <div class="tag-row">
              <el-tag v-for="tag in row.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
              <span v-if="!row.tags?.length" class="muted">无标签</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="170" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDrafts(row, '/preview-center')">
              <el-icon style="margin-right:4px"><View /></el-icon> 预览
            </el-button>
            <el-button size="small" type="primary" @click="openDrafts(row, '/publish-center')">
              <el-icon style="margin-right:4px"><Promotion /></el-icon> 发布
            </el-button>
            <el-button size="small" type="danger" plain @click="deleteContent(row)">
              <el-icon style="margin-right:4px"><Delete /></el-icon>
            </el-button>
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
import { Plus, Promotion, Clock, Refresh, Document, Connection, View, Delete, CircleCheckFilled } from '@element-plus/icons-vue'
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
  store.setCurrentContentId(content.id)
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
      store.clearCurrentContent()
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
