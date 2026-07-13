<template>
  <div class="shared-page">
    <div class="page-header">
      <h1>知识广场</h1>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索文件..."
        prefix-icon="Search"
        clearable
        style="width: 300px"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 文件列表 -->
    <div v-else class="file-grid">
      <div
        v-for="file in filteredFiles"
        :key="file.id"
        class="file-card"
      >
        <div class="file-icon" :class="getFileTypeClass(file.file_type)">
          <el-icon><Document /></el-icon>
        </div>
        <div class="file-info">
          <h3>{{ file.filename }}</h3>
          <p>{{ file.description || '暂无描述' }}</p>
          <div class="file-meta">
            <span><el-icon><Document /></el-icon> {{ file.file_type.toUpperCase() }}</span>
            <span><el-icon><View /></el-icon> {{ file.view_count }} 次查看</span>
            <span><el-icon><CopyDocument /></el-icon> {{ file.copy_count }} 次添加</span>
            <span class="file-uploader">上传人: {{ file.uploader_name || '未知' }}</span>
          </div>
        </div>
        <div class="file-actions">
          <el-button type="primary" size="small" @click="handleAdd(file)" :loading="copyingId === file.id">
            添加
          </el-button>
        </div>
      </div>
      <el-empty v-if="filteredFiles.length === 0 && !loading" description="暂无公开文件" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, View, CopyDocument, Loading, Search } from '@element-plus/icons-vue'
import { getSharedFiles, addFile } from '../api/files'

const files = ref([])
const loading = ref(true)
const copyingId = ref(null)
const searchText = ref('')

const filteredFiles = computed(() => {
  if (!searchText.value) return files.value
  const keyword = searchText.value.toLowerCase()
  return files.value.filter(file =>
    file.filename.toLowerCase().includes(keyword) ||
    (file.description && file.description.toLowerCase().includes(keyword))
  )
})

onMounted(async () => {
  try {
    const { data } = await getSharedFiles()
    files.value = data || []
  } catch (e) {
    console.error('加载文件失败:', e)
    ElMessage.error('加载公开文件失败')
  } finally {
    loading.value = false
  }
})

function getFileTypeClass(type) {
  const classes = {
    pdf: 'type-pdf',
    docx: 'type-word',
    doc: 'type-word',
    md: 'type-md',
    txt: 'type-txt',
    html: 'type-html'
  }
  return classes[type] || ''
}

async function handleAdd(file) {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    return
  }

  copyingId.value = file.id
  try {
    await addFile(file.id)
    ElMessage.success(`已添加「${file.filename}」到我的文件`)
    // 更新引用次数
    files.value = files.value.map(item =>
      item.id === file.id ? { ...item, copy_count: (item.copy_count || 0) + 1 } : item
    )
  } catch (e) {
    if (e.response?.data?.error?.message) {
      ElMessage.error(e.response.data.error.message)
    } else {
      ElMessage.error('添加失败，请重试')
    }
  } finally {
    copyingId.value = null
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

.search-bar {
  margin-bottom: 24px;
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

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.file-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.file-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.file-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 12px;
  background: #f1f5f9;
  color: #64748b;
}

.file-icon.type-pdf { background: #fee2e2; color: #ef4444; }
.file-icon.type-word { background: #dbeafe; color: #3b82f6; }
.file-icon.type-md { background: #dcfce7; color: #22c55e; }
.file-icon.type-txt { background: #f1f5f9; color: #64748b; }
.file-icon.type-html { background: #ffedd5; color: #f97316; }

.file-info {
  flex: 1;
}

.file-info h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #1e293b;
}

.file-info p {
  margin: 0 0 12px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.file-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.file-uploader {
  color: #3b82f6;
}

.file-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}
</style>
