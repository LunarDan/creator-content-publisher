<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">
          <el-icon><EditPen /></el-icon>
        </div>
        <span>Creator Publisher</span>
      </div>

      <div class="sidebar-section-label">核心功能</div>

      <router-link v-for="item in mainNav" :key="item.path" :to="item.path">
        <span class="sidebar-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </span>
        <span>{{ item.label }}</span>
      </router-link>

      <div class="sidebar-divider" />

      <div class="sidebar-section-label">管理</div>

      <router-link v-for="item in secondaryNav" :key="item.path" :to="item.path">
        <span class="sidebar-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </span>
        <span>{{ item.label }}</span>
      </router-link>

      <div class="sidebar-footer">
        <router-link to="/settings">
          <span class="sidebar-icon">
            <el-icon><Setting /></el-icon>
          </span>
          <span>系统设置</span>
        </router-link>
      </div>
    </aside>

    <main class="main">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { EditPen, DataBoard, Document, Connection, View, Promotion, Clock, Setting } from '@element-plus/icons-vue'

const mainNav = [
  { path: '/dashboard', label: '仪表盘', icon: DataBoard },
  { path: '/content-editor', label: '内容创作', icon: EditPen },
  { path: '/adaptation-center', label: '平台适配', icon: Connection },
  { path: '/preview-center', label: '预览中心', icon: View },
  { path: '/publish-center', label: '发布中心', icon: Promotion },
]

const secondaryNav = [
  { path: '/publish-history', label: '发布历史', icon: Clock },
]
</script>
