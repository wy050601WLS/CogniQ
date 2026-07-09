<template>
  <div class="profile-page">
    <h1>个人中心</h1>

    <!-- 头像 -->
    <el-card class="avatar-card">
      <template #header>
        <div class="card-header">
          <span>头像</span>
        </div>
      </template>
      <div class="avatar-section">
        <div class="avatar-preview">
          <img v-if="user?.avatar" :src="user.avatar" alt="头像" />
          <div v-else class="avatar-placeholder">{{ (user?.nickname || user?.username || 'U')[0] }}</div>
        </div>
        <div class="avatar-actions">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="handleAvatarChange"
          >
            <el-button type="primary" :loading="uploadingAvatar">更换头像</el-button>
          </el-upload>
          <p class="avatar-hint">支持 JPG/PNG/GIF/WebP，最大 5MB</p>
        </div>
      </div>
    </el-card>

    <!-- 基本信息 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="80px">
        <el-form-item label="用户名">
          <el-input :value="user?.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input :value="user?.email" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-tag :type="user?.role === 'admin' ? 'danger' : ''">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="profileForm.nickname" placeholder="请输入昵称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSaveProfile" :loading="saving">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 修改密码 -->
    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { uploadAvatar, updateProfile, changePassword } from '../api/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const saving = ref(false)
const changingPassword = ref(false)
const uploadingAvatar = ref(false)

const profileForm = ref({
  nickname: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileRules = {
  nickname: [
    { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

onMounted(async () => {
  await authStore.fetchUser()
  profileForm.value.nickname = user.value?.nickname || ''
})

async function handleAvatarChange(file) {
  const rawFile = file.raw
  if (!rawFile) return

  // 验证文件大小
  if (rawFile.size > 5 * 1024 * 1024) {
    ElMessage.error('头像文件大小不能超过 5MB')
    return
  }

  uploadingAvatar.value = true
  try {
    const { data } = await uploadAvatar(rawFile)
    // 更新 store 中的用户信息
    authStore.user.avatar = data.avatar_url
    ElMessage.success('头像上传成功')
  } catch (e) {
    ElMessage.error('头像上传失败')
  } finally {
    uploadingAvatar.value = false
  }
}

async function handleSaveProfile() {
  try {
    await profileFormRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    await updateProfile(profileForm.value)
    await authStore.fetchUser()
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleChangePassword() {
  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }

  changingPassword.value = true
  try {
    await changePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    ElMessage.success('密码修改成功')
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    passwordFormRef.value.resetFields()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}
</script>

<style scoped>
.profile-page h1 {
  margin: 0 0 24px;
  font-size: 24px;
}

.avatar-card,
.info-card,
.password-card {
  max-width: 500px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  font-weight: 600;
}

.avatar-hint {
  font-size: 12px;
  color: #94a3b8;
  margin: 8px 0 0;
}
</style>
