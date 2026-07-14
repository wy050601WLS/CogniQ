import api from './index'

// 文件管理
export const getMyFiles = (params) => api.get('/files', { params })
export const uploadFile = (file, description, tagIds) => {
  const formData = new FormData()
  formData.append('file', file)
  if (description) {
    formData.append('description', description)
  }
  if (tagIds && tagIds.length > 0) {
    formData.append('tag_ids', tagIds.join(','))
  }
  return api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const getFile = (id) => api.get(`/files/${id}`)
export const updateFile = (id, data) => api.put(`/files/${id}`, data)
export const deleteFile = (id) => api.delete(`/files/${id}`)
export const replaceFile = (id, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.put(`/files/${id}/replace`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const generateDescription = (id) => api.post(`/files/${id}/description`)
export const getFileVersions = (id) => api.get(`/files/${id}/versions`)
export const rollbackVersion = (id, version) => api.post(`/files/${id}/rollback/${version}`)

// 文件分享
export const getSharedFiles = (params) => api.get('/files/shared', { params })
export const addFile = (id) => api.post(`/files/${id}/add`)

// 文件预览
export const previewFile = (id) => api.get(`/files/${id}/preview`)

// 对话
export const getConversations = (params) => api.get('/conversations', { params })
export const createConversation = (data) => api.post('/conversations', data)
export const getMessages = (id) => api.get(`/conversations/${id}/messages`)
export const deleteConversation = (id) => api.delete(`/conversations/${id}`)
export const searchConversations = (q) => api.get('/conversations/search', { params: { q } })

// 聊天（流式）
export const chatStream = async (data, onChunk, onSources, onEnd) => {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('未登录')
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 120000)

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ ...data, stream: true }),
      signal: controller.signal,
    })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('登录已过期，请重新登录')
      }
      throw new Error(`请求失败: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === 'chunk') onChunk(event.content)
            if (event.type === 'sources') onSources(event.documents)
            if (event.type === 'end') onEnd(event)
          } catch (e) {
            console.warn('SSE parse error:', e)
          }
        }
      }
    }

    // 处理 buffer 中剩余的数据
    if (buffer.startsWith('data: ')) {
      try {
        const event = JSON.parse(buffer.slice(6))
        if (event.type === 'chunk') onChunk(event.content)
        if (event.type === 'sources') onSources(event.documents)
        if (event.type === 'end') onEnd(event)
      } catch (e) {
        console.warn('SSE parse error:', e)
      }
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('回答超时，请稍后重试')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

// 反馈
export const submitFeedback = (data) => api.post('/feedback', data)
