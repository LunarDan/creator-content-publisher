<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布历史</h1>
      <p>查看模拟发布和后续真实发布任务。</p>
    </div>
    <el-table :data="tasks" border>
      <el-table-column prop="platform" label="平台" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="mode" label="模式" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="created_at" label="创建时间" />
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
</script>
