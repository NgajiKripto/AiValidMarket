import apiClient from './index'

export function submitIdea(ideaText) {
  return apiClient.post('/api/validation/validate', { idea: ideaText })
}

export function getValidationStatus(taskId) {
  return apiClient.get(`/api/validation/status/${taskId}`)
}

export function getValidationResult(taskId) {
  return apiClient.get(`/api/validation/result/${taskId}`)
}

export function chatWithAgent(taskId, message, chatHistory) {
  return apiClient.post('/api/validation/chat', {
    task_id: taskId,
    message,
    chat_history: chatHistory
  })
}
