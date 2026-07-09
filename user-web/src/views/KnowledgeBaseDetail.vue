<template>
  <div class="kb-detail-page">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="header-info">
        <h1>{{ kb?.name || '加载中...' }}</h1>
        <div class="header-meta" v-if="kb">
          <el-tag size="small" v-if="kb.is_public" type="success">公开</el-tag>
          <el-tag size="small" v-if="kb.is_official" type="warning">官方</el-tag>
          <span class="meta-text">{{ kb.doc_count }} 篇文档</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="$router.push({ path: '/chat', query: { kbId: kb?.id } })">
          <el-icon><ChatDotRound /></el-icon> 开始问答
        </el-button>
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon> 上传文档
        </el-button>
      </div>
    </div>

    <!-- 知识库信息 -->
    <el-card v-if="kb" class="info-card">
      <div class="kb-info">
        <div class="info-item">
          <span class="info-label">嵌入模型</span>
          <span class="info-value">{{ kb.embedding_model }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">分块大小</span>
          <span class="info-value">{{ kb.chunk_size }} 字符</span>
        </div>
        <div class="info-item">
          <span class="info-label">分块重叠</span>
          <span class="info-value">{{ kb.chunk_overlap }} 字符</span>
        </div>
        <div class="info-item">
          <span class="info-label">创建时间</span>
          <span class="info-value">{{ formatDate(kb.created_at) }}</span>
        </div>
      </div>
      <p class="kb-desc" v-if="kb.description">{{ kb.description }}</p>
    </el-card>

    <!-- 文档列表 -->
    <el-card class="doc-card">
      <template #header>
        <div class="card-header">
          <span>文档列表</span>
          <el-button type="primary" size="small" @click="showUploadDialog = true">
            <el-icon><Plus /></el-icon> 上传
          </el-button>
        </div>
      </template>

      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <el-table v-else :data="documents" stripe>
        <el-table-column prop="filename" label="文件名">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon"><Document /></el-icon>
              {{ row.filename }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.file_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="80" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button text type="danger" size="small" @click="handleDeleteDoc(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && documents.length === 0" description="暂无文档">
        <el-button type="primary" @click="showUploadDialog = true">上传第一个文档</el-button>
      </el-empty>
    </el-card>

    <!-- 上传文档对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传文档" width="500px" :close-on-click-modal="false">
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        accept=".pdf,.docx,.doc,.md,.txt,.html,.htm"
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、Word、Markdown、TXT、HTML 格式，单个文件最大 50MB
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" class="selected-file">
        <el-icon><Document /></el-icon>
        <span>{{ selectedFile.name }}</span>
        <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
        <el-button text type="danger" @click="selectedFile = null">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading" :disabled="!selectedFile">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, ChatDotRound, Upload, Document, Plus, Close, Loading
} from '@element-plus/icons-vue'
import { getKnowledgeBase, getDocuments, uploadDocument, deleteDocument } from '../api/knowledgeBase'

const route = useRoute()
const router = useRouter()
const kb = ref(null)
const documents = ref([])
const loading = ref(true)
const showUploadDialog = ref(false)
const selectedFile = ref(null)
const uploading = ref(false)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [kbRes, docRes] = await Promise.all([
      getKnowledgeBase(route.params.id),
      getDocuments(route.params.id),
    ])
    kb.value = kbRes.data
    documents.value = docRes.data || []
  } catch (e) {
    console.error('加载失败:', e)
    ElMessage.error('加载知识库信息失败')
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

function handleFileChange(file) {
  const maxSize = 50 * 1024 * 1024
  if (file.raw.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    selectedFile.value = null
    return
  }
  selectedFile.value = file.raw
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  try {
    await uploadDocument(route.params.id, selectedFile.value)
    ElMessage.success('上传成功，文档正在处理中')
    showUploadDialog.value = false
    selectedFile.value = null
    await loadData()
  } catch (e) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleDeleteDoc(doc) {
  try {
    await ElMessageBox.confirm(`确定删除文档 ${doc.filename}？`, '确认删除', {
      type: 'warning'
    })
    await deleteDocument(doc.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.kb-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-info {
  flex: 1;
}

.header-info h1 {
  margin: 0 0 4px;
  font-size: 24px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-text {
  font-size: 13px;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.info-card {
  margin-bottom: 20px;
}

.kb-info {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #94a3b8;
}

.info-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}

.kb-desc {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

.doc-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #94a3b8;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #94a3b8;
}

.upload-area {
  width: 100%;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  margin-top: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.selected-file .file-size {
  flex: 1;
  text-align: right;
  color: #94a3b8;
  font-size: 13px;
}
</style>
