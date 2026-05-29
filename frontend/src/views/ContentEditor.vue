<template>
  <AppLayout>
    <div class="page-header">
      <h1>内容创作</h1>
      <p>输入一份原始内容，作为后续多平台适配的来源。</p>
    </div>
    <el-card>
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入内容标题" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" placeholder="一句话概括内容" />
        </el-form-item>
        <el-form-item label="正文">
          <el-input v-model="form.body" type="textarea" :rows="12" placeholder="支持 Markdown 风格文本" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="tagText" placeholder="用逗号分隔，例如 AI,效率工具,自媒体" />
        </el-form-item>
        <el-form-item label="目标平台">
          <el-checkbox-group v-model="selectedPlatforms">
            <el-checkbox v-for="p in platforms" :key="p.key" :label="p.key">{{ p.name }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-button type="primary" @click="saveAndAdapt">保存并生成平台草稿</el-button>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '../components/AppLayout.vue'
import { contentApi } from '../api/content'
import { platformApi } from '../api/platform'
import { useContentStore } from '../stores/content'

const router = useRouter()
const store = useContentStore()
const platforms = ref([])
const selectedPlatforms = ref(['wechat_official', 'zhihu', 'bilibili', 'xiaohongshu'])
const tagText = ref('')
const form = reactive({ title: '', summary: '', body: '', content_type: 'article', cover_image: '' })

onMounted(async () => {
  const res = await platformApi.list()
  platforms.value = res.data.data
})

async function saveAndAdapt() {
  if (!form.title || !form.body) {
    ElMessage.warning('请填写标题和正文')
    return
  }
  const payload = { ...form, tags: tagText.value.split(/[,，]/).map(t => t.trim()).filter(Boolean) }
  const created = await contentApi.create(payload)
  const contentId = created.data.data.id
  await contentApi.adapt(contentId, selectedPlatforms.value)
  store.currentContentId = contentId
  ElMessage.success('已生成平台草稿')
  router.push('/adaptation-center')
}
</script>
