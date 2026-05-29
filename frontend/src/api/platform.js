import http from './http'

export const platformApi = {
  list: () => http.get('/platforms'),
}
