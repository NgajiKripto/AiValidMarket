import apiClient from './index'

export function getMemorySessions(limit = 10, offset = 0) {
  return apiClient.get('/api/memory/sessions', { params: { limit, offset } })
}

export function searchMemories(query, limit = 5, type = null) {
  return apiClient.post('/api/memory/search', { query, limit, type })
}

export function getMemoryStats() {
  return apiClient.get('/api/memory/stats')
}

export function getSessionDetail(sessionId) {
  return apiClient.get(`/api/memory/sessions/${sessionId}`)
}

export function deleteMemory(memoryId) {
  return apiClient.delete(`/api/memory/${memoryId}`)
}
