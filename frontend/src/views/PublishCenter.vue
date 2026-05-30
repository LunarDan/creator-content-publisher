<template>
  <AppLayout>
    <div class="page-header">
      <h1>发布中心</h1>
      <p>选择多个平台草稿，一键完成模拟发布。</p>
    </div>

    <el-empty v-if="!store.drafts.length" description="暂无可发布草稿，请先生成平台草稿" />
    <template v-else>
      <el-card class="publish-toolbar">
        <div class="toolbar-content">
          <div>
            <strong>待发布草稿：{{ store.drafts.length }} 个</strong>
            <p class="muted">已选择 {{ selectedDraftIds.length }} 个平台草稿</p>
          </div>
          <div class="toolbar-actions">
            <el-button @click="selectAll">全选</el-button>
            <el-button @click="clearSelection">清空</el-button>
            <el-button type="primary" :loading="publishing" @click="simulateBatch">一键模拟发布</el-button>
          </div>
        </div>
      </el-card>

      <el-checkbox-group v-model="selectedDraftIds" class="draft-grid">
        <el-card v-for="draft in store.drafts" :key="draft.id" class="publish-card">
          <div class="card-header">
            <el-checkbox :label="draft.id">{{ platformName(draft.platform) }}</el-checkbox>
            <div class="card-actions">
              <el-tag type="success">模拟发布</el-tag>
              <el-button
                v-if="draft.platform === 'wechat_official'"
                size="small"
                type="primary"
                plain
                :loading="wechatPublishingId === draft.id"
                @click.stop="saveWechatDraft(draft)"
              >
                保存到公众号草稿箱
              </el-button>
              <el-button
                v-if="draft.platform === 'bilibili'"
                size="small"
                type="primary"
                plain
                :loading="browserPublishingId === draft.id"
                @click.stop="saveBilibiliDraftWithBrowser(draft)"
              >
                浏览器保存到 B站草稿
              </el-button>
            </div>
          </div>
          <h3>{{ draft.title }}</h3>
          <p class="muted">{{ draft.summary || '暂无摘要' }}</p>
          <p class="draft-body">{{ draft.body }}</p>
          <div class="tag-row">
            <el-tag v-for="tag in draft.tags" :key="tag">{{ tag }}</el-tag>
          </div>
        </el-card>
      </el-checkbox-group>

      <el-dialog v-model="wechatDialogVisible" title="公众号草稿发布结果" width="620px">
        <el-alert
          type="success"
          show-icon
          :closable="false"
          title="公众号草稿已创建成功。"
        />
        <div v-if="wechatResult" class="browser-result">
          <p>{{ wechatResult.message }}</p>
          <el-descriptions border :column="1">
            <el-descriptions-item label="标题">{{ wechatResult.draft.title }}</el-descriptions-item>
            <el-descriptions-item label="摘要">{{ wechatResult.draft.summary || '-' }}</el-descriptions-item>
            <el-descriptions-item label="正文">
              <pre>{{ wechatResult.draft.body }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="Media ID">{{ wechatResult.result.external_id || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <template #footer>
          <el-button type="primary" @click="wechatDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="browserDialogVisible" title="B站浏览器保存草稿" width="640px">
        <el-alert
          type="warning"
          show-icon
          :closable="false"
          title="系统会尝试自动填充标题、简介并点击保存草稿；如果遇到登录、验证码、风控或无法确认成功，需要你在 B站页面手动保存。"
        />
        <div v-if="browserResult" class="browser-result">
          <p>{{ browserResult.message }}</p>
          <el-descriptions border :column="1">
            <el-descriptions-item label="标题">{{ browserResult.draft.title }}</el-descriptions-item>
            <el-descriptions-item label="简介">
              <pre>{{ browserResult.draft.body }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="标签">{{ (browserResult.draft.tags || []).join('、') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="视频文件">{{ browserResult.draft.video_path || '未填写，请在 B站页面手动上传' }}</el-descriptions-item>
            <el-descriptions-item label="已尝试填充">{{ (browserResult.filled || []).join('、') || '暂无' }}</el-descriptions-item>
          </el-descriptions>
          <el-input v-model="publishUrl" class="publish-url" placeholder="可选：发布后的视频链接，不填也可以确认完成" />
          <div class="manual-actions">
            <el-button @click="copyDraftText(browserResult.draft.title)">复制标题</el-button>
            <el-button @click="copyDraftText(browserResult.draft.body)">复制简介</el-button>
            <el-button @click="copyDraftText((browserResult.draft.tags || []).join('、'))">复制标签</el-button>
          </div>
        </div>
        <template #footer>
          <el-button @click="browserDialogVisible = false">稍后处理</el-button>
          <el-button type="primary" :loading="completing" @click="completeManualPublish">我已保存草稿，记录完成</el-button>
        </template>
      </el-dialog>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { publishApi } from '../api/publish'
import { contentApi } from '../api/content'
import { useContentStore } from '../stores/content'
import { platformName } from '../utils/platform'

const router = useRouter()
const store = useContentStore()
const selectedDraftIds = ref([])
const publishing = ref(false)
const wechatPublishingId = ref(null)
const wechatDialogVisible = ref(false)
const wechatResult = ref(null)
const browserPublishingId = ref(null)
const browserDialogVisible = ref(false)
const browserResult = ref(null)
const browserTask = ref(null)
const publishUrl = ref('')
const completing = ref(false)

onMounted(async () => {
  store.restoreCurrentContentId()
  if (!store.drafts.length && store.currentContentId) {
    const res = await contentApi.drafts(store.currentContentId)
    store.drafts = res.data.data || []
  }
  selectAll()
})

function selectAll() {
  selectedDraftIds.value = store.drafts.map(draft => draft.id)
}

function clearSelection() {
  selectedDraftIds.value = []
}

async function simulateBatch() {
  if (!selectedDraftIds.value.length) {
    ElMessage.warning('请先选择要发布的平台草稿')
    return
  }

  publishing.value = true
  try {
    const res = await publishApi.simulateBatch(selectedDraftIds.value)
    const results = res.data.data || []
    const failedCount = results.filter(item => item.status === 'failed').length
    if (failedCount) {
      ElMessage.warning(`模拟发布完成，其中 ${failedCount} 个草稿发布失败`)
    } else {
      ElMessage.success('一键模拟发布完成')
    }
    router.push('/publish-history')
  } finally {
    publishing.value = false
  }
}

async function saveWechatDraft(draft) {
  wechatPublishingId.value = draft.id
  try {
    const res = await publishApi.wechatDraft(draft.id)
    wechatResult.value = {
      draft,
      result: res.data.data.result,
      message: res.data.data.result.message,
    }
    wechatDialogVisible.value = true
    ElMessage.success('已保存到公众号草稿箱')
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || '公众号草稿发布失败')
  } finally {
    wechatPublishingId.value = null
  }
}

async function saveBilibiliDraftWithBrowser(draft) {
  browserPublishingId.value = draft.id
  try {
    const res = await publishApi.browserBilibili(draft.id, true)
    browserTask.value = res.data.data.task
    browserResult.value = res.data.data.result
    publishUrl.value = ''
    if (browserTask.value.status === 'success') {
      ElMessage.success('已自动保存到 B站草稿')
      router.push('/publish-history')
      return
    }
    browserDialogVisible.value = true
    ElMessage.warning('已打开浏览器，仍需要你在 B站页面人工确认草稿')
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || 'B站浏览器保存草稿启动失败')
  } finally {
    browserPublishingId.value = null
  }
}

async function copyDraftText(text) {
  try {
    await navigator.clipboard.writeText(text || '')
    ElMessage.success('已复制')
  } catch (error) {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}

async function completeManualPublish() {
  if (!browserTask.value) {
    return
  }

  completing.value = true
  try {
    await publishApi.completeManual(browserTask.value.id, publishUrl.value.trim())
    ElMessage.success('草稿保存记录已保存')
    browserDialogVisible.value = false
    router.push('/publish-history')
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || '保存发布记录失败')
  } finally {
    completing.value = false
  }
}
</script>
