<template>
  <div class="files-page">
    <div class="page-header">
      <h1>我的文件</h1>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon> 上传文件
      </el-button>
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
        <el-option label="文件最大" value="size_desc" />
        <el-option label="文件最小" value="size_asc" />
      </el-select>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 文件列表 -->
    <div v-else class="file-list">
      <div
        v-for="file in filteredFiles"
        :key="file.id"
        class="file-item"
        @click="openFile(file)"
      >
        <div class="file-icon" :class="getFileTypeClass(file.file_type)">
          <el-icon><Document /></el-icon>
        </div>
        <div class="file-info">
          <div class="file-name">{{ file.filename }}</div>
          <div class="file-desc">{{ file.description || '暂无描述' }}</div>
          <div class="file-meta">
            <span class="file-type">{{ file.file_type.toUpperCase() }}</span>
            <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
            <span class="file-uploader" v-if="file.owner_id !== currentUserId">上传人: {{ file.uploader_name }}</span>
            <span class="file-time">{{ formatDate(file.updated_at) }}</span>
          </div>
          <div class="file-tags" v-if="file.tags && file.tags.length > 0">
            <el-tag v-for="tag in file.tags" :key="tag.id" size="small" :style="{ backgroundColor: tag.color, color: '#fff' }">
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
        <div class="file-actions" @click.stop>
          <el-button text size="small" @click="openFile(file)">
            <el-icon><View /></el-icon> 查看
          </el-button>
          <el-button v-if="file.owner_id === currentUserId" text size="small" @click="editFile(file)">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <el-button v-if="file.owner_id === currentUserId || file.is_reference" text type="danger" size="small" @click="handleDelete(file)">
            <el-icon><Delete /></el-icon> 删除
          </el-button>
        </div>
      </div>

      <el-empty v-if="filteredFiles.length === 0 && !loading" description="暂无文件" />
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传文件" width="500px" :close-on-click-modal="false">
      <el-upload
        ref="uploadRef"
        drag
        multiple
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="uploadFileList"
        accept=".pdf,.docx,.doc,.md,.txt,.html,.htm"
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF、Word、Markdown、TXT、HTML 格式，单个文件最大 50MB</div>
        </template>
      </el-upload>
      <el-input v-model="uploadDescription" type="textarea" :rows="3" placeholder="文件描述（可选）" style="margin-top: 16px" />
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑文件信息" width="500px">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="文件名" prop="filename">
          <el-input v-model="editForm.filename" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="公开">
          <el-switch v-model="editForm.is_public" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEdit" :loading="editing">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Document, View, Edit, Delete, Loading, Search } from '@element-plus/icons-vue'
import { getMyFiles, uploadFile, updateFile, deleteFile } from '../api/files'
import { useAuthStore } from '../stores/auth'
import { formatFileSize, getFileTypeClass, formatDate } from '../utils/format'

const router = useRouter()
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const files = ref([])
const loading = ref(true)
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

// 上传相关
const showUploadDialog = ref(false)
const uploadFileList = ref([])
const uploadDescription = ref('')
const uploading = ref(false)

// 编辑相关
const showEditDialog = ref(false)
const editFormRef = ref(null)
const editForm = ref({ filename: '', description: '', is_public: false })
const editRules = {
  filename: [
    { required: true, message: '请输入文件名', trigger: 'blur' },
    { max: 255, message: '文件名不超过 255 个字符', trigger: 'blur' },
  ],
}
const editing = ref(false)
const editingFile = ref(null)

const filteredFiles = computed(() => {
  let result = files.value

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    result = result.filter(file => file.filename.toLowerCase().includes(keyword))
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
        case 'size': return desc * ((b.file_size || 0) - (a.file_size || 0))
        default: return 0
      }
    })
  }

  return result
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getMyFiles()
    files.value = data || []
  } catch (e) {
    console.error('加载文件失败:', e)
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

function openFile(file) {
  router.push(`/files/${file.id}`)
}

function editFile(file) {
  editingFile.value = file
  editForm.value = {
    filename: file.filename,
    description: file.description || '',
    is_public: file.is_public
  }
  showEditDialog.value = true
}

function handleFileChange(file) {
  uploadFileList.value.push(file)
}

async function handleUpload() {
  if (uploadFileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  const MAX_SIZE = 50 * 1024 * 1024
  const ALLOWED_TYPES = ['.pdf', '.docx', '.doc', '.md', '.txt', '.html', '.htm']

  for (const file of uploadFileList.value) {
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!ALLOWED_TYPES.includes(ext)) {
      ElMessage.error(`"${file.name}" 不支持的文件格式`)
      return
    }
    if (file.size > MAX_SIZE) {
      ElMessage.error(`"${file.name}" 文件大小不能超过 50MB`)
      return
    }
  }

  uploading.value = true
  try {
    for (const file of uploadFileList.value) {
      await uploadFile(file.raw, uploadDescription.value)
    }
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    uploadFileList.value = []
    uploadDescription.value = ''
    await loadData()
  } catch (e) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleEdit() {
  if (!editingFile.value) return
  if (editFormRef.value) {
    try {
      await editFormRef.value.validate()
    } catch {
      return
    }
  }

  editing.value = true
  try {
    await updateFile(editingFile.value.id, editForm.value)
    ElMessage.success('保存成功')
    showEditDialog.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    editing.value = false
  }
}

async function handleDelete(file) {
  try {
    await ElMessageBox.confirm('确定删除该文件？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteFile(file.id)
    files.value = files.value.filter(f => f.id !== file.id)
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

.file-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.file-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
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
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: #1e293b;
  font-size: 16px;
}

.file-desc {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.file-type {
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
}

.file-uploader {
  color: #3b82f6;
}

.file-tags {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.file-actions {
  display: flex;
  gap: 8px;
}

/* 深色模式 */
.dark .file-item {
  background: #1e293b;
  border-color: #334155;
}

.dark .file-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.dark .file-icon {
  background: #334155;
  color: #94a3b8;
}

.dark .file-name {
  color: #e2e8f0;
}

.dark .file-desc {
  color: #94a3b8;
}

.dark .filter-bar .el-input__wrapper,
.dark .filter-bar .el-select .el-input__wrapper {
  background-color: #1e293b;
}
</style>
