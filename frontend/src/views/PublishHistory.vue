<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布历史</h1>
      <p>查看模拟发布和后续真实发布任务。</p>
    </div>
    <el-table :data="tasks" border>
      <el-table-column prop="platform" label="平台" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="mode" label="模式" width="110" />
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
      <el-table-column prop="created_at" label="创建时间" min-width="160" />
      <el-table-column label="完成时间" min-width="160">
        <template #default="{ row }">
          <span>{{ row.finished_at || '-' }}</span>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'

const tasks = ref([])
onMounted(async () => {
  tasks.value = (await publishApi.tasks()).data.data
})

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
  }
  return statusMap[status] || status
}
</script>
