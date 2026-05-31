<template>
  <AppLayout>
    <div class="page-header">
      <h1>预览中心</h1>
      <p>预览并微调各平台草稿，保存后再进入发布中心。</p>
    </div>

    <el-empty v-if="!store.drafts.length" description="暂无预览内容，请先生成平台草稿">
      <el-button type="primary" @click="router.push('/content-editor')">
        <el-icon style="margin-right:6px"><EditPen /></el-icon> 前往内容创作
      </el-button>
    </el-empty>

    <div v-else class="preview-list">
      <div v-for="draft in store.drafts" :key="draft.id" class="preview-section">
        <el-card>
          <template #header>
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
              <div style="display:flex;align-items:center;gap:12px">
                <span class="platform-pill">{{ platformName(draft.platform) }}</span>
                <el-tag v-if="draft.platform === 'kuaishou'" size="small" type="warning" effect="light" round>新平台</el-tag>
              </div>
              <el-button type="primary" :loading="savingId === draft.id" @click="saveDraft(draft)">
                <el-icon style="margin-right:4px"><Check /></el-icon> 保存修改
              </el-button>
            </div>
          </template>

          <div v-if="editForms[draft.id]" class="preview-layout">
            <!-- 左侧预览区 -->
            <div class="preview-pane">
              <div class="preview-mock">
                <h2 class="preview-title">{{ editForms[draft.id].title || draft.title }}</h2>
                <p v-if="editForms[draft.id].summary" class="preview-summary">{{ editForms[draft.id].summary }}</p>
                <div class="preview-body">{{ editForms[draft.id].body || draft.body }}</div>
                <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
                  <el-tag v-for="tag in previewTags(draft.id)" :key="tag" size="small" type="info">{{ tag }}</el-tag>
                </div>
              </div>
            </div>

            <!-- 右侧编辑区 -->
            <div class="edit-pane">
              <el-form label-position="top" size="default">
                <el-form-item label="标题">
                  <el-input v-model="editForms[draft.id].title" placeholder="请输入平台标题" />
                </el-form-item>

                <el-form-item label="摘要">
                  <el-input v-model="editForms[draft.id].summary" placeholder="请输入平台摘要" />
                </el-form-item>

                <el-form-item label="正文">
                  <el-input v-model="editForms[draft.id].body" type="textarea" :rows="10" placeholder="请输入平台正文" />
                </el-form-item>

                <el-form-item label="标签（逗号分隔）">
                  <el-input v-model="editForms[draft.id].tagText" placeholder="例如 创作者, 效率工具" />
                </el-form-item>

                <!-- 知乎 -->
                <template v-if="draft.platform === 'zhihu'">
                  <el-form-item label="文章封面路径">
                    <el-input v-model="editForms[draft.id].coverImage" placeholder="本地图片路径，可留空" />
                  </el-form-item>
                  <el-form-item label="创作声明">
                    <el-select v-model="editForms[draft.id].zhihuCreationDeclaration" style="width:100%">
                      <el-option label="不声明" value="no_label" />
                      <el-option label="原创" value="original" />
                      <el-option label="转载" value="repost" />
                      <el-option label="授权转载" value="authorized" />
                    </el-select>
                  </el-form-item>
                </template>

                <!-- B站 -->
                <template v-if="draft.platform === 'bilibili'">
                  <el-form-item label="创作声明">
                    <el-select v-model="editForms[draft.id].creationDeclaration" style="width:100%">
                      <el-option label="无需标注" value="no_label" />
                      <el-option label="原创 / 自制" value="original" />
                      <el-option label="转载" value="repost" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="视频文件路径">
                    <el-input v-model="editForms[draft.id].videoPath" placeholder="例如 C:/Users/.../Videos/demo.mp4" />
                  </el-form-item>
                </template>

                <!-- 快手 -->
                <template v-if="draft.platform === 'kuaishou'">
                  <el-form-item label="作者声明 / 补充说明">
                    <el-input v-model="editForms[draft.id].authorDeclaration" placeholder="例如 原创、转载，留空则手动处理" />
                  </el-form-item>
                  <el-form-item label="封面图片路径">
                    <el-input v-model="editForms[draft.id].thumbnailPath" placeholder="例如 C:/Users/.../Pictures/cover.jpg" />
                  </el-form-item>
                  <el-form-item label="视频文件路径">
                    <el-input v-model="editForms[draft.id].videoPath" placeholder="例如 C:/Users/.../Videos/demo.mp4" />
                  </el-form-item>
                </template>
              </el-form>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen, Check } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'
import { contentApi } from '../api/content'
import { useContentStore } from '../stores/content'
import { platformName } from '../utils/platform'

const router = useRouter()
const store = useContentStore()
const editForms = reactive({})
const savingId = ref(null)

onMounted(async () => {
  store.restoreCurrentContentId()
  if (store.currentContentId) {
    await loadDraftsWithKuaishou()
  }
  initEditForms()
})

async function loadDraftsWithKuaishou() {
  const res = await contentApi.drafts(store.currentContentId)
  store.drafts = res.data.data || []
  if (!store.drafts.some(draft => draft.platform === 'kuaishou')) {
    const adaptRes = await contentApi.adapt(store.currentContentId, ['kuaishou'])
    const kuaishouDrafts = adaptRes.data.data || []
    store.drafts = [...store.drafts, ...kuaishouDrafts.filter(draft => !store.drafts.some(item => item.id === draft.id))]
  }
}

function initEditForms() {
  store.drafts.forEach((draft) => {
    editForms[draft.id] = {
      title: draft.title || '',
      summary: draft.summary || '',
      body: draft.body || '',
      tagText: (draft.tags || []).join(','),
      videoPath: draft.extra_config?.video_path || '',
      creationDeclaration: draft.extra_config?.creation_declaration || 'no_label',
      coverImage: draft.extra_config?.zhihu_cover_image || draft.cover_image || '',
      zhihuCreationDeclaration: draft.extra_config?.zhihu_creation_declaration || 'no_label',
      thumbnailPath: draft.extra_config?.thumbnail_path || draft.cover_image || '',
      authorDeclaration: draft.extra_config?.author_declaration || '',
    }
  })
}

function parseTags(tagText) {
  return tagText.split(/[,，]/).map(tag => tag.trim()).filter(Boolean)
}

function previewTags(draftId) {
  return parseTags(editForms[draftId]?.tagText || '')
}

async function saveDraft(draft) {
  const form = editForms[draft.id]
  if (!form.title || !form.body) {
    ElMessage.warning('标题和正文不能为空')
    return
  }
  savingId.value = draft.id
  try {
    const payload = {
      title: form.title,
      summary: form.summary,
      body: form.body,
      tags: parseTags(form.tagText),
      cover_image: draft.cover_image || '',
      extra_config: {
        ...(draft.extra_config || {}),
        video_path: form.videoPath || '',
        creation_declaration: form.creationDeclaration || '',
        zhihu_cover_image: form.coverImage || '',
        zhihu_creation_declaration: form.zhihuCreationDeclaration || '',
        thumbnail_path: form.thumbnailPath || '',
        author_declaration: form.authorDeclaration || '',
      },
      validation_warnings: draft.validation_warnings || [],
    }
    const res = await contentApi.updateDraft(draft.id, payload)
    const updatedDraft = res.data.data
    const index = store.drafts.findIndex(item => item.id === draft.id)
    if (index !== -1) store.drafts[index] = updatedDraft
    editForms[draft.id] = {
      title: updatedDraft.title || '',
      summary: updatedDraft.summary || '',
      body: updatedDraft.body || '',
      tagText: (updatedDraft.tags || []).join(','),
      videoPath: updatedDraft.extra_config?.video_path || '',
      creationDeclaration: updatedDraft.extra_config?.creation_declaration || '',
      coverImage: updatedDraft.extra_config?.zhihu_cover_image || updatedDraft.cover_image || '',
      zhihuCreationDeclaration: updatedDraft.extra_config?.zhihu_creation_declaration || 'no_label',
      thumbnailPath: updatedDraft.extra_config?.thumbnail_path || updatedDraft.cover_image || '',
      authorDeclaration: updatedDraft.extra_config?.author_declaration || '',
    }
    ElMessage.success('草稿已保存')
  } finally {
    savingId.value = null
  }
}
</script>

<style scoped>
.preview-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.preview-section {
  width: 100%;
}

.preview-layout {
  display: flex;
  gap: 40px;
}

.preview-pane {
  flex: 1;
  min-width: 0;
}

.preview-mock {
  padding: 32px;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.preview-title {
  margin: 0 0 16px;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-text-primary);
}

.preview-summary {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0 0 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
}

.preview-body {
  white-space: pre-wrap;
  line-height: 1.9;
  font-size: 15px;
  color: var(--color-text-primary);
}

.edit-pane {
  width: 400px;
  flex-shrink: 0;
  max-height: calc(100vh - 240px);
  overflow-y: auto;
  padding-right: 4px;
}

@media (max-width: 1100px) {
  .preview-layout {
    flex-direction: column;
    gap: 24px;
  }
  .edit-pane {
    width: 100%;
    max-height: none;
    overflow-y: visible;
  }
}
</style>
