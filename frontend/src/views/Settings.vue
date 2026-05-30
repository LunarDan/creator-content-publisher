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
        <el-step title="填充完成后系统会尝试自动点击发布；遇到验证码、二次验证、风控或无法确认成功时会停下等待人工处理" />
        <el-step title="如果自动发布未确认成功，你在 B站页面检查内容并手动确认保存草稿或发布" />
        <el-step title="发布完成后把 B站链接回填到系统，记录到发布历史" />
      </el-steps>
    </el-card>

    <el-card class="settings-card">
      <template #header>快手浏览器发布助手</template>
      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="快手当前仅作为发布助手：系统会打开创作页、辅助上传和填充内容，不会自动点击最终发布按钮，也不会绕过验证码、安全验证或平台风控。"
      />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击快手发布助手后在打开的快手创作者中心手动登录" />
        <el-step title="预览中心可填写视频路径、封面图片路径和作者声明/补充说明" />
        <el-step title="系统会尝试上传视频、填充描述和标签，并设置封面和作者声明" />
        <el-step title="遇到登录、验证码、安全验证、风控或页面结构变化时，请在快手页面人工处理" />
        <el-step title="确认发布或保存后，可回到系统记录发布完成" />
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

.settings-card {
  margin-top: 16px;
}
</style>
