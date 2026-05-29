import { defineStore } from 'pinia'
import { ref } from 'vue'

const CURRENT_CONTENT_KEY = 'currentContentId'

export const useContentStore = defineStore('content', () => {
  const currentContentId = ref(null)
  const contents = ref([])
  const drafts = ref([])

  function setCurrentContentId(id) {
    currentContentId.value = id
    if (id) {
      localStorage.setItem(CURRENT_CONTENT_KEY, String(id))
    } else {
      localStorage.removeItem(CURRENT_CONTENT_KEY)
    }
  }

  function restoreCurrentContentId() {
    const storedId = localStorage.getItem(CURRENT_CONTENT_KEY)
    currentContentId.value = storedId ? Number(storedId) : null
  }

  function clearCurrentContent() {
    currentContentId.value = null
    drafts.value = []
    localStorage.removeItem(CURRENT_CONTENT_KEY)
  }

  return {
    currentContentId,
    contents,
    drafts,
    setCurrentContentId,
    restoreCurrentContentId,
    clearCurrentContent,
  }
})
