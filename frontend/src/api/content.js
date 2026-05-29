import http from './http'

export const contentApi = {
  list: () => http.get('/contents'),
  create: (data) => http.post('/contents', data),
  update: (id, data) => http.put(`/contents/${id}`, data),
  delete: (id) => http.delete(`/contents/${id}`),
  get: (id) => http.get(`/contents/${id}`),
  adapt: (id, platforms) => http.post(`/contents/${id}/adapt`, { platforms }),
  drafts: (id) => http.get(`/contents/${id}/platform-drafts`),
  updateDraft: (draftId, data) => http.put(`/platform-drafts/${draftId}`, data),
}
