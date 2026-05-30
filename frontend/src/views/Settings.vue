<template>
  <AppLayout>
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置 AI 改写、平台账号、真实发布策略和模板。</p>
    </div>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>公众号草稿发布</span>
          <el-button type="primary" :loading="checkingWechat" @click="checkWechatToken">检测微信配置</el-button>
        </div>
      </template>
      <el-alert
        type="info"
        show-icon
        :closable="false"
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
        show-icon
        :closable="false"
        :title="wechatCheckMessage"
      />
    </el-card>

    <el-card class="settings-card">
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
      <template #header>知乎发布助手</template>
      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="知乎当前仅作为发布助手：系统会打开创作页、辅助填充内容，并在遇到风控或验证码时停下等待人工处理，不会自动点击最终发布按钮。"
      />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击知乎发布助手后在打开的知乎创作页手动登录" />
        <el-step title="登录态会保存在本机浏览器数据目录 backend/data/browser/zhihu，类似普通浏览器缓存" />
        <el-step title="系统会尝试打开专栏写作页或创作中心，并填充标题和正文" />
        <el-step title="系统默认不会自动点击最终发布按钮；如果需要栏目/话题/实名校验，请你人工处理" />
        <el-step title="如果自动填充后未确认成功，请在知乎页面人工检查并完成保存或发布" />
        <el-step title="完成后可在系统里确认任务完成并记录到发布历史" />
      </el-steps>
    </el-card>

    <el-card class="settings-card">
      <template #header>抖音浏览器辅助发布</template>
      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="当前版本不会保存抖音账号密码，也不会绕过验证码、安全验证或平台风控。"
      />
      <el-steps class="settings-steps" direction="vertical" :active="4">
        <el-step title="首次使用时，点击抖音浏览器辅助发布后在打开的抖音创作者中心手动登录" />
        <el-step title="登录态会保存在本机浏览器数据目录 backend/data/browser/douyin，类似普通浏览器缓存" />
        <el-step title="系统会尝试上传视频并填充标题、简介和话题标签" />
        <el-step title="上传完成后系统会按抖音项目逻辑尝试点击发布；如果要求封面，会尝试选择推荐封面后继续发布" />
        <el-step title="遇到验证码、安全验证、风控、页面变化或无法确认状态时，系统会停下等待人工处理" />
        <el-step title="如果自动发布未确认成功，请在抖音页面人工检查并完成发布" />
        <el-step title="发布完成后可在系统里确认任务完成并记录到发布历史" />
      </el-steps>
    </el-card>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
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
  } finally {
    checkingWechat.value = false
  }
}
</script>

<style scoped>
.settings-card + .settings-card {
  margin-top: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.settings-desc,
.settings-steps,
.settings-alert {
  margin-top: 16px;
}
</style>
