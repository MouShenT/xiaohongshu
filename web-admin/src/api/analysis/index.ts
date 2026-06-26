import http from '@/utils/http'

export const credentialApi = {
  list() {
    return http.get('/credential')
  },
  create(name: string, cookies: string) {
    return http.post('/credential', { name, cookies })
  },
  delete(id: number) {
    return http.delete(`/credential/${id}`)
  },
}

export const taskApi = {
  create(data: { type: string; params?: Record<string, any>; credentialId?: number }) {
    return http.post('/task', data)
  },
  get(id: number) {
    return http.get(`/task/${id}`)
  },
  list(params?: { page?: number; size?: number; status?: string }) {
    return http.get('/task', { params })
  },
}

export const hotRadarApi = {
  getTrending(limit = 20) {
    return http.get('/analysis/hot-radar/trending', { params: { limit } })
  },
  analyze(keyword: string) {
    return http.post('/analysis/hot-radar/analyze', { keyword })
  },
}

export const articleApi = {
  analyze(noteId: string) {
    return http.post('/analysis/article/analyze', { noteId })
  },
}

export const noteApi = {
  search(params: { keyword: string; limit?: number; sort?: string }) {
    return http.get('/note/search', { params })
  },
  detail(noteId: string) {
    return http.get(`/note/${noteId}`)
  },
  comments(noteId: string, limit = 50) {
    return http.get(`/note/${noteId}/comments`, { params: { limit } })
  },
}
