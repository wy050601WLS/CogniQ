import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login } from '../api'

export const useAdminAuthStore = defineStore('adminAuth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const user = ref(null)

  // 初始化时从 localStorage 加载用户信息
  const savedUser = localStorage.getItem('admin_user')
  if (savedUser) {
    try {
      user.value = JSON.parse(savedUser)
    } catch {
      user.value = null
    }
  }

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const username = computed(() => user.value?.nickname || user.value?.username || '管理员')

  async function doLogin(username, password) {
    const { data } = await login(username, password)

    if (data.user?.role !== 'admin') {
      throw new Error('需要管理员权限才能访问')
    }

    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('admin_token', data.access_token)
    localStorage.setItem('admin_user', JSON.stringify(data.user))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  }

  return { token, user, isLoggedIn, isAdmin, username, doLogin, logout }
})
