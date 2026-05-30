import http from './http'

export const publishApi = {
  simulate: (platform_draft_id) => http.post('/publish/simulate', { platform_draft_id }),
  simulateBatch: (platformDraftIds) => http.post('/publish/simulate-batch', { platform_draft_ids: platformDraftIds }),
  browserBilibili: (platform_draft_id, auto_publish = true) => http.post('/publish/bilibili/browser', { platform_draft_id, auto_publish }),
  completeManual: (taskId, publish_url) => http.post(`/publish/tasks/${taskId}/complete-manual`, { publish_url }),
  tasks: () => http.get('/publish/tasks'),
}
