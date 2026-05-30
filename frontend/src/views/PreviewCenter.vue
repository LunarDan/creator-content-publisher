<template>
  <AppLayout>
    <div class="page-header">
      <h1>预览中心</h1>
      <p>预览并微调各平台草稿，保存后再进入发布中心。</p>
    </div>

    <el-empty v-if="!store.drafts.length" description="暂无预览内容，请先生成平台草稿" />
    <div v-else class="preview-grid">
      <el-card v-for="draft in store.drafts" :key="draft.id" class="preview-card">
        <template #header>
          <div class="card-header">
            <span class="platform-pill">{{ platformName(draft.platform) }}</span>
            <el-button type="primary" size="small" :loading="savingId === draft.id" @click="saveDraft(draft)">
              保存修改
            </el-button>
          </div>
        </template>

        <div v-if="editForms[draft.id]" class="preview-layout">
          <div class="preview-pane">
            <h2>{{ editForms[draft.id].title || draft.title }}</h2>
            <p class="muted">{{ editForms[draft.id].summary || '暂无摘要' }}</p>
            <p class="preview-body">{{ editForms[draft.id].body || draft.body }}</p>
            <div class="tag-row">
              <el-tag v-for="tag in previewTags(draft.id)" :key="tag">{{ tag }}</el-tag>
            </div>
          </div>

          <el-form class="edit-pane" label-position="top">
            <el-form-item label="标题">
              <el-input v-model="editForms[draft.id].title" placeholder="请输入平台标题" />
            </el-form-item>
            <el-form-item label="摘要">
              <el-input v-model="editForms[draft.id].summary" placeholder="请输入平台摘要" />
            </el-form-item>
            <el-form-item label="正文">
              <el-input v-model="editForms[draft.id].body" type="textarea" :rows="8" placeholder="请输入平台正文" />
            </el-form-item>
            <el-form-item label="标签">
              <el-input v-model="editForms[draft.id].tagText" placeholder="用逗号分隔，例如 创作者,效率工具" />
            </el-form-item>
            <el-form-item v-if="draft.platform === 'bilibili'" label="创作声明">
              <el-select v-model="editForms[draft.id].creationDeclaration" placeholder="请选择 B站创作声明">
                <el-option label="无需标注" value="no_label" />
                <el-option label="原创 / 自制" value="original" />
                <el-option label="转载" value="repost" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="draft.platform === 'bilibili'" label="视频文件路径">
              <el-input v-model="editForms[draft.id].videoPath" placeholder="例如 C:/Users/30983/Videos/demo.mp4" />
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { contentApi } from '../api/content'
import { useContentStore } from '../stores/content'
import { platformName } from '../utils/platform'

const store = useContentStore()
const editForms = reactive({})
const savingId = ref(null)

onMounted(async () => {
  store.restoreCurrentContentId()
  if (!store.drafts.length && store.currentContentId) {
    const res = await contentApi.drafts(store.currentContentId)
    store.drafts = res.data.data || []
  }
  initEditForms()
})

function initEditForms() {
  store.drafts.forEach((draft) => {
    editForms[draft.id] = {
      title: draft.title || '',
      summary: draft.summary || '',
      body: draft.body || '',
      tagText: (draft.tags || []).join(','),
      videoPath: draft.extra_config?.video_path || '',
      creationDeclaration: draft.extra_config?.creation_declaration || 'no_label',
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
      },
      validation_warnings: draft.validation_warnings || [],
    }
    const res = await contentApi.updateDraft(draft.id, payload)
    const updatedDraft = res.data.data
    const index = store.drafts.findIndex(item => item.id === draft.id)
    if (index !== -1) {
      store.drafts[index] = updatedDraft
    }
    editForms[draft.id] = {
      title: updatedDraft.title || '',
      summary: updatedDraft.summary || '',
      body: updatedDraft.body || '',
      tagText: (updatedDraft.tags || []).join(','),
      videoPath: updatedDraft.extra_config?.video_path || '',
      creationDeclaration: updatedDraft.extra_config?.creation_declaration || '',
    }
    ElMessage.success('草稿已保存')
  } finally {
    savingId.value = null
  }
}
</script>
