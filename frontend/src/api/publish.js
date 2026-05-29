import http from './http'

export const publishApi = {
  simulate: (platform_draft_id) => http.post('/publish/simulate', { platform_draft_id }),
  simulateBatch: (platformDraftIds) => http.post('/publish/simulate-batch', { platform_draft_ids: platformDraftIds }),
  tasks: () => http.get('/publish/tasks'),
}
