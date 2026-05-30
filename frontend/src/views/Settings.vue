<template>
  <AppLayout>
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置 AI 改写、平台账号、真实发布策略和模板。</p>
    </div>

    <el-card>
      <template #header>B站浏览器发布</template>
      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="当前版本不会保存 B站账号密码，也不会绕过验证码或平台风控。"
      />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击浏览器发布后在打开的 B站窗口里登录；登录态会保存在本机数据目录" />
        <el-step title="内容创作页可填写视频文件路径，系统会尝试自动上传该视频" />
        <el-step title="系统会在上传页出现后尝试填充标题、简介等信息" />
        <el-step title="你在 B站页面检查内容、处理验证码或二次验证，并手动确认保存草稿或发布" />
        <el-step title="发布完成后把 B站链接回填到系统，记录到发布历史" />
      </el-steps>
    </el-card>
  </AppLayout>
</template>

<script setup>
import AppLayout from '../components/AppLayout.vue'
</script>

<style scoped>
.settings-steps {
  margin-top: 16px;
}
</style>
