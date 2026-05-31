<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布中心</h1>
      <p>选择平台草稿，一键模拟发布或启动浏览器发布助手。</p>
    </div>

    <el-empty v-if="!store.drafts.length" description="暂无可发布草稿，请先生成平台草稿">
      <el-button type="primary" @click="router.push('/content-editor')">
        <el-icon style="margin-right:6px"><EditPen /></el-icon> 前往内容创作
      </el-button>
    </el-empty>

    <template v-else>
      <!-- 工具栏 -->
      <div class="publish-bar">
        <div class="publish-bar-left">
          <strong>待发布草稿：{{ store.drafts.length }} 个</strong>
          <span class="muted">| 已选 {{ selectedDraftIds.length }} 个</span>
        </div>
        <div class="publish-bar-right">
          <el-button @click="selectAll">全选</el-button>
          <el-button @click="clearSelection">清空</el-button>
          <el-button type="primary" :loading="publishing" @click="simulateBatch">
            <el-icon style="margin-right:6px"><Finished /></el-icon> 一键模拟发布
          </el-button>
          <el-button type="success" :loading="realPublishing" @click="publishSelectedDrafts">
            <el-icon style="margin-right:6px"><Promotion /></el-icon> 一键发布多平台
          </el-button>
        </div>
      </div>

      <!-- 草稿列表 -->
      <el-checkbox-group v-model="selectedDraftIds">
        <div v-for="draft in store.drafts" :key="draft.id" class="publish-item">
          <el-card>
            <div class="publish-item-header">
              <el-checkbox :label="draft.id" size="large">
                <span class="publish-platform-name">{{ platformName(draft.platform) }}</span>
              </el-checkbox>
              <el-tag type="success" effect="light" round size="small">模拟发布</el-tag>
            </div>

            <h3 class="publish-item-title">{{ draft.title }}</h3>

            <p v-if="draft.summary" class="muted" style="margin-bottom:12px">{{ draft.summary }}</p>

            <p class="draft-body-text">{{ draft.body }}</p>

            <div class="tag-row" style="margin:12px 0">
              <el-tag v-for="tag in draft.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
            </div>

            <!-- 平台操作按钮 -->
            <div class="publish-item-actions">
              <el-button
                v-if="draft.platform === 'wechat_official'"
                type="primary" plain :loading="wechatPublishingId === draft.id"
                @click.stop="saveWechatDraft(draft)"
              >
                <el-icon style="margin-right:4px"><Document /></el-icon> 保存到公众号草稿箱
              </el-button>
              <el-button
                v-if="draft.platform === 'zhihu'"
                plain :loading="browserPublishingId === draft.id"
                @click.stop="publishZhihuWithBrowser(draft)"
              >
                <el-icon style="margin-right:4px"><Connection /></el-icon> 知乎发布助手
              </el-button>
              <el-button
                v-if="draft.platform === 'douyin'"
                plain :loading="browserPublishingId === draft.id"
                @click.stop="saveDouyinDraftWithBrowser(draft)"
              >
                <el-icon style="margin-right:4px"><VideoPlay /></el-icon> 辅助发布到抖音
              </el-button>
              <el-button
                v-if="draft.platform === 'bilibili'"
                plain :loading="browserPublishingId === draft.id"
                @click.stop="saveBilibiliDraftWithBrowser(draft)"
              >
                <el-icon style="margin-right:4px"><VideoCamera /></el-icon> 保存到 B站草稿
              </el-button>
              <el-button
                v-if="draft.platform === 'xiaohongshu'"
                plain :loading="browserPublishingId === draft.id"
                @click.stop="openXiaohongshuBrowserAssistant(draft)"
              >
                <el-icon style="margin-right:4px"><PictureFilled /></el-icon> 小红书发布助手
              </el-button>
              <el-button
                v-if="draft.platform === 'kuaishou'"
                plain :loading="browserPublishingId === draft.id"
                @click.stop="openKuaishouBrowserAssistant(draft)"
              >
                <el-icon style="margin-right:4px"><VideoCamera /></el-icon> 快手发布助手
              </el-button>
            </div>
          </el-card>
        </div>
      </el-checkbox-group>

      <!-- WeChat Dialog -->
      <el-dialog v-model="wechatDialogVisible" title="公众号草稿发布结果" width="620px">
        <el-alert type="success" show-icon :closable="false" title="公众号草稿已创建成功。" />
        <div v-if="wechatResult" class="dialog-section">
          <p>{{ wechatResult.message }}</p>
          <el-descriptions border :column="1">
            <el-descriptions-item label="标题">{{ wechatResult.draft.title }}</el-descriptions-item>
            <el-descriptions-item label="摘要">{{ wechatResult.draft.summary || '-' }}</el-descriptions-item>
            <el-descriptions-item label="正文"><pre>{{ wechatResult.draft.body }}</pre></el-descriptions-item>
            <el-descriptions-item label="Media ID">{{ wechatResult.result.external_id || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <template #footer>
          <el-button type="primary" @click="wechatDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>

      <!-- Browser Dialog -->
      <el-dialog v-model="browserDialogVisible" :title="browserDialogTitle" width="640px">
        <el-alert type="warning" show-icon :closable="false" :title="browserDialogTip" />
        <div v-if="browserResult" class="dialog-section">
          <p>{{ browserResult.message }}</p>
          <el-descriptions border :column="1">
            <el-descriptions-item label="标题">{{ browserResult.draft.title }}</el-descriptions-item>
            <el-descriptions-item :label="browserDraft?.platform === 'zhihu' ? '正文' : '简介'">
              <pre>{{ browserResult.draft.body }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="标签">{{ (browserResult.draft.tags || []).join('、') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="视频文件">{{ browserResult.draft.video_path || `未填写，请在 ${browserPlatformName} 页面手动上传` }}</el-descriptions-item>
            <el-descriptions-item v-if="['kuaishou', 'xiaohongshu'].includes(browserTask?.platform)" label="封面图片">
              {{ browserResult.draft.thumbnail_path || `未填写，请在 ${browserPlatformName} 页面手动设置` }}
            </el-descriptions-item>
            <el-descriptions-item v-if="browserTask?.platform === 'kuaishou'" label="作者声明">
              {{ browserResult.draft.author_declaration || '未填写，请在快手页面手动设置' }}
            </el-descriptions-item>
            <el-descriptions-item v-if="browserTask?.platform === 'xiaohongshu'" label="内容声明">
              {{ browserResult.draft.content_declaration || '未填写，请在小红书页面手动设置' }}
            </el-descriptions-item>
            <el-descriptions-item v-if="browserTask?.platform === 'xiaohongshu'" label="原创声明">
              {{ browserResult.draft.original_declaration || '未开启，请在小红书页面手动设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="已尝试填充">{{ (browserResult.filled || []).join('、') || '暂无' }}</el-descriptions-item>
          </el-descriptions>
          <el-input v-model="publishUrl" style="margin-top:16px" placeholder="可选：发布后的内容链接" />
          <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
            <el-button size="small" @click="copyDraftText(browserResult.draft.title)">复制标题</el-button>
            <el-button size="small" @click="copyDraftText(browserResult.draft.body)">复制{{ browserDraft?.platform === 'zhihu' ? '正文' : '简介' }}</el-button>
            <el-button size="small" @click="copyDraftText((browserResult.draft.tags || []).join('、'))">复制标签</el-button>
            <el-button v-if="browserDraft?.platform === 'zhihu'" size="small" @click="copyDraftText(browserResult.draft.cover_image)">复制封面路径</el-button>
            <el-button v-if="browserTask?.platform && ['bilibili', 'kuaishou', 'xiaohongshu'].includes(browserTask.platform)" size="small" @click="copyDraftText(browserResult.draft.video_path)">复制视频路径</el-button>
            <el-button v-if="browserTask?.platform && ['kuaishou', 'xiaohongshu'].includes(browserTask.platform)" size="small" @click="copyDraftText(browserResult.draft.thumbnail_path)">复制封面路径</el-button>
          </div>
        </div>
        <template #footer>
          <el-button @click="browserDialogVisible = false">稍后处理</el-button>
          <el-button type="primary" :loading="completing" @click="completeManualPublish">我已在平台完成，记录完成</el-button>
        </template>
      </el-dialog>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen, Finished, Promotion, Document, Connection, VideoPlay, VideoCamera, PictureFilled } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'
import { contentApi } from '../api/content'
import { useContentStore } from '../stores/content'
import { platformName } from '../utils/platform'

const router = useRouter()
const store = useContentStore()
const selectedDraftIds = ref([])
const publishing = ref(false)
const realPublishing = ref(false)
const wechatPublishingId = ref(null)
const wechatDialogVisible = ref(false)
const wechatResult = ref(null)
const browserPublishingId = ref(null)
const browserDialogVisible = ref(false)
const browserDraft = ref(null)
const browserResult = ref(null)
const browserTask = ref(null)
const publishUrl = ref('')
const completing = ref(false)

const browserPlatformName = computed(() => platformName(browserTask.value?.platform || 'bilibili'))
const browserDialogTitle = computed(() => `${browserPlatformName.value} 浏览器发布助手`)
const browserDialogTip = computed(() => {
  if (browserTask.value?.platform === 'kuaishou') return '系统会尝试上传视频、填充描述/标签、设置封面和作者声明；不会自动点击最终发布按钮，遇到登录、验证码或风控时需要你在快手页面手动处理。'
  if (browserTask.value?.platform === 'xiaohongshu') return '系统会尝试上传视频、填充标题/正文/话题、设置封面和内容声明；不会自动点击最终发布按钮，遇到登录、验证码或风控时需要你在小红书页面手动处理。'
  return '系统会尝试自动填充标题、简介并点击保存草稿；如果遇到登录、验证码、风控或无法确认成功，需要你在平台页面手动保存。'
})

onMounted(async () => {
  store.restoreCurrentContentId()
  if (store.currentContentId) {
    await loadDraftsWithKuaishou()
  }
  selectAll()
})

async function loadDraftsWithKuaishou() {
  const res = await contentApi.drafts(store.currentContentId)
  store.drafts = res.data.data || []
  if (!store.drafts.some(draft => draft.platform === 'kuaishou')) {
    const adaptRes = await contentApi.adapt(store.currentContentId, ['kuaishou'])
    const kuaishouDrafts = adaptRes.data.data || []
    store.drafts = [...store.drafts, ...kuaishouDrafts.filter(d => !store.drafts.some(item => item.id === d.id))]
  }
}

function selectAll() { selectedDraftIds.value = store.drafts.map(d => d.id) }
function clearSelection() { selectedDraftIds.value = [] }

async function simulateBatch() {
  if (!selectedDraftIds.value.length) { ElMessage.warning('请先选择要发布的平台草稿'); return }
  publishing.value = true
  try {
    const res = await publishApi.simulateBatch(selectedDraftIds.value)
    const results = res.data.data || []
    const failedCount = results.filter(item => item.status === 'failed').length
    ElMessage[failedCount ? 'warning' : 'success'](failedCount ? `模拟发布完成，其中 ${failedCount} 个草稿发布失败` : '一键模拟发布完成')
    router.push('/publish-history')
  } finally { publishing.value = false }
}

async function publishSelectedDrafts() {
  if (!selectedDraftIds.value.length) { ElMessage.warning('请先选择要发布的平台草稿'); return }
  realPublishing.value = true
  try {
    const selected = store.drafts.filter(d => selectedDraftIds.value.includes(d.id))
    const results = await Promise.allSettled(selected.map(d => publishDraft(d)))
    const failedCount = results.filter(r => r.status === 'rejected').length
    ElMessage[failedCount ? 'warning' : 'success'](failedCount ? `已同时启动发布助手，其中 ${failedCount} 个平台启动失败` : '已同时启动所选平台发布助手')
    router.push('/publish-history')
  } finally { realPublishing.value = false }
}

function publishDraft(draft) {
  if (draft.platform === 'wechat_official') return publishApi.wechatDraft(draft.id)
  if (draft.platform === 'zhihu') return publishApi.browserZhihu(draft.id, false)
  if (draft.platform === 'douyin') return publishApi.browserDouyin(draft.id, true)
  if (draft.platform === 'bilibili') return publishApi.browserBilibili(draft.id, true)
  if (draft.platform === 'xiaohongshu') return publishApi.browserXiaohongshu(draft.id)
  if (draft.platform === 'kuaishou') return publishApi.browserKuaishou(draft.id)
  return publishApi.simulate(draft.id)
}

async function saveWechatDraft(draft) {
  wechatPublishingId.value = draft.id
  try {
    const res = await publishApi.wechatDraft(draft.id)
    wechatResult.value = { draft, result: res.data.data.result, message: res.data.data.result.message }
    wechatDialogVisible.value = true
    ElMessage.success('已保存到公众号草稿箱')
  } catch (error) { ElMessage.error(error.response?.data?.msg || '公众号草稿发布失败') }
  finally { wechatPublishingId.value = null }
}

async function handleBrowserPublish(draft, apiCall, successMsg, warningMsg) {
  browserPublishingId.value = draft.id; browserDraft.value = draft
  try {
    const res = await apiCall(draft.id)
    browserTask.value = res.data.data.task; browserResult.value = res.data.data.result; publishUrl.value = ''
    if (browserTask.value.status === 'success') { ElMessage.success(successMsg); router.push('/publish-history'); return }
    browserDialogVisible.value = true
    ElMessage.warning(warningMsg)
  } catch (error) { ElMessage.error(error.response?.data?.msg || '启动失败') }
  finally { browserPublishingId.value = null }
}

async function publishZhihuWithBrowser(draft) {
  await handleBrowserPublish(draft, (id) => publishApi.browserZhihu(id, false), '知乎发布或草稿保存成功', '已打开知乎发布助手，请在知乎页面人工检查、保存或发布')
}

async function saveDouyinDraftWithBrowser(draft) {
  await handleBrowserPublish(draft, (id) => publishApi.browserDouyin(id, true), '抖音自动发布成功', '已打开浏览器并尝试自动发布，请在抖音页面检查是否需要人工处理')
}

async function saveBilibiliDraftWithBrowser(draft) {
  await handleBrowserPublish(draft, (id) => publishApi.browserBilibili(id, true), '已自动保存到 B站草稿', '已打开浏览器，仍需要你在 B站页面人工确认草稿')
}

async function openXiaohongshuBrowserAssistant(draft) {
  await handleBrowserPublish(draft, (id) => publishApi.browserXiaohongshu(id), '', '已打开小红书发布助手，请在小红书页面人工检查并完成发布')
}

async function openKuaishouBrowserAssistant(draft) {
  await handleBrowserPublish(draft, (id) => publishApi.browserKuaishou(id), '', '已打开快手发布助手，请在快手页面人工检查并完成发布')
}

async function copyDraftText(text) {
  try { await navigator.clipboard.writeText(text || ''); ElMessage.success('已复制') }
  catch (error) { ElMessage.error('复制失败，请手动选择文本复制') }
}

async function completeManualPublish() {
  if (!browserTask.value) return
  completing.value = true
  try {
    await publishApi.completeManual(browserTask.value.id, publishUrl.value.trim())
    ElMessage.success('发布记录已保存')
    browserDialogVisible.value = false
    router.push('/publish-history')
  } catch (error) { ElMessage.error(error.response?.data?.msg || '保存发布记录失败') }
  finally { completing.value = false }
}
</script>

<style scoped>
.publish-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, var(--color-primary-50), #FEFCE8);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
}

.publish-bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.publish-bar-left strong {
  font-size: var(--text-lg);
}

.publish-bar-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.publish-item {
  margin-bottom: 20px;
}

.publish-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.publish-platform-name {
  font-weight: 700;
  font-size: var(--text-base);
}

.publish-item-title {
  margin: 0 0 8px;
  font-size: var(--text-xl);
  font-weight: 600;
}

.draft-body-text {
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

.publish-item-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-light);
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.dialog-section {
  margin-top: 20px;
}

.dialog-section p {
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}
</style>
