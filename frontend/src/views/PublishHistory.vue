<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布历史</h1>
      <p>查看模拟发布和后续真实发布任务。</p>
    </div>
    <el-table :data="tasks" border>
      <el-table-column label="平台" width="120">
        <template #default="{ row }">
          <span>{{ platformName(row.platform) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column label="模式" width="110">
        <template #default="{ row }">
          <span>{{ modeText(row.mode) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发布链接" min-width="160">
        <template #default="{ row }">
          <span>{{ row.publish_url || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="外部ID" min-width="160">
        <template #default="{ row }">
          <span>{{ row.external_id || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="180">
        <template #default="{ row }">
          <span>{{ formatLocalTime(row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'manual_pending'"
            size="small"
            type="primary"
            @click="confirmManual(row)"
          >
            确认已完成
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'
import { platformName } from '../utils/platform'

const tasks = ref([])
onMounted(loadTasks)

function formatLocalTime(value) {
  if (!value) return '-'
  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const withTimezone = /([zZ]|[+-]\d\d:\d\d)$/.test(normalized) ? normalized : `${normalized}Z`
  const date = new Date(withTimezone)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

async function loadTasks() {
  tasks.value = (await publishApi.tasks()).data.data
}

async function confirmManual(row) {
  try {
    await ElMessageBox.confirm(`确认该 ${platformName(row.platform)} 发布已经在浏览器中完成？`, '确认发布完成', {
      confirmButtonText: '确认完成',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await publishApi.completeManual(row.id, row.publish_url || '')
    ElMessage.success('发布任务已确认完成')
    await loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '确认失败')
    }
  }
}

function statusType(status) {
  if (status === 'simulated' || status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  return 'warning'
}

function statusText(status) {
  const statusMap = {
    simulated: '模拟成功',
    success: '成功',
    failed: '失败',
    pending: '等待中',
    running: '发布中',
    manual_pending: '等待人工完成',
  }
  return statusMap[status] || status
}

function modeText(mode) {
  const modeMap = {
    simulate: '模拟发布',
    browser: '浏览器助手',
    manual: '辅助发布',
    wechat_draft: '公众号草稿',
  }
  return modeMap[mode] || mode
}
</script>
