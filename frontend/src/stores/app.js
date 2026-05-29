import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const platforms = ref([])
  const loading = ref(false)

  return { platforms, loading }
})
