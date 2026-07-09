<template>
  <div class="docs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文档管理</span>
          <span class="total-count">共 {{ documents.length }} 个文档</span>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索文件名..."
          prefix-icon="Search"
          clearable
          style="width: 250px"
        />
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
          <el-option label="已完成" value="completed" />
          <el-option label="处理中" value="processing" />
          <el-option label="失败" value="error" />
        </el-select>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <el-table v-else :data="filteredDocs" stripe>
        <el-table-column prop="filename" label="文件名">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon" :class=" getFileTypeClass(row.file_type)">
                <Document />
              </el-icon>
              <div>
                <div class="name-text">{{ row.filename }}</div>
                <div class="name-meta">{{ formatFileSize(row.file_size) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getTagType(row.file_type)">
              {{ row.file_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="100" align="center" />
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button text type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredDocs.length === 0" description="暂无文档" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Loading } from '@element-plus/icons-vue'
import { getAdminDocuments, deleteAdminDocument } from '../api'

const documents = ref([])
const loading = ref(true)
const searchText = ref('')
const statusFilter = ref('')

const filteredDocs = computed(() => {
  let result = documents.value

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    result = result.filter(doc => doc.filename.toLowerCase().includes(keyword))
  }

  if (statusFilter.value) {
    result = result.filter(doc => doc.status === statusFilter.value)
  }

  return result
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getAdminDocuments()
    documents.value = data || []
  } catch (e) {
    console.error('加载文档失败:', e)
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

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

function getTagType(type) {
  const types = {
    pdf: 'danger',
    docx: '',
    doc: '',
    md: 'success',
    txt: 'info',
    html: 'warning'
  }
  return types[type] || 'info'
}

function getStatusType(status) {
  const types = {
    completed: 'success',
    processing: 'warning',
    pending: 'info',
    error: 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    completed: '已完成',
    processing: '处理中',
    pending: '等待中',
    error: '失败'
  }
  return texts[status] || status
}

async function handleDelete(doc) {
  try {
    await ElMessageBox.confirm(
      `确定删除文档「${doc.filename}」？此操作将删除相关向量数据，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteAdminDocument(doc.id)
    documents.value = documents.value.filter(d => d.id !== doc.id)
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

.total-count {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}

.filter-bar {
  display: flex;
  gap: 12px;
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

.file-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 24px;
  color: #94a3b8;
}

.file-icon.type-pdf { color: #ef4444; }
.file-icon.type-word { color: #3b82f6; }
.file-icon.type-md { color: #22c55e; }
.file-icon.type-txt { color: #94a3b8; }
.file-icon.type-html { color: #f97316; }

.name-text {
  font-weight: 500;
  color: #1e293b;
}

.name-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}
</style>
