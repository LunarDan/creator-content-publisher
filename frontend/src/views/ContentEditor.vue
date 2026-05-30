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
        <el-form-item label="封面">
          <el-input v-model="form.cover_image" placeholder="请输入封面地址或本地路径" />
        </el-form-item>
        <el-form-item label="视频文件路径">
          <el-input v-model="form.video_path" placeholder="例如 C:/Users/30983/Videos/demo.mp4 或 C:\\Users\\30983\\Videos\\demo.mp4" />
          <p class="field-help">填写本机视频文件绝对路径，B站、抖音和快手浏览器发布都会使用。建议使用 mp4 文件。</p>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="tagText" placeholder="用逗号分隔，例如 AI,效率工具,自媒体" />
        </el-form-item>
        <el-form-item label="目标平台">
          <el-checkbox-group v-model="selectedPlatforms">
            <el-checkbox v-for="p in platforms" :key="p.key" :label="p.key">{{ p.name }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <div class="form-actions">
          <el-button type="primary" :loading="saving" @click="saveAndAdapt">保存并生成平台草稿</el-button>
          <el-button @click="fillDemoContent">填入示例内容</el-button>
        </div>
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
const selectedPlatforms = ref(['wechat_official', 'zhihu', 'bilibili', 'xiaohongshu', 'douyin', 'kuaishou'])
const tagText = ref('')
const form = reactive({ title: '', summary: '', body: '', content_type: 'article', cover_image: '', video_path: '' })
const saving = ref(false)

onMounted(async () => {
  const res = await platformApi.list()
  platforms.value = res.data.data
})

function fillDemoContent() {
  form.title = '如何用 AI 工具提升创作者内容分发效率'
  form.summary = '本文介绍创作者如何借助 AI 完成多平台内容改写、预览和发布。'
  form.body = `随着内容平台越来越多，创作者需要面对不同平台的标题长度、表达风格和内容结构要求。

本工具通过统一内容输入、多平台自动适配、草稿预览编辑和模拟发布流程，帮助创作者减少重复劳动。

首先，用户只需要输入一份原始内容。系统会根据公众号、知乎、B站、小红书等平台特点，自动生成不同风格的草稿。

其次，用户可以在预览中心对草稿进行人工微调，保证内容质量和平台表达效果。

最后，用户可以通过发布中心一键模拟发布，并在发布历史中查看每个平台的发布记录。`
  tagText.value = 'AI,内容创作,效率工具,自媒体'
}

async function saveAndAdapt() {
  if (!form.title || !form.body) {
    ElMessage.warning('请填写标题和正文')
    return
  }
  saving.value = true
  try {
    const payload = { ...form, tags: tagText.value.split(/[,，]/).map(t => t.trim()).filter(Boolean) }
    const created = await contentApi.create(payload)
    const contentId = created.data.data.id
    await contentApi.adapt(contentId, selectedPlatforms.value)
    store.setCurrentContentId(contentId)
    ElMessage.success('已生成平台草稿')
    router.push('/adaptation-center')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.field-help {
  margin: 6px 0 0;
  color: #909399;
  font-size: 12px;
}
</style>
