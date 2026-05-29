import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useContentStore = defineStore('content', () => {
  const currentContentId = ref(null)
  const contents = ref([])
  const drafts = ref([])

  return { currentContentId, contents, drafts }
})
