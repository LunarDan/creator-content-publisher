<template>
  <AppLayout>
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置各平台发布能力、微信 API 账号和浏览器发布策略。</p>
    </div>

    <!-- 公众号配置 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="platform-pill">公众号</span>
            <strong>草稿发布配置</strong>
          </div>
          <el-button type="primary" :loading="checkingWechat" @click="checkWechatToken">
            <el-icon style="margin-right:6px"><Connection /></el-icon> 检测微信配置
          </el-button>
        </div>
      </template>
      <el-alert
        type="info" show-icon :closable="false"
        title="测试号阶段只需要 AppID 和 AppSecret 即可检测 access_token；正式创建草稿还需要默认封面素材 ID。"
      />
      <el-descriptions class="settings-desc" border :column="1">
        <el-descriptions-item label="WECHAT_APP_ID">测试号 / 公众号 AppID</el-descriptions-item>
        <el-descriptions-item label="WECHAT_APP_SECRET">测试号 / 公众号 AppSecret</el-descriptions-item>
        <el-descriptions-item label="WECHAT_DEFAULT_THUMB_MEDIA_ID">正式公众号草稿默认封面素材 ID，测试号阶段可先留空</el-descriptions-item>
      </el-descriptions>
      <el-alert
        v-if="wechatCheckMessage"
        class="settings-alert"
        :type="wechatCheckType"
        show-icon :closable="false"
        :title="wechatCheckMessage"
      />
    </el-card>

    <!-- B站 -->
    <el-card class="settings-card">
      <template #header>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="platform-pill">B站</span>
          <strong>浏览器发布说明</strong>
        </div>
      </template>
      <el-alert type="warning" show-icon :closable="false" title="当前版本不会保存 B站账号密码，也不会绕过验证码或平台风控。" />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击浏览器发布后在打开的 B站窗口里登录；登录态会保存在本机数据目录" />
        <el-step title="内容创作页可填写视频文件路径，系统会尝试自动上传该视频" />
        <el-step title="系统会在上传页出现后尝试填充标题、简介等信息" />
        <el-step title="填充完成后系统会尝试自动点击发布；遇到验证码、二次验证、风控或无法确认成功时会停下等待人工处理" />
        <el-step title="如果自动发布未确认成功，你在 B站页面检查内容并手动确认保存草稿或发布" />
        <el-step title="发布完成后把 B站链接回填到系统，记录到发布历史" />
      </el-steps>
    </el-card>

    <!-- 知乎 -->
    <el-card class="settings-card">
      <template #header>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="platform-pill" style="background:#EFF6FF;color:#2563EB">知乎</span>
          <strong>发布助手说明</strong>
        </div>
      </template>
      <el-alert type="warning" show-icon :closable="false"
        title="知乎当前仅作为发布助手：系统会打开创作页、辅助填充内容，并在遇到风控或验证码时停下等待人工处理，不会自动点击最终发布按钮。" />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击知乎发布助手后在打开的知乎创作页手动登录" />
        <el-step title="登录态会保存在本机浏览器数据目录 backend/data/browser/zhihu，类似普通浏览器缓存" />
        <el-step title="系统会尝试打开专栏写作页或创作中心，并填充标题和正文" />
        <el-step title="系统默认不会自动点击最终发布按钮；如果需要栏目/话题/实名校验，请你人工处理" />
        <el-step title="如果自动填充后未确认成功，请在知乎页面人工检查并完成保存或发布" />
        <el-step title="完成后可在系统里确认任务完成并记录到发布历史" />
      </el-steps>
    </el-card>

    <!-- 抖音 -->
    <el-card class="settings-card">
      <template #header>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="platform-pill" style="background:#FEF3C7;color:#D97706">抖音</span>
          <strong>浏览器辅助发布说明</strong>
        </div>
      </template>
      <el-alert type="warning" show-icon :closable="false" title="当前版本不会保存抖音账号密码，也不会绕过验证码、安全验证或平台风控。" />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击抖音浏览器辅助发布后在打开的抖音创作者中心手动登录" />
        <el-step title="登录态会保存在本机浏览器数据目录 backend/data/browser/douyin，类似普通浏览器缓存" />
        <el-step title="系统会尝试上传视频并填充标题、简介和话题标签" />
        <el-step title="上传完成后系统会按抖音项目逻辑尝试点击发布；如果要求封面，会尝试选择推荐封面后继续发布" />
        <el-step title="遇到验证码、安全验证、风控、页面变化或无法确认状态时，系统会停下等待人工处理" />
        <el-step title="如果自动发布未确认成功，请在抖音页面人工检查并完成发布" />
      </el-steps>
    </el-card>

    <!-- 小红书 -->
    <el-card class="settings-card">
      <template #header>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="platform-pill" style="background:#FCE7F3;color:#DB2777">小红书</span>
          <strong>浏览器发布助手说明</strong>
        </div>
      </template>
      <el-alert type="warning" show-icon :closable="false"
        title="小红书当前作为发布助手：系统会打开创作页、辅助上传视频并填充内容，不会自动点击最终发布按钮，也不会绕过验证码、安全验证或平台风控。" />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击小红书发布助手后在打开的小红书创作中心手动登录" />
        <el-step title="登录态会保存在本机浏览器数据目录 backend/data/browser/xiaohongshu，类似普通浏览器缓存" />
        <el-step title="系统会尝试上传视频、填充标题、正文和话题，并设置封面和内容声明" />
        <el-step title="遇到登录、验证码、安全验证、风控或页面结构变化时，请在小红书页面人工处理" />
        <el-step title="确认发布或保存后，可回到系统记录发布完成" />
      </el-steps>
    </el-card>

    <!-- 快手 -->
    <el-card class="settings-card">
      <template #header>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="platform-pill" style="background:#FFF7ED;color:#EA580C">快手</span>
          <strong>浏览器发布助手说明</strong>
        </div>
      </template>
      <el-alert type="warning" show-icon :closable="false"
        title="快手当前仅作为发布助手：系统会打开创作页、辅助上传和填充内容，不会自动点击最终发布按钮，也不会绕过验证码、安全验证或平台风控。" />
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'

const checkingWechat = ref(false)
const wechatCheckMessage = ref('')
const wechatCheckType = ref('success')

async function checkWechatToken() {
  checkingWechat.value = true
  try {
    const res = await publishApi.wechatTokenCheck()
    wechatCheckType.value = 'success'
    wechatCheckMessage.value = res.data.data.message
    ElMessage.success('微信配置检测通过')
  } catch (error) {
    wechatCheckType.value = 'error'
    wechatCheckMessage.value = error.response?.data?.msg || '微信配置检测失败'
    ElMessage.error(wechatCheckMessage.value)
  } finally { checkingWechat.value = false }
}
</script>

<style scoped>
.settings-card + .settings-card {
  margin-top: var(--space-5);
}

.settings-desc,
.settings-steps,
.settings-alert {
  margin-top: var(--space-4);
}
</style>
