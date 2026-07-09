import api from './index'

// 知识库
export const getMarketplace = () => api.get('/knowledge-bases/marketplace')
export const getMyKnowledgeBases = () => api.get('/knowledge-bases/my')
export const createKnowledgeBase = (data) => api.post('/knowledge-bases', data)
export const getKnowledgeBase = (id) => api.get(`/knowledge-bases/${id}`)
export const updateKnowledgeBase = (id, data) => api.put(`/knowledge-bases/${id}`, data)
export const deleteKnowledgeBase = (id) => api.delete(`/knowledge-bases/${id}`)
export const copyKnowledgeBase = (id) => api.post(`/knowledge-bases/${id}/copy`)

// 文档
export const getDocuments = (kbId) => api.get(`/knowledge-bases/${kbId}/documents`)
export const uploadDocument = (kbId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/knowledge-bases/${kbId}/documents/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const deleteDocument = (id) => api.delete(`/documents/${id}`)

// 对话
export const getConversations = () => api.get('/conversations')
export const createConversation = (data) => api.post('/conversations', data)
export const getMessages = (id) => api.get(`/conversations/${id}/messages`)
export const deleteConversation = (id) => api.delete(`/conversations/${id}`)
export const searchConversations = (q) => api.get(`/conversations/search`, { params: { q } })

// 聊天（流式）
export const chatStream = async (data, onChunk, onSources, onEnd) => {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('未登录')
  }

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ ...data, stream: true }),
    })

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
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
      // 保留最后一个可能不完整的行在 buffer 中
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === 'chunk') onChunk(event.content)
            if (event.type === 'sources') onSources(event.documents)
            if (event.type === 'end') onEnd(event)
          } catch (e) {
            // 忽略解析错误
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
        // 忽略解析错误
      }
    }
  } catch (error) {
    if (error.message === '未登录') {
      window.location.href = '/login'
    }
    throw error
  }
}

// 收藏
export const getFavorites = () => api.get('/favorites')
export const addFavorite = (kbId) => api.post('/favorites', { knowledge_base_id: kbId })
export const removeFavorite = (id) => api.delete(`/favorites/${id}`)

// 反馈
export const submitFeedback = (data) => api.post('/feedback', data)
