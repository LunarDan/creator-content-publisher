import http from './http'

export const publishApi = {
  simulate: (platform_draft_id) => http.post('/publish/simulate', { platform_draft_id }),
  tasks: () => http.get('/publish/tasks'),
}
