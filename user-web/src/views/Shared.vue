<template>
  <div class="shared-page">
    <div class="page-header">
      <h1>知识广场</h1>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索文件名..."
        prefix-icon="Search"
        clearable
        style="width: 250px"
      />
      <el-select v-model="fileTypeFilter" placeholder="文件格式" clearable style="width: 120px">
        <el-option v-for="t in fileTypeOptions" :key="t" :label="t.toUpperCase()" :value="t" />
      </el-select>
      <el-select v-model="uploaderFilter" placeholder="上传人" clearable style="width: 140px">
        <el-option v-for="u in uploaderOptions" :key="u" :label="u" :value="u" />
      </el-select>
      <el-select v-model="tagFilter" placeholder="标签" clearable style="width: 140px">
        <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
      </el-select>
      <el-select v-model="sortBy" placeholder="排序方式" style="width: 160px">
        <el-option label="最新上传" value="newest_desc" />
        <el-option label="最早上传" value="newest_asc" />
        <el-option label="热度最高" value="hot_desc" />
        <el-option label="热度最低" value="hot_asc" />
        <el-option label="查看最多" value="views_desc" />
        <el-option label="查看最少" value="views_asc" />
      </el-select>
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
import { getFileTypeClass } from '../utils/format'

const files = ref([])
const loading = ref(true)
const copyingId = ref(null)
const searchText = ref('')
const fileTypeFilter = ref('')
const uploaderFilter = ref('')
const tagFilter = ref('')
const sortBy = ref('newest_desc')

const fileTypeOptions = computed(() => {
  const types = new Set(files.value.map(f => f.file_type))
  return [...types].sort()
})

const uploaderOptions = computed(() => {
  const names = new Set(files.value.map(f => f.uploader_name || '未知'))
  return [...names].sort()
})

const tagOptions = computed(() => {
  const tags = new Set()
  files.value.forEach(f => {
    if (f.tags) f.tags.forEach(t => tags.add(t.name))
  })
  return [...tags].sort()
})

const filteredFiles = computed(() => {
  let result = files.value

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    result = result.filter(file =>
      file.filename.toLowerCase().includes(keyword) ||
      (file.description && file.description.toLowerCase().includes(keyword))
    )
  }

  if (fileTypeFilter.value) {
    result = result.filter(file => file.file_type === fileTypeFilter.value)
  }

  if (uploaderFilter.value) {
    result = result.filter(file => (file.uploader_name || '未知') === uploaderFilter.value)
  }

  if (tagFilter.value) {
    result = result.filter(file => file.tags && file.tags.some(t => t.name === tagFilter.value))
  }

  if (sortBy.value) {
    const [field, order] = sortBy.value.split('_')
    const desc = order === 'desc' ? 1 : -1
    result = [...result].sort((a, b) => {
      switch (field) {
        case 'newest': return desc * (new Date(b.updated_at) - new Date(a.updated_at))
        case 'hot': return desc * ((b.copy_count || 0) - (a.copy_count || 0))
        case 'views': return desc * ((b.view_count || 0) - (a.view_count || 0))
        default: return 0
      }
    })
  }

  return result
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

async function handleAdd(file) {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    return
  }

  copyingId.value = file.id
  try {
    await addFile(file.id)
    ElMessage.success(`已添加「${file.filename}」，可在"我的文件"中查看`)
    // 更新引用次数
    files.value = files.value.map(item =>
      item.id === file.id ? { ...item, copy_count: (item.copy_count || 0) + 1 } : item
    )
  } catch (e) {
    // 错误由 axios 拦截器统一处理
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

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
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

/* 深色模式 */
.dark .file-card {
  background: #1e293b;
  border-color: #334155;
}

.dark .file-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.dark .file-icon {
  background: #334155;
  color: #94a3b8;
}

.dark .file-info h3 {
  color: #e2e8f0;
}

.dark .file-info p {
  color: #94a3b8;
}

.dark .file-meta {
  color: #64748b;
}

.dark .file-actions {
  border-top-color: #334155;
}
</style>
