import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const isInitialized = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  async function doLogin(username, password) {
    const { data } = await login(username, password)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    isInitialized.value = true
  }

  async function doRegister(username, email, password, nickname) {
    const { data } = await register(username, email, password, nickname)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    isInitialized.value = true
  }

  async function fetchUser() {
    if (!token.value) {
      isInitialized.value = true
      return
    }
    try {
      const { data } = await getMe()
      user.value = data
    } catch (e) {
      logout()
    } finally {
      isInitialized.value = true
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    isInitialized.value = true
  }

  // 如果有 token，自动获取用户信息
  if (token.value) {
    fetchUser()
  } else {
    isInitialized.value = true
  }

  return { token, user, isLoggedIn, isInitialized, doLogin, doRegister, fetchUser, logout }
})
