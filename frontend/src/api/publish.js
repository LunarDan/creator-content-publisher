import http from './http'

export const publishApi = {
  simulate: (platform_draft_id) => http.post('/publish/simulate', { platform_draft_id }),
  simulateBatch: (platformDraftIds) => http.post('/publish/simulate-batch', { platform_draft_ids: platformDraftIds }),
  browserBilibili: (platform_draft_id, auto_publish = true) => http.post('/publish/bilibili/browser', { platform_draft_id, auto_publish }),
  browserDouyin: (platform_draft_id, auto_publish = true) => http.post('/publish/douyin/browser', { platform_draft_id, auto_publish }),
  wechatDraft: (platform_draft_id) => http.post('/publish/wechat/draft', { platform_draft_id }),
  wechatConfig: () => http.get('/publish/wechat/config'),
  wechatTokenCheck: () => http.get('/publish/wechat/token-check'),
  completeManual: (taskId, publish_url) => http.post(`/publish/tasks/${taskId}/complete-manual`, { publish_url }),
  tasks: () => http.get('/publish/tasks'),
}
