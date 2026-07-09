<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <span class="user-count">共 {{ users.length }} 个用户</span>
        </div>
      </template>

      <!-- 搜索 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索用户名或邮箱..."
          prefix-icon="Search"
          clearable
          style="width: 250px"
        />
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <el-table v-else :data="filteredUsers" stripe>
        <el-table-column prop="username" label="用户名">
          <template #default="{ row }">
            <div class="user-name">
              <div class="user-avatar">{{ (row.username || '?')[0].toUpperCase() }}</div>
              <div>
                <div class="name-text">{{ row.username }}</div>
                <div class="name-email">{{ row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="昵称" width="120">
          <template #default="{ row }">
            {{ row.nickname || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : ''">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleToggleStatus(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              @click="handleDelete(row)"
              :disabled="row.id === currentUserId"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredUsers.length === 0" description="暂无用户" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getUsers, deleteUser, updateUser } from '../api'

const users = ref([])
const loading = ref(true)
const searchText = ref('')
const currentUserId = ref('')

const filteredUsers = computed(() => {
  if (!searchText.value) return users.value
  const keyword = searchText.value.toLowerCase()
  return users.value.filter(user =>
    user.username.toLowerCase().includes(keyword) ||
    user.email.toLowerCase().includes(keyword) ||
    (user.nickname && user.nickname.toLowerCase().includes(keyword))
  )
})

onMounted(async () => {
  // 获取当前登录的管理员 ID
  const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}')
  currentUserId.value = adminUser.id || ''
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getUsers()
    users.value = data || []
  } catch (e) {
    console.error('加载用户失败:', e)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleToggleStatus(user) {
  const newStatus = user.status === 'active' ? 'disabled' : 'active'
  const actionText = newStatus === 'disabled' ? '禁用' : '启用'

  try {
    await ElMessageBox.confirm(`确定${actionText}用户 ${user.username}？`, '确认')
    await updateUser(user.id, { status: newStatus })
    user.status = newStatus
    ElMessage.success(`已${actionText}`)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(`${actionText}失败`)
    }
  }
}

async function handleDelete(user) {
  try {
    await ElMessageBox.confirm(
      `确定删除用户 ${user.username}？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteUser(user.id)
    users.value = users.value.filter(u => u.id !== user.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-count {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}

.filter-bar {
  margin-bottom: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 0;
  color: #94a3b8;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: #1e293b;
}

.name-email {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}
</style>
