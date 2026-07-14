import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Token 刷新队列
let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status
    const originalRequest = error.config

    // 401 未授权 — 尝试刷新 Token
    if (status === 401 && !originalRequest._retry) {
      // 跳过 refresh 接口本身的 401（避免死循环）
      if (originalRequest.url === '/auth/refresh') {
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        router.push('/login')
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // 动态导入避免循环依赖
        const { useAuthStore } = await import('../stores/auth')
        const authStore = useAuthStore()
        const newToken = await authStore.doRefreshToken()
        processQueue(null, newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        router.push('/login')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    const message = error.response?.data?.error?.message
      || error.response?.data?.detail
      || error.message
      || '请求失败'

    // 403 禁止
    if (status === 403) {
      ElMessage.error('没有权限执行此操作')
      return Promise.reject(error)
    }

    // 404 未找到
    if (status === 404) {
      ElMessage.warning('请求的资源不存在')
      return Promise.reject(error)
    }

    // 500 服务器错误
    if (status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
      return Promise.reject(error)
    }

    // 超时
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络')
      return Promise.reject(error)
    }

    // 其他错误
    if (message !== '登录已过期，请重新登录') {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default api
