<template>
  <div class="history-page">
    <div class="page-header">
      <h1>对话历史</h1>
      <el-input
        v-model="searchQuery"
        placeholder="搜索对话..."
        prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="handleSearch"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 对话列表 -->
    <div v-else class="conv-list">
      <div
        v-for="conv in filteredConversations"
        :key="conv.id"
        class="conv-item"
        @click="openConversation(conv)"
      >
        <div class="conv-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="conv-info">
          <div class="conv-title">{{ conv.title }}</div>
          <div class="conv-time">{{ formatTime(conv.updated_at) }}</div>
        </div>
        <el-button text type="danger" size="small" @click.stop="handleDelete(conv)">
          删除
        </el-button>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredConversations.length === 0" class="empty-state">
        <el-empty :description="searchQuery ? '未找到匹配的对话' : '暂无对话记录'">
          <el-button v-if="!searchQuery" type="primary" @click="$router.push('/chat')">开始新对话</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Loading, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getConversations, deleteConversation, searchConversations } from '../api/files'

const router = useRouter()
const conversations = ref([])
const loading = ref(true)
const searchQuery = ref('')
const searchResults = ref(null)

const filteredConversations = computed(() => {
  return searchResults.value !== null ? searchResults.value : conversations.value
})

let searchTimeout = null
function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!searchQuery.value.trim()) {
    searchResults.value = null
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const { data } = await searchConversations(searchQuery.value)
      searchResults.value = data.results || []
    } catch (e) {
      console.error('搜索失败:', e)
    }
  }, 300)
}

onMounted(async () => {
  await loadData()
})

onUnmounted(() => {
  if (searchTimeout) clearTimeout(searchTimeout)
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getConversations()
    conversations.value = data || []
  } catch (e) {
    console.error('加载对话失败:', e)
    ElMessage.error('加载对话历史失败')
  } finally {
    loading.value = false
  }
}

function formatTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / 86400000)

  if (days === 0) return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  if (days === 1) return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

function openConversation(conv) {
  router.push({ path: '/chat', query: { convId: conv.id } })
}

async function handleDelete(conv) {
  try {
    await ElMessageBox.confirm('确定删除该对话？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteConversation(conv.id)
    conversations.value = conversations.value.filter(c => c.id !== conv.id)
    if (searchResults.value) {
      searchResults.value = searchResults.value.filter(c => c.id !== conv.id)
    }
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 0;
  color: #94a3b8;
}

.conv-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.conv-item:hover {
  background: #f5f7fa;
}

.conv-item:last-child {
  border-bottom: none;
}

.conv-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-title {
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.empty-state {
  padding: 60px 0;
}

/* 深色模式 */
.dark .history-page {
  background: #0f172a;
}

.dark .conv-list {
  background: #1e293b;
  border-color: #334155;
}

.dark .conv-item {
  border-bottom-color: #334155;
}

.dark .conv-item:hover {
  background: #334155;
}

.dark .conv-item.active {
  background: rgba(59, 130, 246, 0.15);
  border-left-color: #3b82f6;
}

.dark .conv-title {
  color: #e2e8f0;
}

.dark .conv-preview {
  color: #94a3b8;
}

.dark .conv-time {
  color: #64748b;
}
</style>
