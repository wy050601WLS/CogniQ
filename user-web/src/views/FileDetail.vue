<template>
  <div class="file-detail-page">
    <div class="page-header">
      <el-button text @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h1>{{ file?.filename || '文件详情' }}</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="file" class="detail-content">
      <!-- 文件信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>文件信息</span>
            <div class="card-actions" v-if="file.owner_id === currentUserId && !file.is_copied">
              <el-button type="primary" size="small" @click="editFile">编辑</el-button>
              <el-button type="warning" size="small" @click="replaceFile">替换内容</el-button>
              <el-button type="danger" size="small" @click="handleDelete">删除</el-button>
            </div>
            <div class="card-actions" v-else-if="file.is_copied">
              <el-tag type="info" size="small">复制文件 - 无修改权</el-tag>
            </div>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ file.filename }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ file.file_type.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(file.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="版本">v{{ file.version }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(file.status)" size="small">{{ getStatusText(file.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="可见性">
            <el-switch v-model="file.is_public" @change="togglePublic" :disabled="file.owner_id !== currentUserId || file.is_copied" />
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ file.description || '暂无描述' }}</el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ formatDate(file.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(file.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="分块数">{{ file.chunk_count }}</el-descriptions-item>
          <el-descriptions-item label="被复制次数">{{ file.copy_count }}</el-descriptions-item>
          <el-descriptions-item label="上传人">{{ file.uploader_name || '未知' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 标签管理 -->
      <el-card class="tags-card">
        <template #header>
          <div class="card-header">
            <span>标签</span>
            <el-button v-if="file.owner_id === currentUserId && !file.is_copied" text size="small" @click="showTagDialog = true">
              <el-icon><Edit /></el-icon> 编辑标签
            </el-button>
          </div>
        </template>
        <div class="tags-list">
          <el-tag v-for="tag in file.tags" :key="tag.id" :style="{ backgroundColor: tag.color, color: '#fff' }">
            {{ tag.name }}
          </el-tag>
          <span v-if="!file.tags || file.tags.length === 0" class="no-tags">暂无标签</span>
        </div>
      </el-card>

      <!-- 文件预览 -->
      <el-card class="preview-card">
        <template #header>
          <div class="card-header">
            <span>文件预览</span>
            <el-button text size="small" @click="loadPreview">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </template>
        <div v-if="previewLoading" class="preview-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载预览...</span>
        </div>
        <div v-else-if="previewContent" class="preview-content">
          <pre>{{ previewContent }}</pre>
        </div>
        <div v-else class="preview-empty">
          <span>暂无预览内容</span>
        </div>
      </el-card>

      <!-- 版本历史 -->
      <el-card class="versions-card">
        <template #header>
          <div class="card-header">
            <span>版本历史</span>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="version in versions"
            :key="version.id"
            :timestamp="formatDate(version.created_at)"
            placement="top"
          >
            <div class="version-item">
              <span class="version-number">v{{ version.version }}</span>
              <span class="version-filename">{{ version.filename }}</span>
              <span class="version-size">{{ formatFileSize(version.file_size) }}</span>
              <el-button v-if="file.version !== version.version" text size="small" @click="handleRollback(version.version)">
                回滚
              </el-button>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑文件信息" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文件名">
          <el-input v-model="editForm.filename" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 标签编辑对话框 -->
    <el-dialog v-model="showTagDialog" title="编辑标签" width="400px">
      <el-select v-model="selectedTagIds" multiple placeholder="选择标签" style="width: 100%">
        <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name" :value="tag.id" />
      </el-select>
      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTags">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Loading, Edit, Refresh } from '@element-plus/icons-vue'
import { getFile, updateFile, replaceFile, deleteFile, getFileVersions, rollbackVersion, previewFile } from '../api/files'
import { useAuthStore } from '../stores/auth'
import api from '../api/index'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const file = ref(null)
const loading = ref(true)
const previewLoading = ref(false)
const previewContent = ref('')
const versions = ref([])

// 编辑相关
const showEditDialog = ref(false)
const editForm = ref({ filename: '', description: '' })

// 标签相关
const showTagDialog = ref(false)
const selectedTagIds = ref([])
const allTags = ref([])

onMounted(async () => {
  await loadFile()
  await loadVersions()
  await loadTags()
})

async function loadFile() {
  loading.value = true
  try {
    const { data } = await getFile(route.params.id)
    file.value = data
    await loadPreview()
  } catch (e) {
    ElMessage.error('加载文件失败')
    router.back()
  } finally {
    loading.value = false
  }
}

async function loadVersions() {
  try {
    const { data } = await getFileVersions(route.params.id)
    versions.value = data || []
  } catch (e) {
    console.error('加载版本历史失败:', e)
  }
}

async function loadTags() {
  try {
    const { data } = await api.get('/tags')
    allTags.value = data || []
  } catch (e) {
    console.error('加载标签失败:', e)
  }
}

async function loadPreview() {
  previewLoading.value = true
  try {
    const { data } = await previewFile(route.params.id)
    previewContent.value = data.content || ''
  } catch (e) {
    console.error('加载预览失败:', e)
  } finally {
    previewLoading.value = false
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getStatusType(status) {
  const types = { completed: 'success', processing: 'warning', pending: 'info', error: 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { completed: '已完成', processing: '处理中', pending: '等待中', error: '失败' }
  return texts[status] || status
}

function editFile() {
  editForm.value = {
    filename: file.value.filename,
    description: file.value.description || ''
  }
  showEditDialog.value = true
}

async function handleEdit() {
  try {
    await updateFile(file.value.id, editForm.value)
    ElMessage.success('保存成功')
    showEditDialog.value = false
    await loadFile()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function togglePublic() {
  try {
    await updateFile(file.value.id, { is_public: file.value.is_public })
    ElMessage.success(file.value.is_public ? '已设为公开' : '已设为私有')
  } catch (e) {
    file.value.is_public = !file.value.is_public
    ElMessage.error('操作失败')
  }
}

function replaceFile() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.pdf,.docx,.doc,.md,.txt,.html,.htm'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      await replaceFile(file.value.id, file)
      ElMessage.success('文件替换成功')
      await loadFile()
      await loadVersions()
    } catch (e) {
      ElMessage.error('替换失败')
    }
  }
  input.click()
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除该文件？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteFile(file.value.id)
    ElMessage.success('删除成功')
    router.push('/files')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleSaveTags() {
  try {
    await updateFile(file.value.id, { tag_ids: selectedTagIds.value })
    ElMessage.success('标签更新成功')
    showTagDialog.value = false
    await loadFile()
  } catch (e) {
    ElMessage.error('更新标签失败')
  }
}

async function handleRollback(version) {
  try {
    await ElMessageBox.confirm(`确定回滚到 v${version}？`, '确认回滚', {
      confirmButtonText: '回滚',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await rollbackVersion(file.value.id, version)
    ElMessage.success('回滚成功')
    await loadFile()
    await loadVersions()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('回滚失败')
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
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

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card, .tags-card, .preview-card, .versions-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.no-tags {
  color: #94a3b8;
  font-size: 14px;
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: #94a3b8;
}

.preview-content {
  max-height: 400px;
  overflow-y: auto;
}

.preview-content pre {
  margin: 0;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.preview-empty {
  text-align: center;
  padding: 40px 0;
  color: #94a3b8;
}

.version-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.version-number {
  font-weight: 600;
  color: #3b82f6;
}

.version-filename {
  color: #1e293b;
}

.version-size {
  color: #94a3b8;
  font-size: 12px;
}
</style>
