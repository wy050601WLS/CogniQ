import api from './index'

export const login = (username, password) =>
  api.post('/auth/login', { username, password })

export const register = (username, email, password, nickname) =>
  api.post('/auth/register', { username, email, password, nickname })

export const getMe = () => api.get('/auth/me')

export const updateProfile = (data) => api.put('/auth/me', data)

export const changePassword = (data) => api.put('/auth/password', data)

export const uploadAvatar = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
