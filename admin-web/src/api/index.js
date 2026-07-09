import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.error?.message
      || error.response?.data?.detail
      || error.message
      || '请求失败'

    if (status === 401) {
      // 清除所有认证状态
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (status >= 500) {
      ElMessage.error('服务器错误')
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

export default api

// 认证
export const login = (username, password) => api.post('/auth/login', { username, password })

// 用户管理
export const getUsers = () => api.get('/admin/users')
export const getUser = (id) => api.get(`/admin/users/${id}`)
export const updateUser = (id, data) => api.put(`/admin/users/${id}`, data)
export const deleteUser = (id) => api.delete(`/admin/users/${id}`)

// 知识库管理
export const getAdminKnowledgeBases = () => api.get('/admin/knowledge-bases')
export const deleteAdminKnowledgeBase = (id) => api.delete(`/admin/knowledge-bases/${id}`)

// 文档管理
export const getAdminDocuments = () => api.get('/admin/documents')
export const deleteAdminDocument = (id) => api.delete(`/admin/documents/${id}`)

// 统计
export const getOverviewStats = () => api.get('/admin/stats/overview')
export const getUserStats = () => api.get('/admin/stats/users')
export const getTrends = () => api.get('/admin/stats/trends')

// 设置（使用统一的 /settings 端点）
export const getAdminSettings = () => api.get('/settings')
export const updateAdminSettings = (data) => api.put('/settings', data)
